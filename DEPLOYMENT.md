# Deployment Guide - Expense MCP Server

## 🚀 Quick Start Deployment

### Step 1: Set Up PostgreSQL Database

Choose one of these cloud PostgreSQL providers:

#### Option A: Supabase (Recommended for Beginners)
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Create new project
4. Wait for database to be provisioned
5. Go to Settings → Database
6. Copy the "Connection string" (URI mode)
7. Run schema:
   - Go to SQL Editor in Supabase dashboard
   - Copy contents of `schema.sql`
   - Click "Run"

#### Option B: Neon (Serverless Postgres)
1. Go to [neon.tech](https://neon.tech)
2. Sign up and create project
3. Copy connection string
4. Connect via `psql` or GUI client
5. Run: `psql $DATABASE_URL < schema.sql`

#### Option C: Railway
1. Go to [railway.app](https://railway.app)
2. Create new project
3. Add PostgreSQL service
4. Copy connection string from Variables tab
5. Connect and run `schema.sql`

---

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your DATABASE_URL
nano .env  # or use your preferred editor
```

Your `.env` should look like:
```
DATABASE_URL=postgresql://user:password@host:port/database
```

---

### Step 3: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 4: Test Locally (Optional)

```bash
# Load environment variables
export $(cat .env | xargs)  # On Windows: use .env file directly

# Run the server
python main.py
```

You should see:
```
FastMCP server running on http://localhost:8000
```

---

### Step 5: Deploy to FastMCP Cloud

```bash
# Login to FastMCP Cloud
fastmcp login

# Deploy the server
fastmcp deploy

# Follow the prompts:
# - Name: expense-management
# - Environment: Copy your DATABASE_URL when prompted
```

After deployment, you'll receive:
- Server URL (e.g., `https://expense-management.fastmcp.com`)
- API endpoint for your backend to call

---

## 🧪 Testing Your Deployment

### Test with FastMCP CLI

```bash
# List available tools
fastmcp tools expense-management

# Test add_expense
fastmcp call expense-management add_expense \
  --user_id "test_user_1" \
  --date "2025-01-15" \
  --amount 45.50 \
  --category "Food" \
  --merchant "Starbucks"

# Test list_expenses
fastmcp call expense-management list_expenses \
  --user_id "test_user_1" \
  --start_date "2025-01-01" \
  --end_date "2025-01-31"
```

### Test with cURL (HTTP endpoint)

```bash
# Replace YOUR_SERVER_URL with your deployment URL
export SERVER_URL="https://expense-management.fastmcp.com"

# Add expense
curl -X POST $SERVER_URL/tools/add_expense \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "date": "2025-01-15",
    "amount": 45.50,
    "category": "Food",
    "merchant": "Starbucks",
    "note": "Coffee meeting"
  }'

# List expenses
curl -X POST $SERVER_URL/tools/list_expenses \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  }'
```

---

## 🔍 Verify Deployment

### Check Server Health

```bash
# Get server info
fastmcp info expense-management

# View logs
fastmcp logs expense-management --tail 50
```

### Check Database

```bash
# Connect to your database
psql $DATABASE_URL

# Verify table exists
\dt

# Check data
SELECT * FROM expenses LIMIT 5;
```

---

## 🔐 Security Checklist

Before going to production:

- [ ] Database connection uses SSL (`?sslmode=require`)
- [ ] DATABASE_URL is stored as environment variable (not in code)
- [ ] Database user has minimal permissions (no DROP/CREATE on production)
- [ ] Backend orchestrator validates user_id before calling MCP
- [ ] FastMCP Cloud endpoint is only accessible by your backend
- [ ] Logs don't contain sensitive data

---

## 📊 Monitoring

### FastMCP Cloud Dashboard

Monitor:
- Request count
- Error rates
- Response times
- Tool usage statistics

### Database Monitoring

Monitor:
- Connection pool usage
- Query performance
- Disk usage
- Index efficiency

**Recommended:** Set up alerts for:
- High error rates (> 5%)
- Slow queries (> 1000ms)
- Connection pool exhaustion

---

## 🚨 Troubleshooting

### "Connection refused" Error

**Cause:** Database not accessible  
**Fix:**
1. Check DATABASE_URL is correct
2. Verify database is running
3. Check firewall rules (allow connections from FastMCP Cloud)
4. Ensure SSL mode is correct

### "Column 'user_id' does not exist"

**Cause:** Schema not created  
**Fix:**
```bash
psql $DATABASE_URL < schema.sql
```

### "Tool not found" Error

**Cause:** Deployment failed  
**Fix:**
```bash
# Check deployment status
fastmcp status expense-management

# Redeploy
fastmcp deploy --force
```

### High Latency

**Possible causes:**
1. Database connection pool exhausted → Increase pool size in `db.py`
2. Missing indexes → Check `schema.sql` indexes are created
3. Database in different region → Move database closer to FastMCP Cloud region

---

## 🔄 Updates and Maintenance

### Deploying Updates

```bash
# Make code changes
git commit -am "Update expense logic"

# Deploy new version
fastmcp deploy

# Rollback if needed
fastmcp rollback expense-management
```

### Database Migrations

**Adding new columns:**
```sql
-- Example: Add payment_method column
ALTER TABLE expenses 
ADD COLUMN payment_method TEXT;
```

**Best practice:**
1. Test migration on staging database first
2. Back up production database
3. Run migration during low-traffic period
4. Deploy code changes after migration

---

## 🎓 Next Steps

After successful deployment:

1. **Integrate with Backend Orchestrator**
   - Point orchestrator to MCP server URL
   - Implement user_id injection logic
   - Add error handling for MCP tool calls

2. **Create Additional MCP Servers**
   - Email MCP server
   - Task MCP server
   - PKOS MCP server
   - Follow same deployment process

3. **Build User Interface**
   - Connect UI to backend orchestrator
   - Implement authentication
   - Display expense data from MCP tools

4. **Set Up Monitoring**
   - Configure alerts
   - Set up log aggregation
   - Monitor user adoption

---

## 📚 Resources

- [FastMCP Cloud Documentation](https://fastmcp.com/docs/cloud)
- [PostgreSQL Best Practices](https://www.postgresql.org/docs/current/index.html)
- [Supabase Guides](https://supabase.com/docs)
- [MCP Specification](https://modelcontextprotocol.io)

---

## 💡 Tips

- **Use staging environment:** Deploy to staging first, test thoroughly
- **Database backups:** Enable automatic backups on your database provider
- **Environment isolation:** Never use production DATABASE_URL for testing
- **Version control:** Commit all changes before deploying
- **Documentation:** Update README.md when adding new tools

---

## ✅ Deployment Checklist

- [ ] PostgreSQL database created
- [ ] Schema applied (`schema.sql`)
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Local testing passed (optional)
- [ ] FastMCP Cloud deployment successful
- [ ] Health check passed
- [ ] Test data inserted and retrieved
- [ ] Logs reviewed (no errors)
- [ ] Backend integration tested
- [ ] Documentation updated

---

**Ready for production!** 🎉
