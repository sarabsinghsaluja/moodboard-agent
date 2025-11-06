"""
Image mood analyzer using AI vision models (OpenAI GPT-4V or Anthropic Claude).
"""

import base64
import os
from typing import Dict, List, Optional
from pathlib import Path
from io import BytesIO

from PIL import Image
import openai
from anthropic import Anthropic

from .mood_classifier import MoodClassifier


class ImageMoodAnalyzer:
    """Analyzes images to detect mood using AI vision models."""

    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """
        Initialize the image analyzer.

        Args:
            provider: "openai" or "anthropic"
            api_key: API key for the chosen provider (or None to use env var)
        """
        self.provider = provider.lower()
        self.mood_names = MoodClassifier.get_mood_names()

        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _get_image_type(self, image_path: str) -> str:
        """Get MIME type from image extension."""
        ext = Path(image_path).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        return mime_types.get(ext, "image/jpeg")

    def _create_analysis_prompt(self) -> str:
        """Create the prompt for mood analysis."""
        mood_list = ", ".join(self.mood_names)

        return f"""Analyze this image and detect its emotional mood/atmosphere.

Available moods: {mood_list}

Analyze the image based on:
1. Colors (warm/cool tones, saturation, brightness)
2. Composition (balance, symmetry, chaos)
3. Subjects/content (people, nature, urban, abstract)
4. Lighting (bright, dark, dramatic, soft)
5. Overall atmosphere and feeling

Provide your response in this exact JSON format:
{{
    "primary_mood": "mood_name",
    "secondary_moods": ["mood1", "mood2"],
    "confidence": 0.85,
    "reasoning": "Brief explanation of why you chose these moods",
    "visual_elements": {{
        "dominant_colors": ["color1", "color2"],
        "brightness": "bright/medium/dark",
        "key_subjects": ["subject1", "subject2"]
    }}
}}

Only use moods from the provided list. Primary mood should be the strongest detected mood. Include 1-2 secondary moods if applicable."""

    def analyze_image_openai(self, image_path: str) -> Dict:
        """Analyze image using OpenAI GPT-4V."""
        base64_image = self._encode_image(image_path)
        image_type = self._get_image_type(image_path)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": self._create_analysis_prompt()
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        # Parse the JSON response
        import json
        result = json.loads(response.choices[0].message.content)
        return result

    def analyze_image_anthropic(self, image_path: str) -> Dict:
        """Analyze image using Anthropic Claude."""
        base64_image = self._encode_image(image_path)
        image_type = self._get_image_type(image_path)

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image_type,
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": self._create_analysis_prompt()
                        }
                    ],
                }
            ],
        )

        # Parse the JSON response
        import json
        result = json.loads(message.content[0].text)
        return result

    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze an image to detect its mood.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing mood analysis results
        """
        # Validate image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Validate image can be opened
        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception as e:
            raise ValueError(f"Invalid image file: {e}")

        # Analyze based on provider
        if self.provider == "openai":
            result = self.analyze_image_openai(image_path)
        else:
            result = self.analyze_image_anthropic(image_path)

        # Validate moods are in our list
        if result["primary_mood"] not in self.mood_names:
            # Default to calm if invalid mood returned
            result["primary_mood"] = "calm"

        result["secondary_moods"] = [
            m for m in result.get("secondary_moods", [])
            if m in self.mood_names
        ]

        return result

    def analyze_image_bytes(self, image_bytes: bytes, filename: str = "image.jpg") -> Dict:
        """
        Analyze an image from bytes (useful for API uploads).

        Args:
            image_bytes: Image data as bytes
            filename: Original filename (for extension detection)

        Returns:
            Dictionary containing mood analysis results
        """
        # Save to temp file and analyze
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        try:
            result = self.analyze_image(tmp_path)
        finally:
            os.unlink(tmp_path)

        return result
