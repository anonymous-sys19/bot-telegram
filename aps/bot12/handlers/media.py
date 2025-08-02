# handlers/media.py
from telegram.ext import CommandHandler
import requests
import subprocess
import os
import re # Para expresiones regulares
from bot12.utils.chat_history import save_history

async def meme(update, context):
    try:
        response = requests.get("https://api.imgflip.com/get_memes")
        response.raise_for_status()
        memes = response.json()["data"]["memes"]
        if not memes:
            await update.message.reply_text("No se encontraron memes. 😿")
            save_history(update.message.chat_id, "Meme: No se encontraron memes")
            return
        
        import random
        selected_meme = random.choice(memes)
        meme_url = selected_meme["url"]
        meme_name = selected_meme["name"]
        
        await update.message.reply_text(f"😂 **{meme_name}**:\n{meme_url}", parse_mode='Markdown')
        save_history(update.message.chat_id, f"Meme: {meme_name} ({meme_url})")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Error de red al obtener meme. 😿 ({e})")
        save_history(update.message.chat_id, f"Error meme (red): {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"Error inesperado al obtener meme. 😿 ({e})")
        save_history(update.message.chat_id, f"Error meme (inesperado): {str(e)}")

async def download(update, context):
    try:
        args = context.args
        if not args:
            await update.message.reply_text("Uso: `/download <URL> [--mp3]`\nEjemplo: `/download https://www.youtube.com/watch?v=dQw4w9WgXcQ --mp3`")
            return
        
        url = args[0]
        mp3_mode = "--mp3" in args

        await update.message.reply_text(f"📥 Iniciando descarga de {url}...")

        # Definir la ruta de descarga para que sea en el directorio actual o uno temporal
        download_dir = "./downloads_temp" # Puedes cambiar esto
        os.makedirs(download_dir, exist_ok=True) # Crear el directorio si no existe
        
        # Configurar comando yt-dlp
        # `-o %(id)s.%(ext)s` para un nombre de archivo único basado en el ID del video
        # `--restrict-filenames` para evitar caracteres problemáticos
        # `-f bestvideo+bestaudio/best` para la mejor calidad de video y audio combinada
        cmd = ["yt-dlp", "--restrict-filenames", "-P", download_dir]
        if mp3_mode:
            cmd.extend(["-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", "%(id)s.%(ext)s"])
        else:
            # Puedes especificar un formato de video/audio específico si lo deseas, ej. -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best", "-o", "%(id)s.%(ext)s"])
        
        cmd.append(url)
        
        # Ejecutar yt-dlp y capturar salida
        process = subprocess.run(cmd, capture_output=True, text=True, check=False) # check=False para manejar el error manualmente
        
        if process.returncode != 0:
            error_message = process.stderr or "Error desconocido al descargar."
            await update.message.reply_text(f"❌ Error al descargar: ```\n{error_message}\n```", parse_mode='MarkdownV2')
            save_history(update.message.chat_id, f"Error descarga yt-dlp: {error_message}")
            return
        
        # Intentar obtener el nombre del archivo descargado de la salida de yt-dlp
        file_path = None
        # Buscar "Destination: " o "Merging formats into " en la salida
        match_dest = re.search(r'Destination:\s+(.+)', process.stdout)
        match_merge = re.search(r'Merging formats into\s+"(.+)"', process.stdout)

        if match_dest:
            file_path = match_dest.group(1).strip()
        elif match_merge:
            file_path = match_merge.group(1).strip()
        else:
            # Si no se encuentra una ruta clara, intentar adivinar basada en el ID y el formato
            # Esto es menos robusto pero puede servir de fallback
            video_id_match = re.search(r'\[.+\]\s+([a-zA-Z0-9_-]{11})', url)
            if video_id_match:
                video_id = video_id_match.group(1)
                expected_ext = "mp3" if mp3_mode else "mp4" # Asumiendo mp4 para video
                # Buscar un archivo que contenga el ID y la extensión esperada en el download_dir
                for f in os.listdir(download_dir):
                    if video_id in f and f.endswith(f".{expected_ext}"):
                        file_path = os.path.join(download_dir, f)
                        break

        if not file_path or not os.path.exists(file_path):
            await update.message.reply_text("No se encontró el archivo descargado localmente. Posible error de yt-dlp o ruta. 😿")
            save_history(update.message.chat_id, "Error: archivo no encontrado después de descarga")
            return

        # Enviar archivo a Telegram
        await update.message.reply_text(f"📤 Subiendo '{os.path.basename(file_path)}' a Telegram...")
        if mp3_mode:
            with open(file_path, 'rb') as audio:
                await update.message.reply_audio(audio=audio, title=os.path.basename(file_path))
        else:
            with open(file_path, 'rb') as video:
                await update.message.reply_document(document=video, filename=os.path.basename(file_path))

        await update.message.reply_text(f"{'🎵' if mp3_mode else '🎬'} Archivo enviado al chat! 😎")
        save_history(update.message.chat_id, f"Descarga {'MP3' if mp3_mode else 'Video'}: {url}, enviado a Telegram")

        # Eliminar archivo local
        os.remove(file_path)
        # También puedes intentar limpiar el directorio si es temporal y está vacío
        if not os.listdir(download_dir):
            os.rmdir(download_dir)
        await update.message.reply_text("🗑️ Archivo local eliminado para cubrir rastros.")

    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"Error en la ejecución de yt-dlp: {e.stderr}. Asegúrate de tenerlo instalado y actualizado. 😿")
        save_history(update.message.chat_id, f"Error yt-dlp subprocess: {str(e)}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Error de red al procesar descarga. 😿 ({e})")
        save_history(update.message.chat_id, f"Error descarga (red): {str(e)}")
    except IndexError:
        await update.message.reply_text("Uso: `/download <URL> [--mp3]`")
        save_history(update.message.chat_id, "Uso incorrecto /download")
    except Exception as e:
        await update.message.reply_text(f"Error inesperado al procesar descarga: {str(e)}. Asegúrate de tener yt-dlp y permisos. 😿")
        save_history(update.message.chat_id, f"Error descarga (inesperado): {str(e)}")

def register_media_handlers(application):
    application.add_handler(CommandHandler("meme", meme))
    application.add_handler(CommandHandler("download", download))