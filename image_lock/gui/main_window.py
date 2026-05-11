"""Main window for the image-extension lock tool. Chinese-only UI."""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import customtkinter as ctk
    HAS_CTK = True
except ImportError:
    ctk = None
    HAS_CTK = False

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    TkinterDnD = None
    DND_FILES = None
    HAS_DND = False

from image_lock.core.config import (
    load_config, save_config, normalise_ext,
    DEFAULT_IMAGE_EXTS, DEFAULT_APP, DEFAULT_INTERVAL,
)
from image_lock.core.locker import apply_rule


APP_TITLE = "图片查看锁定小工具"
DROP_DEFAULT_DELAY_MS = 5000

if HAS_CTK:
    BASE_TK = ctk.CTk
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
elif HAS_DND:
    BASE_TK = TkinterDnD.Tk
else:
    BASE_TK = tk.Tk


def _icon_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "resources", "icon.ico"))


def _png_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "resources", "icon.png"))


class ExtButton(tk.Frame):
    """A square card-style toggle button for one extension."""

    NORMAL_BG = "#f4f6fb"
    NORMAL_FG = "#222222"
    LOCKED_BG = "#e74c3c"
    LOCKED_FG = "#ffffff"
    BORDER = "#c8d0e0"

    def __init__(self, master, ext, locked, on_toggle, **kw):
        super().__init__(master, bd=0, highlightthickness=1,
                         highlightbackground=self.BORDER,
                         width=104, height=72, **kw)
        self.pack_propagate(False)
        self.ext = ext
        self.locked = locked
        self.on_toggle = on_toggle

        self.lbl_ext = tk.Label(self, text="." + ext,
                                font=("Microsoft YaHei", 14, "bold"))
        self.lbl_ext.pack(pady=(10, 0))

        self.lbl_state = tk.Label(self, text="未锁",
                                  font=("Microsoft YaHei", 10))
        self.lbl_state.pack()

        for w in (self, self.lbl_ext, self.lbl_state):
            w.bind("<Button-1>", self._click)

        self._refresh()

    def _click(self, _evt=None):
        self.locked = not self.locked
        self._refresh()
        if self.on_toggle:
            self.on_toggle(self.ext, self.locked)

    def set_locked(self, locked, fire=True):
        if self.locked == locked:
            return
        self.locked = locked
        self._refresh()
        if fire and self.on_toggle:
            self.on_toggle(self.ext, self.locked)

    def _refresh(self):
        if self.locked:
            bg, fg, txt = self.LOCKED_BG, self.LOCKED_FG, "已锁 \U0001F512"
        else:
            bg, fg, txt = self.NORMAL_BG, self.NORMAL_FG, "未锁"
        for w in (self, self.lbl_ext, self.lbl_state):
            w.configure(bg=bg)
        self.lbl_ext.configure(fg=fg)
        self.lbl_state.configure(fg=fg, text=txt)


