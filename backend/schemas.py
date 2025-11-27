from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PlayerCreate(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)

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
        from_attributes = True

class GamePlay(BaseModel):
    player_name: str
    player_choice: str 

class GameResult(BaseModel):
    player_choice: str
    ai_choice: str
    result: str 
    message: str
    updated_score: PlayerResponse

class GameHistoryReponse(BaseModel):
    id: int
    player_name: str
    player_choice: str
    ai_choice: str  # Correction de la faute "ai_chioce"
    result: str
    timestamp: datetime

    class Config:
        from_attributes = True

class LeaderboardEntry(BaseModel):
    rank: int 
    player_name: str
    score: int
    games_played: int
    wins : int 
    win_rate: float

    class Config:
        from_attributes = True