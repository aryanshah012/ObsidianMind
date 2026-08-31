"""
Authentication and User Management Service for ObsidianMind.
Provides SQLite-backed user storage, secure PBKDF2 password hashing,
JWT token issuance/verification, and per-user workspace provisioning.
"""

import os
import uuid
import time
import hmac
import hashlib
import sqlite3
import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import jwt

from app.config import settings
from app.models.user import UserRegisterRequest, UserResponse, UserInDB
from app.services.vault_manager import VaultManager


class AuthService:
    """Manages user persistence, authentication, and JWT lifecycle."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (settings.DATA_DIR / "users.db")
        self._init_db()
        self._seed_demo_user()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a thread-safe connection with row factory."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path), timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create users table if not already present."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    full_name TEXT NOT NULL DEFAULT '',
                    created_at REAL NOT NULL
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
            conn.commit()

    def _seed_demo_user(self) -> None:
        """Ensure a ready-to-test demo account exists for quick onboarding."""
        try:
            if not self.get_user_by_username("demo"):
                self.register_user(
                    UserRegisterRequest(
                        username="demo",
                        email="demo@obsidianmind.ai",
                        password="demopassword123",
                        full_name="Demo Explorer",
                    )
                )
        except Exception:
            pass

    @staticmethod
    def hash_password(password: str, salt_hex: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash password with PBKDF2-HMAC-SHA256 (100,000 iterations).
        Returns (password_hash_hex, salt_hex).
        """
        if salt_hex:
            salt_bytes = bytes.fromhex(salt_hex)
        else:
            salt_bytes = os.urandom(24)
            salt_hex = salt_bytes.hex()

        pwd_hash = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=password.encode("utf-8"),
            salt=salt_bytes,
            iterations=100_000,
        )
        return pwd_hash.hex(), salt_hex

    @classmethod
    def verify_password(cls, password: str, password_hash: str, salt: str) -> bool:
        """Constant-time verification of password hash."""
        computed_hash, _ = cls.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, password_hash)

    def create_access_token(self, user: UserResponse) -> str:
        """Generate signed JWT access token for user."""
        now = datetime.datetime.now(datetime.timezone.utc)
        expire = now + datetime.timedelta(days=settings.JWT_EXPIRE_DAYS)
        payload = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }
        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return token

    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify signature and expiration of JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except (jwt.PyJWTError, Exception):
            return None

    def register_user(self, req: UserRegisterRequest) -> UserResponse:
        """Register a new user, initialize their isolated workspace directory and metadata."""
        clean_username = req.username.strip()
        clean_email = req.email.strip().lower()

        # Check existing user
        if self.get_user_by_username(clean_username):
            raise ValueError(f"Username '{clean_username}' is already taken.")
        if self.get_user_by_email(clean_email):
            raise ValueError(f"Email '{clean_email}' is already registered.")

        user_id = f"u_{uuid.uuid4().hex[:12]}"
        password_hash, salt = self.hash_password(req.password)
        now_ts = time.time()
        full_name = (req.full_name or clean_username).strip()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (id, username, email, password_hash, salt, full_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, clean_username, clean_email, password_hash, salt, full_name, now_ts),
            )
            conn.commit()

        # Provision personal isolated user storage & default vault workspace
        user_storage = settings.USERS_DIR / user_id
        user_storage.mkdir(parents=True, exist_ok=True)
        (user_storage / "vaults" / "default").mkdir(parents=True, exist_ok=True)
        (user_storage / "uploads").mkdir(parents=True, exist_ok=True)

        # Initialize user's personal vault manager
        VaultManager(user_id=user_id)

        return UserResponse(
            id=user_id,
            username=clean_username,
            email=clean_email,
            full_name=full_name,
            created_at=now_ts,
        )

    def authenticate_user(self, username_or_email: str, password: str) -> Optional[UserResponse]:
        """Authenticate user by username or email and password."""
        ident = username_or_email.strip()
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM users
                WHERE username = ? OR email = ?
                LIMIT 1
                """,
                (ident, ident.lower()),
            ).fetchone()

        if not row:
            return None

        user_db = UserInDB(**dict(row))
        if not self.verify_password(password, user_db.password_hash, user_db.salt):
            return None

        return UserResponse(
            id=user_db.id,
            username=user_db.username,
            email=user_db.email,
            full_name=user_db.full_name,
            created_at=user_db.created_at,
        )

    def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Fetch user by ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ? LIMIT 1", (user_id,)).fetchone()
        if not row:
            return None
        return UserResponse(**dict(row))

    def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Fetch user by username."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ? LIMIT 1", (username.strip(),)).fetchone()
        if not row:
            return None
        return UserResponse(**dict(row))

    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Fetch user by email."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ? LIMIT 1", (email.strip().lower(),)).fetchone()
        if not row:
            return None
        return UserResponse(**dict(row))


# Singleton instance
auth_service = AuthService()
