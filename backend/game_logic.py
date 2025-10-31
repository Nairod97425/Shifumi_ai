import random
from typing import Tuple


# Choix possible
CHOICES = ["Pierre", "Feuille", "Ciseaux"]


def get_ai_choice() -> str:
    """
    Génère le choix aléatoire de l'IA

    Returns:
    str: Le choix de l'IA (Pierre, Feuille, Ciseaux)
    """
    return random.choice(CHOICES)


def determine_winner(player_choice: str, ai_choice: str) -> Tuple[str, str]:
    """
    Détermine le gagnant d'une partie de Shifumi

    Args:
        player_choice: Le choix du joueur
        ai_choice: Le choix de l'IA

    Returns:
        Tuple[str, str]: (résultat, message)
        - résultat: "Win", "Loss" ou "Draw"
        - message: Message descriptif du résultat
    """

    # Normaliser les choix
    # (enlever les espaces et mettre en majuscule la première lettre)
    player = player_choice.strip().capitalize()
    ai = ai_choice.strip().capitalize()

    # Vérifier que les choix sont valides
    if player not in CHOICES or ai not in CHOICES:
        return "Error", "Choix invalide"

    # Égalité
    if player == ai:
        return "Draw", f"Égalité ! Vous avez tous les deux choisi {player}"

    # Règles du Shifumi : Pierre > Ciseaux, Ciseaux > Feuille, Feuille > Pierre
    winning_combinations = {
        ("Pierre", "Ciseaux"): True,    # Pierre bat Ciseaux
        ("Ciseaux", "Feuille"): True,   # Ciseaux bat Feuille
        ("Feuille", "Pierre"): True,    # Feuille bat Pierre
    }

    # Vérifier si le joueur gagne
    if (player, ai) in winning_combinations:
        return "Win", f"Vous gagnez ! {player} bat {ai}"

    # Sinon, l'IA gagne
    return "Loss", f"Vous perdez ! {ai} bat {player}"


def calculate_score(result: str, current_score: int) -> int:
    """
    Calcule le nouveau score en fonction du résultat

    Args:
        result: "Win", "Loss" ou "Draw"
        current_score: Score actuel du joueur

    Returns:
        int: Nouveau score
    """
    score_changes = {
        "Win": 3,      # +3 points pour une victoire
        "Draw": 1,     # +1 point pour une égalité
        "Loss": 0      # 0 point pour une défaite
    }

    return current_score + score_changes.get(result, 0)


def is_valid_choice(choice: str) -> bool:
    """
    Vérifie si un choix est valide

    Args:
        choice: Le choix à vérifier

    Returns:
        bool: True si le choix est valide, False sinon
    """
    return choice.strip().capitalize() in CHOICES
