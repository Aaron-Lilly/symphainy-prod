# Running the Default Guides Seeding Script

**Purpose:** Seed default guides (PSO, AAR, Variable Whole Life Insurance Policy) into Supabase.

---

## Prerequisites

1. **Supabase Migration Run:**
   - The `guides` table must exist (from `migrations/001_create_insights_lineage_tables.sql`)
   - If you haven't run the migration yet, do that first

2. **Supabase Credentials:**
   - Supabase project URL
   - Supabase service role key (not anon key)

---

## Step 1: Set Environment Variables

**Option A: Export in current shell (temporary):**
```bash
export SUPABASE_URL="https://your-project-id.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key-here"
```

**Option B: Inline with command (one-time):**
```bash
SUPABASE_URL="https://your-project-id.supabase.co" \
SUPABASE_SERVICE_KEY="your-service-role-key-here" \
python3 scripts/seed_default_guides.py
```

**Where to find these:**
- **SUPABASE_URL:** Supabase Dashboard → Settings → API → Project URL
- **SUPABASE_SERVICE_KEY:** Supabase Dashboard → Settings → API → `service_role` key (⚠️ Keep secret!)

---

## Step 2: Run the Seeding Script

```bash
cd /home/founders/demoversion/symphainy_source_code
python3 scripts/seed_default_guides.py
```

**Expected Output:**
```
Seeding default guides...
✅ Seeded guide: PSO Permit Guide
✅ Seeded guide: AAR (After Action Report) Guide
✅ Seeded guide: Variable Whole Life Insurance Policy Record for Migration
Seeded 3/3 default guides
```

---

## Step 3: Verify in Supabase

### Quick Verification (SQL Editor)

Run this query in Supabase SQL Editor:

```sql
-- Count default guides
SELECT COUNT(*) as count FROM guides WHERE type = 'default';
-- Should return: 3

-- List all default guides
SELECT guide_id, name, type, version 
FROM guides 
WHERE type = 'default'
ORDER BY guide_id;
```

**Expected Results:**
- `aar_report_guide` - AAR (After Action Report) Guide
- `pso_permit_guide` - PSO Permit Guide  
- `variable_whole_life_policy_guide` - Variable Whole Life Insurance Policy Record for Migration

### Detailed Verification

See: `docs/execution/verify_guides_in_supabase.md` for complete verification steps.

---

## Troubleshooting

### Error: "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set"
- **Solution:** Export environment variables before running script

### Error: "Table 'guides' does not exist"
- **Solution:** Run migration first: `migrations/001_create_insights_lineage_tables.sql`

### Error: "Failed to seed guide"
- **Solution:** Check Supabase logs for detailed error
- Verify service key has proper permissions
- Check if guide already exists (duplicate key error)

### Script runs but no guides appear
- **Solution:** 
  1. Check Supabase logs
  2. Verify RLS policies allow inserts
  3. Check tenant_id in query: `SELECT * FROM guides WHERE tenant_id = '00000000-0000-0000-0000-000000000000'`

---

## What Gets Created

The script creates 3 default guides:

1. **PSO Permit Guide** (`pso_permit_guide`)
   - Entities: permit, applicant, property, regulation
   - For analyzing permit documents

2. **AAR Report Guide** (`aar_report_guide`)
   - Entities: event, action, outcome, lesson_learned
   - For analyzing after-action reports

3. **Variable Whole Life Insurance Policy Record for Migration** (`variable_whole_life_policy_guide`)
   - Entities: policy, policyholder, beneficiary, coverage, premium, migration_info
   - For analyzing and migrating Variable Whole Life Insurance Policy records

All guides are stored with:
- `type = "default"`
- `tenant_id = "00000000-0000-0000-0000-000000000000"` (system tenant)
- Full `fact_pattern` (entities + relationships)
- Full `output_template` (result formatting)

---

## Next Steps After Seeding

Once verified:
1. ✅ Default guides are available for `interpret_data_guided` intent
2. ✅ Can test guided discovery with: `guide_id = "pso_permit_guide"`
3. ✅ Ready to proceed with Phase 3
