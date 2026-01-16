# How to Verify Default Guides in Supabase

**Purpose:** Verify that default guides were successfully seeded in Supabase.

---

## Verification Steps

### 1. Via Supabase Dashboard (Easiest)

1. **Navigate to Table Editor:**
   - Go to your Supabase project dashboard
   - Click "Table Editor" in the left sidebar
   - Find and click on the `guides` table

2. **Check for Default Guides:**
   - You should see 3 rows with `type = "default"`
   - Verify the following guide_ids exist:
     - `pso_permit_guide`
     - `aar_report_guide`
     - `variable_whole_life_policy_guide`

3. **Verify Guide Structure:**
   - Click on each guide row to view details
   - Check that `fact_pattern` (JSONB) contains entities and relationships
   - Check that `output_template` (JSONB) contains template structure
   - Verify `tenant_id` is `00000000-0000-0000-0000-000000000000` (system tenant)

---

### 2. Via SQL Query (Most Reliable)

**Run this query in Supabase SQL Editor:**

```sql
-- Count default guides
SELECT COUNT(*) as default_guide_count 
FROM guides 
WHERE type = 'default';

-- Should return: 3

-- List all default guides with details
SELECT 
    guide_id,
    name,
    type,
    version,
    created_at,
    fact_pattern->'entities' as entities,
    fact_pattern->'relationships' as relationships
FROM guides 
WHERE type = 'default'
ORDER BY guide_id;

-- Should return 3 rows:
-- 1. aar_report_guide - AAR (After Action Report) Guide
-- 2. pso_permit_guide - PSO Permit Guide
-- 3. variable_whole_life_policy_guide - Variable Whole Life Insurance Policy Record for Migration
```

**Expected Results:**

| guide_id | name | type | version |
|----------|------|------|---------|
| `aar_report_guide` | AAR (After Action Report) Guide | default | 1.0 |
| `pso_permit_guide` | PSO Permit Guide | default | 1.0 |
| `variable_whole_life_policy_guide` | Variable Whole Life Insurance Policy Record for Migration | default | 1.0 |

---

### 3. Verify Fact Pattern Structure

**Check PSO Permit Guide fact pattern:**

```sql
SELECT 
    guide_id,
    jsonb_pretty(fact_pattern) as fact_pattern_formatted
FROM guides 
WHERE guide_id = 'pso_permit_guide';
```

**Expected entities:**
- `permit` (with attributes: permit_id, permit_type, status, issue_date, expiry_date)
- `applicant` (with attributes: applicant_name, applicant_id, contact_info)
- `property` (with attributes: property_address, property_id, property_type)
- `regulation` (with attributes: regulation_code, regulation_name, compliance_status)

**Expected relationships:**
- `permit` → `applicant` (owned_by)
- `permit` → `property` (applies_to)
- `permit` → `regulation` (governed_by)

---

### 4. Verify Output Template Structure

**Check output template:**

```sql
SELECT 
    guide_id,
    jsonb_pretty(output_template) as output_template_formatted
FROM guides 
WHERE guide_id = 'pso_permit_guide';
```

**Expected structure:**
- `version`: "1.0"
- `structure`: Contains permit_summary and compliance sections

---

## Troubleshooting

### If guides don't exist:

1. **Check if migration ran:**
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name = 'guides';
   ```
   - If no results, run migration first: `migrations/001_create_insights_lineage_tables.sql`

2. **Check for errors in seeding:**
   - Review script output for error messages
   - Check Supabase logs for insert errors

3. **Re-run seeding script:**
   ```bash
   python3 scripts/seed_default_guides.py
   ```

### If guides exist but are incomplete:

1. **Check fact_pattern structure:**
   ```sql
   SELECT guide_id, fact_pattern 
   FROM guides 
   WHERE type = 'default';
   ```
   - Verify JSONB structure is valid

2. **Delete and re-seed:**
   ```sql
   DELETE FROM guides WHERE type = 'default';
   ```
   Then re-run seeding script.

---

## Quick Verification Query

**Run this to verify everything at once:**

```sql
SELECT 
    guide_id,
    name,
    type,
    CASE 
        WHEN fact_pattern IS NULL THEN '❌ Missing fact_pattern'
        WHEN fact_pattern->'entities' IS NULL THEN '❌ Missing entities'
        WHEN fact_pattern->'relationships' IS NULL THEN '❌ Missing relationships'
        ELSE '✅ Valid'
    END as fact_pattern_status,
    CASE 
        WHEN output_template IS NULL THEN '❌ Missing output_template'
        WHEN output_template->'version' IS NULL THEN '❌ Missing version'
        ELSE '✅ Valid'
    END as output_template_status
FROM guides 
WHERE type = 'default'
ORDER BY guide_id;
```

**All rows should show:**
- `fact_pattern_status`: ✅ Valid
- `output_template_status`: ✅ Valid

---

## Next Steps

Once verified:
1. ✅ Default guides are ready for use
2. ✅ Can test `interpret_data_guided` intent with `guide_id = "pso_permit_guide"`
3. ✅ Ready to proceed with Phase 3
