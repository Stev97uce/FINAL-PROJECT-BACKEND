"""
Dependency injection for services and repositories
Dependency Inversion Principle - high-level modules depend on abstractions
"""
from app.security import get_current_user_id, get_current_user

# Re-export for convenience
__all__ = ["get_current_user_id", "get_current_user"]
