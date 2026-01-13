"""
Test suite for Expense MCP Server

Run with: pytest test_expenses.py -v

Prerequisites:
- Set DATABASE_URL environment variable
- Run schema.sql on test database
- Install: pip install pytest pytest-asyncio
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from tools import (
    add_expense_tool,
    list_expenses_tool,
    summarize_expenses_tool,
    monthly_report_tool,
    validate_date_string,
    validate_month_string
)
from models import ExpenseModel


# Test user IDs
TEST_USER_1 = "test_user_1"
TEST_USER_2 = "test_user_2"


class TestDateValidation:
    """Test date string validation"""
    
    def test_valid_date(self):
        result = validate_date_string("2025-01-15")
        assert result == date(2025, 1, 15)
    
    def test_invalid_date_format(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_string("2025/01/15")
    
    def test_invalid_date_value(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_string("2025-13-45")
    
    def test_valid_month(self):
        year, month = validate_month_string("2025-01")
        assert year == 2025
        assert month == 1
    
    def test_invalid_month_format(self):
        with pytest.raises(ValueError, match="Invalid month format"):
            validate_month_string("2025/01")


class TestAddExpense:
    """Test add_expense tool"""
    
    def test_add_valid_expense(self):
        result = add_expense_tool(
            user_id=TEST_USER_1,
            date="2025-01-15",
            amount=45.50,
            category="Food",
            merchant="Starbucks",
            note="Coffee meeting"
        )
        
        assert result["user_id"] == TEST_USER_1
        assert result["amount"] == 45.50
        assert result["category"] == "Food"
        assert result["merchant"] == "Starbucks"
        assert result["note"] == "Coffee meeting"
        assert "id" in result
    
    def test_add_expense_minimum_fields(self):
        result = add_expense_tool(
            user_id=TEST_USER_1,
            date="2025-01-16",
            amount=100.00,
            category="Transport"
        )
        
        assert result["user_id"] == TEST_USER_1
        assert result["amount"] == 100.00
        assert result["category"] == "Transport"
        assert result["merchant"] is None
        assert result["note"] is None
    
    def test_add_expense_empty_user_id(self):
        with pytest.raises(ValueError, match="user_id is required"):
            add_expense_tool(
                user_id="",
                date="2025-01-15",
                amount=50.00,
                category="Food"
            )
    
    def test_add_expense_negative_amount(self):
        with pytest.raises(ValueError, match="amount must be positive"):
            add_expense_tool(
                user_id=TEST_USER_1,
                date="2025-01-15",
                amount=-50.00,
                category="Food"
            )
    
    def test_add_expense_zero_amount(self):
        with pytest.raises(ValueError, match="amount must be positive"):
            add_expense_tool(
                user_id=TEST_USER_1,
                date="2025-01-15",
                amount=0,
                category="Food"
            )
    
    def test_add_expense_invalid_date(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            add_expense_tool(
                user_id=TEST_USER_1,
                date="2025/01/15",
                amount=50.00,
                category="Food"
            )
    
    def test_add_expense_empty_category(self):
        with pytest.raises(ValueError, match="category is required"):
            add_expense_tool(
                user_id=TEST_USER_1,
                date="2025-01-15",
                amount=50.00,
                category=""
            )


class TestListExpenses:
    """Test list_expenses tool"""
    
    @pytest.fixture(autouse=True)
    def setup_expenses(self):
        """Create test expenses before each test"""
        # Add expenses for user 1
        add_expense_tool(TEST_USER_1, "2025-01-10", 50.00, "Food")
        add_expense_tool(TEST_USER_1, "2025-01-15", 100.00, "Transport")
        add_expense_tool(TEST_USER_1, "2025-01-20", 75.00, "Food")
        
        # Add expenses for user 2 (should be isolated)
        add_expense_tool(TEST_USER_2, "2025-01-12", 200.00, "Food")
        
        yield
        
        # TODO: Cleanup test data after each test
    
    def test_list_expenses_date_range(self):
        expenses = list_expenses_tool(
            user_id=TEST_USER_1,
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        assert len(expenses) >= 3
        assert all(exp["user_id"] == TEST_USER_1 for exp in expenses)
        
        # Verify ordering (oldest first)
        dates = [exp["date"] for exp in expenses]
        assert dates == sorted(dates)
    
    def test_list_expenses_narrow_range(self):
        expenses = list_expenses_tool(
            user_id=TEST_USER_1,
            start_date="2025-01-15",
            end_date="2025-01-15"
        )
        
        # Should only return expense from Jan 15
        assert all(exp["date"] == "2025-01-15" for exp in expenses)
    
    def test_list_expenses_no_results(self):
        expenses = list_expenses_tool(
            user_id=TEST_USER_1,
            start_date="2025-12-01",
            end_date="2025-12-31"
        )
        
        assert expenses == []
    
    def test_list_expenses_user_isolation(self):
        """Verify users cannot see each other's data"""
        expenses_user1 = list_expenses_tool(
            TEST_USER_1, "2025-01-01", "2025-01-31"
        )
        expenses_user2 = list_expenses_tool(
            TEST_USER_2, "2025-01-01", "2025-01-31"
        )
        
        # User 1 should not see user 2's expenses
        assert all(exp["user_id"] == TEST_USER_1 for exp in expenses_user1)
        assert all(exp["user_id"] == TEST_USER_2 for exp in expenses_user2)
        
        # Different counts
        assert len(expenses_user1) != len(expenses_user2)
    
    def test_list_expenses_invalid_date_order(self):
        with pytest.raises(ValueError, match="start_date .* cannot be after end_date"):
            list_expenses_tool(
                TEST_USER_1,
                start_date="2025-01-31",
                end_date="2025-01-01"
            )


