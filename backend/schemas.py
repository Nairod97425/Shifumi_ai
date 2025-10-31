from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Schéma pour créer un joueur
class PlayerCreate(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)

# Schéma pour la réponse du joueur
class PlayerResponse(BaseModel):
    id: int
    player_name: str
    score: int
    games_played: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    created_at: datetime

    class Config:
        from_attributes =True

# Schéma pour enregistrer une partie 
class GamePlay(BaseModel):
    player_name: str
    player_choice: str # "Pierre", "Feuille", "Ciseaux"

# Schéma pour le résultat d'une partie
class GameResult(BaseModel):
    id: int
    player_choice: str
    ai_choice: str
    result: str # "Win", "Lose", "Draw"
    message: str
    updated_score: PlayerResponse

# Schéma pour l'historique d'une partie
class GameHistoryReponse(BaseModel):
    id: int
    player_name: str
    player_choice: str
    ai_chioce: str
    result: str
    timestamp: datetime

    class Config:
        from_attributes = True

# Schéma pour le classement
class LeaderboardEntry(BaseModel):
    rank: int 
    player_name: str
    score: int
    games_played: int
    wins : int 
    win_rate: float

    class Config:
        from_attributes = True

# Schéma pour la détecton de geste 
class GestureDetecction(BaseModel):
    gesture: Optional[str] = None # "Pierre", "Feuille", "Ciseaux"
    confidence: float = 0.0
    detected: bool = False