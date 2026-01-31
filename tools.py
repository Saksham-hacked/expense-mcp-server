"""
MCP Tool definitions for Expense Management Server.

Exposes exactly 4 tools as specified:
1. add_expense
2. list_expenses
3. summarize_expenses
4. monthly_report
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List
from models import ExpenseModel


def validate_date_string(date_str: str) -> date:
    """
    Validate and parse YYYY-MM-DD date string.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        datetime.date object
        
    Raises:
        ValueError: If date format is invalid
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(
            f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD"
        )


def validate_month_string(month_str: str) -> tuple[int, int]:
    """
    Validate and parse YYYY-MM month string.
    
    Args:
        month_str: Month string in YYYY-MM format
        
    Returns:
        Tuple of (year, month)
        
    Raises:
        ValueError: If month format is invalid
    """
    try:
        dt = datetime.strptime(month_str, "%Y-%m")
        return dt.year, dt.month
    except ValueError:
        raise ValueError(
            f"Invalid month format: '{month_str}'. Expected YYYY-MM"
        )


def add_expense_tool(
    user_id: str,
    date: str,
    amount: float,
    category: str,
    merchant: str = None,
    note: str = None
) -> Dict[str, Any]:
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
        
    Raises:
        ValueError: If validation fails
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        raise ValueError("user_id is required and cannot be empty")
    
    expense_date = validate_date_string(date)
    
    if amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")
    
    if not category or not category.strip():
        raise ValueError("category is required and cannot be empty")
    
    # Convert to Decimal for precision
    amount_decimal = Decimal(str(amount))
    
    # Insert expense
    result = ExpenseModel.add_expense(
        user_id=user_id,
        expense_date=expense_date,
        amount=amount_decimal,
        category=category.strip(),
        merchant=merchant.strip() if merchant else None,
        note=note.strip() if note else None
    )
    
    # Convert Decimal and date to JSON-serializable types
    return {
        "id": str(result["id"]),
        "user_id": result["user_id"],
        "date": result["date"].isoformat(),
        "amount": float(result["amount"]),
        "category": result["category"],
        "merchant": result["merchant"],
        "note": result["note"],
        "created_at": result["created_at"].isoformat()
    }


def list_expenses_tool(
    user_id: str,
    start_date: str,
    end_date: str
) -> List[Dict[str, Any]]:
    """
    List a user's expenses within a date range.
    
    Args:
        user_id: User identifier (required)
        start_date: Range start in YYYY-MM-DD format (required)
        end_date: Range end in YYYY-MM-DD format (required)
        
    Returns:
        Array of expense objects ordered by date ASC
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        raise ValueError("user_id is required and cannot be empty")
    
    start = validate_date_string(start_date)
    end = validate_date_string(end_date)
    
    if start > end:
        raise ValueError(
            f"start_date ({start_date}) cannot be after end_date ({end_date})"
        )
    
    # Get expenses
    expenses = ExpenseModel.list_expenses(user_id, start, end)
    
    # Convert to JSON-serializable format
    return [
        {
            "id": str(exp["id"]),
            "user_id": exp["user_id"],
            "date": exp["date"].isoformat(),
            "amount": float(exp["amount"]),
            "category": exp["category"],
            "merchant": exp["merchant"],
            "note": exp["note"],
            "created_at": exp["created_at"].isoformat()
        }
        for exp in expenses
    ]


def summarize_expenses_tool(
    user_id: str,
    start_date: str,
    end_date: str
) -> List[Dict[str, Any]]:
    """
    Summarize expenses by category within a date range.
    
    Args:
        user_id: User identifier (required)
        start_date: Range start in YYYY-MM-DD format (required)
        end_date: Range end in YYYY-MM-DD format (required)
        
    Returns:
        Array of {category, total} objects ordered by total DESC
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        raise ValueError("user_id is required and cannot be empty")
    
    start = validate_date_string(start_date)
    end = validate_date_string(end_date)
    
    if start > end:
        raise ValueError(
            f"start_date ({start_date}) cannot be after end_date ({end_date})"
        )
    
    # Get category summary
    summary = ExpenseModel.summarize_by_category(user_id, start, end)
    
    # Convert to JSON-serializable format
    return [
        {
            "category": item["category"],
            "total": float(item["total"])
        }
        for item in summary
    ]


def monthly_report_tool(
    user_id: str,
    month: str
) -> Dict[str, Any]:
    """
    Generate a monthly expense report.
    
    Args:
        user_id: User identifier (required)
        month: Month in YYYY-MM format (required)
        
    Returns:
        Monthly report with total_spending, category_breakdown, and summary
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        raise ValueError("user_id is required and cannot be empty")
    
    year, month_num = validate_month_string(month)
    
    # Get monthly summary
    summary = ExpenseModel.get_monthly_summary(user_id, year, month_num)
    
    # Convert category breakdown to JSON-serializable
    category_breakdown = [
        {
            "category": item["category"],
            "total": float(item["total"])
        }
        for item in summary["category_breakdown"]
    ]
    
    # Generate natural language summary
    total = summary["total_spending"]
    count = summary["expense_count"]
    
    if count == 0:
        summary_text = f"No expenses recorded for {month}."
    else:
        top_category = category_breakdown[0] if category_breakdown else None
        if top_category:
            summary_text = (
                f"In {month}, you spent {total:.2f}Rs across {count} expenses. "
                f"Your highest spending category was {top_category['category']} "
                f"at {top_category['total']:.2f}Rs."
            )
        else:
            summary_text = f"In {month}, you spent {total:.2f}Rs across {count} expenses."
    
    return {
        "user_id": user_id,
        "month": month,
        "total_spending": total,
        "expense_count": count,
        "category_breakdown": category_breakdown,
        "summary": summary_text
    }
