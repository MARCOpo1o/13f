# Development Mode - Auth Bypass

## Quick Toggle for Local Development

You can now **bypass password protection** during local development for faster testing.

---

## How to Use

### **Enable Auth Bypass (Default)**

**In `config.py`:**
```python
DEBUG = True
DISABLE_AUTH_IN_DEV = True  # ✅ No password needed locally
```

**Result**: Go directly to `http://localhost:5000` - no login required!

**Visual indicator**: Yellow banner shows "⚠️ DEV MODE: Authentication disabled"

---

### **Test With Auth Enabled**

**In `config.py`:**
```python
DEBUG = True
DISABLE_AUTH_IN_DEV = False  # 🔒 Password required (testing auth flow)
```

**Result**: Must login to access app

---

### **Production (Vercel)**

**In `config.py`:**
```python
DEBUG = False  # 🔒 Auth ALWAYS required in production
DISABLE_AUTH_IN_DEV = True  # ← This is IGNORED when DEBUG=False
```

**Result**: Password protection always active (even if DISABLE_AUTH_IN_DEV = True)

---

## Safety Features

### **Double Check Protection**
Auth bypass only works when **BOTH** are true:
- ✅ `DEBUG = True` (development mode)
- ✅ `DISABLE_AUTH_IN_DEV = True` (bypass enabled)

### **Production Safety**
```python
if DEBUG=False:  # Production
    # Auth bypass is COMPLETELY IGNORED
    # Password is ALWAYS required
```

**You cannot accidentally disable auth in production!**

---

## Use Cases

| Scenario | DEBUG | DISABLE_AUTH | Result |
|----------|-------|--------------|--------|
| **Local dev (fast)** | `True` | `True` | ✅ No password |
| **Testing auth flow** | `True` | `False` | 🔒 Password required |
| **Production** | `False` | `True` | 🔒 Password required |
| **Production** | `False` | `False` | 🔒 Password required |

---

## Visual Indicators

### **Dev Mode Active**
```
⚠️ DEV MODE: Authentication disabled for local development
```
Yellow banner appears at top of page

### **Normal Mode**
No banner - password protection active

---

## Best Practices

### **During Development**
```python
DISABLE_AUTH_IN_DEV = True  # ✅ Fast iteration
```

### **Before Deploying**
1. Test with auth enabled:
   ```python
   DISABLE_AUTH_IN_DEV = False
   ```
2. Verify login works
3. Deploy with `DEBUG = False`

### **On Vercel**
Vercel automatically sets production environment, so:
- Auth is always enabled ✓
- No risk of exposing app ✓

---

## Why This Exists

**Problem**: During development, logging in every time you test gets annoying.

**Solution**: Temporarily bypass auth in dev mode only.

**Industry standard**: Django, Rails, Laravel all have similar features.

**Examples**:
- Django: `DEBUG = True` disables CSRF in shell
- Rails: `config.force_ssl = false` in dev
- Laravel: `APP_ENV=local` changes security behavior

---

## How It Works (Technical)

### **The Decorator**
```python
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if we're in dev mode with bypass enabled
        if config.DEBUG and config.DISABLE_AUTH_IN_DEV:
            return f(*args, **kwargs)  # Skip auth check
        
        # Otherwise, require authentication
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
```

### **The Safety Check**
```python
# Both must be True to bypass
config.DEBUG and config.DISABLE_AUTH_IN_DEV
```

If either is False → auth is required.

---

## Testing Commands

### **Start with auth disabled**
```bash
python app.py
# Visit http://localhost:5000 (direct access)
```

### **Start with auth enabled**
```bash
# Edit config.py: DISABLE_AUTH_IN_DEV = False
python app.py
# Visit http://localhost:5000 (redirects to /login)
```

---

Built by Marco Qin with industry guidance from Stephen

