"""
Network optimization module for AETHERFLOW.

Provides connection pooling, persistent connections, and network metrics
to reduce overhead (DNS + TCP + TLS handshake).
"""
from .connection_pool import ConnectionPool, ConnectionPoolStats

__all__ = ["ConnectionPool", "ConnectionPoolStats"]
