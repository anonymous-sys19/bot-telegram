# nada.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="apscheduler") 

from telegram.ext import Application, CommandHandler, MessageHandler, filters, JobQueue
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.append(current_dir)

from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde .env
# Importar la configuración y los módulos de handlers
from config import check_env_vars
from handlers.general import register_general_handlers
from handlers.crypto import register_crypto_handlers
from handlers.network import register_network_handlers
from handlers.media import register_media_handlers
from handlers.ai import register_ai_handlers

def main():
    # Verificar que las variables de entorno estén configuradas
    if not check_env_vars():
        exit(1) # Salir si faltan variables esenciales

    # Obtener el TOKEN del bot desde las variables de entorno
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN no está configurado.")
        exit(1)

    # Construir la aplicación del bot
    application = Application.builder().token(TOKEN).job_queue(JobQueue()).build()

    # Registrar todos los handlers desde los módulos
    register_general_handlers(application)
    register_crypto_handlers(application)
    register_network_handlers(application)
    register_media_handlers(application)
    register_ai_handlers(application)

    print("Bot iniciado. Escuchando mensajes...")
    # Iniciar el bot y mantenerlo en polling
    application.run_polling()

if __name__ == "__main__":
    main()