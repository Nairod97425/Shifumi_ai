from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
import database
import schemas
import game_logic
from datetime import datetime, timezone

# --- INITIALISATION AUTOMATIQUE DE LA BDD ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        database.init_db()
        print("✅ Base de données initialisée avec succès (Tables créées)")
    except Exception as e:
        print(f"❌ Erreur critique BDD: {e}")
    yield

app = FastAPI(
    title="Shifumi AI API",
    lifespan=lifespan
)

# --- CONFIGURATION CORS (Pour autoriser React/Vite) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Accepte toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTES ---

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/players/", response_model=schemas.PlayerResponse)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(database.get_db)):
    db_player = db.query(database.PlayerScore).filter(
        database.PlayerScore.player_name == player.player_name
    ).first()
    
    if db_player:
        return db_player
    
    new_player = database.PlayerScore(player_name=player.player_name)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player

@app.post("/play/", response_model=schemas.GameResult)
def play_game(game: schemas.GamePlay, db: Session = Depends(database.get_db)):
    # 1. Validation
    if not game_logic.is_valid_choice(game.player_choice):
        raise HTTPException(status_code=400, detail="Choix invalide")
    
    # 2. Récupération Joueur
    player = db.query(database.PlayerScore).filter(
        database.PlayerScore.player_name == game.player_name
    ).first()
    
    if not player:
        # Création auto si le joueur n'existe pas encore
        player = database.PlayerScore(player_name=game.player_name)
        db.add(player)
        db.commit()
        db.refresh(player)
    
    # 3. Logique de jeu
    ai_choice = game_logic.get_ai_choice()
    result, message = game_logic.determine_winner(game.player_choice, ai_choice)
    
    # 4. Mise à jour stats
    player.games_played += 1
    if result == "Win":
        player.wins += 1
    elif result == "Loss":
        player.losses += 1
    else:
        player.draws += 1
        
    player.score = game_logic.calculate_score(result, player.score)
    
    if player.games_played > 0:
        player.win_rate = round((player.wins / player.games_played) * 100, 2)
    
    player.updated_at = database.get_utc_now()
    
    # 5. Historique
    game_history = database.GameHistory(
        player_name=game.player_name,
        player_choice=game.player_choice,
        ai_choice=ai_choice,
        result=result
    )
    db.add(game_history)
    
    db.commit()
    db.refresh(player)
    
    return schemas.GameResult(
        player_choice=game.player_choice,
        ai_choice=ai_choice,
        result=result,
        message=message,
        updated_score=player
    )

@app.get("/leaderboard/", response_model=List[schemas.LeaderboardEntry])
def get_leaderboard(limit: int = 10, db: Session = Depends(database.get_db)):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)