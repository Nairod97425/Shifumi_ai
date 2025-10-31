# import cv2
# import numpy as np
# import random
# import time
# from database import init_db, SessionLocal, update_player_stats, save_game_history, get_leaderboard, get_player_history

# def determine_winner(player_choice, ai_choice):
#     """Détermine le gagnant et retourne le résultat."""
#     if player_choice == ai_choice:
#         return {"result": "Draw", "message": "Égalité !"}
#     elif (
#         (player_choice == "Pierre" and ai_choice == "Ciseaux") or
#         (player_choice == "Feuille" and ai_choice == "Pierre") or
#         (player_choice == "Ciseaux" and ai_choice == "Feuille")
#     ):
#         return {"result": "Win", "message": "Vous gagnez !"}
#     else:
#         return {"result": "Loss", "message": "L'ordinateur gagne !"}

# class ShifumiGame:
#     def __init__(self, player_name="Joueur1"):
#         self.player_name = player_name
#         self.choices = ["Pierre", "Feuille", "Ciseaux"]
#         self.player_choice = None
#         self.computer_choice = None
#         self.result = ""
#         self.score_player = 0
#         self.score_computer = 0

#         self.game_state = "waiting"
#         self.countdown_start = 0
#         self.countdown_duration = 3

#         self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
#         self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)

#         self.roi_top = 100
#         self.roi_bottom = 400
#         self.roi_left = 100
#         self.roi_right = 400

#         self.db = SessionLocal()

#     def __del__(self):
#         """Ferme la connexion à la base de données"""
#         if hasattr(self, 'db'):
#             self.db.close()

#     def detect_hand(self, frame):
#         """Détecte la main dans la ROI"""
#         roi = frame[self.roi_top:self.roi_bottom, self.roi_left:self.roi_right]

#         hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

#         mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)

#         kernel = np.ones((5, 5), np.uint8)
#         mask = cv2.dilate(mask, kernel, iterations=2)
#         mask = cv2.GaussianBlur(mask, (5, 5), 100)

#         contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#         return contours, mask, roi

#     def analyze_gesture(self, contours):
#         """Analyse le geste basé sur les contours"""
#         if not contours:
#             return None

#         max_contour = max(contours, key=cv2.contourArea)
#         area = cv2.contourArea(max_contour)

#         if area < 5000:
#             return None

#         hull = cv2.convexHull(max_contour, returnPoints=False)

#         if len(max_contour) > 3 and len(hull) > 3:
#             defects = cv2.convexityDefects(max_contour, hull)

#             if defects is not None:
#                 finger_count = 0

#                 for i in range(defects.shape[0]):
#                     s, e, f, d = defects[i, 0]
#                     start = tuple(max_contour[s][0])
#                     end = tuple(max_contour[e][0])
#                     far = tuple(max_contour[f][0])

#                     a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
#                     b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
#                     c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)

#                     angle = np.arccos((b**2 + c**2 - a**2) / (2 * b * c))

#                     if angle <= np.pi / 2 and d > 10000:
#                         finger_count += 1

#                 if finger_count == 0:
#                     return "Pierre"
#                 elif finger_count == 1:
#                     return "Ciseaux"
#                 elif finger_count >= 4:
#                     return "Feuille"

#         perimeter = cv2.arcLength(max_contour, True)
#         circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0

#         if circularity > 0.6:
#             return "Pierre"
#         elif area > 20000:
#             return "Feuille"
#         else:
#             return "Ciseaux"

#     def determine_winner(self, player, computer):
#         """Détermine le gagnant et met à jour la base de données."""
#         result = determine_winner(player, computer)

#         if result["result"] == "Win":
#             self.score_player += 1
#         elif result["result"] == "Loss":
#             self.score_computer += 1

#         try:
#             updated_player = update_player_stats(self.db, self.player_name, result["result"])
#             save_game_history(self.db, self.player_name, player, computer, result["result"])
#             print(f"Stats mises à jour - Score total: {updated_player.score}, Victoires: {updated_player.wins}")
#         except Exception as e:
#             print(f"Erreur lors de l'enregistrement: {e}")

#         return result["message"]

#     def show_leaderboard(self, frame):
#         """Affiche le classement sur le frame"""
#         h, w, _ = frame.shape

#         overlay = frame.copy()
#         cv2.rectangle(overlay, (50, 50), (w - 50, h - 50), (0, 0, 0), -1)
#         cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

#         cv2.putText(frame, "CLASSEMENT", (w//2 - 120, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

#         try:
#             leaderboard = get_leaderboard(self.db, limit=5)
#             y_pos = 150

#             cv2.putText(frame, "Rang  Joueur           Score  Victoires  Taux", (80, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
#             y_pos += 40

