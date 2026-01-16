# Quick Verification Checklist - Phase 1 & 2

**Purpose:** Quick checklist to verify Phase 1 & 2 are working before Phase 3.

---

## ✅ Step 1: Code Verification (COMPLETE)

**Status:** ✅ PASSED

Run verification script:
```bash
cd /home/founders/demoversion/symphainy_source_code
python3 scripts/verify_phase1_2.py
```

**Results:**
- ✅ All imports work
- ✅ Orchestrator has Phase 2 handlers
- ✅ Realm declares all intents
- ✅ Services initialized correctly

---

## ⏳ Step 2: Database Setup (YOUR TASK)

### 2.1 Run Migration

**File:** `migrations/001_create_insights_lineage_tables.sql`

**In Supabase SQL Editor:**
1. Copy contents of migration file
2. Paste into SQL Editor
3. Execute
4. Verify tables created:
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name IN ('parsed_results', 'embeddings', 'guides');
   ```
   Should return 3 rows.

### 2.2 Seed Default Guides

**Run seeding script:**
```bash
cd /home/founders/demoversion/symphainy_source_code
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-key"
python3 scripts/seed_default_guides.py
```

**Verify in Supabase:**
```sql
SELECT guide_id, name, type 
FROM guides 
WHERE type = 'default';
```
Should return 3 guides.

**See:** `docs/execution/run_seeding_script.md` for detailed instructions.

---

## ⏳ Step 3: Functional Verification (OPTIONAL)

### 3.1 Test Phase 1: Data Quality

**Intent:** `assess_data_quality`

**Test:**
- Upload a file
- Parse the file
- Call `assess_data_quality` intent
- Verify quality assessment returned

### 3.2 Test Phase 2: Self Discovery

**Intent:** `interpret_data_self_discovery`

**Test:**
- Use parsed file from above
- Call `interpret_data_self_discovery` intent
- Verify entities and relationships discovered

### 3.3 Test Phase 2: Guided Discovery

**Intent:** `interpret_data_guided`

**Test:**
- Use parsed file from above
- Call `interpret_data_guided` intent with `guide_id = "pso_permit_guide"`
- Verify matched entities, unmatched data, suggestions returned

---

## ✅ Ready for Phase 3?

**Checklist:**
- [x] Code verification passed
- [ ] Migration run (your task)
- [ ] Default guides seeded (your task)
- [ ] Guides verified in Supabase (your task)
- [ ] (Optional) Functional tests passed

**Once checklist complete:** ✅ Ready to proceed with Phase 3!

---

## Quick Commands Reference

```bash
# Verify code
python3 scripts/verify_phase1_2.py

# Seed guides (after setting env vars)
python3 scripts/seed_default_guides.py

# Verify guides in Supabase (SQL)
SELECT guide_id, name FROM guides WHERE type = 'default';
```
