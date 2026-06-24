"""
●'◡'● Lunara — Circle Desktop Pet + Dịch thuật
- Bôi đen text bất kỳ → Lunara dịch sang tiếng Việt
- Ném, nảy, squash/stretch
- Double-click đổi mood, chuột phải menu

Yêu cầu:
  pip install pyperclip anthropic

Chạy: python circle_pet.py
"""
import tkinter as tk
import random, time, math, threading
import subprocess, sys

# ── Auto-install dependencies ─────────────────────────────────────────────────
def ensure(pkg, import_name=None):
    try:
        __import__(import_name or pkg)
    except ImportError:
        print(f"Cài {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

ensure("pyperclip")
ensure("anthropic")

import pyperclip
import anthropic

# ── Config ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = "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"   # ← dán API key vào đây
                                           # Lấy tại: https://console.anthropic.com

SIZE      = 80
FPS       = 60
GRAVITY   = 0.55
BOUNCE    = 0.75
FRICTION  = 0.985

MOODS = [
    ("●'◡'●", "#FF9EC4", "#e0608a"),
    ("●'▽'●", "#A8D8EA", "#4a9abf"),
    ("●'ᴗ'●", "#B5EAD7", "#3aaa80"),
    ("●'_'●", "#FFD9A0", "#e09030"),
    ("●'◕'●", "#D4A8FF", "#8844cc"),
]
SAYS = ["Wheee~!", "Boing!", "Yay!", "Hehe~", "✨", "♪"]

# ── Translation popup ──────────────────────────────────────────────────────────
class TranslatePopup:
    def __init__(self, root, x, y, col):
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.config(bg="#1a0a2e")

        # Frame viền
        frame = tk.Frame(self.win, bg=col, padx=2, pady=2)
        frame.pack()

        inner = tk.Frame(frame, bg="#1a0a2e", padx=14, pady=10)
        inner.pack()

        # Header
        hdr = tk.Frame(inner, bg="#1a0a2e")
        hdr.pack(fill="x")
        tk.Label(hdr, text="🌸 Lunara dịch", font=("Segoe UI", 9, "bold"),
                 bg="#1a0a2e", fg=col).pack(side="left")
        tk.Button(hdr, text="✕", font=("Segoe UI", 8), bg="#1a0a2e", fg="#aaaaaa",
                  relief="flat", cursor="hand2",
                  command=self.win.destroy).pack(side="right")

        # Text area
        self.txt = tk.Text(inner, width=38, height=5,
                           font=("Segoe UI", 10), bg="#0d0520", fg="#f0e6ff",
                           relief="flat", wrap="word", padx=8, pady=6,
                           state="disabled", cursor="arrow",
                           insertbackground="white")
        self.txt.pack(pady=(6,0))

        # Copy button
        self.copy_btn = tk.Button(inner, text="📋 Copy", font=("Segoe UI", 8),
                                  bg="#2d0850", fg="white", relief="flat",
                                  cursor="hand2", padx=8, pady=3,
                                  command=self._copy)
        self.copy_btn.pack(anchor="e", pady=(4,0))

        self._result = ""

        # Position — avoid going off screen
        self.win.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        wx = min(x, sw - 340)
        wy = min(y, sh - 200)
        self.win.geometry(f"+{wx}+{wy}")

        # Drag popup
        self.win.bind("<ButtonPress-1>",  self._dp)
        self.win.bind("<B1-Motion>",      self._dm)

    def set_text(self, txt):
        self._result = txt
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.insert("end", txt)
        self.txt.config(state="disabled")
        # Auto-resize height
        lines = txt.count("\n") + 1
        h = min(max(lines, 3), 10)
        self.txt.config(height=h)

    def _copy(self):
        if self._result:
            pyperclip.copy(self._result)
            self.copy_btn.config(text="✓ Đã copy!")
            self.win.after(1500, lambda: self.copy_btn.config(text="📋 Copy"))

    def _dp(self, e): self._ox=e.x_root; self._oy=e.y_root
    def _dm(self, e):
        x=self.win.winfo_x()+(e.x_root-self._ox)
        y=self.win.winfo_y()+(e.y_root-self._oy)
        self.win.geometry(f"+{x}+{y}")
        self._ox=e.x_root; self._oy=e.y_root


# ── Main Pet ──────────────────────────────────────────────────────────────────
class CirclePet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "#010101")
        self.root.config(bg="#010101")

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

        self.x  = float(self.sw // 2)
        self.y  = float(self.sh - SIZE - 100)
        self.vx = 3.0
        self.vy = 0.0
        self.sq = 1.0
        self.st = 1.0

        self.mood_idx = 0
        self.face, self.col, self.dark = MOODS[0]

        self.bubble     = None
        self.bubble_tid = None
        self.translating = False     # đang dịch
        self._last_clip  = ""        # clipboard trước đó
        self._popup      = None      # cửa sổ dịch hiện tại

        self._dragging  = False
        self._drag_hist = []

        W = SIZE + 80; H = SIZE + 70
        self.W = W; self.H = H
        self.root.geometry(f"{W}x{H}+{int(self.x)}+{int(self.y)}")

        self.cv = tk.Canvas(self.root, width=W, height=H,
                            bg="#010101", highlightthickness=0)
        self.cv.pack()

        self.cv.bind("<ButtonPress-1>",   self._press)
        self.cv.bind("<B1-Motion>",       self._drag_move)
        self.cv.bind("<ButtonRelease-1>", self._release)
        self.cv.bind("<Double-Button-1>", self._dbl)
        self.cv.bind("<Button-3>",        self._rmenu)

        # Poll clipboard mỗi 600ms để phát hiện text bôi đen
        self._poll_clipboard()
        self._tick()

    # ── Clipboard polling ────────────────────────────────────────────────────
    def _poll_clipboard(self):
        try:
            clip = pyperclip.paste()
            if (clip and clip != self._last_clip
                    and len(clip.strip()) > 1
                    and not self.translating):
                self._last_clip = clip
                self._do_translate(clip.strip())
        except Exception:
            pass
        self.root.after(600, self._poll_clipboard)

    def _do_translate(self, text):
        # Giới hạn độ dài
        if len(text) > 2000:
            text = text[:2000] + "…"

        # Chỉ dịch nếu không phải tiếng Việt thuần
        self.translating = True
        self._say("Đang dịch...")

        # Tạo popup loading
        px = int(self.x) + self.W + 10
        py = int(self.y)
        if self._popup and self._popup.win.winfo_exists():
            self._popup.win.destroy()
        popup = TranslatePopup(self.root, px, py, self.col)
        popup.set_text("⏳ Đang dịch...")
        self._popup = popup

        def run():
            try:
                client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                msg = client.messages.create(
                    model="claude-haiku-4-5",
                    max_tokens=1024,
                    messages=[{
                        "role": "user",
                        "content": (
                            f"Dịch đoạn văn bản sau sang tiếng Việt tự nhiên, "
                            f"giữ nguyên định dạng nếu có. "
                            f"Chỉ trả về bản dịch, không giải thích thêm:\n\n{text}"
                        )
                    }]
                )
                result = msg.content[0].text.strip()
            except anthropic.AuthenticationError:
                result = "❌ API key chưa đúng!\nVào file circle_pet.py\nđổi ANTHROPIC_API_KEY"
            except Exception as e:
                result = f"❌ Lỗi: {str(e)[:80]}"

            def update():
                if popup.win.winfo_exists():
                    popup.set_text(result)
                self.translating = False
                self._say("Dịch xong! ✓")
            self.root.after(0, update)

        threading.Thread(target=run, daemon=True).start()

    # ── Physics ──────────────────────────────────────────────────────────────
    def _physics(self):
        if self._dragging:
            return
        self.vy += GRAVITY
        self.vx *= FRICTION
        self.x  += self.vx
        self.y  += self.vy

        floor = self.sh - SIZE - 55
        if self.y >= floor:
            self.y = float(floor)
            impact = abs(self.vy)
            self.vy = -impact * BOUNCE
            if abs(self.vy) < 2.5: self.vy = 0.0
            sq = max(0.55, 1.0 - impact * 0.05)
            self.sq = sq; self.st = 2.0 - sq
            if impact > 5 and not self.translating:
                self._say(random.choice(["Boing!", "Ow!", "●'◡'●"]))
        if self.y < 0:
            self.y = 0.0; self.vy = abs(self.vy) * BOUNCE
        if self.x < 0:
            self.x = 0.0; self.vx = abs(self.vx) * BOUNCE
            if not self.translating: self._say("Ow!")
        elif self.x > self.sw - SIZE - 20:
            self.x = float(self.sw - SIZE - 20)
            self.vx = -abs(self.vx) * BOUNCE
            if not self.translating: self._say("Ow!")

        self.sq += (1.0 - self.sq) * 0.20
        self.st += (1.0 - self.st) * 0.20
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

    # ── Draw ─────────────────────────────────────────────────────────────────
    def _draw(self):
        c = self.cv; c.delete("all")
        cx = self.W // 2; cy = self.H // 2 + 4
        rw = int((SIZE/2) * self.st)
        rh = int((SIZE/2) * self.sq)

        # Shadow
        sw2 = int(rw*0.9); sh2 = max(2, int(5*self.sq*0.6))
        c.create_oval(cx-sw2, cy+rh, cx+sw2, cy+rh+sh2*2, fill="#330055", outline="")

        # Vòng ngoài khi đang dịch
        if self.translating:
            c.create_oval(cx-rw-5, cy-rh-5, cx+rw+5, cy+rh+5,
                          outline="#ffffff", width=2, dash=(4,3))

        # Body
        c.create_oval(cx-rw,   cy-rh,   cx+rw,   cy+rh,   fill=self.dark, outline="")
        c.create_oval(cx-rw+3, cy-rh+3, cx+rw-3, cy+rh-3, fill=self.col,  outline="")
        # Shine
        c.create_oval(cx-rw//3, cy-rh//2, cx+rw//8, cy-rh//6,
                      fill="white", outline="")

        # Face — spin khi dịch
        face = self.face
        if self.translating:
            faces = ["●'◕'●","●'○'●","●'◉'●"]
            face  = faces[(int(time.time()*3)) % 3]
        fsz = max(9, int(12 * min(self.sq, 1.0)))
        c.create_text(cx, cy+2, text=face,
                      font=("Segoe UI Emoji", fsz), fill="white")

        # Trail khi bay nhanh
        spd = math.hypot(self.vx, self.vy)
        if spd > 8 and not self._dragging:
            for i in range(1, 4):
                tr = int(rw * 0.45 * (1 - i/4))
                ox = int(-self.vx * i * 0.35)
                oy = int(-self.vy * i * 0.25)
                c.create_oval(cx+ox-tr, cy+oy-tr, cx+ox+tr, cy+oy+tr,
                              fill=self.dark, outline="", stipple="gray25")

        # Bubble
        if self.bubble:
            bx, by = cx, cy - rh - 20
            c.create_oval(bx-44, by-15, bx+44, by+15,
                          fill="white", outline=self.dark, width=2)
            c.create_polygon(bx-6, by+15, bx+6, by+15, bx, by+23,
                             fill="white", outline="")
            c.create_text(bx, by, text=self.bubble,
                          font=("Segoe UI", 9), fill="#333")

    def _tick(self):
        self._physics(); self._draw()
        self.root.after(1000 // FPS, self._tick)

    # ── Bubble ────────────────────────────────────────────────────────────────
    def _say(self, txt):
        self.bubble = txt
        if self.bubble_tid: self.root.after_cancel(self.bubble_tid)
        self.bubble_tid = self.root.after(2200, lambda: setattr(self, "bubble", None))

    # ── Mouse ─────────────────────────────────────────────────────────────────
    def _press(self, e):
        self._dragging = True; self.vx = 0; self.vy = 0
        self._off_x = e.x_root - int(self.x)
        self._off_y = e.y_root - int(self.y)
        self._drag_hist = [(time.time(), e.x_root, e.y_root)]

    def _drag_move(self, e):
        self.x = float(e.x_root - self._off_x)
        self.y = float(e.y_root - self._off_y)
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
        now = time.time()
        self._drag_hist.append((now, e.x_root, e.y_root))
        self._drag_hist = [(t,x,y) for t,x,y in self._drag_hist if now-t < 0.08]

    def _release(self, e):
        self._dragging = False
        if len(self._drag_hist) >= 2:
            t0,x0,y0 = self._drag_hist[0]; t1,x1,y1 = self._drag_hist[-1]
            dt = t1-t0
            if dt > 0.001:
                self.vx = max(-28, min(28, (x1-x0)/dt * 0.055))
                self.vy = max(-28, min(28, (y1-y0)/dt * 0.055))
                if math.hypot(self.vx,self.vy) > 10:
                    self._say(random.choice(["Wheee~!", "Woah!", "Yay!"]))
        else:
            self.vy = -5.0

    def _dbl(self, e):
        self.mood_idx = (self.mood_idx + 1) % len(MOODS)
        self.face, self.col, self.dark = MOODS[self.mood_idx]
        self._say(random.choice(SAYS))

    def _rmenu(self, e):
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="🌐 Dịch clipboard ngay", command=lambda: self._do_translate(pyperclip.paste()) if pyperclip.paste() else None)
        m.add_separator()
        m.add_command(label="💬 Nói",       command=lambda: self._say(random.choice(SAYS)))
        m.add_command(label="🎲 Đổi mood",  command=lambda: self._dbl(None))
        m.add_command(label="⬆️  Tung lên",  command=lambda: setattr(self,'vy',-22.0))
        m.add_command(label="💥 Ném mạnh",  command=lambda: self.__dict__.update({'vx':random.choice([-20,20]),'vy':-18.0}))
        m.add_separator()
        m.add_command(label="❌ Thoát",      command=self.root.destroy)
        m.tk_popup(e.x_root, e.y_root)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    if ANTHROPIC_API_KEY == "YOUR_API_KEY_HERE":
        print("="*55)
        print("⚠️  Chưa có API key!")
        print("   Mở file circle_pet.py")
        print("   Tìm dòng: ANTHROPIC_API_KEY = \"YOUR_API_KEY_HERE\"")
        print("   Thay bằng key của bạn tại: https://console.anthropic.com")
        print("="*55)
    print("●'◡'● Lunara đang chạy!")
    print("  Bôi đen text bất kỳ → Lunara tự dịch sang tiếng Việt")
    print("  Kéo nhanh + thả = ném")
    print("  Double-click = đổi mood | Chuột phải = menu")
    CirclePet().run()