// Service de détection de gestes avec TensorFlow.js
import * as tf from '@tensorflow/tfjs';
import * as handpose from '@tensorflow-models/handpose';

class GestureDetector {
  constructor() {
    this.model = null;
    this.isRunning = false;
    this.videoElement = null;
    this.canvasElement = null;
    this.canvasCtx = null;
    this.onResultsCallback = null;
    this.animationFrameId = null;
  }

  // Initialiser TensorFlow.js et le modèle HandPose
  async initialize(videoElement, canvasElement) {
    try {
      console.log('🔄 Initialisation TensorFlow.js...');
      
      this.videoElement = videoElement;
      this.canvasElement = canvasElement;
      this.canvasCtx = canvasElement.getContext('2d');

      // Initialiser TensorFlow.js backend
      await tf.ready();
      console.log('✅ TensorFlow.js prêt');

      // Charger le modèle HandPose
      console.log('🔄 Chargement du modèle HandPose...');
      this.model = await handpose.load();
      console.log('✅ Modèle HandPose chargé');

      return true;
    } catch (error) {
      console.error('❌ Erreur initialisation:', error);
      return false;
    }
  }

  // Démarrer la détection en boucle
  async start() {
    if (!this.model || !this.videoElement) {
      console.error('❌ Modèle ou vidéo non initialisé');
      return false;
    }

    this.isRunning = true;
    console.log('✅ Détection démarrée');
    this.detectLoop();
    return true;
  }

  // Boucle de détection
  async detectLoop() {
    if (!this.isRunning) return;

    try {
      // Détecter les mains
      const predictions = await this.model.estimateHands(this.videoElement);

      // Effacer le canvas
      this.canvasCtx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);
      
      // Dessiner la vidéo
      this.canvasCtx.drawImage(
        this.videoElement,
        0, 0,
        this.canvasElement.width,
        this.canvasElement.height
      );

      if (predictions.length > 0) {
        const hand = predictions[0];
        
        // Dessiner la main
        this.drawHand(hand);
        
        // Reconnaître le geste
        const gesture = this.recognizeGesture(hand.landmarks);
        
        // Appeler le callback
        if (this.onResultsCallback) {
          this.onResultsCallback({
            detected: true,
            gesture: gesture,
            landmarks: hand.landmarks
          });
        }
      } else {
        // Aucune main détectée
        if (this.onResultsCallback) {
          this.onResultsCallback({
            detected: false,
            gesture: null,
            landmarks: null
          });
        }
      }
    } catch (error) {
      console.error('Erreur détection:', error);
    }

    // Continuer la boucle
    this.animationFrameId = requestAnimationFrame(() => this.detectLoop());
  }

  // Dessiner la main sur le canvas
  drawHand(hand) {
    const landmarks = hand.landmarks;

    // Connexions des doigts
    const connections = [
      [0, 1], [1, 2], [2, 3], [3, 4], // Pouce
      [0, 5], [5, 6], [6, 7], [7, 8], // Index
      [0, 9], [9, 10], [10, 11], [11, 12], // Majeur
      [0, 13], [13, 14], [14, 15], [15, 16], // Annulaire
      [0, 17], [17, 18], [18, 19], [19, 20], // Auriculaire
      [5, 9], [9, 13], [13, 17] // Paume
    ];

    // Dessiner les connexions
    this.canvasCtx.strokeStyle = '#00FF00';
    this.canvasCtx.lineWidth = 2;

    connections.forEach(([start, end]) => {
      this.canvasCtx.beginPath();
      this.canvasCtx.moveTo(landmarks[start][0], landmarks[start][1]);
      this.canvasCtx.lineTo(landmarks[end][0], landmarks[end][1]);
      this.canvasCtx.stroke();
    });

    // Dessiner les points
    landmarks.forEach(([x, y]) => {
      this.canvasCtx.fillStyle = '#FF0000';
      this.canvasCtx.beginPath();
      this.canvasCtx.arc(x, y, 5, 0, 2 * Math.PI);
      this.canvasCtx.fill();
    });
  }

  // Compter les doigts levés
  countFingers(landmarks) {
    let fingersUp = 0;

    // Pouce (comparaison horizontale)
    // landmarks[4] = bout du pouce, landmarks[3] = articulation
    if (landmarks[4][0] < landmarks[3][0] - 30) {
      fingersUp++;
    }

    // Autres doigts (comparaison verticale)
    const fingerTips = [8, 12, 16, 20]; // Bouts des doigts
    const fingerPips = [6, 10, 14, 18]; // Articulations

    fingerTips.forEach((tipIndex, i) => {
      const pipIndex = fingerPips[i];
      // Si le bout est au-dessus de l'articulation (Y plus petit)
      if (landmarks[tipIndex][1] < landmarks[pipIndex][1] - 20) {
        fingersUp++;
      }
    });

    return fingersUp;
  }

  // Reconnaître le geste
  recognizeGesture(landmarks) {
    const fingersCount = this.countFingers(landmarks);

    // Pierre : 0 ou 1 doigt (poing fermé)
    if (fingersCount <= 1) {
      return 'Pierre';
    }

    // Feuille : 4 ou 5 doigts (main ouverte)
    if (fingersCount >= 4) {
      return 'Feuille';
    }

    // Ciseaux : 2 doigts (index et majeur levés)
    if (fingersCount === 2) {
      const indexUp = landmarks[8][1] < landmarks[6][1] - 20;
      const middleUp = landmarks[12][1] < landmarks[10][1] - 20;
      
      if (indexUp && middleUp) {
        return 'Ciseaux';
      }
    }

    return null;
  }

  // Arrêter la détection
  stop() {
    this.isRunning = false;
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
    console.log('🛑 Détection arrêtée');
  }

  // Définir le callback
  setOnResults(callback) {
    this.onResultsCallback = callback;
  }
}

export default GestureDetector;