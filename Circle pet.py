"""
●'◡'● Circle Desktop Pet — Throw Physics
Chạy: python circle_pet.py
"""
import tkinter as tk
import random
import time

SIZE    = 80
FPS     = 60
GRAVITY = 0.55
BOUNCE  = 0.75   # hệ số nảy
FRICTION= 0.985  # ma sát ngang

MOODS = [
    ("●'◡'●", "#FF9EC4", "#e0608a"),
    ("●'▽'●", "#A8D8EA", "#4a9abf"),
    ("●'ᴗ'●", "#B5EAD7", "#3aaa80"),
    ("●'_'●", "#FFD9A0", "#e09030"),
    ("●'◕'●", "#D4A8FF", "#8844cc"),
]

SAYS = ["Wheee~!", "Boing!", "Ow!", "Yay!", "Hehe~", "●'◡'●", "✨", "♪"]

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

        self.sq = 1.0   # squash y
        self.st = 1.0   # stretch x

        self.mood_idx = 0
        self.face, self.col, self.dark = MOODS[0]

        self.bubble      = None
        self.bubble_tid  = None

        # Drag / throw tracking
        self._dragging   = False
        self._drag_hist  = []   # [(time, x, y), ...] để tính vận tốc ném

        W = SIZE + 80
        H = SIZE + 70
        self.W = W; self.H = H
        self.root.geometry(f"{W}x{H}+{int(self.x)}+{int(self.y)}")

        self.cv = tk.Canvas(self.root, width=W, height=H,
                            bg="#010101", highlightthickness=0)
        self.cv.pack()

        self.cv.bind("<ButtonPress-1>",   self._press)
        self.cv.bind("<B1-Motion>",       self._drag)
        self.cv.bind("<ButtonRelease-1>", self._release)
        self.cv.bind("<Double-Button-1>", self._dbl)
        self.cv.bind("<Button-3>",        self._rmenu)

        self._tick()

    # ── Physics ──────────────────────────────────────────────
    def _physics(self):
        if self._dragging:
            return

        self.vy += GRAVITY
        self.vx *= FRICTION
        self.x  += self.vx
        self.y  += self.vy

        floor = self.sh - SIZE - 55
        # Floor bounce
        if self.y >= floor:
            self.y = float(floor)
            impact = abs(self.vy)
            self.vy = -impact * BOUNCE
            if abs(self.vy) < 2.5:
                self.vy = 0.0
            # squash proportional to impact
            sq = max(0.55, 1.0 - impact * 0.05)
            self.sq = sq
            self.st = 2.0 - sq          # giữ diện tích
            if impact > 5:
                self._say(random.choice(["Boing!", "Ow!", "●'◡'●"]))

        # Ceiling
        if self.y < 0:
            self.y = 0.0
            self.vy = abs(self.vy) * BOUNCE

        # Walls
        if self.x < 0:
            self.x = 0.0
            self.vx = abs(self.vx) * BOUNCE
            self._say("Ow!")
        elif self.x > self.sw - SIZE - 20:
            self.x = float(self.sw - SIZE - 20)
            self.vx = -abs(self.vx) * BOUNCE
            self._say("Ow!")

        # Recover squash/stretch
        self.sq += (1.0 - self.sq) * 0.20
        self.st += (1.0 - self.st) * 0.20

        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

    # ── Draw ─────────────────────────────────────────────────
    def _draw(self):
        c = self.cv
        c.delete("all")
        cx = self.W // 2
        cy = self.H // 2 + 4

        rw = int((SIZE / 2) * self.st)
        rh = int((SIZE / 2) * self.sq)

        # Shadow
        sw2 = int(rw * 0.9)
        sh2 = max(2, int(5 * self.sq * 0.6))
        c.create_oval(cx-sw2, cy+rh, cx+sw2, cy+rh+sh2*2,
                      fill="#330055", outline="")

        # Body
        c.create_oval(cx-rw, cy-rh, cx+rw, cy+rh, fill=self.dark, outline="")
        c.create_oval(cx-rw+3, cy-rh+3, cx+rw-3, cy+rh-3,
                      fill=self.col, outline="")

        # Shine
        c.create_oval(cx-rw//3, cy-rh//2,
                      cx+rw//8, cy-rh//6,
                      fill="white", outline="")

        # Face
        fsz = max(9, int(12 * min(self.sq, 1.0)))
        c.create_text(cx, cy+2, text=self.face,
                      font=("Segoe UI Emoji", fsz), fill="white")

        # Speed trail dots
        spd = math.hypot(self.vx, self.vy) if not self._dragging else 0
        if spd > 8:
            for i in range(1, 4):
                alpha = i / 4
                tr = int(rw * 0.5 * alpha)
                ox = int(-self.vx * i * 0.35)
                oy = int(-self.vy * i * 0.25)
                c.create_oval(cx+ox-tr, cy+oy-tr, cx+ox+tr, cy+oy+tr,
                              fill=self.dark, outline="", stipple="gray25")

        # Bubble
        if self.bubble:
            bx, by = cx, cy - rh - 20
            c.create_oval(bx-40, by-14, bx+40, by+14,
                          fill="white", outline=self.dark, width=2)
            c.create_polygon(bx-6, by+14, bx+6, by+14, bx, by+22,
                             fill="white", outline="")
            c.create_text(bx, by, text=self.bubble,
                          font=("Segoe UI", 9), fill="#333")

    def _tick(self):
        self._physics()
        self._draw()
        self.root.after(1000 // FPS, self._tick)

    # ── Bubble ───────────────────────────────────────────────
    def _say(self, txt):
        self.bubble = txt
        if self.bubble_tid:
            self.root.after_cancel(self.bubble_tid)
        self.bubble_tid = self.root.after(2000, lambda: setattr(self, "bubble", None))

    # ── Mouse events ─────────────────────────────────────────
    def _press(self, e):
        self._dragging = True
        self.vx = 0; self.vy = 0
        self._off_x = e.x_root - int(self.x)
        self._off_y = e.y_root - int(self.y)
        self._drag_hist = [(time.time(), e.x_root, e.y_root)]

    def _drag(self, e):
        self.x = float(e.x_root - self._off_x)
        self.y = float(e.y_root - self._off_y)
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
        now = time.time()
        self._drag_hist.append((now, e.x_root, e.y_root))
        # Chỉ giữ 80ms gần nhất
        self._drag_hist = [(t,x,y) for t,x,y in self._drag_hist if now-t < 0.08]

    def _release(self, e):
        self._dragging = False
        # Tính vận tốc từ lịch sử kéo
        if len(self._drag_hist) >= 2:
            t0,x0,y0 = self._drag_hist[0]
            t1,x1,y1 = self._drag_hist[-1]
            dt = t1 - t0
            if dt > 0.001:
                self.vx = (x1 - x0) / dt * 0.055
                self.vy = (y1 - y0) / dt * 0.055
                # Giới hạn tốc độ tối đa
                self.vx = max(-28, min(28, self.vx))
                self.vy = max(-28, min(28, self.vy))
                spd = (self.vx**2 + self.vy**2) ** 0.5
                if spd > 10:
                    self._say(random.choice(["Wheee~!", "Woah!", "Yay!"]))
        else:
            self.vy = -5.0   # nhảy nhẹ nếu chỉ click

    def _dbl(self, e):
        self.mood_idx = (self.mood_idx + 1) % len(MOODS)
        self.face, self.col, self.dark = MOODS[self.mood_idx]
        self._say(random.choice(SAYS))

    def _rmenu(self, e):
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="💬 Nói",        command=lambda: self._say(random.choice(SAYS)))
        m.add_command(label="🎲 Đổi mood",   command=lambda: self._dbl(None))
        m.add_command(label="⬆️  Tung lên",   command=lambda: setattr(self, 'vy', -22.0))
        m.add_command(label="💥 Ném mạnh",   command=lambda: self.__dict__.update({'vx':random.choice([-20,20]),'vy':-18.0}))
        m.add_separator()
        m.add_command(label="❌ Thoát",       command=self.root.destroy)
        m.tk_popup(e.x_root, e.y_root)

    def run(self):
        self.root.mainloop()

import math

if __name__ == "__main__":
    print("●'◡'● Circle Pet — Throw Edition")
    print("  Kéo nhanh rồi thả = ném!")
    print("  Double-click = đổi mood")
    print("  Chuột phải = menu")
    CirclePet().run()