import os
import json
import random
from groq import Groq
from dotenv import load_dotenv

# Charger les variables d'env
load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CHOICES = ["Pierre", "Feuille", "Ciseaux"]

def get_ai_move_smart(player_history: list) -> dict:
    """
    Utilise Groq pour déterminer le prochain coup basé sur l'historique du joueur.
    Retourne un dictionnaire { "choice": str, "message": str }
    """
    
    # Formatage de l'historique pour le prompt
    # history est une liste de tuples ou dicts : [{"player": "Pierre", "result": "Win"}, ...]
    history_text = "\n".join([f"- Tour -{i+1}: Joueur a fait {m['player_choice']}, Résultat: {m['result']}" for i, m in enumerate(player_history)])

    system_prompt = """
    Tu es un champion mondial de Pierre-Feuille-Ciseaux. Tu joues contre un humain.
    Ton but est de PREDIRE son prochain coup et de le BATTRE.
    
    Règles :
    1. Analyse l'historique des coups précédents de l'adversaire pour trouver un pattern.
    2. Choisis ton coup (Pierre, Feuille, ou Ciseaux) pour battre ce que tu penses qu'il va jouer.
    3. Génère une phrase courte (max 10 mots) pour le taquiner ou commenter ton choix (en français).
    
    Réponds UNIQUEMENT au format JSON strict :
    {
        "ai_choice": "Pierre" | "Feuille" | "Ciseaux",
        "commentary": "ta phrase ici"
    }
    """

    user_prompt = f"""
    Voici les 5 derniers coups de ton adversaire :
    {history_text}
    
    S'il n'y a pas d'historique, joue de manière imprévisible.
    Quel est ton prochain coup ?
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192", # Modèle rapide et intelligent
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"} # Force le JSON
        )
        
        content = completion.choices[0].message.content
        response_data = json.loads(content)
        
        # Validation de sécurité (au cas où l'IA hallucine)
        if response_data["ai_choice"] not in CHOICES:
            raise ValueError("Choix invalide de l'IA")
            
        return response_data

    except Exception as e:
        print(f"⚠️ Erreur Groq (Fallback sur Random): {e}")
        # Fallback : Si l'API plante ou est lente, on revient au random
        return {
            "ai_choice": random.choice(CHOICES),
            "commentary": "L'esprit de la machine est flou... je joue au hasard !"
        }