#             for idx, player in enumerate(leaderboard, 1):
#                 color = (0, 255, 0) if player.player_name == self.player_name else (255, 255, 255)
#                 text = f"{idx}.    {player.player_name[:15]:<15}  {player.score:>4}     {player.wins:>3}      {player.win_rate:.1f}%"
#                 cv2.putText(frame, text, (80, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
#                 y_pos += 35
#         except Exception as e:
#             cv2.putText(frame, f"Erreur: {str(e)}", (80, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

#         cv2.putText(frame, "Appuyez sur L pour fermer", (w//2 - 180, h - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

#     def run(self):
#         cap = cv2.VideoCapture(0)
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#         show_leaderboard_flag = False

#         print("=== SHIFUMI GAME ===")
#         print(f"Joueur: {self.player_name}")
#         print("\nInstructions:")
#         print("1. Placez votre main dans le cadre vert")
#         print("2. Appuyez sur ESPACE pour jouer")
#         print("3. Faites votre geste: Pierre, Feuille ou Ciseaux")
#         print("4. Appuyez sur L pour voir le classement")
#         print("5. Appuyez sur R pour réinitialiser les scores de session")
#         print("6. Appuyez sur Q pour quitter")

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             frame = cv2.flip(frame, 1)
#             h, w, c = frame.shape

#             if show_leaderboard_flag:
#                 self.show_leaderboard(frame)
#             else:
#                 cv2.rectangle(frame, (self.roi_left, self.roi_top), (self.roi_right, self.roi_bottom), (0, 255, 0), 2)

#                 cv2.rectangle(frame, (0, 0), (w, 60), (50, 50, 50), -1)
#                 cv2.putText(frame, f"{self.player_name} - Session: {self.score_player} vs {self.score_computer}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

#                 contours, mask, roi = self.detect_hand(frame)

#                 if self.game_state == "waiting":
#                     cv2.putText(frame, "ESPACE:Jouer | L:Classement | R:Reset | Q:Quitter", (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

#                     gesture = self.analyze_gesture(contours)
#                     if gesture:
#                         cv2.putText(frame, f"Geste: {gesture}", (10, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

#                     mask_resized = cv2.resize(mask, (150, 150))
#                     mask_colored = cv2.cvtColor(mask_resized, cv2.COLOR_GRAY2BGR)
#                     frame[70:220, w-160:w-10] = mask_colored

#                 elif self.game_state == "countdown":
#                     elapsed = time.time() - self.countdown_start
#                     remaining = self.countdown_duration - int(elapsed)

#                     if remaining > 0:
#                         cv2.putText(frame, str(remaining), (w//2 - 40, h//2), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 8)

#                         self.player_choice = self.analyze_gesture(contours)
#                     else:
#                         if not self.player_choice:
#                             self.player_choice = "Aucun"

#                         self.computer_choice = random.choice(self.choices)

#                         if self.player_choice != "Aucun":
#                             self.result = self.determine_winner(self.player_choice, self.computer_choice)
#                         else:
#                             self.result = "Aucun geste détecté!"

#                         self.game_state = "showing_result"
#                         self.countdown_start = time.time()

#                 elif self.game_state == "showing_result":
#                     overlay = frame.copy()
#                     cv2.rectangle(overlay, (50, h//2 - 150), (w - 50, h//2 + 150), (0, 0, 0), -1)
#                     cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

#                     cv2.putText(frame, f"Vous: {self.player_choice}", (80, h//2 - 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
#                     cv2.putText(frame, f"Ordinateur: {self.computer_choice}", (80, h//2 - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

#                     if "gagnez" in self.result:
#                         color = (0, 255, 0)
#                     elif "Égalité" in self.result:
#                         color = (255, 255, 0)
#                     else:
#                         color = (0, 0, 255)

#                     cv2.putText(frame, self.result, (80, h//2 + 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

#                     if time.time() - self.countdown_start > 3:
#                         self.game_state = "waiting"
#                         self.player_choice = None
#                         self.computer_choice = None

#             cv2.imshow('Shifumi Game', frame)

#             key = cv2.waitKey(1) & 0xFF
#             if key == ord('q'):
#                 break
#             elif key == ord(' ') and self.game_state == "waiting" and not show_leaderboard_flag:
#                 self.game_state = "countdown"
#                 self.countdown_start = time.time()
#                 self.player_choice = None
#             elif key == ord('r') and not show_leaderboard_flag:
#                 self.score_player = 0
#                 self.score_computer = 0
#                 print("Scores de session réinitialisés")
#             elif key == ord('l'):
#                 show_leaderboard_flag = not show_leaderboard_flag

#         cap.release()
#         cv2.destroyAllWindows()

# if __name__ == "__main__":
#     print("Initialisation de la base de données...")
#     init_db()

#     player_name = input("Entrez votre nom (ou appuyez sur Entrée pour 'Joueur1'): ").strip()
#     if not player_name:
#         player_name = "Joueur1"

#     print(f"\nBienvenue {player_name}!")

#     game = ShifumiGame(player_name=player_name)
#     game.run()