class TestSummarizeExpenses:
    """Test summarize_expenses tool"""
    
    @pytest.fixture(autouse=True)
    def setup_expenses(self):
        """Create test expenses with multiple categories"""
        add_expense_tool(TEST_USER_1, "2025-01-10", 50.00, "Food")
        add_expense_tool(TEST_USER_1, "2025-01-12", 75.00, "Food")
        add_expense_tool(TEST_USER_1, "2025-01-15", 100.00, "Transport")
        add_expense_tool(TEST_USER_1, "2025-01-18", 200.00, "Entertainment")
        add_expense_tool(TEST_USER_1, "2025-01-20", 25.00, "Food")
        
        yield
    
    def test_summarize_by_category(self):
        summary = summarize_expenses_tool(
            user_id=TEST_USER_1,
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        # Should have 3 categories
        categories = {item["category"] for item in summary}
        assert "Food" in categories
        assert "Transport" in categories
        assert "Entertainment" in categories
        
        # Verify Food total (50 + 75 + 25 = 150)
        food_total = next(
            item["total"] for item in summary 
            if item["category"] == "Food"
        )
        assert food_total == 150.00
    
    def test_summarize_ordering(self):
        """Verify results are ordered by total DESC"""
        summary = summarize_expenses_tool(
            TEST_USER_1, "2025-01-01", "2025-01-31"
        )
        
        totals = [item["total"] for item in summary]
        assert totals == sorted(totals, reverse=True)
    
    def test_summarize_empty_range(self):
        summary = summarize_expenses_tool(
            TEST_USER_1, "2025-12-01", "2025-12-31"
        )
        
        assert summary == []


class TestMonthlyReport:
    """Test monthly_report tool"""
    
    @pytest.fixture(autouse=True)
    def setup_expenses(self):
        """Create test expenses for a specific month"""
        add_expense_tool(TEST_USER_1, "2025-01-05", 100.00, "Food")
        add_expense_tool(TEST_USER_1, "2025-01-10", 200.00, "Transport")
        add_expense_tool(TEST_USER_1, "2025-01-15", 50.00, "Food")
        add_expense_tool(TEST_USER_1, "2025-01-20", 150.00, "Entertainment")
        
        yield
    
    def test_monthly_report_structure(self):
        report = monthly_report_tool(
            user_id=TEST_USER_1,
            month="2025-01"
        )
        
        # Verify structure
        assert "user_id" in report
        assert "month" in report
        assert "total_spending" in report
        assert "expense_count" in report
        assert "category_breakdown" in report
        assert "summary" in report
        
        assert report["user_id"] == TEST_USER_1
        assert report["month"] == "2025-01"
    
    def test_monthly_report_totals(self):
        report = monthly_report_tool(TEST_USER_1, "2025-01")
        
        # Total: 100 + 200 + 50 + 150 = 500
        assert report["total_spending"] == 500.00
        assert report["expense_count"] >= 4
    
    def test_monthly_report_category_breakdown(self):
        report = monthly_report_tool(TEST_USER_1, "2025-01")
        
        breakdown = report["category_breakdown"]
        categories = {item["category"] for item in breakdown}
        
        assert "Food" in categories
        assert "Transport" in categories
        assert "Entertainment" in categories
    
    def test_monthly_report_summary_text(self):
        report = monthly_report_tool(TEST_USER_1, "2025-01")
        
        summary = report["summary"]
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "2025-01" in summary
        assert "$" in summary  # Should contain dollar amount
    
    def test_monthly_report_empty_month(self):
        report = monthly_report_tool(TEST_USER_1, "2025-12")
        
        assert report["total_spending"] == 0.0
        assert report["expense_count"] == 0
        assert report["category_breakdown"] == []
        assert "No expenses recorded" in report["summary"]
    
    def test_monthly_report_invalid_month_format(self):
        with pytest.raises(ValueError, match="Invalid month format"):
            monthly_report_tool(TEST_USER_1, "2025/01")


class TestDataIsolation:
    """Test multi-user data isolation"""
    
    def test_users_cannot_see_each_others_expenses(self):
        # User 1 adds expense
        exp1 = add_expense_tool(TEST_USER_1, "2025-01-15", 100.00, "Food")
        
        # User 2 adds expense
        exp2 = add_expense_tool(TEST_USER_2, "2025-01-15", 200.00, "Food")
        
        # User 1 lists expenses
        user1_expenses = list_expenses_tool(
            TEST_USER_1, "2025-01-01", "2025-01-31"
        )
        
        # Should only see own expenses
        user1_ids = {exp["id"] for exp in user1_expenses}
        assert exp1["id"] in user1_ids
        assert exp2["id"] not in user1_ids
    
    def test_summary_isolation(self):
        # Both users spend on Food
        add_expense_tool(TEST_USER_1, "2025-01-15", 100.00, "Food")
        add_expense_tool(TEST_USER_2, "2025-01-15", 200.00, "Food")
        
        # Get summaries
        summary1 = summarize_expenses_tool(
            TEST_USER_1, "2025-01-01", "2025-01-31"
        )
        summary2 = summarize_expenses_tool(
            TEST_USER_2, "2025-01-01", "2025-01-31"
        )
        
        # Different totals
        total1 = next(
            item["total"] for item in summary1 
            if item["category"] == "Food"
        )
        total2 = next(
            item["total"] for item in summary2 
            if item["category"] == "Food"
        )
        
        assert total1 != total2


# TODO: Add integration tests for database connection
# TODO: Add tests for concurrent user operations
# TODO: Add performance tests for large datasets
# TODO: Add tests for database error handling
