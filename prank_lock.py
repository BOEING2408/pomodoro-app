"""
🍅 番茄钟 - 整蛊专注锁屏版
开机自启 → 全屏锁定 → 唯一出口：输入 OMG 解锁
"""
import tkinter as tk
from tkinter import font as tkfont
import ctypes
import sys
import os
import time
import threading
import winreg
import subprocess

# ─── Windows API ────────────────────────────────────────────
user32   = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_LWIN   = 0x5B
VK_RWIN   = 0x5C
VK_DELETE = 0x2E
VK_F4     = 0x73
VK_ESCAPE = 0x1B
VK_TAB    = 0x09
VK_F1     = 0x70
VK_MENU   = 0x12   # Alt

WH_KEYBOARD_LL = 13
WM_KEYDOWN     = 0x0100
WM_SYSKEYDOWN  = 0x0104

BLOCKED_KEYS = {VK_LWIN, VK_RWIN, VK_ESCAPE, VK_F4, VK_TAB}

# ─── 低级键盘钩子 ─────────────────────────────────────────────
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p))

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
        kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        vk = kb.vkCode
        # 拦截 Win键、Esc、Alt+F4、Ctrl+Alt+Del(部分)、Alt+Tab
        if vk in BLOCKED_KEYS:
            return 1
        # 拦截 Alt+F4
        if vk == VK_F4 and (user32.GetAsyncKeyState(VK_MENU) & 0x8000):
            return 1
        # 拦截 Alt+Tab
        if vk == VK_TAB and (user32.GetAsyncKeyState(VK_MENU) & 0x8000):
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
APP_NAME  = "PomodoroFocusLock"
EXE_PATH  = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
SCRIPT    = f'"{sys.executable}" "{os.path.abspath(__file__)}"' if not getattr(sys, 'frozen', False) else f'"{EXE_PATH}"'

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

