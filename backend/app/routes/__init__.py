# app/routes/__init__.py

from .search import search_bp
from .user import user_bp

__all__ = ["search_bp", "user_bp"]