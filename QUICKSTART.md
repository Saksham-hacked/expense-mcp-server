# ⚡ Quick Start Guide - 5 Minutes to Deployment

## 🎯 Goal
Get your Expense MCP Server running in the cloud in under 5 minutes.

---

## Step 1: Database (2 minutes)

### Option: Supabase (Easiest)

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project" → Sign in with GitHub
3. Click "New Project"
4. Fill in:
   - **Name:** `expense-mcp-db`
   - **Database Password:** (save this!)
   - **Region:** Choose closest to you
5. Click "Create new project" (wait ~2 minutes)
6. Once ready, go to **Settings** → **Database**
7. Scroll to "Connection string" → Copy the **URI** format
8. Replace `[YOUR-PASSWORD]` with your actual password

Your DATABASE_URL looks like:
```
postgresql://postgres:YOUR_PASSWORD@db.abc123xyz.supabase.co:5432/postgres
```

---

## Step 2: Apply Schema (1 minute)

### Method A: Supabase SQL Editor (Recommended)

1. In Supabase dashboard, click **SQL Editor** (left sidebar)
2. Click "New query"
3. Open `schema.sql` from this project
4. Copy entire contents
5. Paste into Supabase SQL Editor
6. Click "Run" (bottom right)
7. Should see "Success. No rows returned"

### Method B: Command Line

```bash
# Replace with your actual DATABASE_URL
export DATABASE_URL="postgresql://postgres:password@db.xyz.supabase.co:5432/postgres"

# Apply schema
psql $DATABASE_URL < schema.sql
```

---

## Step 3: Configure Environment (30 seconds)

```bash
# In your expense-mcp-server directory
cp .env.example .env

# Edit .env
nano .env  # or use any text editor
```

Paste your DATABASE_URL:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xyz.supabase.co:5432/postgres
```

Save and exit.

---

## Step 4: Install Dependencies (30 seconds)

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 5: Test Locally (1 minute)

```bash
# Load environment variables
export $(cat .env | xargs)  # Windows: just use the .env file

# Run server
python main.py
```

You should see:
```
[INFO] FastMCP server starting...
[INFO] Tools registered: add_expense, list_expenses, summarize_expenses, monthly_report
```

Press Ctrl+C to stop.

---

## Step 6: Deploy to FastMCP Cloud (1 minute)

```bash
# Login (first time only)
fastmcp login

# Deploy
fastmcp deploy

# When prompted:
# - Server name: expense-management
# - Environment variables: Paste your DATABASE_URL
```

After deployment:
```
✓ Server deployed successfully!
URL: https://expense-management-abc123.fastmcp.com
```

---

## ✅ Verification

Test your deployed server:

```bash
# Get server info
fastmcp info expense-management

# Test add_expense
fastmcp call expense-management add_expense \
  --user_id "test_user" \
  --date "2025-01-15" \
  --amount 50.00 \
  --category "Food" \
  --merchant "Test Store"

# Test list_expenses
fastmcp call expense-management list_expenses \
  --user_id "test_user" \
  --start_date "2025-01-01" \
  --end_date "2025-01-31"
```

You should see your expense returned!

---

## 🎉 Success!

Your Expense MCP Server is now:
- ✅ Running in the cloud
- ✅ Connected to PostgreSQL
- ✅ Ready to accept requests
- ✅ Multi-user ready

---

## 🔄 Next Steps

### Integrate with Backend
Point your backend orchestrator to:
```
https://expense-management-abc123.fastmcp.com
```

### Add Test Data
```bash
# Add multiple expenses
fastmcp call expense-management add_expense \
  --user_id "demo_user" \
  --date "2025-01-10" \
  --amount 45.50 \
  --category "Food" \
  --merchant "Starbucks"

fastmcp call expense-management add_expense \
  --user_id "demo_user" \
  --date "2025-01-12" \
  --amount 100.00 \
  --category "Transport" \
  --merchant "Uber"

# Get monthly report
fastmcp call expense-management monthly_report \
  --user_id "demo_user" \
  --month "2025-01"
```

### Monitor Server
```bash
# View logs
fastmcp logs expense-management --tail 50

# Check status
fastmcp status expense-management
```

---

## 🆘 Troubleshooting

### "Database connection failed"
- Verify DATABASE_URL is correct
- Check password has no special characters that need escaping
- Ensure Supabase project is not paused

### "Tool not found"
- Redeploy: `fastmcp deploy --force`
- Check logs: `fastmcp logs expense-management`

### "Invalid date format"
- Use YYYY-MM-DD format
- Example: `2025-01-15` not `01/15/2025`

---

## 📱 Quick Reference

### Tools Available

1. **add_expense** - Add new expense
   - Required: user_id, date, amount, category
   - Optional: merchant, note

2. **list_expenses** - List expenses
   - Required: user_id, start_date, end_date

3. **summarize_expenses** - Category summary
   - Required: user_id, start_date, end_date

4. **monthly_report** - Monthly analysis
   - Required: user_id, month (YYYY-MM)

### Date Formats
- Date: `YYYY-MM-DD` (e.g., `2025-01-15`)
- Month: `YYYY-MM` (e.g., `2025-01`)

---

## 🎓 Learn More

- Full docs: See `README.md`
- Deployment details: See `DEPLOYMENT.md`
- Project overview: See `PROJECT_SUMMARY.md`

---

**Time to deployment: ~5 minutes** ⚡

**You're ready to build!** 🚀
