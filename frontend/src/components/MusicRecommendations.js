import React from 'react';
import './MusicRecommendations.css';

function MusicRecommendations({ recommendations, playlists }) {
  const formatDuration = (ms) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = ((ms % 60000) / 1000).toFixed(0);
    return `${minutes}:${seconds.padStart(2, '0')}`;
  };

  return (
    <div className="music-recommendations">
      <h2 className="section-title">Music Recommendations</h2>

      <div className="mood-info-bar">
        <div className="mood-badge">{recommendations.mood}</div>
        <p className="mood-description">{recommendations.mood_description}</p>
      </div>

      {recommendations.genres && recommendations.genres.length > 0 && (
        <div className="genres">
          <span className="genre-label">Genres:</span>
          {recommendations.genres.map((genre, index) => (
            <span key={index} className="genre-tag">
              {genre}
            </span>
          ))}
        </div>
      )}

      <div className="tracks-container">
        <h3 className="subsection-title">
          {recommendations.track_count} Tracks Found
        </h3>

        <div className="tracks-list">
          {recommendations.tracks.map((track, index) => (
            <div key={index} className="track-card">
              <div className="track-number">{index + 1}</div>

              {track.image && (
                <img
                  src={track.image}
                  alt={track.album}
                  className="track-image"
                />
              )}

              <div className="track-info">
                <h4 className="track-name">{track.name}</h4>
                <p className="track-artist">{track.artist}</p>
                <p className="track-album">{track.album}</p>
              </div>

              <div className="track-actions">
                <span className="track-duration">{formatDuration(track.duration_ms)}</span>
                {track.preview_url && (
                  <audio controls className="track-preview">
                    <source src={track.preview_url} type="audio/mpeg" />
                  </audio>
                )}
                {track.url && (
                  <a
                    href={track.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="spotify-link"
                  >
                    🎵 Open in Spotify
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {playlists && playlists.length > 0 && (
        <div className="playlists-container">
          <h3 className="subsection-title">Curated Playlists</h3>
          <div className="playlists-grid">
            {playlists.map((playlist, index) => (
              <div key={index} className="playlist-card">
                {playlist.image && (
                  <img
                    src={playlist.image}
                    alt={playlist.name}
                    className="playlist-image"
                  />
                )}
                <div className="playlist-info">
                  <h4 className="playlist-name">{playlist.name}</h4>
                  {playlist.description && (
                    <p className="playlist-description">{playlist.description}</p>
                  )}
                  {playlist.tracks && (
                    <p className="playlist-tracks">{playlist.tracks} tracks</p>
                  )}
                  {playlist.url && (
                    <a
                      href={playlist.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="playlist-link"
                    >
                      Open Playlist
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default MusicRecommendations;
