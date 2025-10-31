from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import database
import schemas
import game_logic
from datetime import datetime, timezone

# Créer l'application FastAPI
app = FastAPI(
    title="Shifumi AI API",
    description="API pour le jeu Shifumi contre une IA",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes dapuis React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL du frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser la base de données au démarrage
@app.get("/startup")
async def startup_event():
    try:
        database.init_db()
        print("✅ Base de données initialisée")
        return {"message": "Base de données initialisée avec succès"}
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'initialisation de la base de données")

# Route de test
@app.get ('/')
def read_root():
    return {
        "message": "Bienvenue sur l'API Shifumi AI",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "players": "/players",
            "leaderboard": "/leaderboard",
            "play": "/play"
        }
    }

# Route de santé (health check)
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc)}

# Créer ou récupérer un joueur
@app.post("/players/", response_model=schemas.PlayerResponse)
def create_player(
    player: schemas.PlayerCreate,
    db: Session = Depends(database.get_db)
):
    """
    Crée un nouveau joueur ou récupère un joueur existant
    """
    # Vérifier si le joueur existe déjà
    db_player = db.query(database.PlayerScore).filter(
        database.PlayerScore.player_name == player.player_name
    ).first()
    
    if db_player:
        return db_player
    
    # Créer un nouveau joueur
    new_player = database.PlayerScore(player_name=player.player_name)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player

# Créer ou récupérer un joueur
@app.post("/players/", response_model=schemas.PlayerResponse)
def create_player(
    player: schemas.PlayerCreate,
    db: Session = Depends(database.get_db)
):
    """
    Crée un nouveau joueur ou récupère un joueur existant
    """
    # Vérifier si le joueur existe déjà
    db_player = db.query(database.PlayerScore).filter(
        database.PlayerScore.player_name == player.player_name
    ).first()
    
    if db_player:
        return db_player
    
    # Créer un nouveau joueur
    new_player = database.PlayerScore(player_name=player.player_name)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player

# Jouer une partie
@app.post("/play/", response_model=schemas.GameResult)
def play_game(
    game: schemas.GamePlay,
    db: Session = Depends(database.get_db)
):
    """
    Joue une partie de Shifumi contre l'IA
    """
    # Vérifier que le choix est valide
    if not game_logic.is_valid_choice(game.player_choice):
        raise HTTPException(
            status_code=400,
            detail="Choix invalide. Choisissez Pierre, Feuille ou Ciseaux"
        )
    
    # Récupérer ou créer le joueur
    player = db.query(database.PlayerScore).filter(
        database.PlayerScore.player_name == game.player_name
    ).first()
    
    if not player:
        player = database.PlayerScore(player_name=game.player_name)
        db.add(player)
        db.commit()
        db.refresh(player)
    
    # Générer le choix de l'IA
    ai_choice = game_logic.get_ai_choice()
    
    # Déterminer le gagnant
    result, message = game_logic.determine_winner(game.player_choice, ai_choice)
    
    # Mettre à jour les statistiques du joueur
    player.games_played += 1
    
    if result == "Win":
        player.wins += 1
        player.score = game_logic.calculate_score(result, player.score)
    elif result == "Loss":
        player.losses += 1
        player.score = game_logic.calculate_score(result, player.score)
    else:  # Draw
        player.draws += 1
        player.score = game_logic.calculate_score(result, player.score)
    
    # Calculer le taux de victoire
    if player.games_played > 0:
        player.win_rate = round((player.wins / player.games_played) * 100, 2)
    
    player.updated_at = datetime.now(timezone.utc)
    
    # Sauvegarder l'historique de la partie
    game_history = database.GameHistory(
        player_name=game.player_name,
        player_choice=game.player_choice,
        ai_choice=ai_choice,
        result=result
    )
    db.add(game_history)
    
    # Sauvegarder les modifications
    db.commit()
    db.refresh(player)
    
    return schemas.GameResult(
        player_choice=game.player_choice,
        ai_choice=ai_choice,
        result=result,
        message=message,
        updated_score=player
    )

# Récupérer le classement
@app.get("/leaderboard/", response_model=List[schemas.LeaderboardEntry])
def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(database.get_db)
):
    """
    Récupère le classement des meilleurs joueurs
    """
    players = db.query(database.PlayerScore).order_by(
        database.PlayerScore.score.desc()
    ).limit(limit).all()
    
    leaderboard = []
    for rank, player in enumerate(players, start=1):
        leaderboard.append(schemas.LeaderboardEntry(
            rank=rank,
            player_name=player.player_name,
            score=player.score,
            games_played=player.games_played,
            wins=player.wins,
            win_rate=player.win_rate
        ))
    
    return leaderboard

# Récupérer l'historique d'un joueur
@app.get("/history/{player_name}", response_model=List[schemas.GameHistoryReponse])
def get_player_history(
    player_name: str,
    limit: int = 20,
    db: Session = Depends(database.get_db)
):
    """
    Récupère l'historique des parties d'un joueur
    """
    history = db.query(database.GameHistory).filter(
        database.GameHistory.player_name == player_name
    ).order_by(database.GameHistory.timestamp.desc()).limit(limit).all()
    
    return history

# Réinitialiser les scores (pour les tests)
@app.delete("/reset/")
def reset_database(db: Session = Depends(database.get_db)):
    """
    Réinitialise toutes les données (À UTILISER AVEC PRÉCAUTION)
    """
    db.query(database.GameHistory).delete()
    db.query(database.PlayerScore).delete()
    db.commit()
    return {"message": "Base de données réinitialisée"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)