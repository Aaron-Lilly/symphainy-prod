# Instructions for Seeding Default Guides

**Purpose:** Populate Supabase with default guides (PSO, AAR, Variable Whole Life Insurance Policy) for guided discovery.

---

## Prerequisites

1. **Supabase Project:** You need a Supabase project with:
   - `guides` table created (via migration `001_create_insights_lineage_tables.sql`)
   - Service key available

2. **Environment Variables:**
   ```bash
   export SUPABASE_URL="https://your-project.supabase.co"
   export SUPABASE_SERVICE_KEY="your-service-role-key"
   ```

---

## Running the Script

### Option 1: Direct Execution

```bash
cd /home/founders/demoversion/symphainy_source_code
python3 scripts/seed_default_guides.py
```

### Option 2: With Environment Variables Inline

```bash
cd /home/founders/demoversion/symphainy_source_code
SUPABASE_URL="https://your-project.supabase.co" \
SUPABASE_SERVICE_KEY="your-service-role-key" \
python3 scripts/seed_default_guides.py
```

### Option 3: Using .env File

Create a `.env` file in the project root:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

Then run:
```bash
cd /home/founders/demoversion/symphainy_source_code
python3 scripts/seed_default_guides.py
```

(Note: You may need to load the .env file manually or use a tool like `python-dotenv`)

---

## Expected Output

```
Seeding default guides...
✅ Seeded guide: PSO Permit Guide
✅ Seeded guide: AAR (After Action Report) Guide
✅ Seeded guide: Variable Whole Life Insurance Policy Record for Migration
Seeded 3/3 default guides
```

---

## Verification

After running the script, verify guides were created:

1. **Via Supabase Dashboard:**
   - Go to Table Editor
   - Select `guides` table
   - Verify 3 records exist with `type = "default"`

2. **Via SQL Query:**
   ```sql
   SELECT guide_id, name, type FROM guides WHERE type = 'default';
   ```

   Should return:
   - `pso_permit_guide` - PSO Permit Guide
   - `aar_report_guide` - AAR (After Action Report) Guide
   - `variable_whole_life_policy_guide` - Variable Whole Life Insurance Policy Record for Migration

---

## Troubleshooting

### Error: "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set"
- **Solution:** Ensure environment variables are set correctly

### Error: "Table 'guides' does not exist"
- **Solution:** Run the migration first:
  ```sql
  -- Execute migrations/001_create_insights_lineage_tables.sql
  ```

### Error: "Failed to seed guide"
- **Solution:** Check Supabase logs for detailed error messages
- Verify service key has proper permissions
- Check if guide already exists (script will fail on duplicate)

---

## Notes

- The script uses a system tenant ID (`00000000-0000-0000-0000-000000000000`) for default guides
- Default guides are available to all tenants (via RLS policies)
- Guides can be updated/deleted later via Guide Registry API
