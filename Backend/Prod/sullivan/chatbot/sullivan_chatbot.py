# Backend/Prod/sullivan/chatbot/sullivan_chatbot.py

import json
import logging
from pathlib import Path
from typing import List, Dict

from fastapi import FastAPI
from ...models.gemini_client import GeminiClient

app = FastAPI()
logger = logging.getLogger(__name__)

def load_screen_plan(path: Path) -> List[Dict]:
    """
    Load screen plan from a JSON file.

    Args:
    path (Path): Path to the JSON file.

    Returns:
    List[Dict]: List of dictionaries representing the screen plan.
    """
    try:
        with open(path, 'r') as f:
            screen_plan = json.load(f)
        return screen_plan
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON: {path}")
        return []

def get_organes_for_corps(corps_id: str, screen_plan_path: Path) -> List[Dict]:
    """
    Get the list of organs for a given corps ID from the screen plan.

    Args:
    corps_id (str): ID of the corps.
    screen_plan_path (Path): Path to the screen plan JSON file.

    Returns:
    List[Dict]: List of dictionaries representing the organs of the corps.
    """
    screen_plan = load_screen_plan(screen_plan_path)
    for corps in screen_plan:
        if corps['id'] == corps_id:
            return corps.get('organs', [])
    return []

async def chat(user_message: str, context: Dict) -> str:
    """
    Chat with the user and return a response.

    Args:
    user_message (str): Message from the user.
    context (Dict): Context for the chat.

    Returns:
    str: Response from the chatbot.
    """
    prompt = f"Tu es Sullivan, assistant pour l'affinage UI. L'utilisateur a dit : {user_message}. Contexte : {context}. Réponds en texte court avec des suggestions ou instructions pour le frontend (ex. affiner les cellules ici, ce bloc en formulaire)."
    gemini_client = GeminiClient(execution_mode='BUILD')
    response = gemini_client.generate(prompt, max_tokens=1024)
    return response