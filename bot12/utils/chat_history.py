# utils/chat_history.py
import json
import os
from datetime import datetime
from bot12.config import HISTORY_FILE, TIMEZONE # Importar desde config

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        return {}
    except json.JSONDecodeError:
        print(f"Advertencia: El archivo de historial '{HISTORY_FILE}' está corrupto. Se creará uno nuevo.")
        return {}
    except Exception as e:
        print(f"Error al cargar historial: {str(e)}")
        return {}

def save_history(chat_id, message):
    history = load_history()
    if str(chat_id) not in history:
        history[str(chat_id)] = []
    
    # Limitar el historial por chat_id para evitar archivos gigantes
    MAX_HISTORY_MESSAGES = 100 # Puedes ajustar este número
    
    history[str(chat_id)].append({"timestamp": str(datetime.now(TIMEZONE)), "message": message})
    
    # Mantener solo los últimos N mensajes
    history[str(chat_id)] = history[str(chat_id)][-MAX_HISTORY_MESSAGES:]

    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error al guardar historial: {str(e)}")