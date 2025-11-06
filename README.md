# 🎨🎵 MoodBoard Agent

A creative multimodal AI project that analyzes images to detect moods and suggests matching music from Spotify.

## Features

- **Image Mood Detection**: Upload an image and AI analyzes its emotional mood using vision models (GPT-4V or Claude)
- **10 Mood Categories**: Calm, Energetic, Romantic, Dark, Melancholic, Joyful, Mysterious, Aggressive, Dreamy, Uplifting
- **Music Recommendations**: Get Spotify track recommendations tailored to the detected mood
- **Playlist Discovery**: Find existing Spotify playlists matching the mood
- **REST API**: Easy-to-use FastAPI endpoints for integration

## How It Works

1. **Upload an image** → Image is analyzed using AI vision models
2. **Mood detection** → AI identifies primary and secondary moods based on:
   - Colors (warm/cool tones, saturation, brightness)
   - Composition and subjects
   - Lighting and atmosphere
3. **Music matching** → Spotify API finds tracks matching the mood's:
   - Energy level
   - Emotional valence (positive/negative)
   - Tempo range
   - Associated genres

## Quick Start

### Prerequisites

- Python 3.8+
- API keys for:
  - OpenAI (for GPT-4V) **OR** Anthropic (for Claude)
  - Spotify Developer Account

### Installation

1. Clone and navigate to the project:
```bash
cd moodboard-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
- Get OpenAI key: https://platform.openai.com/api-keys
- Get Anthropic key: https://console.anthropic.com/
- Get Spotify credentials: https://developer.spotify.com/dashboard

### Running the API

```bash
# From the project root
python -m uvicorn src.api:app --reload
```

The API will be available at: `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

## API Endpoints

### Complete Analysis
```bash
POST /analyze
```
Upload an image for complete mood analysis + music recommendations

**Example:**
```bash
curl -X POST "http://localhost:8000/analyze?track_limit=10&include_playlists=true" \
  -F "file=@path/to/image.jpg"
```

### Mood Detection Only
```bash
POST /mood
```
Analyze image mood without music recommendations

### Get Music by Mood
```bash
GET /recommendations/{mood_name}?limit=20
```
Get music recommendations for a specific mood

### List Available Moods
```bash
GET /moods
```
Get all mood categories with descriptions and attributes

### Search Playlists
```bash
GET /playlists/{mood_name}?limit=10
```
Find existing Spotify playlists for a mood

## Supported Moods

| Mood | Energy | Valence | Genres | Use Cases |
|------|--------|---------|--------|-----------|
| **Calm** | Low | Positive | Ambient, Lo-fi, Classical | Meditation, Study |
| **Energetic** | High | Positive | EDM, Pop, Rock | Workout, Party |
| **Romantic** | Medium | Positive | R&B, Soul, Jazz | Date night, Relaxation |
| **Dark** | Medium | Negative | Industrial, Metal, Dark Ambient | Intense focus, Drama |
| **Melancholic** | Low | Negative | Indie, Folk, Blues | Reflection, Contemplation |
| **Joyful** | High | Very Positive | Pop, Funk, Disco | Celebration, Happy moments |
| **Mysterious** | Medium | Neutral | Ambient, Experimental | Exploration, Curiosity |
| **Aggressive** | Very High | Negative | Metal, Hardcore, Punk | Intense workout, Anger release |
| **Dreamy** | Low | Positive | Dream Pop, Shoegaze | Sleep, Daydreaming |
| **Uplifting** | High | Positive | Trance, Inspirational | Motivation, Hope |

## Example Usage

### Python Client

```python
import requests

# Upload image for analysis
with open("sunset.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"file": f},
        params={"track_limit": 15, "include_playlists": True}
    )

result = response.json()
print(f"Detected mood: {result['mood_analysis']['primary_mood']}")
print(f"Confidence: {result['mood_analysis']['confidence']}")
print(f"Found {result['music_recommendations']['track_count']} tracks")
```

### JavaScript Client

```javascript
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('http://localhost:8000/analyze?track_limit=20', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log('Primary mood:', data.mood_analysis.primary_mood);
console.log('Tracks:', data.music_recommendations.tracks);
```

## Project Structure

```
moodboard-agent/
├── src/
│   ├── __init__.py
│   ├── api.py                  # FastAPI application
│   ├── image_analyzer.py       # AI vision mood detection
│   ├── music_matcher.py        # Spotify integration
│   └── mood_classifier.py      # Mood definitions
├── data/
│   └── mood_music_mappings.json  # Mood-to-music configurations
├── models/                     # (Optional) Local ML models
├── tests/                      # Unit tests
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md
```

## Configuration

### Vision Provider

Choose between OpenAI or Anthropic in `.env`:
```bash
VISION_PROVIDER=openai  # or "anthropic"
```

### Mood Customization

Edit `src/mood_classifier.py` to:
- Add new moods
- Adjust energy/valence levels
- Modify genre associations
- Update keywords

### Music Parameters

Customize in `data/mood_music_mappings.json`:
- Spotify genre preferences
- Audio feature targets
- Artist recommendations

## Advanced Features

### Multi-Mood Analysis

The system detects primary and secondary moods for nuanced recommendations:
- 60% of tracks match primary mood
- 40% blend in secondary moods
- Creates more diverse, interesting playlists

### Audio Feature Matching

Spotify recommendations use:
- **Energy**: Intensity level (0-1)
- **Valence**: Musical positivity (0-1)
- **Tempo**: BPM range
- **Acousticness**: Acoustic vs electronic
- **Instrumentalness**: Vocal vs instrumental

## Limitations

- Requires active API keys (costs may apply)
- Spotify free tier has rate limits
- Vision API calls count toward usage quotas
- Image analysis accuracy depends on image quality

## Future Enhancements

- [ ] Add local ML models (CLIP, ViT) for offline mood detection
- [ ] Create web UI for image upload and visualization
- [ ] Support for video mood analysis
- [ ] Generate custom Spotify playlists (requires user auth)
- [ ] Multi-language support
- [ ] Batch image processing
- [ ] Mood history tracking and analytics

## Troubleshooting

**Error: "Image analyzer not initialized"**
- Check your `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`

**Error: "Music matcher not initialized"**
- Verify `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` in `.env`
- Ensure credentials are from https://developer.spotify.com/dashboard

**No tracks returned**
- Some mood/genre combinations may have limited results
- Try adjusting the mood parameters in `mood_classifier.py`

## Contributing

Contributions welcome! Areas for improvement:
- Additional mood categories
- Better genre mappings
- UI/UX enhancements
- Testing and documentation

## License

MIT License - feel free to use for personal or commercial projects.

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [OpenAI GPT-4V](https://openai.com/) / [Anthropic Claude](https://anthropic.com/) - Vision AI
- [Spotify API](https://developer.spotify.com/) - Music data
- [Spotipy](https://spotipy.readthedocs.io/) - Spotify Python client

---

**Enjoy creating your mood-matched soundscapes! 🎨🎵**
