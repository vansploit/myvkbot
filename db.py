import sqlite3
from typing import Optional, Dict, List, Any

class SQLiteDatabase:
    def __init__(self, db_name: str = "bot_database.db"):
        """Инициализация базы данных SQLite."""
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        """Создает таблицу users, если её нет."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                state TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()

    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавляет пользователя в базу данных."""
        self.cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, first_name, last_name))
        self.connection.commit()

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает данные пользователя по его ID."""
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        if result:
            columns = [desc[0] for desc in self.cursor.description]
            return dict(zip(columns, result))
        return None

    def update_user(self, user_id: int, **kwargs):
        """Обновляет данные пользователя."""
        if not kwargs:
            return

        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]

        self.cursor.execute(f"""
            UPDATE users SET {set_clause} WHERE user_id = ?
        """, values)
        self.connection.commit()

    def delete_user(self, user_id: int):
        """Удаляет пользователя из базы данных."""
        self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        self.connection.commit()

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Возвращает список всех пользователей."""
        self.cursor.execute("SELECT * FROM users")
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def close(self):
        """Закрывает соединение с базой данных."""
        self.connection.close()

    def __enter__(self):
        """Поддержка контекстного менеджера (with)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие соединения при выходе из with."""
        self.close()
        
MyDB = SQLiteDatabase("test.db")
with MyDB as db:
    db.add_user(123, username="Test")
    print(db.get_all_users())