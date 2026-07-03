# 🔧 Installation Fix - "Externally Managed Environment" Error

## Problem

When running `pip install -r requirements.txt`, you get this error:

```
error: externally-managed-environment
```

This happens on modern Linux distributions (Ubuntu 23.04+, Fedora 38+, Debian 12+) that restrict direct pip installations to protect system Python.

## Solution: Use Python Virtual Environment

The fix is simple - use a Python virtual environment. This isolates the project from your system Python.

### Quick Fix (One Command)

Run this from the project directory:

```bash
cd /home/ubuntu/Desktop/Project1
bash setup.sh
```

This automatically:
- ✅ Creates a virtual environment
- ✅ Activates it
- ✅ Installs all dependencies
- ✅ Shows you next steps

### Manual Setup (If setup.sh doesn't work)

```bash
cd /home/ubuntu/Desktop/Project1

# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# You should see (venv) before your prompt

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "import fastapi, streamlit, anthropic; print('✅ Success!')"
```

## Key Points

### What is a Virtual Environment?

A virtual environment is an isolated Python environment for your project. It:
- ✅ Doesn't affect system Python
- ✅ Avoids permission errors
- ✅ Keeps dependencies organized
- ✅ Works on all platforms

### Every Time You Use the Project

Always activate the virtual environment first:

```bash
cd /home/ubuntu/Desktop/Project1
source venv/bin/activate
```

You'll see `(venv)` appear in your terminal prompt.

### To Deactivate (Optional)

When done working on the project:

```bash
deactivate
```

The `(venv)` will disappear from your prompt.

## What We Fixed

The original setup had these issues:

**Before:**
```bash
pip install -r requirements.txt  # ❌ Error: externally managed
```

**After:**
```bash
python3 -m venv venv             # Create isolated environment
source venv/bin/activate         # Activate it
pip install -r requirements.txt  # ✅ Works!
```

## Updated Installation Steps

### Step 1: Setup (First Time Only)

```bash
cd /home/ubuntu/Desktop/Project1

# Option A: Automated (recommended)
bash setup.sh

# Option B: Manual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Start Services

```bash
# Make sure venv is activated (you should see (venv) in prompt)
source venv/bin/activate

# Start all services
chmod +x run_all_services.sh
./run_all_services.sh
```

### Step 3: Access the UI

Open in browser:
```
http://localhost:8501
```

## Files Updated

- ✅ `requirements.txt` - Simplified, compatible versions
- ✅ `setup.sh` - New automated setup script
- ✅ `START_HERE.md` - Updated with venv instructions
- ✅ `QUICKSTART.md` - Updated with venv instructions

## Common Errors After Installation

### "ModuleNotFoundError: No module named 'distutils'"

Python 3.12+ removed `distutils`. Fix:

```bash
source venv/bin/activate
pip install setuptools>=68.0
```

See [DISTUTILS_FIX.md](DISTUTILS_FIX.md) for details.

## Troubleshooting

### "venv: command not found"

Python 3 venv module not installed. Install it:

```bash
# Ubuntu/Debian
sudo apt-get install python3.12-venv

# Then try again:
python3 -m venv venv
```

### "source: command not found"

You're using a non-bash shell. Try:

```bash
# For zsh
source venv/bin/activate

# For fish
source venv/bin/activate.fish

# For Windows PowerShell
venv\Scripts\Activate.ps1
```

### "pip: permission denied"

You didn't activate the virtual environment. Make sure to run:

```bash
source venv/bin/activate
```

### Pip still complains about externally managed

Make sure you're in the virtual environment:

```bash
# Check if (venv) appears in your prompt
# If not, activate it:
source venv/bin/activate

# Then try pip again
pip install -r requirements.txt
```

## Complete Fresh Start

If something goes wrong, you can start over:

```bash
cd /home/ubuntu/Desktop/Project1

# Remove old virtual environment
rm -rf venv

# Start fresh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## What's Different from Original

The new setup:
1. Uses virtual environment (best practice)
2. Simplified dependencies (removed conflicting packages)
3. Easier setup script (setup.sh)
4. Updated documentation (this guide)
5. Same functionality (all features work!)

## After Installation

Once installed, you're ready to:

1. **Run the system**:
   ```bash
   source venv/bin/activate
   ./run_all_services.sh
   ```

2. **Test the API**:
   ```bash
   source venv/bin/activate
   python test_api.py
   ```

3. **Verify setup**:
   ```bash
   source venv/bin/activate
   python verify_setup.py
   ```

## More Information

- [Python Virtual Environments (Official Docs)](https://docs.python.org/3/tutorial/venv.html)
- [Virtual Environments Best Practices](https://docs.python.org/3/library/venv.html)

---

**Having issues?** Make sure to:
1. Use `setup.sh` or follow the manual steps exactly
2. Activate the virtual environment every time
3. Check that `(venv)` appears in your prompt
4. Never use `sudo` with pip in a virtual environment

✅ **You're all set! Now follow the next steps in START_HERE.md** 🚀
