"""
Authentication service for user management
"""

import sqlite3
import aiosqlite
import logging
from datetime import datetime
from typing import Optional, Dict
import uuid

from app.core.security import get_password_hash, verify_password
from app.models.auth import UserCreate
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for user authentication and management"""

    def __init__(self):
        self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")

    async def initialize_db(self):
        """Initialize the user database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def create_user(self, user_create: UserCreate) -> Dict:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_create.password)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (id, username, email, hashed_password, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                user_create.username,
                user_create.email,
                hashed_password,
                True,
                datetime.utcnow().isoformat()
            ))
            await db.commit()

        return {
            "id": user_id,
            "username": user_create.username,
            "email": user_create.email,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }

    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username and password"""
        user = await self.get_user_by_username(username)
        if not user:
            return None

        if not verify_password(password, user["hashed_password"]):
            return None

        if not user["is_active"]:
            return None

        return user

    async def update_user_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users 
                SET updated_at = ? 
                WHERE id = ?
            """, (datetime.utcnow().isoformat(), user_id))
            await db.commit()


# Global service instance
auth_service = AuthService()
