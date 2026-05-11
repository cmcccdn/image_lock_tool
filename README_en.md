# Image Lock Tool

<p align="right">
  <a href="README.md">中文</a> | <b>English</b>
</p>

Lock the default opener for image formats (jpg / png / webp / …) on Windows so that the viewer **you** pick stays the default — even when other apps try to steal it back.

> Sub-project of [`defaultapp_locker`](../defaultapp_locker). It reuses the same four-layer registry-locking + periodic re-enforcement strategy, focused specifically on the "image viewer" use case.

---

## Features

- 25 built-in image extensions (jpg / jpeg / png / gif / bmp / webp / svg / ico / tiff / tif / raw / psd / heic / heif / avif / jfif / pjpeg / pjp / apng / cur / dds / exr / hdr / tga / xcf)
- Each extension shown as a **square card-button**; click to toggle "locked / unlocked"
- **Select-all-lock / Invert / Select-none** in one click
- Big eye-catching **【Apply Lock】** button — writes the registry through all four layers and verifies
- **Configurable check interval** (default 120 s = 2 min)
- **Add custom extensions** by hand
- **Drag a file onto the window** → extension is auto-detected and a dialog offers
  - **Add and lock (default)**
  - **Add only, do not lock**
  - **Cancel**
  - 5-second countdown — auto-confirm "add and lock" on timeout
- Chinese-only UI ("图片查看锁定小工具")
- Bundled icon: a padlock locking an image card

---

## Directory layout

```
image_lock_tool/
├── gui.py                         entry point (run as administrator)
├── requirements.txt
├── test_core.py                   config-layer unit tests (cross-platform)
├── image_lock/
│   ├── core/
│   │   ├── config.py              JSON persistence / default extensions
│   │   └── locker.py              4-layer registry lock (assoc / ftype / HKCR / UserChoice)
│   ├── service/
│   │   └── lock_service.py        Windows service, periodic re-check
│   └── gui/
│       ├── main_window.py         main window
│       ├── tray.py                system tray
│       └── icon_gen.py            generates icon.png + icon.ico
├── resources/
│   ├── icon.png
│   └── icon.ico
└── scripts/
    ├── build.bat                  one-shot PyInstaller build
    ├── build_gui.spec
    ├── build_service.spec
    ├── start_gui.bat
    ├── install_service.bat
    └── uninstall_service.bat
```

---

## Installation

```cmd
python -m pip install -r requirements.txt
```

Optional dependencies:

| Package          | Required             | Purpose                                  |
| ---------------- | -------------------- | ---------------------------------------- |
| `customtkinter`  | recommended          | Modern Tk theme (falls back to plain Tk) |
| `Pillow`         | required             | Icon generation / system tray            |
| `pystray`        | recommended          | System tray                              |
| `tkinterdnd2`    | recommended          | Drag-and-drop (window still works without it; just no DnD) |
| `pywin32`        | required on Windows  | Registry / background service            |

---

## Usage

### 1. Generate icons (first time, or after editing `icon_gen.py`)

```cmd
python -m image_lock.gui.icon_gen
```

Writes `resources/icon.png` and `resources/icon.ico`.

### 2. Launch the GUI (must run as administrator)

```cmd
scripts\start_gui.bat
```

or

```cmd
python gui.py
```

If launched without admin rights it will trigger a UAC re-elevation automatically.

### 3. Install the periodic re-check service (optional but strongly recommended)

```cmd
scripts\install_service.bat
```

Uninstall:

```cmd
scripts\uninstall_service.bat
```

The service rewrites the registry every "check interval" seconds (set in the GUI), making the lock persistent.

### 4. Build the EXE

```cmd
scripts\build.bat
```

Outputs in `dist\`:

- `ImageLockTool.exe` — GUI, with icon and UAC manifest
- `ImageLockToolService.exe` — background service

---

## Config file location

| Platform                   | Path                                                  |
| -------------------------- | ----------------------------------------------------- |
| Windows                    | `C:\ProgramData\image-lock-tool\config.json`          |
| Other (dev fallback)       | `~/.image-lock-tool/config.json`                      |

Schema:

```json
{
  "app": "C:\\Windows\\System32\\mspaint.exe",
  "checkInterval": 120,
  "enabled": true,
  "extensions": { "jpg": true, "png": true, "webp": false, "...": false }
}
```

---

## Tests

```cmd
python test_core.py -v
```

Tests run on macOS / Linux / Windows (no dependency on `winreg`).

---

## License

Apache License 2.0 — see [`LICENSE`](LICENSE).
