"""
Expense Management MCP Server

A FastMCP-based Model Context Protocol server for expense tracking.
Designed for cloud deployment with PostgreSQL and multi-user support.

This server exposes 4 MCP tools:
- add_expense: Add a new expense
- list_expenses: List expenses in a date range
- summarize_expenses: Summarize expenses by category
- monthly_report: Generate monthly expense report

Architecture:
- Each user's data is isolated via user_id
- No authentication (user_id injected by backend orchestrator)
- Cloud-ready (FastMCP Cloud deployment)
- PostgreSQL for persistent storage
"""

from fastmcp import FastMCP
from tools import (
    add_expense_tool,
    list_expenses_tool,
    summarize_expenses_tool,
    monthly_report_tool
)

# Initialize FastMCP server
mcp = FastMCP("Expense Management")


@mcp.tool()
def add_expense(
    user_id: str,
    date: str,
    amount: float,
    category: str,
    merchant: str = None,
    note: str = None
) -> dict:
    """
    Add a new expense for a user.
    
    Args:
        user_id: User identifier (required)
        date: Expense date in YYYY-MM-DD format (required)
        amount: Expense amount, must be positive (required)
        category: Expense category (required)
        merchant: Merchant name (optional)
        note: Additional note (optional)
        
    Returns:
        Created expense record with generated id
        
    Example:
        {
            "user_id": "user_123",
            "date": "2025-01-15",
            "amount": 45.50,
            "category": "Food",
            "merchant": "Starbucks",
            "note": "Coffee meeting"
        }
    """
    return add_expense_tool(user_id, date, amount, category, merchant, note)


@mcp.tool()
def list_expenses(
    user_id: str,
    start_date: str,
    end_date: str
) -> list:
    """
    List a user's expenses within a date range.
    
    Args:
        user_id: User identifier (required)
        start_date: Range start in YYYY-MM-DD format (required)
        end_date: Range end in YYYY-MM-DD format (required)
        
    Returns:
        Array of expense objects ordered by date ASC
        
    Example:
        {
            "user_id": "user_123",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31"
        }
    """
    return list_expenses_tool(user_id, start_date, end_date)


@mcp.tool()
def summarize_expenses(
    user_id: str,
    start_date: str,
    end_date: str
) -> list:
    """
    Summarize expenses by category within a date range.
    
    Args:
        user_id: User identifier (required)
        start_date: Range start in YYYY-MM-DD format (required)
        end_date: Range end in YYYY-MM-DD format (required)
        
    Returns:
        Array of {category, total} objects ordered by total DESC
        
    Example:
        {
            "user_id": "user_123",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31"
        }
    """
    return summarize_expenses_tool(user_id, start_date, end_date)


@mcp.tool()
def monthly_report(
    user_id: str,
    month: str
) -> dict:
    """
    Generate a monthly expense report.
    
    Args:
        user_id: User identifier (required)
        month: Month in YYYY-MM format (required)
        
    Returns:
        Monthly report with total_spending, category_breakdown, and summary
        
    Example:
        {
            "user_id": "user_123",
            "month": "2025-01"
        }
    """
    return monthly_report_tool(user_id, month)


# Entry point for FastMCP Cloud deployment
if __name__ == "__main__":
    # FastMCP Cloud will handle transport automatically
    # No need to specify stdio/sse - defaults to HTTP
   mcp.run()
   

