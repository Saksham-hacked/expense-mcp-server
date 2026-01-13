"""
SQL query helpers and data access layer for Expense MCP Server.

All queries enforce user_id isolation for multi-user safety.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
from db import db


class ExpenseModel:
    """
    Data access layer for expense operations.
    All methods enforce user_id isolation.
    """
    
    @staticmethod
    def add_expense(
        user_id: str,
        expense_date: date,
        amount: Decimal,
        category: str,
        merchant: Optional[str] = None,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Insert a new expense and return the created record.
        
        Args:
            user_id: User identifier (mandatory)
            expense_date: Date of expense
            amount: Expense amount (must be positive)
            category: Expense category
            merchant: Optional merchant name
            note: Optional note
            
        Returns:
            Created expense record with id
            
        Raises:
            ValueError: If amount <= 0 or user_id is empty
        """
        if not user_id or not user_id.strip():
            raise ValueError("user_id is required and cannot be empty")
        
        if amount <= 0:
            raise ValueError(f"amount must be positive, got {amount}")
        
        query = """
            INSERT INTO expenses (user_id, date, amount, category, merchant, note)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, date, amount, category, merchant, note, created_at
        """
        
        result = db.execute_insert_returning(
            query,
            (user_id, expense_date, amount, category, merchant, note)
        )
        
        if not result:
            raise RuntimeError("Failed to insert expense")
        
        return result
    
    @staticmethod
    def list_expenses(
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        List all expenses for a user within a date range.
        
        Args:
            user_id: User identifier
            start_date: Range start (inclusive)
            end_date: Range end (inclusive)
            
        Returns:
            List of expense records ordered by date ASC
        """
        if not user_id or not user_id.strip():
            raise ValueError("user_id is required and cannot be empty")
        
        query = """
            SELECT id, user_id, date, amount, category, merchant, note, created_at
            FROM expenses
            WHERE user_id = %s
              AND date BETWEEN %s AND %s
            ORDER BY date ASC, created_at ASC
        """
        
        return db.execute_query(query, (user_id, start_date, end_date))
    
    @staticmethod
    def summarize_by_category(
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Summarize expenses by category within a date range.
        
        Args:
            user_id: User identifier
            start_date: Range start (inclusive)
            end_date: Range end (inclusive)
            
        Returns:
            List of {category, total} dicts ordered by total DESC
        """
        if not user_id or not user_id.strip():
            raise ValueError("user_id is required and cannot be empty")
        
        query = """
            SELECT 
                category,
                SUM(amount) as total
            FROM expenses
            WHERE user_id = %s
              AND date BETWEEN %s AND %s
            GROUP BY category
            ORDER BY total DESC
        """
        
        return db.execute_query(query, (user_id, start_date, end_date))
    
    @staticmethod
    def get_monthly_summary(
        user_id: str,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive monthly expense summary.
        
        Args:
            user_id: User identifier
            year: Year (e.g., 2025)
            month: Month (1-12)
            
        Returns:
            Dictionary with total_spending and category_breakdown
        """
        if not user_id or not user_id.strip():
            raise ValueError("user_id is required and cannot be empty")
        
        # Calculate month boundaries
        from calendar import monthrange
        last_day = monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        # Get total spending
        total_query = """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE user_id = %s
              AND date BETWEEN %s AND %s
        """
        total_result = db.execute_query(total_query, (user_id, start_date, end_date))
        total_spending = float(total_result[0]['total']) if total_result else 0.0
        
        # Get category breakdown
        category_breakdown = ExpenseModel.summarize_by_category(
            user_id, start_date, end_date
        )
        
        return {
            "user_id": user_id,
            "year": year,
            "month": month,
            "total_spending": total_spending,
            "category_breakdown": category_breakdown,
            "expense_count": len(
                ExpenseModel.list_expenses(user_id, start_date, end_date)
            )
        }
