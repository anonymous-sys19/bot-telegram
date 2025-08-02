# utils/api_calls.py
import google.generativeai as genai
import os
from bot12.config import GEMINI_SYSTEM_PROMPT # Importar el prompt del sistema desde config

# Configurar Gemini (solo una vez)
# La API Key se obtiene directamente del entorno al configurar el modelo
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")
else:
    print("Advertencia: GEMINI_API_KEY no configurada. Las funciones de IA no estarán disponibles.")
    gemini_model = None

def query_gemini(prompt):
    if not gemini_model:
        return "Error: La API de Gemini no está configurada. Por favor, define GEMINI_API_KEY en tus variables de entorno."
    try:
        full_prompt = f"{GEMINI_SYSTEM_PROMPT}\n\n{prompt}"
        response = gemini_model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error al consultar Gemini: {str(e)}. Posiblemente la API Key es inválida o hay un problema de red."