import React, { useEffect, useState } from 'react';
import apiService from '../services/api';

const Leaderboard = ({ currentPlayer }) => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLeaderboard();
    
    // Rafraîchir toutes les 10 secondes
    const interval = setInterval(fetchLeaderboard, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const data = await apiService.getLeaderboard(10);
      setLeaderboard(data);
      setError(null);
    } catch (err) {
      console.error('Erreur récupération classement:', err);
      setError('Impossible de charger le classement');
    } finally {
      setLoading(false);
    }
  };

  const getMedalEmoji = (rank) => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return `#${rank}`;
    }
  };

  if (loading && leaderboard.length === 0) {
    return (
      <div className="leaderboard">
        <h2>🏆 Classement</h2>
        <div className="loading">Chargement...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="leaderboard">
        <h2>🏆 Classement</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="leaderboard">
      <h2>🏆 Classement</h2>
      
      {leaderboard.length === 0 ? (
        <p className="no-data">Aucun joueur pour le moment</p>
      ) : (
        <div className="leaderboard-list">
          {leaderboard.map((player) => (
            <div
              key={player.rank}
              className={`leaderboard-item ${
                currentPlayer === player.player_name ? 'current-player' : ''
              } ${player.rank <= 3 ? 'top-three' : ''}`}
            >
              <div className="rank">{getMedalEmoji(player.rank)}</div>
              
              <div className="player-info">
                <div className="player-name">
                  {player.player_name}
                  {currentPlayer === player.player_name && (
                    <span className="you-badge">Vous</span>
                  )}
                </div>
                <div className="player-stats">
                  {player.games_played} parties • {player.wins} victoires
                </div>
              </div>
              
              <div className="player-score">
                <div className="score">{player.score}</div>
                <div className="win-rate">{player.win_rate}%</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Leaderboard;