# Expense Management MCP Server

**A cloud-ready, multi-user expense tracking capability built with FastMCP and PostgreSQL.**

---

## 🎯 What This MCP Server Does

This is a **Model Context Protocol (MCP) server** that provides expense management capabilities. It exposes 4 tools that AI assistants (like Claude) can use to:

- Add expenses with details (date, amount, category, merchant, notes)
- List expenses within date ranges
- Summarize spending by category
- Generate monthly expense reports

**Key Design Principle:** This server is a **capability boundary** — it owns expense data and logic, nothing more.

---

## 🧩 Why MCP?

This project uses the **Model Context Protocol** to create a **modular, tool-driven AI system**:

1. **Separation of Concerns**: This server only handles expenses — other capabilities (emails, tasks, calendar) are separate MCP servers
2. **AI-Powered Interfaces**: Any AI assistant can use these tools without custom integrations
3. **Composability**: Multiple MCP servers can work together via a backend orchestrator
4. **Cloud-Native**: Designed to run on FastMCP Cloud with zero local dependencies

**MCP is NOT:**
- A chatbot framework
- A UI framework
- A monolithic backend
- An authentication system

**MCP IS:**
- A protocol for exposing capabilities to AI assistants
- A way to build composable, tool-based systems
- A boundary between capability logic and orchestration

---

## 🛠️ Exposed MCP Tools

### 1. `add_expense`

Add a new expense for a user.

**Input:**
```json
{
  "user_id": "user_123",
  "date": "2025-01-15",
  "amount": 45.50,
  "category": "Food",
  "merchant": "Starbucks",
  "note": "Coffee meeting"
}
```

**Returns:** Created expense with generated UUID

---

### 2. `list_expenses`

List expenses within a date range.

