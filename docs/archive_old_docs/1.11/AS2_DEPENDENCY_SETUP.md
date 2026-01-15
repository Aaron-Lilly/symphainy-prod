# AS2 Dependency Setup Guide

**Date:** January 2026  
**Status:** ✅ **DOCUMENTED**

---

## 🎯 Overview

`pyas2lib` is an **optional dependency** for full AS2 decryption support. The EDI adapter will work without it (using fallback method), but for production AS2 support, `pyas2lib` is recommended.

---

## 📋 Installation Options

### Option 1: Poetry (Recommended)

```bash
# Install with AS2 extra
poetry install --extras as2

# Or add to existing installation
poetry add pyas2lib --extras as2
```

### Option 2: pip

```bash
# Install from requirements file
pip install -r requirements-as2.txt

# Or install directly
pip install pyas2lib>=1.4.4
```

### Option 3: Add to requirements.txt

If you want AS2 support always available, add to `requirements.txt`:

```txt
pyas2lib>=1.4.4
```

---

## 🐳 Docker Container Setup

### For Dockerfiles using requirements.txt

**Option A: Include in main requirements.txt**
```dockerfile
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
```

**Option B: Install separately**
```dockerfile
COPY requirements.txt requirements-as2.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-as2.txt
```

**Option C: Install directly**
```dockerfile
RUN pip install --no-cache-dir pyas2lib>=1.4.4
```

### Recommended Dockerfile Pattern

```dockerfile
# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Install base dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install optional AS2 support (if needed)
# Uncomment if AS2 support is required:
# COPY requirements-as2.txt ./
# RUN pip install --no-cache-dir -r requirements-as2.txt
```

---

## ✅ Verification

After installation, verify AS2 support:

```python
# Test import
from symphainy_platform.foundations.public_works.adapters.as2_decryption import AS2Decryptor

# Check if pyas2lib is available
try:
    import pyas2lib
    print("✅ pyas2lib available - full AS2 support enabled")
except ImportError:
    print("⚠️  pyas2lib not available - using fallback method")
```

---

## 🔄 Fallback Behavior

**Without `pyas2lib`:**
- EDI adapter will use `cryptography` library for basic S/MIME decryption
- Limited AS2 features (simplified parsing)
- Warning logged: "pyas2lib not available - will use manual S/MIME decryption"

**With `pyas2lib`:**
- Full AS2 support
- Message parsing
- Decryption
- Signature verification
- MDN handling

---

## 📝 Files Updated

1. **pyproject.toml** - Added `pyas2lib` as optional extra
2. **requirements.txt** - Added note about optional dependencies
3. **requirements-as2.txt** - Created for AS2 support
4. **Dockerfiles** - No changes needed (use requirements-as2.txt if needed)

---

## 🚀 Production Recommendation

**For production AS2 support:**
1. Install `pyas2lib` in your Docker container
2. Add `requirements-as2.txt` to your build process
3. Or include `pyas2lib>=1.4.4` directly in `requirements.txt`

**For development/testing:**
- Optional - fallback method works for basic testing
- Install when you need full AS2 features

---

## ✅ Summary

**Status:** ✅ **DEPENDENCY MANAGEMENT COMPLETE**

**Files:**
- ✅ `pyproject.toml` - Added as optional extra
- ✅ `requirements-as2.txt` - Created for AS2 support
- ✅ `requirements.txt` - Added documentation note

**Installation:**
- Poetry: `poetry install --extras as2`
- pip: `pip install -r requirements-as2.txt`
- Docker: Include `requirements-as2.txt` in build

**Ready for:** Production deployment with optional AS2 support
