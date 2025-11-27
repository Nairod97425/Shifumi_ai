import React, { useState, useEffect, useRef } from 'react';
import WebcamCapture from './components/WebcamCapture';
import apiService from './services/api';
import './App.css';

function App() {
  const [playerName, setPlayerName] = useState("Joueur 1");
  const [gameResult, setGameResult] = useState(null);
  const [playerStats, setPlayerStats] = useState(null);
  
  // États pour le jeu
  const [timer, setTimer] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [message, setMessage] = useState("Préparez-vous !");
  
  // --- CORRECTION ICI : Utilisation de Ref pour l'instantanéité ---
  const gestureRef = useRef(null); // Stocke la valeur réelle pour l'envoi API
  const [displayGesture, setDisplayGesture] = useState(null); // Juste pour l'affichage visuel

  useEffect(() => {
    const initPlayer = async () => {
      try {
        const player = await apiService.createPlayer(playerName);
        setPlayerStats(player);
      } catch (error) {
        console.error("Erreur init joueur", error);
      }
    };
    initPlayer();
  }, []);

  // Gestion du décompte (Timer)
  useEffect(() => {
    if (timer === 0) {
      finalizeMove();
      setTimer(null);
      return;
    }

    if (timer > 0) {
      const countdown = setTimeout(() => {
        setTimer(timer - 1);
      }, 1000);
      return () => clearTimeout(countdown);
    }
  }, [timer]);

  const startRound = () => {
    setGameResult(null);
    setMessage("Préparez votre main...");
    setIsPlaying(true);
    setTimer(3); // 3 secondes
    gestureRef.current = null; // On vide la mémoire du dernier geste
  };

  // --- CORRECTION MAJEURE ICI ---
  // Cette fonction tourne en permanence quand la caméra détecte quelque chose
  const handleGestureDetected = (gesture) => {
    // 1. On stocke immédiatement dans la Ref (mémoire instantanée)
    gestureRef.current = gesture;
    
    // 2. On met à jour l'affichage seulement si on joue (pour éviter de faire clignoter l'interface)
    if (isPlaying) {
      setDisplayGesture(gesture);
      console.log("Geste vu:", gesture); // Pour vérifier dans la console F12
    }
  };

  const finalizeMove = async () => {
    // On récupère la valeur depuis la Ref (c'est la plus fiable à l'instant T)
    const finalGesture = gestureRef.current;

    console.log("🛑 STOP ! Geste final capturé :", finalGesture);

    if (!finalGesture) {
      setMessage("⚠️ Aucun geste détecté ! Maintenez la main devant la caméra.");
      setIsPlaying(false);
      return;
    }

    try {
      setMessage(`Envoi de : ${finalGesture}...`);
      const result = await apiService.playGame(playerName, finalGesture);
      
      setGameResult(result);
      setPlayerStats(result.updated_score);
      setMessage(result.message);
    } catch (error) {
      console.error(error);
      setMessage("Erreur de connexion au serveur.");
    } finally {
      setIsPlaying(false);
      setDisplayGesture(null);
    }
  };

  return (
    <div className="app-container">
      <h1>Shifumi AI 🤖</h1>

      {playerStats && (
        <div className="stats-bar">
          <span>Joueur: {playerStats.player_name}</span>
          <span>Score: {playerStats.score}</span>
        </div>
      )}

      <div className="game-area" style={{ position: 'relative', width: '640px', margin: '0 auto' }}>
        
        {/* Affichage du Timer */}
        {timer > 0 && (
          <div className="timer-overlay">{timer}</div>
        )}

        {/* Affichage du geste détecté en temps réel (feedback visuel) */}
        {isPlaying && displayGesture && (
          <div style={{
            position: 'absolute', top: 10, right: 10, 
            background: 'rgba(0,0,0,0.7)', color: 'white', 
            padding: '10px', borderRadius: '5px', zIndex: 50
          }}>
            Détecté : {displayGesture}
          </div>
        )}

        <WebcamCapture 
          onGestureDetected={handleGestureDetected} 
          isActive={true} 
        />
      </div>

      <div className="game-controls">
        {!timer && (
          <button onClick={startRound} disabled={isPlaying}>
            {gameResult ? "Rejouer" : "Lancer la manche !"}
          </button>
        )}
      </div>

      <div className="result-area">
        <h2>{message}</h2>
        {gameResult && (
          <div className="final-result">
            <h3 style={{
              fontSize: '2rem',
              color: gameResult.result === 'Win' ? '#4caf50' : 
                     gameResult.result === 'Loss' ? '#f44336' : '#ff9800'
            }}>
              {gameResult.result === 'Win' ? 'VICTOIRE !' : 
               gameResult.result === 'Loss' ? 'PERDU...' : 'ÉGALITÉ'}
            </h3>
            <div style={{display:'flex', gap:'20px', justifyContent:'center', fontSize:'1.5rem'}}>
               <div>Vous: {gameResult.player_choice}</div>
               <div>VS</div>
               <div>IA: {gameResult.ai_choice}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;