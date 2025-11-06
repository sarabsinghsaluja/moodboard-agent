"""
Mood classification system with predefined mood categories and attributes.
"""

from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class Mood:
    """Represents a mood with its musical attributes."""
    name: str
    energy: float  # 0.0 to 1.0
    valence: float  # 0.0 (negative) to 1.0 (positive)
    tempo_range: tuple  # (min_bpm, max_bpm)
    genres: List[str]
    keywords: List[str]


class MoodClassifier:
    """Classifies and manages mood categories."""

    MOODS = {
        "calm": Mood(
            name="calm",
            energy=0.2,
            valence=0.6,
            tempo_range=(60, 90),
            genres=["ambient", "chill", "lo-fi", "classical", "acoustic"],
            keywords=["peaceful", "serene", "tranquil", "relaxing", "soft", "gentle"]
        ),
        "energetic": Mood(
            name="energetic",
            energy=0.9,
            valence=0.8,
            tempo_range=(120, 180),
            genres=["edm", "pop", "rock", "electronic", "dance"],
            keywords=["upbeat", "vibrant", "dynamic", "lively", "fast", "intense"]
        ),
        "romantic": Mood(
            name="romantic",
            energy=0.4,
            valence=0.7,
            tempo_range=(70, 100),
            genres=["r&b", "soul", "jazz", "classical", "love songs"],
            keywords=["love", "passion", "tender", "intimate", "warm", "dreamy"]
        ),
        "dark": Mood(
            name="dark",
            energy=0.6,
            valence=0.2,
            tempo_range=(80, 120),
            genres=["industrial", "metal", "dark ambient", "goth", "techno"],
            keywords=["mysterious", "ominous", "heavy", "brooding", "shadows", "intense"]
        ),
        "melancholic": Mood(
            name="melancholic",
            energy=0.3,
            valence=0.3,
            tempo_range=(60, 85),
            genres=["indie", "folk", "blues", "sad", "alternative"],
            keywords=["sad", "nostalgic", "reflective", "lonely", "wistful", "somber"]
        ),
        "joyful": Mood(
            name="joyful",
            energy=0.8,
            valence=0.9,
            tempo_range=(110, 140),
            genres=["pop", "funk", "disco", "happy", "uplifting"],
            keywords=["happy", "cheerful", "bright", "sunny", "playful", "optimistic"]
        ),
        "mysterious": Mood(
            name="mysterious",
            energy=0.5,
            valence=0.5,
            tempo_range=(70, 110),
            genres=["ambient", "electronic", "experimental", "cinematic"],
            keywords=["enigmatic", "atmospheric", "ethereal", "curious", "haunting"]
        ),
        "aggressive": Mood(
            name="aggressive",
            energy=0.95,
            valence=0.3,
            tempo_range=(140, 200),
            genres=["metal", "hardcore", "punk", "hard rock", "drum and bass"],
            keywords=["powerful", "fierce", "raw", "angry", "intense", "chaotic"]
        ),
        "dreamy": Mood(
            name="dreamy",
            energy=0.3,
            valence=0.7,
            tempo_range=(70, 95),
            genres=["ambient", "dream pop", "shoegaze", "indie", "chillwave"],
            keywords=["floating", "surreal", "hazy", "ethereal", "soft", "otherworldly"]
        ),
        "uplifting": Mood(
            name="uplifting",
            energy=0.7,
            valence=0.85,
            tempo_range=(100, 130),
            genres=["trance", "progressive", "inspirational", "gospel", "anthemic"],
            keywords=["inspiring", "hopeful", "motivating", "euphoric", "empowering"]
        )
    }

    @classmethod
    def get_mood(cls, mood_name: str) -> Mood:
        """Get mood object by name."""
        return cls.MOODS.get(mood_name.lower())

    @classmethod
    def get_all_moods(cls) -> Dict[str, Mood]:
        """Get all available moods."""
        return cls.MOODS

    @classmethod
    def get_mood_names(cls) -> List[str]:
        """Get list of all mood names."""
        return list(cls.MOODS.keys())

    @classmethod
    def find_similar_moods(cls, mood_name: str, threshold: float = 0.3) -> List[str]:
        """
        Find moods similar to the given mood based on energy and valence.

        Args:
            mood_name: Name of the reference mood
            threshold: Maximum distance to consider moods similar (0-1)

        Returns:
            List of similar mood names
        """
        reference_mood = cls.get_mood(mood_name)
        if not reference_mood:
            return []

        similar = []
        for name, mood in cls.MOODS.items():
            if name == mood_name:
                continue

            # Calculate Euclidean distance in energy-valence space
            distance = (
                (mood.energy - reference_mood.energy) ** 2 +
                (mood.valence - reference_mood.valence) ** 2
            ) ** 0.5

            if distance <= threshold:
                similar.append(name)

        return similar

    @classmethod
    def get_mood_description(cls, mood_name: str) -> str:
        """Get a human-readable description of a mood."""
        mood = cls.get_mood(mood_name)
        if not mood:
            return "Unknown mood"

        return (
            f"{mood.name.title()}: "
            f"Energy level {mood.energy:.0%}, "
            f"{'positive' if mood.valence > 0.5 else 'negative'} sentiment. "
            f"Associated with {', '.join(mood.genres[:3])} music."
        )