class MainWindow(BASE_TK):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("960x720")
        self.minsize(820, 620)
        try:
            self.iconbitmap(_icon_path())
        except Exception:
            pass

        self.cfg = load_config()
        self.ext_buttons = {}
        self._drop_after_id = None

        self._build_ui()
        self._populate_ext_grid()
        self._setup_dnd()

    # ----- UI -----
    def _build_ui(self):
        root = tk.Frame(self, bg="#ffffff")
        root.pack(fill="both", expand=True)

        # Header
        header = tk.Frame(root, bg="#2c3e50", height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=APP_TITLE, bg="#2c3e50", fg="#ffffff",
                 font=("Microsoft YaHei", 18, "bold")).pack(side="left", padx=20)
        tk.Label(header, text="锁定图片格式默认打开方式",
                 bg="#2c3e50", fg="#bbd6ff",
                 font=("Microsoft YaHei", 11)).pack(side="left", padx=8)

        # Settings row
        cfg_box = tk.LabelFrame(root, text="设置",
                                font=("Microsoft YaHei", 11, "bold"),
                                bg="#ffffff", padx=12, pady=10)
        cfg_box.pack(fill="x", padx=14, pady=(12, 8))

        tk.Label(cfg_box, text="目标查看程序：", bg="#ffffff",
                 font=("Microsoft YaHei", 10)).grid(row=0, column=0, sticky="w")
        self.var_app = tk.StringVar(value=self.cfg.get("app", DEFAULT_APP))
        tk.Entry(cfg_box, textvariable=self.var_app, width=60).grid(
            row=0, column=1, sticky="we", padx=6)
        tk.Button(cfg_box, text="浏览…", command=self._pick_app).grid(
            row=0, column=2, padx=4)

        tk.Label(cfg_box, text="检查周期（秒）：", bg="#ffffff",
                 font=("Microsoft YaHei", 10)).grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.var_interval = tk.IntVar(value=int(self.cfg.get("checkInterval", DEFAULT_INTERVAL)))
        tk.Spinbox(cfg_box, from_=10, to=86400, increment=10,
                   textvariable=self.var_interval, width=10).grid(
            row=1, column=1, sticky="w", padx=6, pady=(8, 0))
        tk.Label(cfg_box, text="（默认 120 秒 = 2 分钟）", bg="#ffffff",
                 fg="#666", font=("Microsoft YaHei", 9)).grid(
            row=1, column=1, sticky="w", padx=(120, 0), pady=(8, 0))

        cfg_box.columnconfigure(1, weight=1)

        # auto-persist whenever the two text widgets change — no need for the
        # user to click "应用锁定" just to save the path / interval.
        self.var_app.trace_add("write", lambda *_: self._persist_settings())
        self.var_interval.trace_add("write", lambda *_: self._persist_settings())

        # Toolbar (select all / invert / none / add custom)
        bar = tk.Frame(root, bg="#ffffff")
        bar.pack(fill="x", padx=14)
        tk.Button(bar, text="全选锁定", width=10,
                  font=("Microsoft YaHei", 10),
                  command=self._select_all).pack(side="left", padx=(0, 6))
        tk.Button(bar, text="反选", width=8,
                  font=("Microsoft YaHei", 10),
                  command=self._invert).pack(side="left", padx=6)
        tk.Button(bar, text="全不选", width=8,
                  font=("Microsoft YaHei", 10),
                  command=self._select_none).pack(side="left", padx=6)

        tk.Label(bar, text="   自定义后缀：", bg="#ffffff",
                 font=("Microsoft YaHei", 10)).pack(side="left")
        self.var_custom = tk.StringVar()
        ent = tk.Entry(bar, textvariable=self.var_custom, width=12,
                       font=("Microsoft YaHei", 10))
        ent.pack(side="left")
        ent.bind("<Return>", lambda _e: self._add_custom())
        tk.Button(bar, text="添加", width=6,
                  font=("Microsoft YaHei", 10),
                  command=self._add_custom).pack(side="left", padx=4)

        # Extension grid (scrollable)
        grid_box = tk.LabelFrame(root, text="图片格式（点击方块切换锁定）",
                                 font=("Microsoft YaHei", 11, "bold"),
                                 bg="#ffffff", padx=8, pady=8)
        grid_box.pack(fill="both", expand=True, padx=14, pady=(8, 8))

        canvas = tk.Canvas(grid_box, bg="#ffffff", highlightthickness=0)
        vbar = tk.Scrollbar(grid_box, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")

        self.grid_inner = tk.Frame(canvas, bg="#ffffff")
        self._grid_window = canvas.create_window((0, 0), window=self.grid_inner, anchor="nw")
        self._canvas = canvas

        def _on_configure(_e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.grid_inner.bind("<Configure>", _on_configure)

        def _on_canvas_configure(e):
            canvas.itemconfigure(self._grid_window, width=e.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        def _on_wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_wheel)

        # Status bar
        self.var_status = tk.StringVar(value="就绪")
        tk.Label(root, textvariable=self.var_status, anchor="w",
                 bg="#eef1f7", fg="#333", padx=10,
                 font=("Microsoft YaHei", 10)).pack(fill="x", side="bottom")

        # Big apply button
        apply_box = tk.Frame(root, bg="#ffffff")
        apply_box.pack(fill="x", side="bottom", padx=14, pady=10)
        self.btn_apply = tk.Button(
            apply_box, text="应 用 锁 定",
            font=("Microsoft YaHei", 22, "bold"),
            bg="#27ae60", fg="#ffffff",
            activebackground="#1f8c4d", activeforeground="#ffffff",
            relief="flat", bd=0, height=2,
            command=self._apply_lock,
        )
        self.btn_apply.pack(fill="x", ipady=6)

    # ----- ext grid -----
    def _populate_ext_grid(self):
        for w in self.grid_inner.winfo_children():
            w.destroy()
        self.ext_buttons.clear()

        exts = list(self.cfg.get("extensions", {}).keys())
        # ensure built-ins come first then customs
        ordered = [e for e in DEFAULT_IMAGE_EXTS if e in exts]
        ordered += [e for e in exts if e not in DEFAULT_IMAGE_EXTS]

        cols = 8
        for i, ext in enumerate(ordered):
            r, c = divmod(i, cols)
            locked = bool(self.cfg["extensions"].get(ext, False))
            btn = ExtButton(self.grid_inner, ext, locked, self._on_btn_toggle)
            btn.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            self.ext_buttons[ext] = btn
        for c in range(cols):
            self.grid_inner.columnconfigure(c, weight=1)

        self._update_status()

    def _on_btn_toggle(self, ext, locked):
        self.cfg.setdefault("extensions", {})[ext] = bool(locked)
        save_config(self.cfg)
        self._update_status()

    def _select_all(self):
        for ext, btn in self.ext_buttons.items():
            self.cfg["extensions"][ext] = True
            btn.set_locked(True, fire=False)
        save_config(self.cfg)
        self._update_status()

    def _select_none(self):
        for ext, btn in self.ext_buttons.items():
            self.cfg["extensions"][ext] = False
            btn.set_locked(False, fire=False)
        save_config(self.cfg)
        self._update_status()

    def _invert(self):
        for ext, btn in self.ext_buttons.items():
            new = not btn.locked
            self.cfg["extensions"][ext] = new
            btn.set_locked(new, fire=False)
        save_config(self.cfg)
        self._update_status()

    def _add_custom(self):
        raw = self.var_custom.get()
        ext = normalise_ext(raw)
        if not ext:
            messagebox.showwarning("提示", "请输入有效的后缀名")
            return
        if ext in self.cfg.get("extensions", {}):
            messagebox.showinfo("提示", f"后缀 .{ext} 已存在")
            self.var_custom.set("")
            return
        self.cfg.setdefault("extensions", {})[ext] = True
        save_config(self.cfg)
        self.var_custom.set("")
        self._populate_ext_grid()

    def _pick_app(self):
        p = filedialog.askopenfilename(
            title="选择查看程序",
            filetypes=[("可执行程序", "*.exe"), ("所有文件", "*.*")],
        )
        if p:
            self.var_app.set(p)

    def _update_status(self):
        n = sum(1 for v in self.cfg.get("extensions", {}).values() if v)
        total = len(self.cfg.get("extensions", {}))
        self.var_status.set(f"已锁定 {n} / {total} 个后缀  •  目标：{self.var_app.get()}")

    def _persist_settings(self):
        """Push the two text-bound settings into self.cfg and save.

        Called from a Tk variable trace so any change to the target-app
        path or the check-interval spinbox is written to disk immediately,
        without the user having to click '应用锁定'.
        """
        self.cfg["app"] = (self.var_app.get() or "").strip() or DEFAULT_APP
        try:
            self.cfg["checkInterval"] = max(1, int(self.var_interval.get()))
        except Exception:
            # Spinbox can be temporarily empty / non-numeric while typing.
            self.cfg["checkInterval"] = DEFAULT_INTERVAL
        save_config(self.cfg)
        try:
            self._update_status()
        except Exception:
            pass

    # ----- apply -----
    def _apply_lock(self):
        # commit settings first
        self.cfg["app"] = self.var_app.get().strip() or DEFAULT_APP
        try:
            self.cfg["checkInterval"] = int(self.var_interval.get())
        except Exception:
            self.cfg["checkInterval"] = DEFAULT_INTERVAL
        self.cfg["enabled"] = True
        save_config(self.cfg)

        locked = [e for e, v in self.cfg.get("extensions", {}).items() if v]
        if not locked:
            messagebox.showinfo("提示", "没有任何后缀被勾选锁定。")
            return

        if os.name != "nt":
            messagebox.showinfo(
                "提示",
                "配置已保存。\n实际写入注册表/关联只能在 Windows 上完成。",
            )
            self._update_status()
            return

        ok, fail = 0, 0
        for ext in locked:
            try:
                r = apply_rule(ext, self.cfg["app"])
                if r.get("success"):
                    ok += 1
                else:
                    fail += 1
            except Exception:
                fail += 1
        messagebox.showinfo("锁定完成",
                            f"成功 {ok} 个，失败 {fail} 个。\n"
                            f"后台服务将每 {self.cfg['checkInterval']} 秒自动复检。")
        self._update_status()

    # ----- drag & drop -----
    def _setup_dnd(self):
        if not HAS_DND:
            return
        try:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

    def _on_drop(self, event):
        # event.data: '{C:/foo bar/a.png} {C:/b.jpg}'
        raw = event.data
        files = self._parse_drop_paths(raw)
        exts = []
        seen = set()
        for f in files:
            base = os.path.basename(f)
            if "." in base:
                e = normalise_ext(base.rsplit(".", 1)[-1])
                if e and e not in seen:
                    seen.add(e)
                    exts.append(e)
        if not exts:
            return
        self._show_drop_dialog(exts)

    def _parse_drop_paths(self, data):
        out = []
        if not data:
            return out
        s = data.strip()
        i = 0
        n = len(s)
        cur = ""
        in_brace = False
        while i < n:
            ch = s[i]
            if ch == "{":
                in_brace = True
                cur = ""
            elif ch == "}":
                in_brace = False
                if cur:
                    out.append(cur)
                cur = ""
            elif ch == " " and not in_brace:
                if cur:
                    out.append(cur)
                cur = ""
            else:
                cur += ch
            i += 1
        if cur:
            out.append(cur)
        return out

    def _show_drop_dialog(self, exts):
        dlg = tk.Toplevel(self)
        dlg.title("拖入文件 — 添加后缀锁定")
        dlg.transient(self)
        dlg.grab_set()
        dlg.configure(bg="#ffffff")
        dlg.geometry("520x260")
        dlg.resizable(False, False)

        tk.Label(dlg, text="检测到以下后缀名：", bg="#ffffff",
                 font=("Microsoft YaHei", 12, "bold")).pack(pady=(16, 6))
        tk.Label(dlg, text="、".join("." + e for e in exts), bg="#ffffff",
                 fg="#c0392b",
                 font=("Microsoft YaHei", 14, "bold"),
                 wraplength=480, justify="center").pack(pady=(0, 10))

        countdown = tk.StringVar(value="将在 5 秒后默认 添加并锁定 …")
        lbl_count = tk.Label(dlg, textvariable=countdown, bg="#ffffff",
                             fg="#555", font=("Microsoft YaHei", 10))
        lbl_count.pack(pady=(0, 10))

        state = {"done": False, "after_id": None, "remaining": 5}

        def cancel_timer():
            if state["after_id"] is not None:
                try:
                    dlg.after_cancel(state["after_id"])
                except Exception:
                    pass
                state["after_id"] = None

        def finish(action):
            if state["done"]:
                return
            state["done"] = True
            cancel_timer()
            try:
                dlg.destroy()
            except Exception:
                pass
            if action == "add_lock":
                self._dnd_add(exts, lock=True)
            elif action == "add_only":
                self._dnd_add(exts, lock=False)

        def tick():
            if state["done"]:
                return
            state["remaining"] -= 1
            if state["remaining"] <= 0:
                finish("add_lock")
                return
            countdown.set(f"将在 {state['remaining']} 秒后默认 添加并锁定 …")
            state["after_id"] = dlg.after(1000, tick)

        btns = tk.Frame(dlg, bg="#ffffff")
        btns.pack(pady=14)
        tk.Button(btns, text="添加并锁定（默认）",
                  font=("Microsoft YaHei", 11, "bold"),
                  bg="#27ae60", fg="#ffffff", relief="flat",
                  width=18, height=2,
                  command=lambda: finish("add_lock")).pack(side="left", padx=8)
        tk.Button(btns, text="只添加 不锁定",
                  font=("Microsoft YaHei", 11),
                  bg="#3498db", fg="#ffffff", relief="flat",
                  width=14, height=2,
                  command=lambda: finish("add_only")).pack(side="left", padx=8)
        tk.Button(btns, text="取消",
                  font=("Microsoft YaHei", 11),
                  bg="#bdc3c7", fg="#222", relief="flat",
                  width=10, height=2,
                  command=lambda: finish("cancel")).pack(side="left", padx=8)

        # any user interaction stops the countdown
        def stop_timer(_e=None):
            cancel_timer()
            countdown.set("等待您的选择 …")
        dlg.bind("<Motion>", stop_timer)
        dlg.bind("<Key>", stop_timer)

        state["after_id"] = dlg.after(1000, tick)

    def _dnd_add(self, exts, lock):
        changed = False
        for e in exts:
            cur = self.cfg.setdefault("extensions", {}).get(e)
            if cur is None:
                self.cfg["extensions"][e] = bool(lock)
                changed = True
            elif lock and not cur:
                self.cfg["extensions"][e] = True
                changed = True
        if changed:
            save_config(self.cfg)
            self._populate_ext_grid()
        if lock and os.name == "nt":
            self._apply_lock()