**Input:**
```json
{
  "user_id": "user_123",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

**Returns:** Array of expenses ordered by date (oldest first)

---

### 3. `summarize_expenses`

Summarize spending by category.

**Input:**
```json
{
  "user_id": "user_123",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

**Returns:**
```json
[
  { "category": "Food", "total": 450.75 },
  { "category": "Transport", "total": 230.00 }
]
```

---

### 4. `monthly_report`

Generate a monthly expense report.

**Input:**
```json
{
  "user_id": "user_123",
  "month": "2025-01"
}
```

**Returns:** Total spending, category breakdown, expense count, and natural language summary

---

## 🔒 Multi-User Isolation

This server is designed for **multi-user environments** with strict data isolation:

- Every query filters by `user_id`
- Users cannot access each other's data
- No user authentication logic (handled by backend orchestrator)
- `user_id` is injected and trusted from the calling system

**Database Pattern:**
```sql
SELECT * FROM expenses 
WHERE user_id = ? AND date BETWEEN ? AND ?
```

All queries enforce `user_id` filtering at the SQL level.

---

## 🏗️ Architecture: Modular Personal Manager System

This MCP server is **one capability module** in a larger Personal Manager system:

```
┌─────────────────────────────────────────────┐
│         Backend Orchestrator                │
│  (Authentication, Routing, Workflows)       │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴───────┬──────────┬──────────┐
       │               │          │          │
   ┌───▼───┐     ┌────▼───┐  ┌───▼───┐  ┌───▼───┐
   │Expense│     │ Email  │  │ Task  │  │ PKOS  │
   │  MCP  │     │  MCP   │  │  MCP  │  │  MCP  │
   └───────┘     └────────┘  └───────┘  └───────┘
```

### Design Principles

1. **Each capability is a separate MCP server**
   - Expense tracking = this server
   - Email management = separate MCP server
   - Task management = separate MCP server
   - Personal knowledge (PKOS) = separate MCP server

2. **MCP servers are isolated**
   - Each owns its database schema
   - Each exposes explicit tools
   - No cross-server dependencies

3. **Backend orchestrator handles:**
   - User authentication
   - MCP server routing
   - Multi-step workflows
   - User session management

4. **AI assistants call tools via orchestrator**
   - User: "How much did I spend on food last month?"
   - Orchestrator: Authenticates user → Calls expense MCP `monthly_report`
   - MCP: Returns data for that user only

---

## 🚀 Adding New Capabilities

When adding new features to the Personal Manager system:

✅ **DO:** Create a new MCP server
- New capability = new MCP server project
- Follow the same structure (main.py, tools.py, models.py, db.py)
- Expose tools for that capability only

❌ **DON'T:** Modify this expense server
- Don't add email/task/calendar logic here
- Don't create cross-capability dependencies
- Don't merge MCP servers

**Example: Adding Task Management**
1. Create `task-mcp-server/` (separate project)
2. Expose tools: `add_task`, `list_tasks`, `complete_task`
3. Use separate database schema for tasks
4. Deploy as separate FastMCP Cloud instance
5. Backend orchestrator routes task-related queries to task MCP

---

## 🗄️ Database Schema

PostgreSQL schema with multi-user isolation:

```sql
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

CREATE INDEX idx_expenses_user_date ON expenses(user_id, date);
```

**Why PostgreSQL?**
- Cloud-hosted (Supabase, Neon, Railway, etc.)
- ACID compliance for financial data
- Strong typing with NUMERIC for currency
- Efficient indexing for date-range queries

---

## 🚀 Deployment

### Prerequisites

1. **PostgreSQL database** (cloud-hosted recommended):
   - [Supabase](https://supabase.com) (free tier available)
   - [Neon](https://neon.tech) (serverless Postgres)
   - [Railway](https://railway.app)

2. **Database setup**:
   ```bash
   psql $DATABASE_URL < schema.sql
   ```

3. **Environment variable**:
   ```bash
   export DATABASE_URL="postgresql://user:password@host:port/database"
   ```

### Deploy to FastMCP Cloud

```bash
# Install dependencies
pip install -r requirements.txt

# Deploy to FastMCP Cloud
fastmcp deploy
```

FastMCP Cloud handles:
- HTTP transport automatically
- Server lifecycle management
- Auto-scaling
- Logging and monitoring

**No local server needed** — this is designed for cloud deployment.

---

## 🧪 Local Testing (Optional)

For development testing only:

```bash
# Set environment variable
export DATABASE_URL="postgresql://localhost/expenses_dev"

# Create test database
createdb expenses_dev
psql expenses_dev < schema.sql

# Run server (for testing tools)
python main.py
```

**Note:** Production deployment should use FastMCP Cloud, not local testing.

---

## 🔐 Security Model

### What This Server Does

- ✅ Validates user_id is present and non-empty
- ✅ Validates input formats (dates, amounts)
- ✅ Enforces data isolation via SQL WHERE clauses
- ✅ Handles database errors gracefully
- ✅ Uses parameterized queries (SQL injection protection)

### What This Server Does NOT Do

- ❌ User authentication (handled by backend)
- ❌ Authorization checks (trusts backend's user_id)
- ❌ Session management
- ❌ Rate limiting (handled by FastMCP Cloud)
- ❌ API key validation

**Security Assumption:** The `user_id` parameter is injected and validated by a trusted backend orchestrator before reaching this MCP server.

---

## 📊 Data Flow Example

**User Query:** "How much did I spend on groceries last month?"

1. **User Interface** (web/mobile app)
   - User authenticated via OAuth/JWT
   - Request sent to backend orchestrator

2. **Backend Orchestrator**
   - Validates user session → extracts `user_id`
   - Determines which MCP server to call (expense MCP)
   - Calls `summarize_expenses` tool with injected `user_id`

3. **Expense MCP Server** (this server)
   - Receives: `{"user_id": "user_123", "start_date": "2024-12-01", "end_date": "2024-12-31"}`
   - Queries: `SELECT category, SUM(amount) FROM expenses WHERE user_id = 'user_123' AND ...`
   - Returns: `[{"category": "Groceries", "total": 450.75}]`

4. **Backend Orchestrator**
   - Formats response for user
   - Returns to user interface

5. **User Interface**
   - Displays: "You spent $450.75 on groceries last month"

---

## 🧩 Extension Points

This server is designed for **extension without modification**:

### Adding New Expense Categories
- No code changes needed
- Categories are free-form text fields
- TODO: Add optional category validation/standardization

### Adding Recurring Expenses
- **Option A:** New MCP tool in this server
- **Option B:** Separate "Recurring Expenses" MCP server
- Recommended: Option B (follows single-responsibility principle)

### Adding Receipt Storage
- **Don't add to this server**
- Create separate "Document Storage" MCP server
- Expense MCP references document IDs

### Adding Budget Tracking
- **Don't add to this server**
- Create separate "Budget Management" MCP server
- Budget MCP can call expense MCP tools if needed

**General Rule:** If a feature isn't directly about recording/querying expenses, it belongs in a separate MCP server.

---

## 🤝 Contributing

When contributing:

1. **Follow the specification** in `docs/phase-1-spec.md`
2. **Don't add features** not in the spec (create new MCP servers instead)
3. **Maintain data isolation** — all queries must filter by user_id
4. **No UI code** — this is a tool server only
5. **No auth code** — user_id is injected externally

---

## 📚 Related Documentation

- [FastMCP Documentation](https://fastmcp.com/docs)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [Anthropic MCP Guide](https://docs.anthropic.com/claude/docs/model-context-protocol)

---

## 🎓 Learning Resources

**New to MCP?**
- [What is MCP?](https://modelcontextprotocol.io/introduction)
- [Building Your First MCP Server](https://fastmcp.com/quickstart)

**Architecture Patterns:**
- Why modular MCP servers > monolithic APIs
- How MCP enables AI-first application architecture
- Building composable capability systems

---

## 📝 License

MIT License - see LICENSE file for details

---

## ✨ Summary

This MCP server demonstrates:

✅ **Single Responsibility** — Expenses only  
✅ **Multi-User Safe** — Strict data isolation  
✅ **Cloud-Ready** — FastMCP Cloud deployment  
✅ **Tool-Driven** — AI assistants call explicit tools  
✅ **Composable** — Part of larger modular system  
✅ **Production-Grade** — Error handling, validation, PostgreSQL  

**Next Steps:**
1. Deploy to FastMCP Cloud
2. Connect backend orchestrator
3. Build additional capability MCP servers (email, tasks, etc.)
4. Create user interface that calls orchestrator

---

**Questions?** Check FastMCP docs or open an issue.
