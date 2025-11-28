# ✊✋✌️ Shifumi GenAI Project

Une application Fullstack de Pierre-Feuille-Ciseaux **Next-Gen**.
Ce projet combine la **Vision par Ordinateur** (Client-side) pour détecter vos mouvements et une **IA Générative** (Server-side) pour vous affronter, analyser votre stratégie et vous provoquer ("Trash Talk").

## 🏗️ Architecture Hybride

Ce projet utilise une architecture moderne séparant la perception de la cognition :

* **👁️ Les Yeux (Frontend)** :
    * **React (Vite)** : Interface utilisateur réactive.
    * **TensorFlow.js / HandPose** : Détection de la main et reconnaissance du geste en temps réel directement dans le navigateur (Zéro latence vidéo).
* **🧠 Le Cerveau (Backend)** :
    * **Python (FastAPI)** : API REST performante.
    * **Groq API (Llama 3)** : IA Générative ultra-rapide qui analyse l'historique du joueur pour prédire son prochain coup et générer des commentaires contextuels.
    * **SQLite & SQLAlchemy** : Persistance des scores, historiques et classements.

---

## 🛠️ Prérequis

* **Python** 3.9 ou supérieur
* **Node.js** 16 ou supérieur
* Une **Webcam** fonctionnelle
* Une **Clé API Groq** (Gratuite, à récupérer sur [console.groq.com](https://console.groq.com))

---

## 🚀 Installation et Lancement

Ce projet nécessite deux terminaux : un pour le serveur API (Backend) et un pour l'interface (Frontend).

### 1. Backend (API Python & IA)

Dans le premier terminal :

```bash
# 1. Créer un environnement virtuel
python -m venv venv
```

### Activer l'environnement

### Windows :
```bash
.\venv\Scripts\activate

source venv/Scripts/activate
```

### Mac/Linux :
```bash
source venv/bin/activate
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

Configuration de l'IA (Important) : Créez un fichier nommé **.env** à la racine du dossier backend et ajoutez votre clé API Groq :

```Ini, TOML
GROQ_API_KEY=gsk_votre_cle_api_ici_xxxxxxxxxxxxxxxxxxxxx
```

Lancer le serveur :

# Le serveur se lancera sur http://localhost:8000
```bash
python main.py
```

Note : La base de données **shifumi.db** sera créée automatiquement au premier lancement.

### 2. Frontend (React Application)
Dans un second terminal, placez-vous dans le dossier frontend :

# 1. Installer les dépendances Node

```bash
npm install
```

# 2. Lancer le serveur de développement
```bash
npm run dev
```

Ouvrez ensuite votre navigateur sur le lien indiqué (généralement http://localhost:5173).

# 🔌 Fonctionnement de l'API

L'API tourne sur **http://localhost:8000**. Une documentation interactive (Swagger) est disponible sur : **http://localhost:8000/docs**.

Flux de données (Data Flow) :

1. Le Frontend détecte le geste (ex: "Pierre") via la webcam et TensorFlow.js.

2. Il envoie ce choix à la route **POST /play/**.

3. Le Backend récupère l'historique des 5 derniers coups du joueur en base de données.

4. Il envoie cet historique à Groq (Llama 3) avec un prompt système ("Agis comme un expert du Shifumi").

5. L'IA renvoie son coup (pour contrer le joueur) et une phrase de provocation.

6. Le résultat est renvoyé au Frontend pour affichage.

# 🐛 Dépannage

La caméra reste noire / ne démarre pas
Permissions : Vérifiez que le navigateur a l'autorisation d'accéder à la caméra.

HTTPS/Localhost : Les navigateurs bloquent l'accès webcam si le site n'est pas sécurisé (sauf sur localhost).

Conflit : Vérifiez qu'aucun autre logiciel (Zoom, Teams) ou script Python (OpenCV local) n'utilise déjà la caméra.

**L'IA joue au hasard ou ne répond pas intelligemment**
Vérifiez que votre fichier **.env** contient bien la clé **GROQ_API_KEY**.

Regardez les logs du terminal Python. Si l'API Groq échoue ou est injoignable, le système passe automatiquement en mode "Fallback" (Aléatoire) pour ne pas bloquer le jeu.

# 📝 Auteurs & Crédits

Projet Shifumi GenAI. Propulsé par Groq, TensorFlow.js et FastAPI.