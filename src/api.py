"""
FastAPI application for MoodBoard Agent.
Upload an image and get mood-matched music recommendations.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .image_analyzer import ImageMoodAnalyzer
from .music_matcher import MusicMatcher
from .mood_classifier import MoodClassifier


# Pydantic models for responses
class MoodAnalysisResponse(BaseModel):
    """Response model for mood analysis."""
    primary_mood: str
    secondary_moods: List[str]
    confidence: float
    reasoning: str
    visual_elements: dict


class TrackInfo(BaseModel):
    """Track information."""
    name: str
    artist: str
    album: str
    url: str
    preview_url: Optional[str]
    duration_ms: int
    image: Optional[str]


class MusicRecommendationResponse(BaseModel):
    """Response model for music recommendations."""
    mood: str
    mood_description: str
    track_count: int
    tracks: List[dict]
    genres: List[str]


class FullAnalysisResponse(BaseModel):
    """Complete response with mood analysis and music recommendations."""
    mood_analysis: dict
    music_recommendations: dict
    playlists: Optional[List[dict]] = None


# Initialize FastAPI app
app = FastAPI(
    title="MoodBoard Agent API",
    description="Upload an image to detect its mood and get matching music recommendations",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize components (will be set on startup)
image_analyzer: Optional[ImageMoodAnalyzer] = None
music_matcher: Optional[MusicMatcher] = None


@app.on_event("startup")
async def startup_event():
    """Initialize analyzers on startup."""
    global image_analyzer, music_matcher

    # Determine which vision provider to use
    vision_provider = os.getenv("VISION_PROVIDER", "openai")

    try:
        image_analyzer = ImageMoodAnalyzer(provider=vision_provider)
        print(f"✓ Image analyzer initialized with {vision_provider}")
    except Exception as e:
        print(f"⚠ Image analyzer initialization failed: {e}")

    try:
        music_matcher = MusicMatcher()
        print("✓ Music matcher initialized")
    except Exception as e:
        print(f"⚠ Music matcher initialization failed: {e}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "MoodBoard Agent API",
        "version": "0.1.0",
        "description": "Upload an image to detect its mood and get matching music",
        "endpoints": {
            "POST /analyze": "Upload image for complete mood + music analysis",
            "POST /mood": "Analyze image mood only",
            "GET /moods": "List all available moods",
            "GET /recommendations/{mood}": "Get music recommendations for a mood"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "image_analyzer": image_analyzer is not None,
        "music_matcher": music_matcher is not None
    }


@app.get("/moods")
async def list_moods():
    """Get list of all available moods with descriptions."""
    moods = MoodClassifier.get_all_moods()

    return {
        "moods": [
            {
                "name": name,
                "description": MoodClassifier.get_mood_description(name),
                "energy": mood.energy,
                "valence": mood.valence,
                "genres": mood.genres,
                "keywords": mood.keywords
            }
            for name, mood in moods.items()
        ]
    }


@app.post("/mood")
async def analyze_mood(file: UploadFile = File(...)):
    """
    Analyze the mood of an uploaded image.

    Args:
        file: Image file (JPEG, PNG, GIF, WebP)

    Returns:
        Mood analysis results
    """
    if not image_analyzer:
        raise HTTPException(
            status_code=503,
            detail="Image analyzer not initialized. Check API keys."
        )

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )

    try:
        # Read image bytes
        image_bytes = await file.read()

        # Analyze mood
        result = image_analyzer.analyze_image_bytes(
            image_bytes,
            filename=file.filename
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing image: {str(e)}"
        )


@app.get("/recommendations/{mood_name}")
async def get_recommendations(
    mood_name: str,
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    Get music recommendations for a specific mood.

    Args:
        mood_name: Name of the mood
        limit: Number of tracks to return (1-100)

    Returns:
        Music recommendations
    """
    if not music_matcher:
        raise HTTPException(
            status_code=503,
            detail="Music matcher not initialized. Check Spotify credentials."
        )

    # Validate mood exists
    if mood_name not in MoodClassifier.get_mood_names():
        raise HTTPException(
            status_code=404,
            detail=f"Mood '{mood_name}' not found. Use /moods to see available moods."
        )

    try:
        recommendations = music_matcher.get_recommendations_by_mood(
            mood_name,
            limit=limit
        )
        return recommendations

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )


@app.post("/analyze")
async def analyze_full(
    file: UploadFile = File(...),
    track_limit: int = Query(default=20, ge=1, le=100),
    include_playlists: bool = Query(default=False)
):
    """
    Complete analysis: detect image mood and get matching music recommendations.

    Args:
        file: Image file (JPEG, PNG, GIF, WebP)
        track_limit: Number of tracks to return (1-100)
        include_playlists: Whether to include existing playlist suggestions

    Returns:
        Complete mood analysis and music recommendations
    """
    if not image_analyzer:
        raise HTTPException(
            status_code=503,
            detail="Image analyzer not initialized. Check API keys."
        )

    if not music_matcher:
        raise HTTPException(
            status_code=503,
            detail="Music matcher not initialized. Check Spotify credentials."
        )

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )

    try:
        # Read image bytes
        image_bytes = await file.read()

        # Analyze mood
        mood_analysis = image_analyzer.analyze_image_bytes(
            image_bytes,
            filename=file.filename
        )

        # Get music recommendations based on detected moods
        music_recommendations = music_matcher.get_multi_mood_recommendations(
            primary_mood=mood_analysis["primary_mood"],
            secondary_moods=mood_analysis.get("secondary_moods", []),
            limit=track_limit
        )

        # Optionally get playlist suggestions
        playlists = None
        if include_playlists:
            try:
                playlists = music_matcher.search_playlist_by_mood(
                    mood_analysis["primary_mood"],
                    limit=5
                )
            except Exception as e:
                print(f"Error fetching playlists: {e}")

        return {
            "mood_analysis": mood_analysis,
            "music_recommendations": music_recommendations,
            "playlists": playlists
        }

    except Exception as e:
        import traceback
        print(f"Error during analysis: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error during analysis: {str(e)}"
        )


@app.get("/playlists/{mood_name}")
async def get_playlists(
    mood_name: str,
    limit: int = Query(default=10, ge=1, le=50)
):
    """
    Search for existing Spotify playlists matching a mood.

    Args:
        mood_name: Name of the mood
        limit: Number of playlists to return (1-50)

    Returns:
        List of playlist suggestions
    """
    if not music_matcher:
        raise HTTPException(
            status_code=503,
            detail="Music matcher not initialized. Check Spotify credentials."
        )

    # Validate mood exists
    if mood_name not in MoodClassifier.get_mood_names():
        raise HTTPException(
            status_code=404,
            detail=f"Mood '{mood_name}' not found. Use /moods to see available moods."
        )

    try:
        playlists = music_matcher.search_playlist_by_mood(mood_name, limit=limit)
        return {"mood": mood_name, "playlists": playlists}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching playlists: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
