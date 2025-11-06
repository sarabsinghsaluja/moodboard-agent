import React, { useState } from 'react';
import './App.css';
import ImageUpload from './components/ImageUpload';
import MoodDisplay from './components/MoodDisplay';
import MusicRecommendations from './components/MusicRecommendations';

function App() {
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [resetKey, setResetKey] = useState(0);

  const handleImageUpload = async (file) => {
    setAnalyzing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/analyze?track_limit=20&include_playlists=true', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze image');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
    setAnalyzing(false);
    setResetKey(prev => prev + 1); // Force re-render of ImageUpload
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎨 MoodBoard Agent 🎵</h1>
        <p>Upload an image to detect its mood and discover matching music</p>
      </header>

      <main className="App-main">
        <ImageUpload key={resetKey} onImageUpload={handleImageUpload} analyzing={analyzing} />

        {(result || error) && (
          <div className="reset-button-container">
            <button className="reset-button" onClick={handleReset}>
              🔄 Analyze Another Image
            </button>
          </div>
        )}

        {error && (
          <div className="error-message">
            <p>❌ Error: {error}</p>
          </div>
        )}

        {analyzing && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Analyzing your image...</p>
          </div>
        )}

        {result && (
          <>
            <MoodDisplay moodAnalysis={result.mood_analysis} />
            <MusicRecommendations
              recommendations={result.music_recommendations}
              playlists={result.playlists}
            />
          </>
        )}
      </main>

      <footer className="App-footer">
        <p>Powered by Anthropic Claude & Spotify</p>
      </footer>
    </div>
  );
}

export default App;
