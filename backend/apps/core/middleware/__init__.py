"""
Middleware personalizado del sistema.
"""
from .logging import RequestLoggingMiddleware

__all__ = ['RequestLoggingMiddleware']
