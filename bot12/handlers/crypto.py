# handlers/crypto.py
from telegram.ext import CommandHandler
import requests
from bot12.utils.chat_history import save_history

async def crypto(update, context):
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        response.raise_for_status() # Lanza excepción para errores HTTP
        price = response.json()["bitcoin"]["usd"]
        await update.message.reply_text(f"💰 Bitcoin: ${price} USD")
        save_history(update.message.chat_id, f"Consulta crypto: ${price}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Error de red al consultar cripto. 😿 ({e})")
        save_history(update.message.chat_id, f"Error crypto (red): {str(e)}")
    except KeyError:
        await update.message.reply_text("Error: No se pudo obtener el precio de Bitcoin. La API podría haber cambiado su respuesta. 😿")
        save_history(update.message.chat_id, "Error crypto (KeyError)")
    except Exception as e:
        await update.message.reply_text(f"Error inesperado al consultar cripto. 😿 ({e})")
        save_history(update.message.chat_id, f"Error crypto (inesperado): {str(e)}")

def register_crypto_handlers(application):
    application.add_handler(CommandHandler("crypto", crypto))