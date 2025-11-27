# ✊✋✌️ Shifumi AI Project

Application Fullstack de Pierre-Feuille-Ciseaux utilisant l'intelligence artificielle pour détecter les gestes de la main via la webcam.

## 🏗️ Architecture

- **Backend** : Python (FastAPI, SQLAlchemy, SQLite). Gère la logique du jeu, les scores et la base de données.
- **Frontend** : React (Vite). Gère l'interface utilisateur et la capture vidéo.
- **IA** : Computer Vision (OpenCV/MediaPipe) pour la reconnaissance de gestes.

## 🛠️ Prérequis

- Python 3.9 ou supérieur
- Node.js 16 ou supérieur
- Une webcam fonctionnelle

---

## 🚀 Installation et Lancement

Ce projet nécessite deux terminaux : un pour le serveur API (Backend) et un pour l'interface (Frontend).

### 1. Backend (API Python)

Dans le premier terminal, installez les dépendances et lancez le serveur :

```bash
# 1. Créer un environnement virtuel (recommandé)
python -m venv venv

# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 2. Installer les paquets requis
pip install -r requirements.txt

# 3. Lancer le serveur API
# Le serveur se lancera sur http://localhost:8000
python main.py
```

***Note : La base de données **shifumi**.db sera créée automatiquement au premier lancement.***

## 2. Frontend (React Application)
Dans un second terminal, lancez l'application web :

```bash
# 1. Installer les dépendances Node
npm install

# 2. Lancer le serveur de développement
npm run dev

```
Ouvrez ensuite votre navigateur sur le lien indiqué (généralement **http://localhost:5173**).

🔌 Points d'accès API (Endpoints)
L'API tourne sur **http://localhost:8000**. Vous pouvez voir la documentation interactive (Swagger) ici : **http://localhost:8000/docs**

Principales routes (voir **main.py**) :

**GET /health** : Vérifier l'état du serveur.

**POST /players/** : Créer ou récupérer un joueur.

**POST /play/** : Jouer un coup (envoie le geste détecté par le front).

**GET /leaderboard/** : Voir le classement.

# 🐛 Dépannage Caméra (Écran Noir)

Si la caméra reste noire :

Permissions : Vérifiez que le navigateur a l'autorisation d'accéder à la caméra (icône cadenas dans la barre d'adresse).

Contexte Sécurisé : Les navigateurs bloquent la caméra si vous n'êtes pas en **localhost** ou en **HTTPS**.

Double Utilisation : Vérifiez qu'aucun autre logiciel (Zoom, Teams, le script python **game_logic_1.py** lancé séparément) n'utilise déjà la caméra.

# 📝 Auteurs & Crédits

Projet Shifumi AI.

### Résumé des actions à faire :

1.  **Remplace** le contenu de ton fichier `WebcamCapture.jsx` par le code fourni ci-dessus (section 1).
2.  **Crée** le fichier `README.md` à la racine de ton projet avec le contenu de la section 2.
3.  **Lance** ton backend (`python main.py`) puis ton frontend (`npm run dev`) pour tester la connexion entre ton API et ton interface.