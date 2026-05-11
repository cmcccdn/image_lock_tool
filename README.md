# 图片查看锁定小工具 (Image Lock Tool)

<p align="right">
  <b>中文</b> | <a href="README_en.md">English</a>
</p>

锁定 Windows 上图片格式（jpg、png、webp …）的默认打开方式，让它始终被你指定的查看程序接管，且不会被其他软件偷偷改回去。

> 本工具是 [`defaultapp_locker`](../defaultapp_locker) 的子项目，复用其四层注册表写入 + 周期复检策略，专门面向"图片"使用场景。

---

## 功能

- 内置常见图片后缀名（jpg / jpeg / png / gif / bmp / webp / svg / ico / tiff / tif / raw / psd / heic / heif / avif / jfif / pjpeg / pjp / apng / cur / dds / exr / hdr / tga / xcf）
- 全部以 **方块按钮** 形式展示，单击切换"锁定 / 未锁"
- 支持 **全选锁定 / 反选 / 全不选**
- 醒目的大号 **【应用锁定】** 按钮，一键写入注册表并复检
- 检查周期 **可自定义**（默认 120 秒 = 2 分钟）
- 支持 **手动添加自定义后缀**
- 支持 **拖拽文件到主窗口**：自动解析后缀名，弹窗提供
  - **添加并锁定（默认）**
  - **只添加 不锁定**
  - **取消**
  - 5 秒倒计时，超时自动 添加并锁定
- 全中文界面，应用名 = "图片查看锁定小工具"
- 自带应用图标：一把锁锁住一张图片

---

## 目录结构

```
image_lock_tool/
├── gui.py                         入口（请用管理员身份运行）
├── requirements.txt
├── test_core.py                   配置层单元测试（跨平台可跑）
├── image_lock/
│   ├── core/
│   │   ├── config.py              JSON 持久化 / 默认后缀
│   │   └── locker.py              注册表 4 层锁定（assoc/ftype/HKCR/UserChoice）
│   ├── service/
│   │   └── lock_service.py        Windows 服务，按周期复检
│   └── gui/
│       ├── main_window.py         主窗口
│       ├── tray.py                系统托盘
│       └── icon_gen.py            自动生成 icon.png + icon.ico
├── resources/
│   ├── icon.png
│   └── icon.ico
└── scripts/
    ├── build.bat                  PyInstaller 一键打包
    ├── build_gui.spec
    ├── build_service.spec
    ├── start_gui.bat
    ├── install_service.bat
    └── uninstall_service.bat
```

---

## 安装

```cmd
python -m pip install -r requirements.txt
```

可选依赖说明：

| 包                | 必需        | 用途                       |
| ---------------- | --------- | ------------------------ |
| `customtkinter`  | 推荐        | 更现代的 Tk 主题（缺失时回退到原生 Tk） |
| `Pillow`         | 必需        | 图标生成 / 系统托盘             |
| `pystray`        | 推荐        | 系统托盘                   |
| `tkinterdnd2`    | 推荐        | 文件拖拽支持（缺失时窗口仍可用，仅无 DnD） |
| `pywin32`        | Windows 必需 | 注册表 / 后台服务              |

---

## 使用

### 1. 生成图标（首次或修改 `icon_gen.py` 后）

```cmd
python -m image_lock.gui.icon_gen
```

会写出 `resources/icon.png` 与 `resources/icon.ico`。

### 2. 启动 GUI（必须以管理员身份运行）

```cmd
scripts\start_gui.bat
```

或

```cmd
python gui.py
```

非管理员启动时会自动弹出 UAC 重新提权。

### 3. 安装周期复检后台服务（可选，强烈推荐）

```cmd
scripts\install_service.bat
```

卸载：

```cmd
scripts\uninstall_service.bat
```

服务会按照 GUI 中设置的"检查周期"重新写回注册表，使锁定持久生效。

### 4. 打包 EXE

```cmd
scripts\build.bat
```

产物在 `dist\` 下：

- `ImageLockTool.exe` —— 带图标、带 UAC 提权清单的 GUI
- `ImageLockToolService.exe` —— 后台服务

---

## 配置文件位置

| 平台         | 路径                                                    |
| ---------- | ----------------------------------------------------- |
| Windows    | `C:\ProgramData\image-lock-tool\config.json`          |
| 其它（开发回退）   | `~/.image-lock-tool/config.json`                      |

字段：

```json
{
  "app": "C:\\Windows\\System32\\mspaint.exe",
  "checkInterval": 120,
  "enabled": true,
  "extensions": { "jpg": true, "png": true, "webp": false, "...": false }
}
```

---

## 测试

```cmd
python test_core.py -v
```

所有用例可在 macOS / Linux / Windows 上跑通（不依赖 winreg）。

---

## 许可

继承父项目 `defaultapp_locker` 的开源许可证。
