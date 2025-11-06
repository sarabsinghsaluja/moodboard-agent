import React from 'react';
import './MoodDisplay.css';

function MoodDisplay({ moodAnalysis }) {
  const moodEmojis = {
    calm: '😌',
    energetic: '⚡',
    romantic: '💕',
    dark: '🌑',
    melancholic: '😔',
    joyful: '😄',
    mysterious: '🔮',
    aggressive: '😤',
    dreamy: '✨',
    uplifting: '🌟',
  };

  const getMoodEmoji = (mood) => {
    return moodEmojis[mood.toLowerCase()] || '🎨';
  };

  return (
    <div className="mood-display">
      <h2 className="section-title">Detected Mood</h2>

      <div className="primary-mood">
        <div className="mood-emoji">{getMoodEmoji(moodAnalysis.primary_mood)}</div>
        <div className="mood-info">
          <h3 className="mood-name">{moodAnalysis.primary_mood}</h3>
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{ width: `${moodAnalysis.confidence * 100}%` }}
            ></div>
          </div>
          <p className="confidence-text">
            {(moodAnalysis.confidence * 100).toFixed(0)}% confidence
          </p>
        </div>
      </div>

      {moodAnalysis.secondary_moods && moodAnalysis.secondary_moods.length > 0 && (
        <div className="secondary-moods">
          <h4>Secondary Moods</h4>
          <div className="mood-tags">
            {moodAnalysis.secondary_moods.map((mood, index) => (
              <span key={index} className="mood-tag">
                {getMoodEmoji(mood)} {mood}
              </span>
            ))}
          </div>
        </div>
      )}

      {moodAnalysis.reasoning && (
        <div className="reasoning">
          <h4>Analysis</h4>
          <p>{moodAnalysis.reasoning}</p>
        </div>
      )}

      {moodAnalysis.visual_elements && (
        <div className="visual-elements">
          <h4>Visual Elements</h4>
          <div className="elements-grid">
            {Object.entries(moodAnalysis.visual_elements).map(([key, value]) => (
              <div key={key} className="element-item">
                <span className="element-key">{key}:</span>
                <span className="element-value">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default MoodDisplay;