# ─── 主界面 ───────────────────────────────────────────────────
励志语录 = [
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

class PrankLockApp:
    def __init__(self):
        self.root = tk.Tk()
        self._setup_window()
        self._build_ui()
        self._start_guardian()
        self._start_quote_rotation()

    # ── 窗口设置 ──────────────────────────────────────────────
    def _setup_window(self):
        root = self.root
        root.title("🍅 专注模式 — 锁定中")
        root.configure(bg="#0d1117")

        # 全屏
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"{sw}x{sh}+0+0")
        root.resizable(False, False)

        # 置顶 + 无边框
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-fullscreen", True)

        # 拦截所有关闭/退出事件
        root.protocol("WM_DELETE_WINDOW", lambda: None)
        root.bind("<Alt-F4>",   lambda e: "break")
        root.bind("<Escape>",   lambda e: "break")
        root.bind("<Alt-Tab>",  lambda e: "break")
        root.bind("<Control-Alt-Delete>", lambda e: "break")
        root.bind("<Super_L>",  lambda e: "break")
        root.bind("<Super_R>",  lambda e: "break")

    # ── 构建 UI ───────────────────────────────────────────────
    def _build_ui(self):
        root = self.root
        sw   = root.winfo_screenwidth()
        sh   = root.winfo_screenheight()
        BG   = "#0d1117"
        RED  = "#ff4757"
        WHITE= "#f0f6fc"
        GRAY = "#8b949e"
        DIM  = "#21262d"

        # ── 顶部标题 ──
        tk.Label(root, text="🍅  专 注 模 式  🍅",
                 font=("Microsoft YaHei", 28, "bold"),
                 fg=RED, bg=BG).place(relx=0.5, rely=0.06, anchor="center")

        tk.Label(root, text="你正处于深度专注状态，请保持专注直到完成目标",
                 font=("Microsoft YaHei", 13),
                 fg=GRAY, bg=BG).place(relx=0.5, rely=0.11, anchor="center")

        # ── 大番茄图标（Canvas 圆形） ──
        canvas_size = min(sw, sh) // 3
        self.canvas = tk.Canvas(root, width=canvas_size, height=canvas_size,
                                bg=BG, highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.38, anchor="center")
        r = canvas_size // 2
        pad = canvas_size // 12
        # 外圈光晕
        self.canvas.create_oval(pad//2, pad//2, canvas_size-pad//2, canvas_size-pad//2,
                                fill="", outline=RED, width=2)
        # 番茄主体
        self.canvas.create_oval(pad, pad, canvas_size-pad, canvas_size-pad,
                                fill="#1a0505", outline=RED, width=3)
        # 叶子
        lw = canvas_size // 5
        lh = canvas_size // 6
        cx = canvas_size // 2
        top = pad - canvas_size // 14
        self.canvas.create_polygon(
            cx, top, cx-lw//2, top+lh, cx+lw//2, top+lh,
            fill="#2ea043", outline=""
        )
        # 中央文字
        self.canvas.create_text(r, r, text="专\n注",
                                font=("Microsoft YaHei", canvas_size//6, "bold"),
                                fill=RED)

        # ── 时钟（实时） ──
        self.clock_var = tk.StringVar()
        tk.Label(root, textvariable=self.clock_var,
                 font=("Consolas", 18), fg=GRAY, bg=BG
                 ).place(relx=0.5, rely=0.62, anchor="center")
        self._update_clock()

        # ── 励志语录 ──
        self.quote_var = tk.StringVar(value=励志语录[0])
        self.quote_lbl = tk.Label(root, textvariable=self.quote_var,
                                  font=("Microsoft YaHei", 14, "italic"),
                                  fg="#58a6ff", bg=BG, wraplength=int(sw*0.7))
        self.quote_lbl.place(relx=0.5, rely=0.70, anchor="center")
        self._quote_idx = 0

        # ── 解锁区域 ──
        unlock_frame = tk.Frame(root, bg=DIM, bd=0)
        unlock_frame.place(relx=0.5, rely=0.83, anchor="center")

        tk.Label(unlock_frame, text="🔐  输入解锁密码：",
                 font=("Microsoft YaHei", 12), fg=GRAY, bg=DIM
                 ).pack(side="left", padx=(16, 8), pady=12)

        self.pwd_var = tk.StringVar()
        self.entry = tk.Entry(
            unlock_frame,
            textvariable=self.pwd_var,
            font=("Consolas", 16, "bold"),
            width=8,
            bg="#161b22", fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            bd=0,
            justify="center"
        )
        self.entry.pack(side="left", padx=4, pady=12, ipady=6)

        self.unlock_btn = tk.Button(
            unlock_frame,
            text="解锁",
            font=("Microsoft YaHei", 12, "bold"),
            bg=RED, fg=WHITE,
            activebackground="#ff6b81",
            relief="flat", bd=0,
            padx=16, pady=6,
            cursor="hand2",
            command=self._try_unlock
        )
        self.unlock_btn.pack(side="left", padx=(4, 16), pady=12)

        self.hint_var = tk.StringVar()
        tk.Label(root, textvariable=self.hint_var,
                 font=("Microsoft YaHei", 11),
                 fg="#f85149", bg=BG).place(relx=0.5, rely=0.90, anchor="center")

        # 绑定回车键
        self.entry.bind("<Return>", lambda e: self._try_unlock())
        # 让输入框始终获得焦点
        self.entry.focus_set()
        root.after(200, self.entry.focus_force)

        # ── 底部提示 ──
        tk.Label(root,
                 text="© 番茄钟专注系统  |  保持专注，拒绝分心",
                 font=("Microsoft YaHei", 9),
                 fg="#30363d", bg=BG
                 ).place(relx=0.5, rely=0.97, anchor="center")

    # ── 实时时钟 ──────────────────────────────────────────────
    def _update_clock(self):
        now = time.strftime("📅 %Y年%m月%d日   🕐 %H:%M:%S")
        self.clock_var.set(now)
        self.root.after(1000, self._update_clock)

    # ── 语录轮换 ──────────────────────────────────────────────
    def _start_quote_rotation(self):
        def rotate():
            self._quote_idx = (self._quote_idx + 1) % len(励志语录)
            self.quote_var.set(励志语录[self._quote_idx])
            self.root.after(8000, rotate)
        self.root.after(8000, rotate)

    # ── 守护线程：持续置顶、抢焦点 ──────────────────────────────
    def _start_guardian(self):
        def guard():
            while self._running:
                try:
                    hwnd = self.root.winfo_id()
                    # 强制置顶
                    user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
                    # 抢夺焦点
                    user32.SetForegroundWindow(hwnd)
                    # 禁用任务管理器（需管理员权限，失败则跳过）
                    try:
                        import winreg as wr
                        k = wr.OpenKey(wr.HKEY_CURRENT_USER,
                                       r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                                       0, wr.KEY_SET_VALUE | wr.KEY_CREATE_SUB_KEY)
                        wr.SetValueEx(k, "DisableTaskMgr", 0, wr.REG_DWORD, 1)
                        wr.CloseKey(k)
                    except Exception:
                        pass
                except Exception:
                    pass
                time.sleep(0.3)
        self._running = True
        t = threading.Thread(target=guard, daemon=True)
        t.start()

    # ── 解锁逻辑 ──────────────────────────────────────────────
    def _try_unlock(self):
        pwd = self.pwd_var.get().strip()
        if pwd == "OMG":
            self._unlock()
        else:
            self.hint_var.set(f"❌  密码错误！提示：三个大写字母")
            self.pwd_var.set("")
            self.entry.focus_force()
            # 抖动效果
            self._shake()

    def _shake(self):
        root = self.root
        x0 = root.winfo_x()
        y0 = root.winfo_y()
        for dx in [10, -10, 8, -8, 5, -5, 0]:
            root.geometry(f"+{x0+dx}+{y0}")
            root.update()
            time.sleep(0.03)

    def _unlock(self):
        self._running = False
        uninstall_hook()
        remove_startup()
        # 恢复任务管理器
        try:
            import winreg as wr
            k = wr.OpenKey(wr.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                           0, wr.KEY_SET_VALUE)
            wr.DeleteValue(k, "DisableTaskMgr")
            wr.CloseKey(k)
        except Exception:
            pass
        self.root.destroy()

    # ── 启动 ──────────────────────────────────────────────────
    def run(self):
        install_hook()
        add_startup()
        # 消息循环（键盘钩子需要）
        def pump_messages():
            msg = ctypes.wintypes.MSG()
            while self._running:
                if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
                time.sleep(0.01)
        t = threading.Thread(target=pump_messages, daemon=True)
        t.start()
        self.root.mainloop()


if __name__ == "__main__":
    # 请求管理员权限（提升后重启）
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            " ".join(f'"{a}"' for a in sys.argv),
            None, 1
        )
        sys.exit()

    app = PrankLockApp()
    app.run()
