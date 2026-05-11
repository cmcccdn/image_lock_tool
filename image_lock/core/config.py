"""Configuration store for the image-extension lock tool.

Schema:
{
    "app": "C:\\\\Windows\\\\System32\\\\mspaint.exe",   # target viewer
    "checkInterval": 120,                                 # seconds, default 2 min
    "enabled": true,                                       # master switch
    "extensions": {                                        # ext -> locked bool
        "jpg": true, "png": true, "webp": false, ...
    }
}
"""
import json
import os

# Built-in image extensions shown as buttons in the UI
DEFAULT_IMAGE_EXTS = [
    "jpg", "jpeg", "png", "gif", "bmp",
    "webp", "svg", "ico", "tiff", "tif",
    "raw", "psd", "heic", "heif", "avif",
    "jfif", "pjpeg", "pjp", "apng", "cur",
    "dds", "exr", "hdr", "tga", "xcf",
]

DEFAULT_APP = "C:\\Windows\\System32\\mspaint.exe"
DEFAULT_INTERVAL = 120  # 2 minutes

DEFAULT_CONFIG = {
    "app": DEFAULT_APP,
    "checkInterval": DEFAULT_INTERVAL,
    "enabled": True,
    "extensions": {ext: False for ext in DEFAULT_IMAGE_EXTS},
}


def get_config_path():
    if os.name == "nt":
        base = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
        d = os.path.join(base, "image-lock-tool")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "config.json")
    # dev fallback
    d = os.path.join(os.path.expanduser("~"), ".image-lock-tool")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "config.json")


def load_config():
    path = get_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # Make sure all default keys exist
            cfg.setdefault("app", DEFAULT_APP)
            cfg.setdefault("checkInterval", DEFAULT_INTERVAL)
            cfg.setdefault("enabled", True)
            cfg.setdefault("extensions", {})
            # Ensure the built-in extensions are always present
            for ext in DEFAULT_IMAGE_EXTS:
                cfg["extensions"].setdefault(ext, False)
            return cfg
        except Exception:
            pass
    # Return a fresh copy — never share the literal DEFAULT_CONFIG dict
    return {
        "app": DEFAULT_APP,
        "checkInterval": DEFAULT_INTERVAL,
        "enabled": True,
        "extensions": {ext: False for ext in DEFAULT_IMAGE_EXTS},
    }


def save_config(cfg):
    path = get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def normalise_ext(ext):
    """'jpg', '.JPG', 'foo.PNG', '*.gif' -> 'jpg' / 'png' / 'gif'."""
    if not ext:
        return ""
    ext = ext.strip().lower()
    # drop everything before the last '.' (turns 'foo.png' / '*.png' into 'png')
    if "." in ext:
        ext = ext.rsplit(".", 1)[-1]
    return ext.lstrip("*")


def get_locked_exts(cfg):
    return [e for e, locked in cfg.get("extensions", {}).items() if locked]
