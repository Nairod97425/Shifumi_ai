import React, { useEffect, useRef, useState } from 'react';
// Assure-toi que ce fichier existe bien dans ton dossier services
import GestureDetector from '../services/gestureDirection'; 
import './WebcamCapture.css';

const WebcamCapture = ({ onGestureDetected, isActive }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const gestureDetectorRef = useRef(null);
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentGesture, setCurrentGesture] = useState(null);
  const [isDetectorReady, setIsDetectorReady] = useState(false);

  useEffect(() => {
    let stream = null;

    const startCamera = async () => {
      try {
        setIsLoading(true);
        console.log('🎬 Démarrage caméra...');

        // 1. Configuration de la caméra
        stream = await navigator.mediaDevices.getUserMedia({
          video: { 
            width: { ideal: 640 }, 
            height: { ideal: 480 },
            facingMode: 'user'
          }
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          
          // Promesse pour attendre que la vidéo joue vraiment
          await new Promise((resolve) => {
            videoRef.current.onloadedmetadata = () => {
              videoRef.current.play().then(resolve);
            };
          });
          
          setIsLoading(false);
          console.log('📹 Flux vidéo actif');

          // 2. Initialisation de l'IA (GestureDetector)
          // On ne lance l'IA que si la vidéo tourne
          if (!gestureDetectorRef.current) {
            gestureDetectorRef.current = new GestureDetector();
          }

          try {
            const initialized = await gestureDetectorRef.current.initialize(
              videoRef.current, 
              canvasRef.current
            );

            if (initialized) {
              setIsDetectorReady(true);
              
              gestureDetectorRef.current.setOnResults((results) => {
                 // Logique de détection
                if (results.detected && results.gesture) {
                  setCurrentGesture(results.gesture);
                  if (onGestureDetected) onGestureDetected(results.gesture);
                } else {
                  setCurrentGesture(null);
                }
              });

              await gestureDetectorRef.current.start();
              console.log('🧠 IA de détection activée');
            }
          } catch (aiError) {
            console.warn("L'IA n'a pas pu démarrer, mais la caméra fonctionne.", aiError);
            // On laisse la vidéo visible même si l'IA échoue
          }
        }

      } catch (err) {
        console.error('❌ Erreur:', err);
        setError("Impossible d'accéder à la caméra. Vérifiez les permissions.");
        setIsLoading(false);
      }
    };

    if (isActive) {
      startCamera();
    }

    // Nettoyage
    return () => {
      console.log('🛑 Arrêt caméra');
      if (gestureDetectorRef.current) {
        gestureDetectorRef.current.stop();
      }
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [isActive]); // On retire onGestureDetected des dépendances pour éviter les re-renders boucle

  return (
    <div className="webcam-container">
      <div className="webcam-wrapper">
        {isLoading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
            <p>Chargement...</p>
          </div>
        )}
        
        {error && (
          <div className="error-overlay">
            <p>⚠️ {error}</p>
          </div>
        )}

        {/* CORRECTION ÉCRAN NOIR : 
            Si le détecteur (canvas) n'est pas prêt, on affiche la vidéo brute.
            Si le détecteur est prêt, on cache la vidéo et on montre le canvas.
        */}
        <video
          ref={videoRef}
          className="webcam-video"
          autoPlay
          playsInline
          muted
          style={{ 
            display: isDetectorReady ? 'none' : 'block',
            transform: 'scaleX(-1)' // Effet miroir
          }}
        />
        
        <canvas
          ref={canvasRef}
          width={640}
          height={480}
          className="webcam-canvas"
          style={{ 
            display: isDetectorReady ? 'block' : 'none' 
          }}
        />

        {currentGesture && (
          <div className="gesture-indicator">
            <span className="gesture-icon">
              {currentGesture === 'Pierre' && '✊'}
              {currentGesture === 'Feuille' && '✋'}
              {currentGesture === 'Ciseaux' && '✌️'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default WebcamCapture;