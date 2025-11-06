"""
Music matcher using Spotify API to find and recommend music based on detected moods.
"""

import os
from typing import Dict, List, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from .mood_classifier import MoodClassifier, Mood


class MusicMatcher:
    """Matches detected moods to music recommendations using Spotify."""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize Spotify client.

        Args:
            client_id: Spotify client ID (or None to use env var)
            client_secret: Spotify client secret (or None to use env var)
        """
        client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "Spotify credentials required. Set SPOTIFY_CLIENT_ID and "
                "SPOTIFY_CLIENT_SECRET environment variables or pass them to __init__"
            )

        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self.spotify = spotipy.Spotify(auth_manager=auth_manager)

    def _get_mood_search_params(self, mood: Mood) -> Dict:
        """Convert mood attributes to Spotify search parameters."""
        return {
            "target_energy": mood.energy,
            "target_valence": mood.valence,
            "min_tempo": mood.tempo_range[0],
            "max_tempo": mood.tempo_range[1],
        }

    def get_recommendations_by_mood(
        self,
        mood_name: str,
        limit: int = 20,
        market: str = "US"
    ) -> Dict:
        """
        Get music recommendations for a specific mood.

        Args:
            mood_name: Name of the mood
            limit: Number of tracks to return (max 100)
            market: Spotify market/country code

        Returns:
            Dictionary with tracks and playlist info
        """
        mood = MoodClassifier.get_mood(mood_name)
        if not mood:
            raise ValueError(f"Unknown mood: {mood_name}")

        tracks = []

        # Strategy 1: Search by genre and mood keywords
        for genre in mood.genres[:2]:  # Use top 2 genres
            query = f"genre:{genre}"
            results = self.spotify.search(
                q=query,
                type="track",
                limit=min(10, limit // 2),
                market=market
            )

            for item in results['tracks']['items']:
                tracks.append(self._format_track(item))

        # Strategy 2: Get recommendations using seed genres and audio features
        if len(mood.genres) > 0:
            seed_genres = mood.genres[:5]  # Spotify allows max 5 seed genres
            params = self._get_mood_search_params(mood)

            try:
                recommendations = self.spotify.recommendations(
                    seed_genres=seed_genres,
                    limit=min(20, limit),
                    market=market,
                    **params
                )

                for item in recommendations['tracks']:
                    track = self._format_track(item)
                    if track not in tracks:  # Avoid duplicates
                        tracks.append(track)

            except Exception as e:
                print(f"Recommendation error: {e}")

        # Limit to requested number
        tracks = tracks[:limit]

        return {
            "mood": mood_name,
            "mood_description": MoodClassifier.get_mood_description(mood_name),
            "track_count": len(tracks),
            "tracks": tracks,
            "genres": mood.genres,
            "audio_attributes": {
                "energy": mood.energy,
                "valence": mood.valence,
                "tempo_range": mood.tempo_range
            }
        }

    def get_multi_mood_recommendations(
        self,
        primary_mood: str,
        secondary_moods: List[str] = None,
        limit: int = 30
    ) -> Dict:
        """
        Get recommendations considering multiple moods.

        Args:
            primary_mood: Main mood detected
            secondary_moods: Additional moods (optional)
            limit: Total number of tracks to return

        Returns:
            Dictionary with combined recommendations
        """
        secondary_moods = secondary_moods or []

        # Get more tracks for primary mood
        primary_limit = int(limit * 0.6)  # 60% for primary
        secondary_limit = limit - primary_limit

        primary_results = self.get_recommendations_by_mood(
            primary_mood,
            limit=primary_limit
        )

        all_tracks = primary_results["tracks"]
        all_genres = set(primary_results["genres"])

        # Add tracks from secondary moods
        if secondary_moods:
            tracks_per_secondary = secondary_limit // len(secondary_moods)

            for mood_name in secondary_moods:
                try:
                    results = self.get_recommendations_by_mood(
                        mood_name,
                        limit=tracks_per_secondary
                    )
                    all_tracks.extend(results["tracks"])
                    all_genres.update(results["genres"])
                except Exception as e:
                    print(f"Error getting recommendations for {mood_name}: {e}")

        return {
            "primary_mood": primary_mood,
            "secondary_moods": secondary_moods,
            "track_count": len(all_tracks),
            "tracks": all_tracks[:limit],
            "genres": list(all_genres)
        }

    def create_playlist_url(self, track_uris: List[str]) -> str:
        """
        Create a Spotify playlist URL from track URIs.

        Note: This creates a URL to open tracks, not an actual saved playlist
        (which would require user authentication).

        Args:
            track_uris: List of Spotify track URIs

        Returns:
            URL to open tracks in Spotify
        """
        # Extract track IDs from URIs
        track_ids = [uri.split(":")[-1] for uri in track_uris[:100]]  # Max 100

        # Create a comma-separated list
        ids_str = ",".join(track_ids)

        return f"https://open.spotify.com/tracks/{ids_str}"

    def _format_track(self, track: Dict) -> Dict:
        """Format Spotify track data for response."""
        return {
            "name": track["name"],
            "artist": ", ".join([artist["name"] for artist in track["artists"]]),
            "album": track["album"]["name"],
            "uri": track["uri"],
            "url": track["external_urls"]["spotify"],
            "preview_url": track.get("preview_url"),
            "duration_ms": track["duration_ms"],
            "image": track["album"]["images"][0]["url"] if track["album"]["images"] else None
        }

    def search_playlist_by_mood(self, mood_name: str, limit: int = 10) -> List[Dict]:
        """
        Search for existing Spotify playlists matching a mood.

        Args:
            mood_name: Name of the mood
            limit: Number of playlists to return

        Returns:
            List of playlist information
        """
        mood = MoodClassifier.get_mood(mood_name)
        if not mood:
            raise ValueError(f"Unknown mood: {mood_name}")

        # Search using mood keywords
        search_terms = [mood_name] + mood.keywords[:2]
        query = " ".join(search_terms)

        results = self.spotify.search(
            q=query,
            type="playlist",
            limit=limit
        )

        playlists = []
        for item in results['playlists']['items']:
            playlists.append({
                "name": item["name"],
                "description": item.get("description", ""),
                "url": item["external_urls"]["spotify"],
                "tracks_total": item["tracks"]["total"],
                "owner": item["owner"]["display_name"],
                "image": item["images"][0]["url"] if item["images"] else None
            })

        return playlists
