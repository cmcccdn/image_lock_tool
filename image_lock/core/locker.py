"""
Default-application locking primitives — copied/adapted from
the parent defaultapp_locker project.

Applies four layers in concert so a default association actually sticks:
  1. assoc / ftype   (legacy cmd.exe mechanism)
  2. HKCR direct write
  3. HKCU \\...\\FileExts\\<ext>\\UserChoice  (ProgId + Hash marker)
  4. (re-applied periodically by the Windows service)
"""
import subprocess
import os
import hashlib
import time

try:
    import winreg
except ImportError:  # non-Windows dev machines — keep importable
    winreg = None


def run_cmd(cmd):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            encoding="gbk", errors="ignore",
        )
        return {"success": result.returncode == 0,
                "stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _normalise_ext(ext):
    return ext if ext.startswith(".") else "." + ext


def set_assoc(ext, progid):
    ext = _normalise_ext(ext)
    return run_cmd(f"assoc {ext}={progid}")


def set_ftype(progid, app_path):
    return run_cmd(f'ftype {progid}="{app_path}" "%1"')


def check_assoc(ext):
    ext = _normalise_ext(ext)
    result = run_cmd(f"assoc {ext}")
    if result.get("success"):
        out = (result.get("stdout") or "").strip()
        if "=" in out:
            return out.split("=")[-1]
    return None


def check_ftype(progid):
    if not progid:
        return None
    result = run_cmd(f"ftype {progid}")
    if result.get("success"):
        out = (result.get("stdout") or "").strip()
        if "=" in out:
            return out.split("=", 1)[-1]
    return None


def set_registry_assoc(ext, app_path, progid=None):
    if winreg is None:
        return {"success": False, "error": "winreg unavailable"}
    ext = _normalise_ext(ext)
    if progid is None:
        progid = ext[1:].upper() + "File"
    try:
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
            winreg.SetValue(key, None, winreg.REG_SZ, progid)
        with winreg.CreateKey(
            winreg.HKEY_CLASSES_ROOT, f"{progid}\\shell\\open\\command"
        ) as key:
            winreg.SetValue(key, None, winreg.REG_SZ, f'"{app_path}" "%1"')
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def set_user_choice(ext, app_path, progid=None):
    if winreg is None:
        return {"success": False, "error": "winreg unavailable"}
    ext = _normalise_ext(ext)
    if progid is None:
        progid = ext[1:].upper() + "File"
    try:
        user_sid = os.environ.get("USERNAME", "unknown")
        timestamp = int(time.time())
        hash_input = f"{progid}{user_sid}{timestamp}".encode("utf-16le")
        hash_value = hashlib.sha256(hash_input).hexdigest()

        path = (
            "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\"
            f"{ext}\\UserChoice"
        )
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, path) as key:
            winreg.SetValueEx(key, "ProgId", 0, winreg.REG_SZ, progid)
            winreg.SetValueEx(key, "Hash", 0, winreg.REG_SZ, hash_value)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def apply_rule(ext, app_path):
    """Apply all four locking layers for a single (ext, app) pair."""
    ext = _normalise_ext(ext)
    progid = ext[1:].upper() + "File"

    results = []
    results.append(("assoc", set_assoc(ext, progid)))
    results.append(("ftype", set_ftype(progid, app_path)))
    results.append(("registry", set_registry_assoc(ext, app_path, progid)))
    results.append(("user_choice", set_user_choice(ext, app_path, progid)))
    return {
        "success": all(r[1].get("success") for r in results),
        "results": results,
    }


def verify_rule(ext, app_path):
    """Cheap check: does the current ftype command line contain our app?"""
    progid = check_assoc(ext)
    current = check_ftype(progid or "")
    if current and app_path.lower() in current.lower():
        return True
    return False
