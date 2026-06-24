import time, random

GRAVITY  = 0.55
BOUNCE   = 0.75
FRICTION = 0.985

class Physics:
    def __init__(self, sw, sh, size):
        self.sw, self.sh, self.size = sw, sh, size
        self.vx = 3.0
        self.vy = 0.0
        self.sq = 1.0
        self.st = 1.0
        self.dragging   = False
        self._drag_hist = []
        self._off_x = self._off_y = 0

    def step(self, x, y):
        self.vy += GRAVITY
        self.vx *= FRICTION
        x += self.vx
        y += self.vy
        hit = False
        floor = self.sh - self.size - 55
        if y >= floor:
            y = float(floor)
            impact = abs(self.vy)
            self.vy = -impact * BOUNCE
            if abs(self.vy) < 2.5: self.vy = 0.0
            sq = max(0.55, 1.0 - impact * 0.05)
            self.sq = sq; self.st = 2.0 - sq
            hit = impact > 5
        if y < 0:
            y = 0.0; self.vy = abs(self.vy) * BOUNCE
        if x < 0:
            x = 0.0; self.vx = abs(self.vx) * BOUNCE; hit = True
        elif x > self.sw - self.size - 20:
            x = float(self.sw - self.size - 20)
            self.vx = -abs(self.vx) * BOUNCE; hit = True
        self.sq += (1.0 - self.sq) * 0.20
        self.st += (1.0 - self.st) * 0.20
        return x, y, hit

    def start_drag(self, mx, my, px, py):
        self.dragging = True
        self.vx = self.vy = 0
        self._off_x = mx - int(px)
        self._off_y = my - int(py)
        self._drag_hist = [(time.time(), mx, my)]

    def update_drag(self, mx, my):
        now = time.time()
        self._drag_hist.append((now, mx, my))
        self._drag_hist = [(t,x,y) for t,x,y in self._drag_hist if now-t < 0.08]
        return float(mx - self._off_x), float(my - self._off_y)

    def end_drag(self):
        self.dragging = False
        if len(self._drag_hist) >= 2:
            t0,x0,y0 = self._drag_hist[0]
            t1,x1,y1 = self._drag_hist[-1]
            dt = t1 - t0
            if dt > 0.001:
                vx = max(-28, min(28, (x1-x0)/dt * 0.055))
                vy = max(-28, min(28, (y1-y0)/dt * 0.055))
                return vx, vy
        return 0.0, -5.0

    def throw_random(self):
        self.vx = random.choice([-20, 20])
        self.vy = -18.0
