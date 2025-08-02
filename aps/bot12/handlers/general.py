# handlers/general.py
from telegram.ext import CommandHandler
from bot12.utils.chat_history import save_history # Asumiendo que save_history se mueve a utils/chat_history.py
from bot12.utils.db_queries import query_random_verse

async def start(update, context):
    await update.message.reply_text("¡Hacker, bienvenido! 😎 Usa /help para el menú épico.")
    save_history(update.message.chat_id, "Bot iniciado")

async def help_command(update, context): # Renombrado para evitar conflicto con help() builtin
    help_text = (
        "🔥 **Bot Hacker Épico** 🔥\n"
        "Tu asistente para ciberespacio y fe 🙏\n\n"
        "📜 **Comandos**:\n"
        "👋 `/hola` - Saluda al bot.\n"
        "💰 `/crypto` - Precio de Bitcoin.\n"
        "🔍 `/scan <IP>` - Escanea puertos (22-80, requiere Nmap).\n"
        "😂 `/meme` - Meme random.\n"
        "🌐 `/ipinfo <IP>` - Info de IP (ciudad, país, ISP).\n"
        "📥 `/download <URL> [--mp3]` - Descarga video (720p) o MP3.\n"
        "📖 `/verse` - Versículo bíblico random.\n"
        "🌍 `/whois <dominio>` - Info de dominio.\n"
        "🧠 `/ask <pregunta>` - Consulta a la IA de Gemini.\n"
        "📚 `/help` - Este menú.\n\n"
        "💡 **Ejemplos**:\n"
        "- `/ipinfo 8.8.8.8`\n"
        "- `/download https://youtube.com/watch?v=VIDEO_ID --mp3`\n"
        "- `/verse`\n"
        "- `/whois google.com`\n"
        "- `/ask ¿Cómo hackear éticamente un servidor?`\n\n"
        "⚠️ **Notas**:\n"
        "- Necesitas yt-dlp, Nmap, y API keys (WHOIS, Gemini).\n"
        "- Coloca `rvr1960.sqlite` en el directorio del script.\n"
        "- Usa éticamente.\n"
        "¡Hackea con fe! 😎🙏"
    )
    await update.message.reply_text(help_text)
    save_history(update.message.chat_id, "Comando /help ejecutado")

async def hola(update, context):
    await update.message.reply_text("¡Hey, soy tu bot épico! ¿Qué hackeamos hoy? 🚀")
    save_history(update.message.chat_id, "Comando /hola ejecutado")

async def verse(update, context):
    try:
        await update.message.reply_text("📖 Buscando un versículo...")
        verse_text = query_random_verse()
        await update.message.reply_text(verse_text)
        save_history(update.message.chat_id, f"Consulta versículo: {verse_text[:50]}...") # Guardar solo una parte del texto
    except Exception as e:
        await update.message.reply_text(f"Error al obtener versículo. 😿 ({e})")
        save_history(update.message.chat_id, f"Error versículo: {str(e)}")


# Función para registrar estos handlers
def register_general_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("hola", hola))
    application.add_handler(CommandHandler("verse", verse))