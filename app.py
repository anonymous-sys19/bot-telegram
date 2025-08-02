# /home/ghostroot/Documentos/GIT/Chat-bot-telegram/run.py

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
# Si tu .env está en el mismo nivel que run.py (es decir, en /home/ghostroot/Documentos/GIT/Chat-bot-telegram/)
load_dotenv()

# Importar la función main de tu bot que ahora es un módulo dentro del paquete bot12
# Asumiendo que tu archivo principal dentro de bot12 se llama 'app.py'
from bot12.main import main # Si se llama 'nada.py', sería from bot12.nada import main

if __name__ == "__main__":
    main() # Llama a la función principal de tu bot