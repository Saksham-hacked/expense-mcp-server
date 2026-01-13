-- Expense Management MCP Server - PostgreSQL Schema
-- Multi-user expense tracking with strict data isolation

CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    category TEXT NOT NULL,
    merchant TEXT,
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for efficient user-specific date range queries
CREATE INDEX idx_expenses_user_date
ON expenses(user_id, date);

-- Optional: Index for category-based queries
CREATE INDEX idx_expenses_user_category
ON expenses(user_id, category);
