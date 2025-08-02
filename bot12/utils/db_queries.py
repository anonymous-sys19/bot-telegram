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


def query_specific_verse(book_name, chapter, verse_num):
    """
    Consulta un versículo específico en la base de datos de la Biblia.
    book_name: Nombre del libro (ej. "Juan", "Salmos").
    chapter: Número del capítulo.
    verse_num: Número del versículo.
    """
    try:
        conn = sqlite3.connect(BIBLE_DB)
        cursor = conn.cursor()

        # Primero, obtener el ID del libro
        cursor.execute("SELECT id FROM book WHERE name = ?", (book_name,))
        book_id_result = cursor.fetchone()

        if not book_id_result:
            conn.close()
            return f"Libro '{book_name}' no encontrado. Verifica el nombre."

        book_id = book_id_result[0]

        # Luego, obtener el versículo
        cursor.execute(
            "SELECT b.name, v.chapter, v.verse, v.text FROM verse v JOIN book b ON v.book_id = b.id WHERE v.book_id = ? AND v.chapter = ? AND v.verse = ?",
            (book_id, chapter, verse_num)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            book, chapter, verse, text = result
            return f"📖 {book} {chapter}:{verse}\n{text}"
        return f"Versículo {book_name} {chapter}:{verse_num} no encontrado. Revisa el capítulo o versículo."
    except sqlite3.Error as e:
        return f"Error de base de datos al buscar versículo: {str(e)}. Verifica la DB y los parámetros."
    except Exception as e:
        return f"Error inesperado al buscar versículo: {str(e)}"