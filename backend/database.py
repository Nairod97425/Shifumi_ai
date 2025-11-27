from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone

# URL de la base de données
SQLALCHEMY_DATA_URL = "sqlite:///shifumi.db"

# Création du moteur
engine = create_engine(
    SQLALCHEMY_DATA_URL,
    connect_args={"check_same_thread": False}
)

Session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Fonction pour la date actuelle (UTC)
def get_utc_now():
    return datetime.now(timezone.utc)

class PlayerScore(Base):
    __tablename__ = "player_scores"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, index=True)
    score = Column(Integer, default=0)
    games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

class GameHistory(Base):
    __tablename__ = "game_history"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, index=True)
    player_choice = Column(String)
    ai_choice = Column(String)  # Correction: ai_choice (et non ai_name)
    result = Column(String)
    timestamp = Column(DateTime, default=get_utc_now)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = Session_local()
    try:
        yield db
    finally:
        db.close()