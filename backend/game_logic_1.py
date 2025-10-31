import cv2
import numpy as np
import random
import time

class ShifumiGame:
    def __init__(self):
        self.choices = ["Pierre", "Feuille", "Ciseaux"]
        self.player_choice = None
        self.computer_choice = None
        self.result = ""
        self.score_player = 0
        self.score_computer = 0
        
        self.game_state = "waiting"  # waiting, countdown, showing_result
        self.countdown_start = 0
        self.countdown_duration = 3
        
        # Détection de peau (HSV)
        self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Zone de détection
        self.roi_top = 100
        self.roi_bottom = 400
        self.roi_left = 100
        self.roi_right = 400
        
    def detect_hand(self, frame):
        """Détecte la main dans la ROI"""
        roi = frame[self.roi_top:self.roi_bottom, self.roi_left:self.roi_right]
        
        # Conversion en HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Masque de peau
        mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)
        
        # Filtrage
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 100)
        
        # Trouver les contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        return contours, mask, roi
    
    def analyze_gesture(self, contours):
        """Analyse le geste basé sur les contours"""
        if not contours:
            return None
        
        # Trouver le plus grand contour
        max_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(max_contour)
        
        if area < 5000:
            return None
        
        # Calculer l'enveloppe convexe
        hull = cv2.convexHull(max_contour, returnPoints=False)
        
        # Trouver les défauts de convexité
        if len(max_contour) > 3 and len(hull) > 3:
            defects = cv2.convexityDefects(max_contour, hull)
            
            if defects is not None:
                # Compter les doigts levés
                finger_count = 0
                
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(max_contour[s][0])
                    end = tuple(max_contour[e][0])
                    far = tuple(max_contour[f][0])
                    
                    # Calculer les angles
                    a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                    b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                    c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                    
                    angle = np.arccos((b**2 + c**2 - a**2) / (2 * b * c))
                    
                    # Si l'angle est inférieur à 90 degrés, c'est un doigt
                    if angle <= np.pi / 2 and d > 10000:
                        finger_count += 1
                
                # Déterminer le geste
                if finger_count == 0:
                    return "Pierre"
                elif finger_count == 1:
                    return "Ciseaux"
                elif finger_count >= 4:
                    return "Feuille"
        
        # Basé sur la zone si pas de défauts détectés
        perimeter = cv2.arcLength(max_contour, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        if circularity > 0.6:
            return "Pierre"
        elif area > 20000:
            return "Feuille"
        else:
            return "Ciseaux"
    
    def determine_winner(self, player, computer):
        """Détermine le gagnant"""
        if player == computer:
            return "Égalité!"
        elif (player == "Pierre" and computer == "Ciseaux") or \
             (player == "Feuille" and computer == "Pierre") or \
             (player == "Ciseaux" and computer == "Feuille"):
            self.score_player += 1
            return "Vous gagnez!"
        else:
            self.score_computer += 1
            return "L'ordinateur gagne!"
    
    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("=== SHIFUMI GAME ===")
        print("Instructions:")
        print("1. Placez votre main dans le cadre vert")
        print("2. Appuyez sur ESPACE pour jouer")
        print("3. Faites votre geste: Pierre, Feuille ou Ciseaux")
        print("4. Appuyez sur Q pour quitter")
        print("5. Appuyez sur R pour réinitialiser les scores")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            
            # Dessiner la zone de détection
            cv2.rectangle(frame, (self.roi_left, self.roi_top), 
                         (self.roi_right, self.roi_bottom), (0, 255, 0), 2)
            
            # Barre d'information en haut
            cv2.rectangle(frame, (0, 0), (w, 60), (50, 50, 50), -1)
            cv2.putText(frame, f"Vous: {self.score_player}  vs  Ordinateur: {self.score_computer}", 
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Détecter la main
            contours, mask, roi = self.detect_hand(frame)
            
            # État du jeu
            if self.game_state == "waiting":
                cv2.putText(frame, "ESPACE pour jouer", 
                           (w//2 - 150, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Afficher le geste détecté en temps réel
                gesture = self.analyze_gesture(contours)
                if gesture:
                    cv2.putText(frame, f"Geste: {gesture}", 
                               (10, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                # Afficher le masque dans un coin
                mask_resized = cv2.resize(mask, (150, 150))
                mask_colored = cv2.cvtColor(mask_resized, cv2.COLOR_GRAY2BGR)
                frame[70:220, w-160:w-10] = mask_colored
            
            elif self.game_state == "countdown":
                elapsed = time.time() - self.countdown_start
                remaining = self.countdown_duration - int(elapsed)
                
                if remaining > 0:
                    cv2.putText(frame, str(remaining), 
                               (w//2 - 40, h//2), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 8)
                    
                    # Détecter le geste du joueur
                    self.player_choice = self.analyze_gesture(contours)
                else:
                    # Fin du compte à rebours
                    if not self.player_choice:
                        self.player_choice = "Aucun"
                    
                    self.computer_choice = random.choice(self.choices)
                    
                    if self.player_choice != "Aucun":
                        self.result = self.determine_winner(self.player_choice, self.computer_choice)
                    else:
                        self.result = "Aucun geste detecte!"
                    
                    self.game_state = "showing_result"
                    self.countdown_start = time.time()
            
            elif self.game_state == "showing_result":
                # Fond semi-transparent
                overlay = frame.copy()
                cv2.rectangle(overlay, (50, h//2 - 150), (w - 50, h//2 + 150), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                
                # Afficher le résultat
                cv2.putText(frame, f"Vous: {self.player_choice}", 
                           (80, h//2 - 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
                cv2.putText(frame, f"Ordinateur: {self.computer_choice}", 
                           (80, h//2 - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
                
                # Couleur du résultat
                if "gagnez" in self.result:
                    color = (0, 255, 0)
                elif "Égalité" in self.result:
                    color = (255, 255, 0)
                else:
                    color = (0, 0, 255)
                
                cv2.putText(frame, self.result, 
                           (80, h//2 + 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
                
                if time.time() - self.countdown_start > 3:
                    self.game_state = "waiting"
                    self.player_choice = None
                    self.computer_choice = None
            
            cv2.imshow('Shifumi Game', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' ') and self.game_state == "waiting":
                self.game_state = "countdown"
                self.countdown_start = time.time()
                self.player_choice = None
            elif key == ord('r'):
                self.score_player = 0
                self.score_computer = 0
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = ShifumiGame()
    game.run()