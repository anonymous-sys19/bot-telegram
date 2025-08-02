# handlers/ai.py
from telegram.ext import CommandHandler
from bot12.utils.api_calls import query_gemini
from bot12.utils.chat_history import save_history

async def ask(update, context):
    try:
        if not context.args:
            await update.message.reply_text("Uso: `/ask <pregunta>`\nEjemplo: `/ask ¿Qué es el caos cuántico?`")
            return
        question = " ".join(context.args)
        await update.message.reply_text("🧠 Pensando... (Recuerda que mi modo ChaosGod está activo)")
        response = query_gemini(question)
        await update.message.reply_text(f"🧠 **Respuesta de ChaosGod**:\n{response}", parse_mode='Markdown')
        save_history(update.message.chat_id, f"Consulta Gemini: {question}")
    except Exception as e:
        await update.message.reply_text(f"Error al consultar IA. 😿 ({e})")
        save_history(update.message.chat_id, f"Error ask: {str(e)}")

def register_ai_handlers(application):
    application.add_handler(CommandHandler("ask", ask))