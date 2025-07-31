import sqlite3
from typing import Optional, Dict, List, Any, Union, Tuple
from datetime import datetime

class UserDatabase:
    def __init__(self, db_name: str = "data/users_db.db"):
        """Инициализация базы данных SQLite."""
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        """Создает таблицы users и banned, если их нет."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                status TEXT DEFAULT 'user',
                roots TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS banned (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                ban_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT,
                unban_time TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        self.connection.commit()

    def user_exists(self, user_id: int):
        """
        Проверяет есть ли пользователь в базе

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если пользователь существует, False если нет
        """
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone() is not None

    def add_user(self, user_id: int, username: Optional[str] = None, 
                 first_name: Optional[str] = None, last_name: Optional[str] = None,
                 status: str = 'user', roots: str = 'user') -> bool:
        """
        Добавляет пользователя в базу данных.
        
        Args:
            user_id: ID пользователя
            username: Имя пользователя (опционально)
            first_name: Имя (опционально)
            last_name: Фамилия (опционально)
            status: Статус пользователя (по умолчанию 'user')
            roots: Права пользователя (по умолчанию 'user')
            
        Returns:
            bool: True если пользователь добавлен, False если произошла ошибка
        """
        try:
            self.cursor.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, status, roots)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, first_name, last_name, status, roots))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            # Пользователь уже существует
            return False

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о пользователе.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[Dict]: Словарь с данными пользователя или None, если пользователь не найден
        """
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        if result:
            columns = [column[0] for column in self.cursor.description]
            return dict(zip(columns, result))
        return None

    def update_user(self, user_id: int, **kwargs) -> bool:
        """
        Обновляет данные пользователя.
        
        Args:
            user_id: ID пользователя
            **kwargs: Поля для обновления (username, first_name, last_name, status, roots)
            
        Returns:
            bool: True если обновление прошло успешно, False если пользователь не найден
        """
        if not kwargs:
            return False
            
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(user_id)
        
        self.cursor.execute(f"""
            UPDATE users SET {set_clause} WHERE user_id = ?
        """, values)
        self.connection.commit()
        return self.cursor.rowcount > 0

    def delete_user(self, user_id: int) -> bool:
        """
        Удаляет пользователя из базы данных.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если пользователь удален, False если пользователь не найден
        """
        self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0

    def ban_user(self, user_id: int, reason: Optional[str] = None, 
                 ban_duration: Optional[int] = None) -> bool:
        """
        Банит пользователя.
        
        Args:
            user_id: ID пользователя
            reason: Причина бана (опционально)
            ban_duration: Длительность бана в секундах (None - перманентный бан)
            
        Returns:
            bool: True если пользователь забанен, False если произошла ошибка
        """
        try:
            unban_time = None
            if ban_duration is not None:
                unban_time = datetime.now().timestamp() + ban_duration
            
            self.cursor.execute("""
                INSERT OR REPLACE INTO banned (user_id, reason, unban_time)
                VALUES (?, ?, ?)
            """, (user_id, reason, unban_time))
            self.connection.commit()
            return True
        except sqlite3.Error:
            return False

    def is_banned(self, user_id: int) -> Union[bool, Dict[str, Any]]:
        """
        Проверяет, забанен ли пользователь.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Union[bool, Dict]: False если пользователь не забанен, 
            иначе словарь с информацией о бане
        """
        self.cursor.execute("""
            SELECT * FROM banned 
            WHERE user_id = ? AND (unban_time IS NULL OR unban_time > ?)
        """, (user_id, datetime.now().timestamp()))
        result = self.cursor.fetchone()
        if result:
            columns = [column[0] for column in self.cursor.description]
            return dict(zip(columns, result))
        return False

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Получает список всех пользователей.
        
        Returns:
            List[Dict]: Список словарей с информацией о пользователях
        """
        self.cursor.execute("SELECT * FROM users")
        columns = [column[0] for column in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_banned_users(self) -> List[Dict[str, Any]]:
        """
        Получает список забаненных пользователей.
        
        Returns:
            List[Dict]: Список словарей с информацией о забаненных пользователях
        """
        self.cursor.execute("""
            SELECT * FROM banned 
            WHERE unban_time IS NULL OR unban_time > CURRENT_TIMESTAMP
        """)
        columns = [column[0] for column in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def close(self):
        """Закрывает соединение с базой данных."""
        self.connection.close()

    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера."""
        self.close()