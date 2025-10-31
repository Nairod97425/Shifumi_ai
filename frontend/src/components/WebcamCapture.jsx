import React, { useEffect, useRef, useState } from 'react';
import GestureDetector from '../services/gestureDirection';
import './WebcamCapture.css';

const WebcamCapture = ({ onGestureDetected, isActive }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const gestureDetectorRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentGesture, setCurrentGesture] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const initializeCamera = async () => {
      try {
        setIsLoading(true);
        setError(null);

        console.log('🎬 Démarrage initialisation caméra...');

        // Créer et initialiser le détecteur de gestes AVANT la webcam
        if (!gestureDetectorRef.current) {
          gestureDetectorRef.current = new GestureDetector();
        }

        // Demander l'accès à la webcam
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { 
            width: 640, 
            height: 480,
            facingMode: 'user'
          }
        });

        if (!isMounted) {
          stream.getTracks().forEach(track => track.stop());
          return;
        }

        if (videoRef.current) {
          videoRef.current.srcObject = stream;

          // Attendre que la vidéo soit prête
          await new Promise((resolve) => {
            videoRef.current.onloadedmetadata = resolve;
          });

          console.log('📹 Vidéo prête');

          // Initialiser le détecteur avec la vidéo et le canvas
          const initialized = await gestureDetectorRef.current.initialize(
            videoRef.current, 
            canvasRef.current
          );

          if (!initialized) {
            throw new Error('Échec initialisation détecteur');
          }

          // Définir le callback pour les résultats
          gestureDetectorRef.current.setOnResults((results) => {
            if (!isMounted) return;
            
            if (results.detected && results.gesture) {
              setCurrentGesture(results.gesture);
              if (onGestureDetected) {
                onGestureDetected(results.gesture);
              }
            } else {
              setCurrentGesture(null);
            }
          });

          // Démarrer la détection
          await gestureDetectorRef.current.start();
          
          if (isMounted) {
            setIsLoading(false);
            console.log('✅ Tout est prêt !');
          }
        }
      } catch (err) {
        console.error('❌ Erreur initialisation caméra:', err);
        if (isMounted) {
          if (err.name === 'NotAllowedError') {
            setError('Accès caméra refusé. Autorisez l\'accès dans les paramètres.');
          } else if (err.name === 'NotFoundError') {
            setError('Aucune caméra détectée sur votre appareil.');
          } else {
            setError(`Erreur: ${err.message}`);
          }
          setIsLoading(false);
        }
      }
    };

    if (isActive) {
      // Petit délai pour s'assurer que tout est chargé
      const timeoutId = setTimeout(() => {
        initializeCamera();
      }, 300);

      return () => {
        clearTimeout(timeoutId);
      };
    }

    // Nettoyage principal (quand isActive devient false ou composant se démonte)
    return () => {
      isMounted = false;
      
      // Copier la référence dans une variable locale AVANT le nettoyage
      const currentVideo = videoRef.current;
      const currentDetector = gestureDetectorRef.current;
      
      if (currentDetector) {
        currentDetector.stop();
      }
      
      if (currentVideo && currentVideo.srcObject) {
        const tracks = currentVideo.srcObject.getTracks();
        tracks.forEach(track => track.stop());
      }
    };
  }, [isActive, onGestureDetected]);

  return (
    <div className="webcam-container">
      <div className="webcam-wrapper">
        {isLoading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
            <p>Chargement de la caméra...</p>
          </div>
        )}
        
        {error && (
          <div className="error-overlay">
            <p>⚠️ {error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="retry-button"
            >
              Réessayer
            </button>
          </div>
        )}

        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          style={{ display: 'none' }}
        />
        
        <canvas
          ref={canvasRef}
          width={640}
          height={480}
          className="webcam-canvas"
        />

        {currentGesture && !isLoading && (
          <div className="gesture-indicator">
            <span className="gesture-icon">
              {currentGesture === 'Pierre' && '✊'}
              {currentGesture === 'Feuille' && '✋'}
              {currentGesture === 'Ciseaux' && '✌️'}
            </span>
            <span className="gesture-name">{currentGesture}</span>
          </div>
        )}
      </div>

      <div className="gesture-legend">
        <div className="legend-item">
          <span className="legend-icon">✊</span>
          <span className="legend-text">Pierre (poing fermé)</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">✋</span>
          <span className="legend-text">Feuille (main ouverte)</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">✌️</span>
          <span className="legend-text">Ciseaux (2 doigts)</span>
        </div>
      </div>
    </div>
  );
};

export default WebcamCapture;