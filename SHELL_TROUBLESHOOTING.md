# Shell Troubleshooting Guide

## Issue
Cursor's integrated shell is failing with:
```
--: eval: line 17: unexpected EOF while looking for matching `)'
--: eval: line 18: syntax error: unexpected end of file
--: line 1: dump_bash_state: command not found
```

This suggests a syntax error in shell initialization, preventing ANY commands from running.

## Solutions to Try

### Option 1: Use External Terminal/SSH
**Recommended:** Use a direct SSH session or external terminal (not Cursor's integrated terminal)

```bash
# SSH into the VM
ssh user@your-vm-ip

# Navigate to project
cd /home/founders/demoversion/symphainy_source_code

# Run the Python script
python3 scripts/fix_experience_service.py

# Or run commands directly
docker-compose build experience
docker-compose stop experience
docker-compose up -d experience
```

### Option 2: Check Cursor Settings
1. Open Cursor Settings (Ctrl+, or Cmd+,)
2. Search for "terminal" or "shell"
3. Check:
   - `terminal.integrated.shell.linux` - Should be `/bin/bash` or `/usr/bin/bash`
   - `terminal.integrated.shellArgs.linux` - Should be empty or `["-l"]`
4. Try changing shell to `/bin/sh` temporarily

### Option 3: Reset Cursor Terminal
1. Close all terminal tabs in Cursor
2. Restart Cursor completely
3. Open a new terminal (Ctrl+` or Terminal > New Terminal)
4. Try a simple command: `echo "test"`

### Option 4: Check Shell Config Files
The error suggests a syntax error in `.bashrc`, `.bash_profile`, or `.profile`:

```bash
# In an external terminal, check for syntax errors:
bash -n ~/.bashrc
bash -n ~/.bash_profile
bash -n ~/.profile

# If errors found, backup and fix:
cp ~/.bashrc ~/.bashrc.backup
# Then edit to fix syntax errors
```

### Option 5: Use Python Scripts Directly
I've created Python scripts that bypass the shell:

1. **Rebuild/Restart Experience:**
   ```bash
   # In external terminal:
   python3 /home/founders/demoversion/symphainy_source_code/scripts/fix_experience_service.py
   ```

2. **Run Test:**
   ```bash
   # In external terminal:
   python3 /home/founders/demoversion/symphainy_source_code/scripts/run_test.py
   ```

### Option 6: Check Cursor's Shell Integration
The error `dump_bash_state: command not found` suggests Cursor is trying to run a custom function that doesn't exist. This might be:
- A Cursor extension issue
- A corrupted Cursor configuration
- A workspace-specific setting

**Try:**
1. Close Cursor
2. Check `.cursor/` directory for config files
3. Temporarily rename `.cursor/` to `.cursor.backup/`
4. Restart Cursor (it will recreate config)
5. If that works, restore config files one by one

### Option 7: Use Docker Exec Directly
If you can access Docker, you might be able to execute commands in containers:

```bash
# In external terminal:
docker exec -it symphainy-experience python3 -c "print('test')"
```

## Verification Steps

Once you get a working terminal, verify the fixes:

1. **Check Model File:**
   ```bash
   grep -A 5 "class IntentSubmitRequest" \
     symphainy_platform/civic_systems/experience/models/intent_request_model.py
   ```
   Should show `tenant_id: str` and `solution_id: str = "default"`

2. **Check Docker Compose:**
   ```bash
   grep -A 3 "healthcheck:" docker-compose.yml | grep -A 1 "experience" -A 3
   ```
   Should show port `8001` not `8529`

3. **Check Service Status:**
   ```bash
   docker-compose ps experience
   docker-compose logs experience --tail 20
   ```

## Next Steps After Shell Works

1. Rebuild Experience: `docker-compose build experience`
2. Restart Experience: `docker-compose stop experience && docker-compose up -d experience`
3. Wait 10 seconds: `sleep 10`
4. Check logs: `docker-compose logs experience --tail 50 | grep tenant_id`
5. Run test: `timeout 90 python3 tests/integration/capabilities/phase2/file_management/test_register_file.py`

## If Nothing Works

The code fixes are already in place:
- ✅ Model file fixed (`intent_request_model.py`)
- ✅ Docker Compose health check fixed

You just need to rebuild/restart the service. If Cursor's shell won't work, use:
- External SSH terminal
- VS Code with remote SSH
- Direct VM console access
- Any terminal that can access the VM
