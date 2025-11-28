from typing import Tuple

CHOICES = ["Pierre", "Feuille", "Ciseaux"]

def is_valid_choice(choice: str) -> bool:
    """Vérifie si le choix envoyé par le front est valide."""
    return choice.strip().capitalize() in CHOICES

def determine_winner(player_choice: str, ai_choice: str) -> Tuple[str, str]:
    """
    Compare les choix et retourne (Résultat, Message technique).
    """
    player = player_choice.strip().capitalize()
    ai = ai_choice.strip().capitalize()

    if player == ai:
        return "Draw", f"Égalité ({player} vs {ai})"

    winning_combinations = {
        ("Pierre", "Ciseaux"),
        ("Ciseaux", "Feuille"),
        ("Feuille", "Pierre"),
    }

    if (player, ai) in winning_combinations:
        return "Win", f"Victoire ! {player} bat {ai}"

    return "Loss", f"Défaite... {ai} bat {player}"

def calculate_score(result: str, current_score: int) -> int:
    """Met à jour le score numérique."""
    if result == "Win":
        return current_score + 3
    elif result == "Draw":
        return current_score + 1
    return current_score