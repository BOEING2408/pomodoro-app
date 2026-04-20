"""
番茄钟桌面应用
功能：计时器（专注/短休/长休）、任务列表、每日进度汇总
      专注模式：全屏置顶 + 自定义背景图片 + 励志语录淡入淡出轮换
技术栈：Python 3.10 + tkinter/ttk + Pillow
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import random
import datetime
import threading
import winsound

from PIL import Image, ImageTk, ImageFilter, ImageEnhance

# ─────────────────────────────────────────────
# 常量
# ─────────────────────────────────────────────
WORK_MIN            = 25
SHORT_BREAK_MIN     = 5
LONG_BREAK_MIN      = 15
LONG_BREAK_INTERVAL = 4

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "pomodoro_data.json")

COLORS = {
    "bg":          "#1E1E2E",
    "surface":     "#2A2A3E",
    "surface2":    "#313145",
    "primary":     "#FF6B6B",
    "short_break": "#4ECDC4",
    "long_break":  "#45B7D1",
    "text":        "#CDD6F4",
    "text_dim":    "#6C7086",
    "accent":      "#F38BA8",
    "success":     "#A6E3A1",
    "warning":     "#FAB387",
    "border":      "#45475A",
    "done_bg":     "#2A3A2A",
    "done_fg":     "#6C7086",
    "focus_bg":    "#0D0D1A",
    "focus_ring":  "#FF6B6B",
    "focus_text":  "#FFFFFF",
    "focus_dim":   "#AAAACC",
    "focus_btn":   "#2A2A3E",
    "focus_btn_h": "#FF6B6B",
    "quote_text":  "#F0EAD6",
    "quote_author":"#CCBBAA",
}

FONTS = {
    "timer":        ("Segoe UI", 64, "bold"),
    "focus_timer":  ("Segoe UI", 110, "bold"),
    "focus_sub":    ("Segoe UI", 20),
    "focus_task":   ("Segoe UI", 15),
    "focus_hint":   ("Segoe UI", 10),
    "focus_quote":  ("Segoe UI", 17, "italic"),
    "focus_author": ("Segoe UI", 12),
    "h1":           ("Segoe UI", 18, "bold"),
    "h2":           ("Segoe UI", 13, "bold"),
    "body":         ("Segoe UI", 11),
    "small":        ("Segoe UI", 9),
}

MODE_LABELS    = {"work": "专注", "short_break": "短休息", "long_break": "长休息"}
MODE_COLORS    = {"work": COLORS["primary"],
                  "short_break": COLORS["short_break"],
                  "long_break": COLORS["long_break"]}
MODE_DURATIONS = {"work": WORK_MIN * 60,
                  "short_break": SHORT_BREAK_MIN * 60,
                  "long_break": LONG_BREAK_MIN * 60}

SUPPORTED_IMG = (
    ("图片文件", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff *.gif"),
    ("所有文件", "*.*"),
)

QUOTE_INTERVAL = 60   # 默认语录轮换间隔（秒）

# ─────────────────────────────────────────────
# 内置语录库（中英双语）
# ─────────────────────────────────────────────
BUILTIN_QUOTES = [
    # 专注与效率
    {"text": "专注是通往卓越的唯一道路。", "author": ""},
    {"text": "一次只做一件事，把它做到极致。", "author": ""},
    {"text": "深度工作是当今世界最有价值的能力。", "author": "卡尔·纽波特"},
    {"text": "The secret of getting ahead is getting started.", "author": "Mark Twain"},
    {"text": "Focus on being productive instead of busy.", "author": "Tim Ferriss"},
    {"text": "It's not about having time, it's about making time.", "author": ""},
    # 坚持与毅力
    {"text": "坚持是成功最重要的品质。", "author": ""},
    {"text": "每一个你不想起床的早晨，都是改变的开始。", "author": ""},
    {"text": "不积跬步，无以至千里；不积小流，无以成江海。", "author": "荀子"},
    {"text": "Success is the sum of small efforts repeated day in and day out.", "author": "Robert Collier"},
    {"text": "It does not matter how slowly you go as long as you do not stop.", "author": "Confucius"},
    {"text": "Fall seven times, stand up eight.", "author": "Japanese Proverb"},
    # 时间与当下
    {"text": "此刻你所拥有的，就是你全部的财富。", "author": ""},
    {"text": "不要等待完美的时机，现在就是最好的时机。", "author": ""},
    {"text": "今日事今日毕。", "author": ""},
    {"text": "Lost time is never found again.", "author": "Benjamin Franklin"},
    {"text": "The present moment is the only moment available to us.", "author": "Thich Nhat Hanh"},
    {"text": "You don't have to be great to start, but you have to start to be great.", "author": "Zig Ziglar"},
    # 成长与突破
    {"text": "舒适区之外，才是成长开始的地方。", "author": ""},
    {"text": "每天进步一点点，终将成就非凡。", "author": ""},
    {"text": "困难是上天给你的礼物，它让你变得更强。", "author": ""},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "In the middle of every difficulty lies opportunity.", "author": "Albert Einstein"},
    # 自律与习惯
    {"text": "自律给我自由。", "author": "乔科·威林克"},
    {"text": "我们是自己习惯的产物。", "author": "亚里士多德"},
    {"text": "先做必须做的，再做可能做的，你会发现不可能的事也做到了。", "author": "阿西西的方济各"},
    {"text": "Discipline is choosing between what you want now and what you want most.", "author": ""},
    {"text": "We are what we repeatedly do. Excellence is not an act, but a habit.", "author": "Aristotle"},
    {"text": "Small daily improvements are the key to staggering long-term results.", "author": ""},
    # 番茄钟专属
    {"text": "这个番茄是你的，全力以赴吧！", "author": ""},
    {"text": "25 分钟，足以改变今天。", "author": ""},
    {"text": "关掉通知，打开专注，世界可以等你。", "author": ""},
    {"text": "One Pomodoro at a time. That's all it takes.", "author": ""},
    {"text": "The tomato is ticking. Make it count.", "author": ""},
    # 心态与平静
    {"text": "静下心来，答案自然会来。", "author": ""},
    {"text": "呼吸，专注，前行。", "author": ""},
    {"text": "你比你想象的更有能力。", "author": ""},
    {"text": "Calm mind brings inner strength and self-confidence.", "author": "Dalai Lama"},
    {"text": "Peace comes from within. Do not seek it without.", "author": "Buddha"},
]


# ─────────────────────────────────────────────
# 数据持久化
# ─────────────────────────────────────────────
def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"tasks": [], "daily_log": {}, "settings": {}, "custom_quotes": []}


def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
# 图片工具
# ─────────────────────────────────────────────
def _make_thumbnail(path: str, size=(80, 50)):
    try:
        img = Image.open(path).convert("RGB")
        img.thumbnail(size, Image.LANCZOS)
        w, h   = img.size
        tw, th = size
        bg     = Image.new("RGB", size, (30, 30, 46))
        bg.paste(img, ((tw - w) // 2, (th - h) // 2))
        return ImageTk.PhotoImage(bg)
    except Exception:
        return None


def _prepare_bg(path: str, sw: int, sh: int,
                blur: float = 0.0, dim: float = 0.45):
    try:
        img    = Image.open(path).convert("RGB")
        iw, ih = img.size
        scale  = max(sw / iw, sh / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        img    = img.resize((nw, nh), Image.LANCZOS)
        left   = (nw - sw) // 2
        top    = (nh - sh) // 2
        img    = img.crop((left, top, left + sw, top + sh))
        if blur > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur))
        img = ImageEnhance.Brightness(img).enhance(dim)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


# ─────────────────────────────────────────────
# 语录管理面板（主界面嵌入）
# ─────────────────────────────────────────────
class QuoteManagerPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["surface"],
                         highlightthickness=1,
                         highlightbackground=COLORS["border"],
                         padx=12, pady=10)
        self.app = app
        self._build()

    def _build(self):
        # 标题 + 开关
        title_row = tk.Frame(self, bg=COLORS["surface"])
        title_row.pack(fill="x", pady=(0, 6))
        tk.Label(title_row, text="💬  励志语录",
                 font=FONTS["h2"], bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(side="left")
        self.enabled_var = tk.BooleanVar(value=self.app.quotes_enabled)
        tk.Checkbutton(
            title_row, text="启用", variable=self.enabled_var,
            font=FONTS["small"],
            bg=COLORS["surface"], fg=COLORS["text_dim"],
            selectcolor=COLORS["surface2"],
            activebackground=COLORS["surface"],
            command=self._on_toggle
        ).pack(side="right")

        # 轮换间隔
        interval_row = tk.Frame(self, bg=COLORS["surface"])
        interval_row.pack(fill="x", pady=(0, 6))
        tk.Label(interval_row, text="轮换间隔",
                 font=FONTS["small"], bg=COLORS["surface"],
                 fg=COLORS["text_dim"]).pack(side="left")
        self.interval_var = tk.IntVar(value=self.app.quote_interval)
        spin = tk.Spinbox(
            interval_row, from_=10, to=300, increment=10,
            textvariable=self.interval_var, width=5,
            font=FONTS["small"],
            bg=COLORS["surface2"], fg=COLORS["text"],
            buttonbackground=COLORS["surface2"],
            relief="flat",
            command=self._on_interval)
        spin.pack(side="left", padx=6)
        spin.bind("<FocusOut>", lambda e: self._on_interval())
        tk.Label(interval_row, text="秒",
                 font=FONTS["small"], bg=COLORS["surface"],
                 fg=COLORS["text_dim"]).pack(side="left")

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", pady=(4, 6))

        # 自定义语录列表
        tk.Label(self, text="自定义语录",
                 font=FONTS["small"], bg=COLORS["surface"],
                 fg=COLORS["text_dim"]).pack(anchor="w")

        list_frame = tk.Frame(self, bg=COLORS["surface2"],
                              highlightthickness=1,
                              highlightbackground=COLORS["border"])
        list_frame.pack(fill="x", pady=(4, 6))

        self.quote_listbox = tk.Listbox(
            list_frame, height=4, font=FONTS["small"],
            bg=COLORS["surface2"], fg=COLORS["text"],
            selectbackground=COLORS["primary"],
            selectforeground="white",
            relief="flat", bd=0, activestyle="none")
        sb = ttk.Scrollbar(list_frame, orient="vertical",
                           command=self.quote_listbox.yview)
        self.quote_listbox.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.quote_listbox.pack(side="left", fill="x", expand=True)

        btn_row = tk.Frame(self, bg=COLORS["surface"])
        btn_row.pack(fill="x")
        tk.Button(
            btn_row, text="＋ 添加语录",
            font=FONTS["small"],
            bg=COLORS["primary"], fg="white",
            activebackground=COLORS["accent"], activeforeground="white",
            relief="flat", bd=0, padx=10, pady=3, cursor="hand2",
            command=self._add_quote
        ).pack(side="left", padx=(0, 6))
        tk.Button(
            btn_row, text="✕ 删除选中",
            font=FONTS["small"],
            bg=COLORS["surface2"], fg=COLORS["text_dim"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            relief="flat", bd=0, padx=10, pady=3, cursor="hand2",
            command=self._del_quote
        ).pack(side="left")

        self._refresh_list()

    def _on_toggle(self):
        self.app.quotes_enabled = self.enabled_var.get()
        self.app._save_settings()

    def _on_interval(self):
        try:
            v = int(self.interval_var.get())
            v = max(10, min(300, v))
        except Exception:
            v = QUOTE_INTERVAL
        self.interval_var.set(v)
        self.app.quote_interval = v
        self.app._save_settings()

    def _add_quote(self):
        text = simpledialog.askstring(
            "添加语录", "请输入语录内容：", parent=self.app)
        if not text or not text.strip():
            return
        author = simpledialog.askstring(
            "添加语录", "请输入作者（可留空）：",
            parent=self.app) or ""
        self.app.data.setdefault("custom_quotes", []).append(
            {"text": text.strip(), "author": author.strip()})
        save_data(self.app.data)
        self._refresh_list()

    def _del_quote(self):
        sel = self.quote_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        quotes = self.app.data.get("custom_quotes", [])
        if 0 <= idx < len(quotes):
            quotes.pop(idx)
            save_data(self.app.data)
            self._refresh_list()

    def _refresh_list(self):
        self.quote_listbox.delete(0, "end")
        for q in self.app.data.get("custom_quotes", []):
            line = q["text"]
            if q.get("author"):
                line += f"  ——{q['author']}"
            if len(line) > 50:
                line = line[:48] + "…"
            self.quote_listbox.insert("end", line)


# ─────────────────────────────────────────────
# 背景设置面板（主界面嵌入）
# ─────────────────────────────────────────────
class BgSettingsPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["surface"],
                         highlightthickness=1,
                         highlightbackground=COLORS["border"],
                         padx=12, pady=10)
        self.app = app
        self._thumb_ref = None
        self._build()

    def _build(self):
        title_row = tk.Frame(self, bg=COLORS["surface"])
        title_row.pack(fill="x", pady=(0, 8))
        tk.Label(title_row, text="🖼  专注背景图片",
                 font=FONTS["h2"], bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(side="left")

        body = tk.Frame(self, bg=COLORS["surface"])
        body.pack(fill="x")

        self.thumb_canvas = tk.Canvas(
            body, width=80, height=50,
            bg=COLORS["surface2"],
            highlightthickness=1,
            highlightbackground=COLORS["border"])
        self.thumb_canvas.pack(side="left", padx=(0, 12))

        btn_col = tk.Frame(body, bg=COLORS["surface"])
        btn_col.pack(side="left", fill="y")
        tk.Button(
            btn_col, text="📂  选择图片",
            font=FONTS["small"],
            bg=COLORS["primary"], fg="white",
            activebackground=COLORS["accent"], activeforeground="white",
            relief="flat", bd=0, padx=12, pady=4, cursor="hand2",
            command=self._choose_image
        ).pack(anchor="w", pady=(0, 4))
        tk.Button(
            btn_col, text="✕  清除图片",
            font=FONTS["small"],
            bg=COLORS["surface2"], fg=COLORS["text_dim"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            relief="flat", bd=0, padx=12, pady=4, cursor="hand2",
            command=self._clear_image
        ).pack(anchor="w")

        self.path_label = tk.Label(
            self, text="", font=FONTS["small"],
            bg=COLORS["surface"], fg=COLORS["text_dim"],
            wraplength=300, anchor="w", justify="left")
        self.path_label.pack(fill="x", pady=(6, 0))

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", pady=(8, 6))

        sliders = tk.Frame(self, bg=COLORS["surface"])
        sliders.pack(fill="x")

        blur_row = tk.Frame(sliders, bg=COLORS["surface"])
        blur_row.pack(fill="x", pady=2)
        tk.Label(blur_row, text="模糊", font=FONTS["small"],
                 bg=COLORS["surface"], fg=COLORS["text_dim"],
                 width=4).pack(side="left")
        self.blur_var = tk.DoubleVar(value=self.app.bg_blur)
        ttk.Scale(blur_row, from_=0, to=20,
                  variable=self.blur_var, orient="horizontal",
                  command=self._on_slider).pack(
            side="left", fill="x", expand=True, padx=6)
        self.blur_lbl = tk.Label(
            blur_row, text=f"{self.app.bg_blur:.0f}",
            font=FONTS["small"], bg=COLORS["surface"],
            fg=COLORS["text"], width=3)
        self.blur_lbl.pack(side="left")

        dim_row = tk.Frame(sliders, bg=COLORS["surface"])
        dim_row.pack(fill="x", pady=2)
        tk.Label(dim_row, text="压暗", font=FONTS["small"],
                 bg=COLORS["surface"], fg=COLORS["text_dim"],
                 width=4).pack(side="left")
        self.dim_var = tk.DoubleVar(value=self.app.bg_dim * 100)
        ttk.Scale(dim_row, from_=10, to=90,
                  variable=self.dim_var, orient="horizontal",
                  command=self._on_slider).pack(
            side="left", fill="x", expand=True, padx=6)
        self.dim_lbl = tk.Label(
            dim_row, text=f"{int(self.app.bg_dim * 100)}%",
            font=FONTS["small"], bg=COLORS["surface"],
            fg=COLORS["text"], width=4)
        self.dim_lbl.pack(side="left")

        self._refresh_thumb()

    def _choose_image(self):
        path = filedialog.askopenfilename(
            title="选择专注背景图片",
            filetypes=SUPPORTED_IMG, parent=self.app)
        if not path:
            return
        self.app.bg_image_path = path
        self.app._save_settings()
        self._refresh_thumb()

    def _clear_image(self):
        self.app.bg_image_path = ""
        self.app._save_settings()
        self._refresh_thumb()

    def _on_slider(self, _=None):
        self.app.bg_blur = round(self.blur_var.get(), 1)
        self.app.bg_dim  = round(self.dim_var.get() / 100, 2)
        self.blur_lbl.config(text=f"{self.app.bg_blur:.0f}")
        self.dim_lbl.config(text=f"{int(self.app.bg_dim * 100)}%")
        self.app._save_settings()

    def _refresh_thumb(self):
        path = self.app.bg_image_path
        self.thumb_canvas.delete("all")
        if path and os.path.isfile(path):
            photo = _make_thumbnail(path, (80, 50))
            if photo:
                self._thumb_ref = photo
                self.thumb_canvas.create_image(0, 0, anchor="nw", image=photo)
            short = os.path.basename(path)
            if len(short) > 38:
                short = "…" + short[-36:]
            self.path_label.config(text=short)
        else:
            self.thumb_canvas.create_text(
                40, 25, text="无图片", font=FONTS["small"],
                fill=COLORS["text_dim"])
            self.path_label.config(text="")


# ─────────────────────────────────────────────
# 专注模式覆盖窗口
# ─────────────────────────────────────────────
class FocusOverlay(tk.Toplevel):
    FADE_STEPS = 20
    FADE_MS    = 30

    def __init__(self, master):
        super().__init__(master)
        self.master_app  = master
        self._bg_photo   = None
        self._current_quote = {}
        self._quote_job  = None

        self.overrideredirect(True)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{sw}x{sh}+0+0")
        self.configure(bg=COLORS["focus_bg"])
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()
        self._enforce_topmost()

        self._build_ui(sw, sh)
        self.bind("<Escape>", lambda e: self._try_exit())

        # 启动语录轮换
        if self.master_app.quotes_enabled:
            self.after(800, lambda: self._fade_in_quote(self._pick_quote()))
        self._schedule_next_quote()

    # ── 置顶守护 ─────────────────────────────
    def _enforce_topmost(self):
        try:
            self.attributes("-topmost", True)
            self.lift()
        except Exception:
            pass
        if self.winfo_exists():
            self.after(500, self._enforce_topmost)

    # ── 构建 UI ──────────────────────────────
    def _build_ui(self, sw, sh):
        cx, cy = sw // 2, sh // 2
        self._sw, self._sh = sw, sh

        self.cv = tk.Canvas(self, width=sw, height=sh,
                            bg=COLORS["focus_bg"], highlightthickness=0)
        self.cv.pack(fill="both", expand=True)

        # 背景图片
        self._bg_img_id = self.cv.create_image(0, 0, anchor="nw",
                                               image=None, tags="bg")
        self._load_bg(sw, sh)

        # 顶部信息
        self._lbl_date = self.cv.create_text(
            sw // 2, 32, text="", font=FONTS["focus_hint"],
            fill=COLORS["focus_dim"], anchor="center")
        self._lbl_count = self.cv.create_text(
            sw - 36, 32, text="", font=FONTS["focus_hint"],
            fill=COLORS["focus_dim"], anchor="e")

        # 圆环
        R = min(sw, sh) * 0.26
        ring_cy = cy - sh * 0.08
        self._ring_cy = ring_cy
        self._R = R
        self.cv.create_oval(
            cx - R, ring_cy - R, cx + R, ring_cy + R,
            outline="#2A2A3E", width=16)
        self._arc = self.cv.create_arc(
            cx - R, ring_cy - R, cx + R, ring_cy + R,
            start=90, extent=-359.9,
            outline=COLORS["focus_ring"], width=16, style="arc")

        # 时间 & 模式
        self._lbl_time = self.cv.create_text(
            cx, ring_cy - 14, text="25:00",
            font=FONTS["focus_timer"], fill=COLORS["focus_text"],
            anchor="center")
        self._lbl_mode = self.cv.create_text(
            cx, ring_cy + R * 0.52, text="专注",
            font=FONTS["focus_sub"], fill=COLORS["focus_ring"],
            anchor="center")

        # 当前任务
        self._lbl_task = self.cv.create_text(
            cx, ring_cy + R + 38, text="",
            font=FONTS["focus_task"], fill=COLORS["focus_dim"],
            anchor="center")

        # 番茄进度点
        self._dot_ids = []
        dot_y         = ring_cy + R + 72
        dot_spacing   = 26
        dot_start_x   = cx - (LONG_BREAK_INTERVAL - 1) * dot_spacing / 2
        for i in range(LONG_BREAK_INTERVAL):
            dx  = dot_start_x + i * dot_spacing
            did = self.cv.create_oval(
                dx - 6, dot_y - 6, dx + 6, dot_y + 6,
                fill=COLORS["surface2"], outline="")
            self._dot_ids.append(did)

        # ── 励志语录区域 ──
        quote_y = sh * 0.82

        # 装饰引号
        self._lbl_open_q = self.cv.create_text(
            cx - 10, quote_y - 34, text="\u201c",
            font=("Segoe UI", 40, "bold"),
            fill=self._blend(COLORS["focus_ring"], 0.0),
            anchor="center")

        # 分隔线（用矩形模拟）
        self._sep_line = self.cv.create_rectangle(
            cx - 120, quote_y - 18, cx + 120, quote_y - 17,
            fill=self._blend(COLORS["border"], 0.0), outline="")

        # 语录正文
        self._lbl_quote = self.cv.create_text(
            cx, quote_y + 4, text="",
            font=FONTS["focus_quote"],
            fill=self._blend(COLORS["quote_text"], 0.0),
            anchor="center", width=int(sw * 0.65),
            justify="center")

        # 作者
        self._lbl_author = self.cv.create_text(
            cx, quote_y + 52, text="",
            font=FONTS["focus_author"],
            fill=self._blend(COLORS["quote_author"], 0.0),
            anchor="center")

        # ── 底部按钮 ──
        btn_frame = tk.Frame(self, bg=COLORS["focus_bg"])
        btn_frame.place(relx=1.0, rely=1.0, anchor="se", x=-24, y=-24)
        tk.Button(
            btn_frame, text="🖼  更换背景",
            font=FONTS["focus_hint"],
            bg=COLORS["focus_btn"], fg=COLORS["focus_dim"],
            activebackground="#444466", activeforeground="white",
            relief="flat", bd=0, padx=12, pady=6, cursor="hand2",
            command=self._change_bg_in_overlay
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            btn_frame, text="⏭  下一条语录",
            font=FONTS["focus_hint"],
            bg=COLORS["focus_btn"], fg=COLORS["focus_dim"],
            activebackground="#444466", activeforeground="white",
            relief="flat", bd=0, padx=12, pady=6, cursor="hand2",
            command=self._next_quote_manual
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            btn_frame, text="⏹  退出专注",
            font=FONTS["focus_hint"],
            bg=COLORS["focus_btn"], fg=COLORS["focus_dim"],
            activebackground=COLORS["focus_btn_h"],
            activeforeground="white",
            relief="flat", bd=0, padx=12, pady=6, cursor="hand2",
            command=self._try_exit
        ).pack(side="left")

        self.cv.create_text(
            cx, sh - 18,
            text="Esc 退出  |  ⏭ 下一条语录  |  🖼 更换背景",
            font=FONTS["focus_hint"],
            fill=self._blend(COLORS["focus_dim"], 0.6),
            anchor="center")

        self._update_display()

    # ── 背景 ─────────────────────────────────
    def _load_bg(self, sw, sh):
        path = self.master_app.bg_image_path
        if path and os.path.isfile(path):
            photo = _prepare_bg(path, sw, sh,
                                blur=self.master_app.bg_blur,
                                dim=self.master_app.bg_dim)
            if photo:
                self._bg_photo = photo
                self.cv.itemconfig(self._bg_img_id, image=photo)
                self.cv.configure(bg="#000000")
                return
        self._bg_photo = None
        self.cv.itemconfig(self._bg_img_id, image="")
        self.cv.configure(bg=COLORS["focus_bg"])

    def _change_bg_in_overlay(self):
        path = filedialog.askopenfilename(
            title="选择专注背景图片",
            filetypes=SUPPORTED_IMG, parent=self)
        if not path:
            return
        self.master_app.bg_image_path = path
        self.master_app._save_settings()
        if hasattr(self.master_app, "_bg_panel"):
            self.master_app._bg_panel._refresh_thumb()
        self._load_bg(self._sw, self._sh)

    # ── 颜色混合工具 ─────────────────────────
    @staticmethod
    def _blend(hex_color: str, alpha: float) -> str:
        """将颜色与专注模式背景色按 alpha 混合，模拟透明度。"""
        bg = (13, 13, 26)
        r  = int(hex_color[1:3], 16)
        g  = int(hex_color[3:5], 16)
        b  = int(hex_color[5:7], 16)
        nr = int(bg[0] + (r - bg[0]) * alpha)
        ng = int(bg[1] + (g - bg[1]) * alpha)
        nb = int(bg[2] + (b - bg[2]) * alpha)
        return f"#{nr:02x}{ng:02x}{nb:02x}"

    # ── 语录逻辑 ─────────────────────────────
    def _pick_quote(self) -> dict:
        pool = list(BUILTIN_QUOTES) + list(
            self.master_app.data.get("custom_quotes", []))
        if not pool:
            return {"text": "专注当下，成就未来。", "author": ""}
        if len(pool) > 1 and self._current_quote:
            pool = [q for q in pool
                    if q.get("text") != self._current_quote.get("text")] or pool
        return random.choice(pool)

    def _schedule_next_quote(self):
        if not self.winfo_exists():
            return
        interval_ms = self.master_app.quote_interval * 1000
        self._quote_job = self.after(interval_ms, self._auto_rotate_quote)

    def _auto_rotate_quote(self):
        if not self.winfo_exists():
            return
        if self.master_app.quotes_enabled:
            self._fade_out_then_in()
        self._schedule_next_quote()

    def _next_quote_manual(self):
        if self._quote_job:
            try:
                self.after_cancel(self._quote_job)
            except Exception:
                pass
        self._fade_out_then_in()
        self._schedule_next_quote()

    def _fade_out_then_in(self):
        self._fade_out_quote(
            callback=lambda: self._fade_in_quote(self._pick_quote()))

    def _fade_out_quote(self, step=0, callback=None):
        if not self.winfo_exists():
            return
        alpha = max(0.0, 1.0 - step / self.FADE_STEPS)
        self._set_quote_alpha(alpha)
        if step < self.FADE_STEPS:
            self.after(self.FADE_MS,
                       lambda: self._fade_out_quote(step + 1, callback))
        else:
            if callback:
                callback()

    def _fade_in_quote(self, quote: dict, step=0):
        if not self.winfo_exists():
            return
        if step == 0:
            self._current_quote = quote
            self._set_quote_text(quote)
        alpha = min(1.0, step / self.FADE_STEPS)
        self._set_quote_alpha(alpha)
        if step < self.FADE_STEPS:
            self.after(self.FADE_MS,
                       lambda: self._fade_in_quote(quote, step + 1))

    def _set_quote_text(self, quote: dict):
        self.cv.itemconfig(self._lbl_quote, text=quote.get("text", ""))
        author = quote.get("author", "")
        self.cv.itemconfig(
            self._lbl_author,
            text=f"—— {author}" if author else "")

    def _set_quote_alpha(self, alpha: float):
        self.cv.itemconfig(
            self._lbl_quote,
            fill=self._blend(COLORS["quote_text"], alpha))
        self.cv.itemconfig(
            self._lbl_author,
            fill=self._blend(COLORS["quote_author"], alpha * 0.85))
        self.cv.itemconfig(
            self._lbl_open_q,
            fill=self._blend(COLORS["focus_ring"], alpha * 0.55))
        self.cv.itemconfig(
            self._sep_line,
            fill=self._blend(COLORS["border"], alpha * 0.7))

    # ── 状态同步 ─────────────────────────────
    def _update_display(self):
        app       = self.master_app
        remaining = app.remaining
        total     = MODE_DURATIONS[app.mode]
        ratio     = remaining / total if total > 0 else 0

        mins, secs = divmod(remaining, 60)
        self.cv.itemconfig(self._lbl_time, text=f"{mins:02d}:{secs:02d}")

        color = MODE_COLORS[app.mode]
        self.cv.itemconfig(self._lbl_mode,
                           text=MODE_LABELS[app.mode], fill=color)
        self.cv.itemconfig(self._arc, outline=color)
        self.cv.itemconfig(
            self._arc,
            extent=(-360 * ratio if ratio > 0 else -0.001))

        task_text = "未选择任务"
        if app.current_task_id is not None:
            for t in app.data.get("tasks", []):
                if t["id"] == app.current_task_id:
                    task_text = f"📌  {t['name']}"
                    break
        self.cv.itemconfig(self._lbl_task, text=task_text)

        today_str = datetime.date.today().strftime("%Y年%m月%d日  %A")
        self.cv.itemconfig(self._lbl_date, text=today_str)
        count = app._today_pomodoro_count()
        self.cv.itemconfig(
            self._lbl_count,
            text=f"今日番茄  {'🍅' * min(count, 8)}  {count} 个")

        done_in_cycle = app.pomodoro_count % LONG_BREAK_INTERVAL
        for i, did in enumerate(self._dot_ids):
            self.cv.itemconfig(
                did,
                fill=color if i < done_in_cycle else COLORS["surface2"])

        if self.winfo_exists() and app.running:
            self.after(200, self._update_display)

    # ── 退出 ─────────────────────────────────
    def _try_exit(self):
        if messagebox.askyesno(
                "退出专注模式",
                "确定要退出专注模式吗？\n计时器将暂停，但进度不会丢失。",
                parent=self):
            self.master_app._exit_focus_mode(paused=True)

    def close_overlay(self):
        if self._quote_job:
            try:
                self.after_cancel(self._quote_job)
            except Exception:
                pass
        if self.winfo_exists():
            self.destroy()


# ─────────────────────────────────────────────
# 主应用
# ─────────────────────────────────────────────
class PomodoroApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🍅 番茄钟")
        self.configure(bg=COLORS["bg"])
        self.resizable(False, False)

        self.data = load_data()

        s = self.data.get("settings", {})
        self.bg_image_path:  str   = s.get("bg_image_path", "")
        self.bg_blur:        float = float(s.get("bg_blur", 0.0))
        self.bg_dim:         float = float(s.get("bg_dim", 0.45))
        self.quotes_enabled: bool  = bool(s.get("quotes_enabled", True))
        self.quote_interval: int   = int(s.get("quote_interval", QUOTE_INTERVAL))

        self.mode             = "work"
        self.remaining        = MODE_DURATIONS["work"]
        self.running          = False
        self._timer_thread    = None
        self._stop_event      = threading.Event()
        self.pomodoro_count   = 0
        self.current_task_id  = None
        self._focus_overlay   = None

        self._build_ui()
        self._refresh_task_list()
        self._refresh_summary()
        self._update_timer_display()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── 设置持久化 ───────────────────────────
    def _save_settings(self):
        self.data.setdefault("settings", {}).update({
            "bg_image_path":  self.bg_image_path,
            "bg_blur":        self.bg_blur,
            "bg_dim":         self.bg_dim,
            "quotes_enabled": self.quotes_enabled,
            "quote_interval": self.quote_interval,
        })
        save_data(self.data)

    # ── 构建主界面 ───────────────────────────
    def _build_ui(self):
        header = tk.Frame(self, bg=COLORS["bg"], pady=10)
        header.pack(fill="x", padx=20)
        tk.Label(header, text="🍅  番茄钟", font=FONTS["h1"],
                 bg=COLORS["bg"], fg=COLORS["primary"]).pack(side="left")
        tk.Label(header, text="专注 · 休息 · 成长",
                 font=FONTS["small"], bg=COLORS["bg"],
                 fg=COLORS["text_dim"]).pack(side="left", padx=12)

        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self._build_timer_panel(main)
        self._build_right_panel(main)

    def _build_timer_panel(self, parent):
        outer = tk.Frame(parent, bg=COLORS["surface"], bd=0,
                         highlightthickness=1,
                         highlightbackground=COLORS["border"])
        outer.pack(side="left", fill="y", padx=(0, 12))

        canvas = tk.Canvas(outer, bg=COLORS["surface"],
                           highlightthickness=0, width=300)
        vsb = ttk.Scrollbar(outer, orient="vertical",
                            command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        panel = tk.Frame(canvas, bg=COLORS["surface"])
        panel_id = canvas.create_window((0, 0), window=panel, anchor="nw")

        def _on_frame_cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas_cfg(e):
            canvas.itemconfig(panel_id, width=e.width)

        panel.bind("<Configure>", _on_frame_cfg)
        canvas.bind("<Configure>", _on_canvas_cfg)
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(
                        int(-1 * (e.delta / 120)), "units"))

        inner = tk.Frame(panel, bg=COLORS["surface"], padx=16, pady=16)
        inner.pack(fill="both", expand=True)

        # 模式切换
        mode_bar = tk.Frame(inner, bg=COLORS["surface"])
        mode_bar.pack(pady=(0, 14))
        self._mode_btns = {}
        for m, label in MODE_LABELS.items():
            btn = tk.Button(
                mode_bar, text=label, font=FONTS["small"],
                bg=COLORS["surface2"], fg=COLORS["text_dim"],
                activebackground=MODE_COLORS[m],
                activeforeground=COLORS["bg"],
                relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
                command=lambda mode=m: self._switch_mode(mode))
            btn.pack(side="left", padx=3)
            self._mode_btns[m] = btn
        self._highlight_mode_btn()

        # 圆环
        self.canvas = tk.Canvas(inner, width=250, height=250,
                                bg=COLORS["surface"], highlightthickness=0)
        self.canvas.pack()
        self._draw_timer_ring()

        # 当前任务
        self.current_task_label = tk.Label(
            inner, text="未选择任务", font=FONTS["small"],
            bg=COLORS["surface"], fg=COLORS["text_dim"], wraplength=210)
        self.current_task_label.pack(pady=(6, 0))

        # 控制按钮
        ctrl = tk.Frame(inner, bg=COLORS["surface"])
        ctrl.pack(pady=8)
        self.btn_start = tk.Button(
            ctrl, text="▶  开始", font=FONTS["h2"],
            bg=COLORS["primary"], fg="white",
            activebackground=COLORS["accent"], activeforeground="white",
            relief="flat", bd=0, padx=20, pady=8, cursor="hand2",
            command=self._toggle_timer)
        self.btn_start.pack(side="left", padx=4)
        tk.Button(
            ctrl, text="↺  重置", font=FONTS["body"],
            bg=COLORS["surface2"], fg=COLORS["text_dim"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            relief="flat", bd=0, padx=12, pady=8, cursor="hand2",
            command=self._reset_timer).pack(side="left", padx=4)

        # 专注模式按钮
        self.btn_focus = tk.Button(
            inner, text="🎯  进入专注模式", font=FONTS["body"],
            bg=COLORS["surface2"], fg=COLORS["warning"],
            activebackground=COLORS["primary"], activeforeground="white",
            relief="flat", bd=0, padx=16, pady=6, cursor="hand2",
            command=self._enter_focus_mode)
        self.btn_focus.pack(pady=(0, 4))

        # 今日番茄数
        self.pomodoro_count_label = tk.Label(
            inner, text="今日番茄：0 🍅", font=FONTS["body"],
            bg=COLORS["surface"], fg=COLORS["warning"])
        self.pomodoro_count_label.pack(pady=(0, 8))

        # 背景设置面板
        self._bg_panel = BgSettingsPanel(inner, self)
        self._bg_panel.pack(fill="x", pady=(0, 8))

        # 语录管理面板
        self._quote_panel = QuoteManagerPanel(inner, self)
        self._quote_panel.pack(fill="x")

    def _build_right_panel(self, parent):
        right = tk.Frame(parent, bg=COLORS["bg"])
        right.pack(side="left", fill="both", expand=True)

        task_header = tk.Frame(right, bg=COLORS["bg"])
        task_header.pack(fill="x", pady=(0, 6))
        tk.Label(task_header, text="📋  任务列表", font=FONTS["h2"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        tk.Button(
            task_header, text="＋ 添加", font=FONTS["small"],
            bg=COLORS["primary"], fg="white",
            activebackground=COLORS["accent"], activeforeground="white",
            relief="flat", bd=0, padx=10, pady=3, cursor="hand2",
            command=self._add_task).pack(side="right")

        list_frame = tk.Frame(right, bg=COLORS["surface"],
                              highlightthickness=1,
                              highlightbackground=COLORS["border"])
        list_frame.pack(fill="both", expand=True, pady=(0, 12))

        self.task_canvas = tk.Canvas(list_frame, bg=COLORS["surface"],
                                     highlightthickness=0, width=320)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                  command=self.task_canvas.yview)
        self.task_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.task_canvas.pack(side="left", fill="both", expand=True)

        self.task_inner = tk.Frame(self.task_canvas, bg=COLORS["surface"])
        self.task_inner_id = self.task_canvas.create_window(
            (0, 0), window=self.task_inner, anchor="nw")
        self.task_inner.bind("<Configure>", self._on_task_frame_configure)
        self.task_canvas.bind("<Configure>", self._on_task_canvas_configure)
        self.task_canvas.bind(
            "<MouseWheel>",
            lambda e: self.task_canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"))

        summary_header = tk.Frame(right, bg=COLORS["bg"])
        summary_header.pack(fill="x", pady=(0, 6))
        tk.Label(summary_header, text="📊  今日进度汇总",
                 font=FONTS["h2"], bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(side="left")

        self.summary_frame = tk.Frame(
            right, bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=14, pady=10)
        self.summary_frame.pack(fill="x")

    # ── 专注模式 ─────────────────────────────
    def _enter_focus_mode(self):
        if self._focus_overlay and self._focus_overlay.winfo_exists():
            self._focus_overlay.lift()
            return
        if not self.running:
            self._start_timer()
            self.btn_start.config(text="⏸  暂停")
        self._focus_overlay = FocusOverlay(self)
        self._focus_overlay.grab_set()
        self.btn_focus.config(text="🎯  专注中…", state="disabled")

    def _exit_focus_mode(self, paused=False):
        if self._focus_overlay:
            try:
                self._focus_overlay.grab_release()
                self._focus_overlay.close_overlay()
            except Exception:
                pass
            self._focus_overlay = None
        self.btn_focus.config(text="🎯  进入专注模式", state="normal")
        if paused:
            self._stop_timer()
            self.btn_start.config(text="▶  开始")
        self.lift()
        self.focus_force()

    # ── 圆环绘制 ─────────────────────────────
    def _draw_timer_ring(self):
        self.canvas.delete("all")
        cx, cy, r = 125, 125, 105
        color = MODE_COLORS[self.mode]
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                outline=COLORS["surface2"], width=12)
        total = MODE_DURATIONS[self.mode]
        ratio = self.remaining / total if total > 0 else 0
        if ratio > 0:
            self.canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=90, extent=-360 * ratio,
                outline=color, width=12, style="arc")
        mins, secs = divmod(self.remaining, 60)
        self.canvas.create_text(cx, cy - 10,
                                text=f"{mins:02d}:{secs:02d}",
                                font=FONTS["timer"], fill=COLORS["text"])
        self.canvas.create_text(cx, cy + 42,
                                text=MODE_LABELS[self.mode],
                                font=FONTS["body"], fill=color)

    # ── 模式切换 ─────────────────────────────
    def _switch_mode(self, mode: str):
        if self.running:
            if not messagebox.askyesno(
                    "切换模式", "计时器正在运行，确定要切换模式并重置吗？"):
                return
        self._stop_timer()
        self.mode      = mode
        self.remaining = MODE_DURATIONS[mode]
        self._highlight_mode_btn()
        self._update_timer_display()
        self.btn_start.config(text="▶  开始")

    def _highlight_mode_btn(self):
        for m, btn in self._mode_btns.items():
            if m == self.mode:
                btn.config(bg=MODE_COLORS[m], fg=COLORS["bg"])
            else:
                btn.config(bg=COLORS["surface2"], fg=COLORS["text_dim"])

    # ── 计时器控制 ───────────────────────────
    def _toggle_timer(self):
        if self.running:
            self._stop_timer()
            self.btn_start.config(text="▶  开始")
        else:
            self._start_timer()
            self.btn_start.config(text="⏸  暂停")

    def _start_timer(self):
        self.running = True
        self._stop_event.clear()
        self._timer_thread = threading.Thread(
            target=self._run_timer, daemon=True)
        self._timer_thread.start()

    def _stop_timer(self):
        self.running = False
        self._stop_event.set()

    def _reset_timer(self):
        self._stop_timer()
        self.remaining = MODE_DURATIONS[self.mode]
        self.btn_start.config(text="▶  开始")
        self._update_timer_display()

    def _run_timer(self):
        while self.remaining > 0 and not self._stop_event.is_set():
            self._stop_event.wait(1)
            if not self._stop_event.is_set():
                self.remaining -= 1
                self.after(0, self._update_timer_display)
        if not self._stop_event.is_set() and self.remaining == 0:
            self.after(0, self._on_timer_complete)

    def _on_timer_complete(self):
        self.running = False
        self.btn_start.config(text="▶  开始")
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass
        if self._focus_overlay and self._focus_overlay.winfo_exists():
            self._exit_focus_mode(paused=False)
        if self.mode == "work":
            self.pomodoro_count += 1
            self._log_pomodoro()
            self._refresh_summary()
            self.pomodoro_count_label.config(
                text=f"今日番茄：{self._today_pomodoro_count()} 🍅")
            messagebox.showinfo(
                "🍅 专注完成！",
                f"太棒了！完成第 {self.pomodoro_count} 个番茄！\n"
                f"累计今日：{self._today_pomodoro_count()} 个\n\n"
                f"接下来去休息一下吧 ☕")
            if self.pomodoro_count % LONG_BREAK_INTERVAL == 0:
                self._switch_mode("long_break")
            else:
                self._switch_mode("short_break")
        else:
            messagebox.showinfo("☕ 休息结束！",
                                "休息时间到，准备好开始下一个番茄了吗？")
            self._switch_mode("work")

    def _update_timer_display(self):
        self._draw_timer_ring()

    # ── 番茄日志 ─────────────────────────────
    def _today_key(self) -> str:
        return datetime.date.today().isoformat()

    def _log_pomodoro(self):
        key = self._today_key()
        log = self.data.setdefault("daily_log", {})
        day = log.setdefault(key, {
            "pomodoros": 0, "tasks_done": 0, "focus_minutes": 0})
        day["pomodoros"]     += 1
        day["focus_minutes"] += WORK_MIN
        if self.current_task_id is not None:
            for t in self.data["tasks"]:
                if t["id"] == self.current_task_id:
                    t["pomodoros"] = t.get("pomodoros", 0) + 1
                    break
        save_data(self.data)

    def _today_pomodoro_count(self) -> int:
        return self.data.get("daily_log", {}).get(
            self._today_key(), {}).get("pomodoros", 0)

    # ── 任务列表 ─────────────────────────────
    def _add_task(self):
        name = simpledialog.askstring(
            "添加任务", "请输入任务名称：", parent=self)
        if not name or not name.strip():
            return
        task = {
            "id":        len(self.data["tasks"]) + 1,
            "name":      name.strip(),
            "done":      False,
            "pomodoros": 0,
            "created":   datetime.datetime.now().isoformat(),
        }
        self.data["tasks"].append(task)
        save_data(self.data)
        self._refresh_task_list()

    def _toggle_task_done(self, task_id: int):
        for t in self.data["tasks"]:
            if t["id"] == task_id:
                t["done"] = not t["done"]
                if t["done"]:
                    key = self._today_key()
                    day = self.data.setdefault(
                        "daily_log", {}).setdefault(key, {
                        "pomodoros": 0, "tasks_done": 0,
                        "focus_minutes": 0})
                    day["tasks_done"] = day.get("tasks_done", 0) + 1
                break
        save_data(self.data)
        self._refresh_task_list()
        self._refresh_summary()

    def _delete_task(self, task_id: int):
        self.data["tasks"] = [
            t for t in self.data["tasks"] if t["id"] != task_id]
        if self.current_task_id == task_id:
            self.current_task_id = None
            self.current_task_label.config(text="未选择任务")
        save_data(self.data)
        self._refresh_task_list()

    def _select_task(self, task_id: int):
        for t in self.data["tasks"]:
            if t["id"] == task_id:
                self.current_task_id = task_id
                self.current_task_label.config(
                    text=f"当前任务：{t['name']}")
                break
        self._refresh_task_list()

    def _refresh_task_list(self):
        for w in self.task_inner.winfo_children():
            w.destroy()
        tasks = self.data.get("tasks", [])
        if not tasks:
            tk.Label(self.task_inner,
                     text="暂无任务，点击「＋ 添加」开始",
                     font=FONTS["small"], bg=COLORS["surface"],
                     fg=COLORS["text_dim"]).pack(pady=20)
            return
        pending = [t for t in tasks if not t.get("done")]
        done    = [t for t in tasks if t.get("done")]
        for t in pending + done:
            self._render_task_row(t)

    def _render_task_row(self, task: dict):
        is_done    = task.get("done", False)
        is_current = task["id"] == self.current_task_id
        row_bg = (COLORS["done_bg"] if is_done else
                  COLORS["surface2"] if is_current else COLORS["surface"])
        row_fg = COLORS["done_fg"] if is_done else COLORS["text"]

        row = tk.Frame(self.task_inner, bg=row_bg, pady=6, padx=10,
                       highlightthickness=1 if is_current else 0,
                       highlightbackground=COLORS["primary"])
        row.pack(fill="x", padx=6, pady=2)

        check = tk.Label(row, text="✅" if is_done else "⬜",
                         font=FONTS["body"], bg=row_bg, cursor="hand2")
        check.pack(side="left", padx=(0, 6))
        check.bind("<Button-1>",
                   lambda e, tid=task["id"]: self._toggle_task_done(tid))

        name_font = ("Segoe UI", 11, "overstrike") if is_done else FONTS["body"]
        name_label = tk.Label(row, text=task["name"], font=name_font,
                               bg=row_bg, fg=row_fg, anchor="w",
                               cursor="hand2")
        name_label.pack(side="left", fill="x", expand=True)
        name_label.bind("<Button-1>",
                        lambda e, tid=task["id"]: self._select_task(tid))

        if task.get("pomodoros", 0) > 0:
            tk.Label(row, text=f"🍅×{task['pomodoros']}",
                     font=FONTS["small"], bg=row_bg,
                     fg=COLORS["warning"]).pack(side="left", padx=4)

        del_btn = tk.Label(row, text="✕", font=FONTS["small"],
                           bg=row_bg, fg=COLORS["text_dim"], cursor="hand2")
        del_btn.pack(side="right", padx=4)
        del_btn.bind("<Button-1>",
                     lambda e, tid=task["id"]: self._delete_task(tid))

    def _on_task_frame_configure(self, event):
        self.task_canvas.configure(
            scrollregion=self.task_canvas.bbox("all"))

    def _on_task_canvas_configure(self, event):
        self.task_canvas.itemconfig(
            self.task_inner_id, width=event.width)

    # ── 每日进度汇总 ─────────────────────────
    def _refresh_summary(self):
        for w in self.summary_frame.winfo_children():
            w.destroy()
        key           = self._today_key()
        day           = self.data.get("daily_log", {}).get(key, {})
        pomodoros     = day.get("pomodoros", 0)
        tasks_done    = day.get("tasks_done", 0)
        focus_min     = day.get("focus_minutes", 0)
        pending_tasks = len([t for t in self.data.get("tasks", [])
                             if not t.get("done")])
        total_tasks   = len(self.data.get("tasks", []))

        today_str = datetime.date.today().strftime("%Y年%m月%d日")
        tk.Label(self.summary_frame, text=f"📅  {today_str}",
                 font=FONTS["small"], bg=COLORS["surface"],
                 fg=COLORS["text_dim"]).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        stats = [
            ("🍅", "完成番茄",  str(pomodoros),     COLORS["primary"]),
            ("⏱",  "专注时长",  f"{focus_min} 分钟", COLORS["warning"]),
            ("✅", "完成任务",  str(tasks_done),    COLORS["success"]),
            ("📌", "待办任务",  str(pending_tasks), COLORS["short_break"]),
        ]
        for col, (icon, label, value, color) in enumerate(stats):
            card = tk.Frame(self.summary_frame, bg=COLORS["surface2"],
                            padx=10, pady=8,
                            highlightthickness=1,
                            highlightbackground=COLORS["border"])
            card.grid(row=1, column=col, padx=4, sticky="nsew")
            self.summary_frame.columnconfigure(col, weight=1)
            tk.Label(card, text=icon, font=("Segoe UI", 18),
                     bg=COLORS["surface2"]).pack()
            tk.Label(card, text=value, font=FONTS["h2"],
                     bg=COLORS["surface2"], fg=color).pack()
            tk.Label(card, text=label, font=FONTS["small"],
                     bg=COLORS["surface2"],
                     fg=COLORS["text_dim"]).pack()

        if total_tasks > 0:
            done_ratio = (total_tasks - pending_tasks) / total_tasks
            bar_frame = tk.Frame(self.summary_frame, bg=COLORS["surface"])
            bar_frame.grid(row=2, column=0, columnspan=4,
                           sticky="ew", pady=(10, 0))
            tk.Label(bar_frame,
                     text=f"任务完成率  {int(done_ratio * 100)}%",
                     font=FONTS["small"], bg=COLORS["surface"],
                     fg=COLORS["text_dim"]).pack(anchor="w")
            bar_bg = tk.Frame(bar_frame, bg=COLORS["surface2"], height=8)
            bar_bg.pack(fill="x", pady=3)
            bar_bg.update_idletasks()
            fill_w = max(4, int(bar_bg.winfo_width() * done_ratio))
            tk.Frame(bar_bg, bg=COLORS["success"], height=8,
                     width=fill_w).place(x=0, y=0)

        history = self._get_week_history()
        if any(v > 0 for v in history.values()):
            hist_frame = tk.Frame(self.summary_frame, bg=COLORS["surface"])
            hist_frame.grid(row=3, column=0, columnspan=4,
                            sticky="ew", pady=(10, 0))
            tk.Label(hist_frame, text="近 7 日番茄",
                     font=FONTS["small"], bg=COLORS["surface"],
                     fg=COLORS["text_dim"]).pack(anchor="w")
            bar_row = tk.Frame(hist_frame, bg=COLORS["surface"])
            bar_row.pack(fill="x", pady=4)
            max_val = max(history.values()) or 1
            for date_str, count in history.items():
                col_frame = tk.Frame(bar_row, bg=COLORS["surface"])
                col_frame.pack(side="left", expand=True, fill="x", padx=2)
                bar_h = max(4, int(60 * count / max_val))
                tk.Frame(col_frame, bg=COLORS["surface"],
                         height=60 - bar_h).pack()
                bar_color = (COLORS["primary"]
                             if date_str == key else COLORS["surface2"])
                tk.Frame(col_frame, bg=bar_color,
                         height=bar_h).pack(fill="x")
                day_label = datetime.date.fromisoformat(
                    date_str).strftime("%d")
                tk.Label(col_frame, text=day_label, font=FONTS["small"],
                         bg=COLORS["surface"],
                         fg=(COLORS["primary"]
                             if date_str == key
                             else COLORS["text_dim"])).pack()

    def _get_week_history(self) -> dict:
        result = {}
        today  = datetime.date.today()
        log    = self.data.get("daily_log", {})
        for i in range(6, -1, -1):
            d = (today - datetime.timedelta(days=i)).isoformat()
            result[d] = log.get(d, {}).get("pomodoros", 0)
        return result

    # ── 关闭 ─────────────────────────────────
    def _on_close(self):
        if self._focus_overlay and self._focus_overlay.winfo_exists():
            if not messagebox.askyesno(
                    "退出", "专注模式正在运行，确定要退出吗？"):
                return
        self._stop_timer()
        save_data(self.data)
        self.destroy()


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = PomodoroApp()
    app.update_idletasks()
    w, h = 960, 680
    sw   = app.winfo_screenwidth()
    sh   = app.winfo_screenheight()
    app.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
    app.mainloop()
