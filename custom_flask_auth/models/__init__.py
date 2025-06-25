"""Database models package."""

from flask_sqlalchemy import SQLAlchemy

# Database instance to be reused by the application

db = SQLAlchemy()

# Import models so they are registered with the package
from .user import User

__all__ = ["db", "User"]