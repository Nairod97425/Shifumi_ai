import React, { useState, useEffect } from 'react';
import WebcamCapture from './components/WebcamCapture';
import Leaderboard from './components/Leaderboard';
import apiService from './services/api';
import './App.css';

function App() {
  // États
  const [gameState, setGameState] = useState('welcome'); // welcome, playing, countdown, result
  const [playerName, setPlayerName] = useState('');
  const [playerData, setPlayerData] = useState(null);
  const [detectedGesture, setDetectedGesture] = useState(null);
  const [countdown, setCountdown] = useState(3);
  const [gameResult, setGameResult] = useState(null);
  const [error, setError] = useState(null);
  const [isApiConnected, setIsApiConnected] = useState(false);

  // Vérifier la connexion à l'API au démarrage
  useEffect(() => {
    checkApiConnection();
  }, []);

  const checkApiConnection = async () => {
    try {
      await apiService.healthCheck();
      setIsApiConnected(true);
      console.log('✅ API connectée');
    } catch (err) {
      setIsApiConnected(false);
      setError('Impossible de se connecter à l\'API. Vérifiez que le backend est démarré.');
      console.error('❌ API non disponible:', err);
    }
  };

  // Gérer le démarrage du jeu
  const handleStartGame = async () => {
    if (!playerName.trim()) {
      setError('Veuillez entrer votre nom');
      return;
    }

    try {
      setError(null);
      const player = await apiService.createPlayer(playerName.trim());
      setPlayerData(player);
      setGameState('playing');
    } catch (err) {
      setError('Erreur lors de la création du joueur');
      console.error(err);
    }
  };

  // Gérer la détection de geste
  const handleGestureDetected = (gesture) => {
    if (gameState === 'playing') {
      setDetectedGesture(gesture);
    }
  };

  // Lancer une partie
  const handlePlay = () => {
    if (!detectedGesture) {
      setError('Aucun geste détecté. Faites un geste devant la caméra.');
      return;
    }

    setError(null);
    setGameState('countdown');
    setCountdown(3);

    // Compte à rebours
    const countdownInterval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(countdownInterval);
          playGame();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  // Jouer contre l'IA
  const playGame = async () => {
    try {
      const result = await apiService.playGame(playerName, detectedGesture);
      setGameResult(result);
      setPlayerData(result.updated_score);
      setGameState('result');

      // Retour au jeu après 4 secondes
      setTimeout(() => {
        setGameState('playing');
        setGameResult(null);
        setDetectedGesture(null);
      }, 4000);
    } catch (err) {
      setError('Erreur lors du jeu');
      setGameState('playing');
      console.error(err);
    }
  };

  // Quitter le jeu
  const handleQuit = () => {
    setGameState('welcome');
    setPlayerName('');
    setPlayerData(null);
    setDetectedGesture(null);
    setGameResult(null);
    setError(null);
  };

  // Rendu de l'écran d'accueil
  const renderWelcome = () => (
    <div className="welcome-screen">
      <h1>🎮 Shifumi AI</h1>
      <p className="subtitle">Jouez au pierre-feuille-ciseaux contre l'IA</p>

      {!isApiConnected && (
        <div className="alert alert-error">
          ⚠️ Connexion à l'API impossible. Vérifiez que le backend est démarré sur http://localhost:8000
        </div>
      )}

      <div className="welcome-form">
        <input
          type="text"
          placeholder="Entrez votre nom"
          value={playerName}
          onChange={(e) => setPlayerName(e.target.value)}
          onKeyUp={(e) => e.key === 'Enter' && handleStartGame()}
          maxLength={50}
          className="name-input"
        />
        <button
          onClick={handleStartGame}
          disabled={!isApiConnected || !playerName.trim()}
          className="btn btn-primary"
        >
          Commencer
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="welcome-info">
        <h3>Comment jouer ?</h3>
        <ul>
          <li>✊ <strong>Pierre</strong> : Fermez votre poing</li>
          <li>✋ <strong>Feuille</strong> : Ouvrez votre main</li>
          <li>✌️ <strong>Ciseaux</strong> : Levez 2 doigts (index et majeur)</li>
        </ul>
      </div>

      <Leaderboard currentPlayer={null} />
    </div>
  );

  // Rendu de l'écran de jeu
  const renderGame = () => (
    <div className="game-screen">
      <div className="game-header">
        <div className="player-info-bar">
          <div className="player-name">👤 {playerName}</div>
          <div className="player-stats">
            <span>Score: <strong>{playerData?.score || 0}</strong></span>
            <span>Parties: <strong>{playerData?.games_played || 0}</strong></span>
            <span>Victoires: <strong>{playerData?.wins || 0}</strong></span>
            <span>Taux: <strong>{playerData?.win_rate || 0}%</strong></span>
          </div>
          <button onClick={handleQuit} className="btn btn-secondary">
            Quitter
          </button>
        </div>
      </div>

      <div className="game-content">
        <div className="game-main">
          <WebcamCapture
            onGestureDetected={handleGestureDetected}
            isActive={gameState === 'playing'}
          />

          {gameState === 'playing' && (
            <div className="game-controls">
              {detectedGesture ? (
                <div className="detected-gesture">
                  <p>Geste détecté : <strong>{detectedGesture}</strong></p>
                  <button onClick={handlePlay} className="btn btn-success btn-large">
                    🎯 Jouer !
                  </button>
                </div>
              ) : (
                <p className="waiting-gesture">
                  Montrez votre geste à la caméra...
                </p>
              )}
            </div>
          )}

          {gameState === 'countdown' && (
            <div className="countdown-overlay">
              <div className="countdown-number">{countdown}</div>
            </div>
          )}

          {gameState === 'result' && gameResult && (
            <div className="result-overlay">
              <div className={`result-card result-${gameResult.result.toLowerCase()}`}>
                <h2 className="result-title">
                  {gameResult.result === 'Win' && '🎉 Victoire !'}
                  {gameResult.result === 'Loss' && '😔 Défaite'}
                  {gameResult.result === 'Draw' && '🤝 Égalité'}
                </h2>
                
                <div className="result-choices">
                  <div className="choice">
                    <div className="choice-label">Vous</div>
                    <div className="choice-icon">
                      {gameResult.player_choice === 'Pierre' && '✊'}
                      {gameResult.player_choice === 'Feuille' && '✋'}
                      {gameResult.player_choice === 'Ciseaux' && '✌️'}
                    </div>
                    <div className="choice-name">{gameResult.player_choice}</div>
                  </div>
                  
                  <div className="vs">VS</div>
                  
                  <div className="choice">
                    <div className="choice-label">IA</div>
                    <div className="choice-icon">
                      {gameResult.ai_choice === 'Pierre' && '✊'}
                      {gameResult.ai_choice === 'Feuille' && '✋'}
                      {gameResult.ai_choice === 'Ciseaux' && '✌️'}
                    </div>
                    <div className="choice-name">{gameResult.ai_choice}</div>
                  </div>
                </div>

                <div className="result-message">{gameResult.message}</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Rendu principal
  return (
    <div className="App">
      {gameState === 'welcome' && renderWelcome()}
      {gameState === 'playing' && renderGame()}
    </div>
  );
}

export default App;
