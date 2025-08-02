# utils/db_queries.py
import sqlite3
from bot12.config import BIBLE_DB # Importar la ruta de la DB desde config

def query_random_verse():
    try:
        conn = sqlite3.connect(BIBLE_DB)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT b.name, v.chapter, v.verse, v.text FROM verse v JOIN book b ON v.book_id = b.id ORDER BY RANDOM() LIMIT 1"
        )
        result = cursor.fetchone()
        conn.close()
        if result:
            book, chapter, verse, text = result
            return f"📖 {book} {chapter}:{verse}\n{text}"
        return "Versículo no encontrado. 😿 Asegúrate de que `rvr1960.sqlite` esté en el directorio correcto."
    except sqlite3.Error as e:
        return f"Error de base de datos al consultar Biblia: {str(e)}. Verifica el archivo `rvr1960.sqlite`."
    except Exception as e:
        return f"Error inesperado al consultar Biblia: {str(e)}"