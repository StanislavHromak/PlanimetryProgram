import sqlite3
import os


class TheoremService:
    """
    Сервіс бази знань (Data Access Object).
    Працює зі справжньою БД SQLite.
    """

    def __init__(self):
        # 1. Визначаємо правильний абсолютний шлях до файлу БД.
        # __file__ вказує на поточний файл (services/knowledge_base.py)
        # os.path.dirname піднімає нас на рівень вище, у корінь проєкту
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.db_path = os.path.join(base_dir, 'database', 'theorems.db')

    def _get_connection(self):
        """Допоміжний приватний метод для створення підключення до БД."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Базу даних не знайдено за шляхом: {self.db_path}. Запустіть database/init_db.py")

        # Підключаємося до файлу SQLite
        return sqlite3.connect(self.db_path)

    def get_theorem(self, name: str) -> dict:
        """
        Шукає теорему в базі даних SQLite за її назвою.
        Повертає словник, який чекають класи розрахунків.
        """
        # Створюємо підключення та курсор
        conn = self._get_connection()
        cursor = conn.cursor()

        # Виконуємо SQL-запит (використовуємо '?' для захисту від SQL-ін'єкцій)
        cursor.execute("SELECT formula, description FROM theorems WHERE name = ?", (name,))
        row = cursor.fetchone()  # Дістаємо один запис

        # Обов'язково закриваємо підключення, щоб не блокувати файл
        conn.close()

        # Якщо теорему знайдено в БД
        if row:
            return {
                "name": name,
                "formula": row[0],  # Перша колонка з SELECT (formula)
                "description": row[1]  # Друга колонка з SELECT (description)
            }

        # Якщо в БД ще немає такого правила (Фоллбек)
        return {
            "name": name,
            "formula": "Формулу не знайдено в БД",
            "description": "Опис відсутній у базі знань. Додайте його через init_db.py."
        }