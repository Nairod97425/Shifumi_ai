from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone

# Configuration de la base de données SQLite
SQLALCHEMY_DATA_URL = "sqlite:///shifumi.db"

# Création du moteur de base de données
engine = create_engine(
    SQLALCHEMY_DATA_URL,
    connect_args={"check_same_thread": False}  # Correction de la faute de frappe
)

# Création de la session locale
Session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Modèle pour les scores des joueurs
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
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

# Modèle pour l'historique des parties
class GameHistory(Base):
    __tablename__ = "game_history"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, index=True)
    player_choice = Column(String)  # Pierre, Feuille, Ciseaux
    ai_name = Column(String)
    result = Column(String)  # Win, Loss, Draw
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

# Créer toutes les tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Fonction pour obtenir une session de base de données
def get_db():
    db = Session_local()
    try:
        yield db
    finally:
        db.close()