# """
# Database connection and helper utilities for Expense MCP Server.

# Handles PostgreSQL connection pooling and provides base query execution.
# Multi-user isolation is enforced at the query level.
# """

# import os
# import traceback
# import psycopg2
# from psycopg2.pool import SimpleConnectionPool
# from psycopg2.extras import RealDictCursor
# from typing import Optional, List, Dict, Any
# from contextlib import contextmanager

# from dotenv import load_dotenv
# load_dotenv()


# class DatabaseConnection:
#     """
#     PostgreSQL connection manager with pooling support.
#     Designed for cloud-hosted databases (Supabase, Neon, etc.)
#     """
    
#     def __init__(self):
#         self.pool: Optional[SimpleConnectionPool] = None
#         self._initialize_pool()
    
#     # def _initialize_pool(self):
#         """Initialize connection pool from environment variables."""

#         db_url = os.getenv("DATABASE_URL")
#         # print("Database URL:", db_url)
        
#         if not db_url:
#             raise ValueError(
#                 "DATABASE_URL environment variable must be set. "
#                 "Format: postgresql://user:password@host:port/database"
#             )
        
#         try:
#             # Create connection pool (min 2, max 10 connections)
#             self.pool = SimpleConnectionPool(
#                 minconn=2,
#                 maxconn=10,
#                 dsn=db_url,
#                 # sslmode='require'
#             )
#         except psycopg2.Error as e:
#             raise ConnectionError(f"Failed to initialize database pool: {e}")
#     def _initialize_pool(self):
#      db_url = os.getenv("DATABASE_URL")

#      if not db_url:
#         raise ValueError("DATABASE_URL environment variable must be set")

#      try:
#         self.pool = SimpleConnectionPool(
#             minconn=1,
#             maxconn=3,
#             dsn=db_url,
#             connect_timeout=5
#         )
#      except Exception as e:
#         print("🔥 DB INIT FAILED 🔥")
#         traceback.print_exc()
#         raise
#     @contextmanager
#     def get_cursor(self):
#         """
#         Context manager for database cursor with automatic connection management.
        
#         Yields:
#             psycopg2.cursor: Database cursor with RealDictCursor factory
#         """
#         conn = None
#         cursor = None
        
#         try:
#             conn = self.pool.getconn()
#             cursor = conn.cursor(cursor_factory=RealDictCursor)
#             yield cursor
#             conn.commit()
#         except Exception as e:
#             if conn:
#                 conn.rollback()
#             raise e
#         finally:
#             if cursor:
#                 cursor.close()
#             if conn:
#                 self.pool.putconn(conn)
    
#     def execute_query(
#         self, 
#         query: str, 
#         params: Optional[tuple] = None
#     ) -> List[Dict[str, Any]]:
#         """
#         Execute a SELECT query and return results as list of dicts.
        
#         Args:
#             query: SQL query string
#             params: Query parameters (optional)
            
#         Returns:
#             List of row dictionaries
#         """
#         with self.get_cursor() as cursor:
#             cursor.execute(query, params or ())
#             return [dict(row) for row in cursor.fetchall()]
    
#     def execute_update(
#         self, 
#         query: str, 
#         params: Optional[tuple] = None
#     ) -> int:
#         """
#         Execute INSERT/UPDATE/DELETE and return affected row count.
        
#         Args:
#             query: SQL query string
#             params: Query parameters (optional)
            
#         Returns:
#             Number of affected rows
#         """
#         with self.get_cursor() as cursor:
#             cursor.execute(query, params or ())
#             return cursor.rowcount
    
#     def execute_insert_returning(
#         self, 
#         query: str, 
#         params: Optional[tuple] = None
#     ) -> Optional[Dict[str, Any]]:
#         """
#         Execute INSERT with RETURNING clause.
        
#         Args:
#             query: SQL query with RETURNING clause
#             params: Query parameters (optional)
            
#         Returns:
#             Dictionary of returned row or None
#         """
#         with self.get_cursor() as cursor:
#             cursor.execute(query, params or ())
#             result = cursor.fetchone()
#             return dict(result) if result else None
    
#     def close(self):
#         """Close all connections in the pool."""
#         if self.pool:
#             self.pool.closeall()


# # Global database instance (initialized once)
# # db = DatabaseConnection()
# _db: Optional[DatabaseConnection] = None

# def get_db() -> DatabaseConnection:
#     global _db
#     if _db is None:
#         _db = DatabaseConnection()
#     return _db

"""
Database connection and helper utilities for Expense MCP Server.

- Cloud-safe (FastMCP, Supabase, Neon, Railway)
- Lazy initialization
- Connection pooling
- SSL handled automatically
"""

import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

load_dotenv()


class DatabaseConnection:
    """
    PostgreSQL connection manager using psycopg v3.
    """

    def __init__(self):
        self.pool: ConnectionPool = self._initialize_pool()

    def _initialize_pool(self) -> ConnectionPool:
        db_url = os.getenv("DATABASE_URL")

        if not db_url:
            raise ValueError("DATABASE_URL environment variable must be set")

        # psycopg v3 handles SSL automatically in cloud environments
        return ConnectionPool(
            conninfo=db_url,
            min_size=1,
            max_size=3,
            timeout=5,
            kwargs={
                "row_factory": dict_row
            }
        )

    @contextmanager
    def get_cursor(self):
        """
        Context manager that yields a cursor and safely returns
        the connection to the pool.
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                yield cursor

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def execute_update(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> int:
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.rowcount

    def execute_insert_returning(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> Optional[Dict[str, Any]]:
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()

    def close(self):
        self.pool.close()


# -------- Lazy global accessor (CRITICAL FOR CLOUD) --------

_db: Optional[DatabaseConnection] = None


def get_db() -> DatabaseConnection:
    global _db
    if _db is None:
        _db = DatabaseConnection()
    return _db
