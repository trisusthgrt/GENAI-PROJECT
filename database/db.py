# Advanced Database Architecture and Connection Management
"""
Sophisticated database infrastructure providing intelligent connection pooling,
session management, and advanced ORM capabilities for the document processing platform.
"""

import os
from typing import Optional, AsyncGenerator, Dict, Any
from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import contextmanager, asynccontextmanager
import logging

from config.settings import ApplicationConfig

# Configure database logger
database_logger = logging.getLogger("database.operations")

# Database Configuration Constants
DEFAULT_DATABASE_URL = "sqlite:///./intelligent_document_processor.db"
DEFAULT_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./intelligent_document_processor.db"

class DatabaseArchitecture:
    """
    Advanced database architecture management providing enterprise-grade
    database connectivity, session handling, and performance optimization.
    """
    
    def __init__(self, database_url: Optional[str] = None, async_url: Optional[str] = None):
        """
        Initialize database architecture with intelligent configuration detection.
        
        Args:
            database_url: Synchronous database connection URL
            async_url: Asynchronous database connection URL
        """
        self.database_url = database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
        self.async_database_url = async_url or os.getenv("ASYNC_DATABASE_URL", DEFAULT_ASYNC_DATABASE_URL)
        
        # Initialize connection engines
        self._sync_engine = None
        self._async_engine = None
        self._session_factory = None
        self._async_session_factory = None
        
        # Performance monitoring
        self._connection_stats = {
            "total_connections": 0,
            "active_sessions": 0,
            "failed_connections": 0
        }
    
    def initialize_synchronous_engine(self, **engine_kwargs) -> None:
        """
        Initialize synchronous database engine with intelligent connection pooling.
        """
        default_config = {
            "echo": ApplicationConfig.DEBUG_MODE,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # 1 hour
            "connect_args": {"check_same_thread": False} if "sqlite" in self.database_url else {}
        }
        
        # Merge with custom configuration
        engine_config = {**default_config, **engine_kwargs}
        
        self._sync_engine = create_engine(self.database_url, **engine_config)
        
        # Configure session factory
        self._session_factory = sessionmaker(
            bind=self._sync_engine,
            autocommit=False,
            autoflush=True,
            expire_on_commit=False
        )
        
        # Add event listeners for monitoring
        self._setup_engine_monitoring(self._sync_engine)
        
        database_logger.info(f"Synchronous database engine initialized: {self.database_url}")
    
    def initialize_asynchronous_engine(self, **engine_kwargs) -> None:
        """
        Initialize asynchronous database engine with advanced async capabilities.
        """
        default_config = {
            "echo": ApplicationConfig.DEBUG_MODE,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "connect_args": {"check_same_thread": False} if "sqlite" in self.async_database_url else {}
        }
        
        # Merge with custom configuration
        engine_config = {**default_config, **engine_kwargs}
        
        self._async_engine = create_async_engine(self.async_database_url, **engine_config)
        
        # Configure async session factory
        self._async_session_factory = async_sessionmaker(
            bind=self._async_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=True,
            expire_on_commit=False
        )
        
        database_logger.info(f"Asynchronous database engine initialized: {self.async_database_url}")
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for synchronous database sessions with automatic cleanup.
        
        Yields:
            Session: SQLAlchemy session instance
        """
        if not self._session_factory:
            self.initialize_synchronous_engine()
        
        session = self._session_factory()
        self._connection_stats["active_sessions"] += 1
        
        try:
            yield session
            session.commit()
            database_logger.debug("Database session committed successfully")
        except Exception as e:
            session.rollback()
            database_logger.error(f"Database session rollback due to error: {e}")
            raise
        finally:
            session.close()
            self._connection_stats["active_sessions"] -= 1
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Async context manager for asynchronous database sessions.
        
        Yields:
            AsyncSession: SQLAlchemy async session instance
        """
        if not self._async_session_factory:
            self.initialize_asynchronous_engine()
        
        async_session = self._async_session_factory()
        self._connection_stats["active_sessions"] += 1
        
        try:
            yield async_session
            await async_session.commit()
            database_logger.debug("Async database session committed successfully")
        except Exception as e:
            await async_session.rollback()
            database_logger.error(f"Async database session rollback due to error: {e}")
            raise
        finally:
            await async_session.close()
            self._connection_stats["active_sessions"] -= 1
    
    def _setup_engine_monitoring(self, engine) -> None:
        """
        Setup comprehensive database engine monitoring and performance tracking.
        """
        @event.listens_for(engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            self._connection_stats["total_connections"] += 1
            database_logger.debug("New database connection established")
        
        @event.listens_for(engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            database_logger.debug("Database connection checked out from pool")
        
        @event.listens_for(engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            database_logger.debug("Database connection returned to pool")
    
    def get_connection_statistics(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive database connection and performance statistics.
        
        Returns:
            Dictionary containing detailed connection metrics
        """
        return {
            **self._connection_stats,
            "engine_status": {
                "sync_engine_initialized": self._sync_engine is not None,
                "async_engine_initialized": self._async_engine is not None
            },
            "configuration": {
                "database_url": self.database_url,
                "async_database_url": self.async_database_url,
                "debug_mode": ApplicationConfig.DEBUG_MODE
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive database health check with connectivity verification.
        
        Returns:
            Health check results with detailed status information
        """
        health_status = {
            "database_connectivity": "unknown",
            "sync_engine_status": "not_initialized",
            "async_engine_status": "not_initialized",
            "health_check_timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Test synchronous connectivity
        if self._sync_engine:
            try:
                with self.get_session() as session:
                    session.execute("SELECT 1")
                health_status["sync_engine_status"] = "healthy"
            except Exception as e:
                health_status["sync_engine_status"] = f"error: {str(e)}"
        
        # Test asynchronous connectivity
        if self._async_engine:
            try:
                async with self.get_async_session() as session:
                    await session.execute("SELECT 1")
                health_status["async_engine_status"] = "healthy"
            except Exception as e:
                health_status["async_engine_status"] = f"error: {str(e)}"
        
        # Overall connectivity assessment
        if (health_status["sync_engine_status"] == "healthy" or 
            health_status["async_engine_status"] == "healthy"):
            health_status["database_connectivity"] = "operational"
        else:
            health_status["database_connectivity"] = "degraded"
        
        return health_status

# Global database architecture instance
database_architecture = DatabaseArchitecture()

# Declarative base for ORM models
DatabaseBase = declarative_base()

# Metadata instance for schema management
database_metadata = MetaData()

# Convenience functions for session management
def get_database_session() -> Session:
    """
    Convenience function to get a synchronous database session.
    
    Returns:
        Session: SQLAlchemy session instance
    """
    return database_architecture.get_session()

async def get_async_database_session() -> AsyncSession:
    """
    Convenience function to get an asynchronous database session.
    
    Returns:
        AsyncSession: SQLAlchemy async session instance
    """
    async with database_architecture.get_async_session() as session:
        return session

# Legacy compatibility functions
def get_db():
    """Legacy compatibility wrapper for database session."""
    return database_architecture.get_session()

# Database initialization function
def initialize_database_infrastructure():
    """
    Initialize complete database infrastructure with both sync and async capabilities.
    Performs comprehensive setup for production-ready database operations.
    """
    database_architecture.initialize_synchronous_engine()
    database_architecture.initialize_asynchronous_engine()
    
    database_logger.info("Complete database infrastructure initialized successfully")

# Example usage and testing
if __name__ == "__main__":
    # Initialize database infrastructure
    initialize_database_infrastructure()
    
    # Test synchronous connectivity
    with database_architecture.get_session() as session:
        result = session.execute("SELECT 'Database connectivity test successful' as message")
        print(result.fetchone())
    
    # Display connection statistics
    stats = database_architecture.get_connection_statistics()
    print(f"Database Statistics: {stats}")
