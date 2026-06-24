import tkinter as tk
import math, time

SIZE = 80

class Renderer:
    def __init__(self, root, W, H, pet):
        self.W, self.H = W, H
        self.pet = pet
        self.canvas = tk.Canvas(root, width=W, height=H,
                                bg="#010101", highlightthickness=0)
        self.canvas.pack()

    def draw(self, x, y):
        c = self.canvas; c.delete("all")
        pet = self.pet
        cx, cy = self.W // 2, self.H // 2 + 4
        ph = pet.physics
        rw = int((SIZE/2) * ph.st)
        rh = int((SIZE/2) * ph.sq)
        col  = pet.mood.color
        dark = pet.mood.dark

        # Shadow
        sw2 = int(rw*0.9); sh2 = max(2, int(5*ph.sq*0.6))
        c.create_oval(cx-sw2, cy+rh, cx+sw2, cy+rh+sh2*2, fill="#330055", outline="")

        # Vòng khi đang dịch
        if pet.translate.translating:
            c.create_oval(cx-rw-5, cy-rh-5, cx+rw+5, cy+rh+5,
                          outline="#ffffff", width=2, dash=(4,3))

        # Body
        c.create_oval(cx-rw,   cy-rh,   cx+rw,   cy+rh,   fill=dark, outline="")
        c.create_oval(cx-rw+3, cy-rh+3, cx+rw-3, cy+rh-3, fill=col,  outline="")
        c.create_oval(cx-rw//3, cy-rh//2, cx+rw//8, cy-rh//6, fill="white", outline="")

        # Face
        face = pet.mood.face
        if pet.translate.translating:
            face = ["●'◕'●","●'○'●","●'◉'●"][int(time.time()*3) % 3]
        fsz = max(9, int(12 * min(ph.sq, 1.0)))
        c.create_text(cx, cy+2, text=face, font=("Segoe UI Emoji", fsz), fill="white")

        # Trail
        spd = math.hypot(ph.vx, ph.vy)
        if spd > 8 and not ph.dragging:
            for i in range(1, 4):
                tr = int(rw * 0.45 * (1-i/4))
                ox = int(-ph.vx * i * 0.35)
                oy = int(-ph.vy * i * 0.25)
                c.create_oval(cx+ox-tr, cy+oy-tr, cx+ox+tr, cy+oy+tr,
                              fill=dark, outline="", stipple="gray25")

        # Bubble
        if pet.bubble:
            bx, by = cx, cy - rh - 20
            c.create_oval(bx-44, by-15, bx+44, by+15,
                          fill="white", outline=dark, width=2)
            c.create_polygon(bx-6, by+15, bx+6, by+15, bx, by+23,
                             fill="white", outline="")
            c.create_text(bx, by, text=pet.bubble,
                          font=("Segoe UI", 9), fill="#333")
