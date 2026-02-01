"""
Connection pool for persistent HTTP connections.

Reduces network overhead (DNS + TCP + TLS handshake) by reusing connections
across multiple requests.
"""
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
import httpx
from loguru import logger


@dataclass
class ConnectionPoolStats:
    """Statistics for connection pool."""
    total_requests: int = 0
    connections_reused: int = 0
    connections_created: int = 0
    dns_lookups_saved: int = 0
    tls_handshakes_saved: int = 0
    network_overhead_reduction_ms: float = 0.0
    connection_reuse_rate: float = 0.0


class ConnectionPool:
    """
    Connection pool for HTTP clients.
    
    Manages persistent httpx.AsyncClient instances to reduce network overhead.
    Each provider gets its own persistent client with connection pooling enabled.
    """
    
    def __init__(self):
        """Initialize connection pool."""
        self._clients: Dict[str, httpx.AsyncClient] = {}
        self.stats = ConnectionPoolStats()
        self._client_configs: Dict[str, Dict] = {}
    
    def get_client(
        self,
        provider: str,
        base_url: str,
        headers: Dict[str, str],
        timeout: int = 120,
        limits: Optional[httpx.Limits] = None
    ) -> httpx.AsyncClient:
        """
        Get or create a persistent HTTP client for a provider.
        
        Args:
            provider: Provider name (e.g., "deepseek", "gemini")
            base_url: Base URL for the API
            headers: Default headers
            timeout: Request timeout
            limits: Connection limits (max_connections, max_keepalive_connections)
            
        Returns:
            httpx.AsyncClient instance (reused if exists)
        """
        # Check if client already exists
        if provider in self._clients:
            self.stats.connections_reused += 1
            self.stats.total_requests += 1
            self._update_stats()
            logger.debug(f"Reusing connection for {provider}")
            return self._clients[provider]
        
        # Create new client with connection pooling
        if limits is None:
            # Default: allow up to 100 connections, keep 20 alive
            limits = httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
                keepalive_expiry=30.0  # Keep connections alive for 30s
            )
        
        client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers=headers,
            limits=limits,
            # Enable HTTP/2 if supported (reduces overhead)
            http2=True
        )
        
        self._clients[provider] = client
        self._client_configs[provider] = {
            "base_url": base_url,
            "headers": headers,
            "timeout": timeout,
            "limits": limits
        }
        
        self.stats.connections_created += 1
        self.stats.total_requests += 1
        
        # Estimate overhead saved (DNS + TCP + TLS)
        # Typical values: DNS ~50ms, TCP ~100ms, TLS ~200ms = ~350ms saved per reuse
        self.stats.dns_lookups_saved += 1
        self.stats.tls_handshakes_saved += 1
        self.stats.network_overhead_reduction_ms += 350.0  # Estimated per reuse
        
        self._update_stats()
        logger.info(f"Created new persistent connection for {provider}")
        
        return client
    
    def close_client(self, provider: str) -> None:
        """Close a specific client."""
        if provider in self._clients:
            # Note: httpx clients should be closed with aclose() in async context
            # This is a sync method, so we just remove from dict
            # Actual closing should be done with close_all()
            del self._clients[provider]
            logger.info(f"Removed client for {provider}")
    
    async def close_all(self) -> None:
        """Close all clients."""
        for provider, client in self._clients.items():
            try:
                await client.aclose()
                logger.debug(f"Closed connection for {provider}")
            except Exception as e:
                logger.error(f"Error closing connection for {provider}: {e}")
        
        self._clients.clear()
        self._client_configs.clear()
        logger.info("All connections closed")
    
    def _update_stats(self) -> None:
        """Update connection reuse rate."""
        if self.stats.total_requests > 0:
            self.stats.connection_reuse_rate = (
                self.stats.connections_reused / self.stats.total_requests
            ) * 100
    
    def get_stats(self) -> ConnectionPoolStats:
        """Get connection pool statistics."""
        self._update_stats()
        return self.stats
    
    def get_summary(self) -> Dict[str, any]:
        """Get summary of connection pool state."""
        self._update_stats()
        
        return {
            "active_connections": len(self._clients),
            "providers": list(self._clients.keys()),
            "total_requests": self.stats.total_requests,
            "connections_reused": self.stats.connections_reused,
            "connections_created": self.stats.connections_created,
            "connection_reuse_rate": self.stats.connection_reuse_rate,
            "dns_lookups_saved": self.stats.dns_lookups_saved,
            "tls_handshakes_saved": self.stats.tls_handshakes_saved,
            "network_overhead_reduction_ms": self.stats.network_overhead_reduction_ms,
            "estimated_time_saved_seconds": self.stats.network_overhead_reduction_ms / 1000
        }


# Global connection pool instance
_global_pool: Optional[ConnectionPool] = None


def get_global_pool() -> ConnectionPool:
    """Get or create global connection pool."""
    global _global_pool
    if _global_pool is None:
        _global_pool = ConnectionPool()
    return _global_pool


async def close_global_pool() -> None:
    """Close global connection pool."""
    global _global_pool
    if _global_pool:
        await _global_pool.close_all()
        _global_pool = None
