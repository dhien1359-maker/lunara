"""
features/walk.py — Đi dạo quanh viền màn hình
Ném/nảy xong tự quay lại viền và đi tiếp.
"""
import math, time, random

class WalkFeature:
    def __init__(self, pet):
        self.pet     = pet
        self.enabled = False
        self.edge    = "bottom"
        self.dir     = 1
        self.speed   = 2.0
        self._returning = False   # đang bay về viền sau khi bị ném

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            self._snap_to_nearest_edge()
            self._returning = False
            self.pet.say("Đi dạo~ 🚶")
        else:
            self._returning = False
            self.pet.say("Nghỉ thôi!")

    def _snap_to_nearest_edge(self):
        p    = self.pet
        size = 80
        cx   = p.x + size/2
        cy   = p.y + size/2
        sw, sh = p.sw, p.sh
        dist = {
            "bottom": sh - cy,
            "top":    cy,
            "left":   cx,
            "right":  sw - cx,
        }
        self.edge = min(dist, key=dist.get)

    def _on_edge(self):
        """Kiểm tra pet đã áp sát viền chưa"""
        p = self.pet
        size = 80
        sw, sh = p.sw, p.sh
        margin = 12
        if self.edge == "bottom" and p.y >= sh - size - 50 - margin:
            return True
        if self.edge == "top"    and p.y <= margin:
            return True
        if self.edge == "left"   and p.x <= margin:
            return True
        if self.edge == "right"  and p.x >= sw - size - margin:
            return True
        return False

    def step(self):
        if not self.enabled:
            return self.pet.x, self.pet.y

        p  = self.pet
        ph = p.physics

        # Đang bị kéo tay — physics tự lo, không làm gì
        if ph.dragging:
            return p.x, p.y

        # Đang bay (bị ném hoặc nảy) — để physics chạy bình thường
        # Khi tốc độ đủ nhỏ VÀ gần sàn → snap về viền và đi tiếp
        speed = math.hypot(ph.vx, ph.vy)
        near_floor = p.y >= p.sh - 80 - 55 - 20

        if speed > 1.5 or not near_floor:
            # Vẫn đang nảy — physics lo
            self._returning = True
            return p.x, p.y

        # Đã dừng nảy → snap về viền gần nhất và đi tiếp
        if self._returning:
            self._returning = False
            self._snap_to_nearest_edge()
            self._align_to_edge()
            ph.vx = 0; ph.vy = 0

        # ── Đi dọc viền ──────────────────────────────────────────────────
        size   = 80
        sw, sh = p.sw, p.sh
        margin = 4
        spd    = self.speed * self.dir

        if self.edge == "bottom":
            p.y = float(sh - size - 50)
            p.x += spd
            if p.x >= sw - size - margin:
                p.x = float(sw - size - margin)
                self.edge = "right"; self.dir = -1
            elif p.x <= margin:
                p.x = float(margin)
                self.edge = "left"; self.dir = 1

        elif self.edge == "top":
            p.y = float(margin)
            p.x += spd
            if p.x >= sw - size - margin:
                p.x = float(sw - size - margin)
                self.edge = "right"; self.dir = 1
            elif p.x <= margin:
                p.x = float(margin)
                self.edge = "left"; self.dir = -1

        elif self.edge == "right":
            p.x = float(sw - size - margin)
            p.y += spd
            if p.y >= sh - size - 50:
                p.y = float(sh - size - 50)
                self.edge = "bottom"; self.dir = -1
            elif p.y <= margin:
                p.y = float(margin)
                self.edge = "top"; self.dir = 1

        elif self.edge == "left":
            p.x = float(margin)
            p.y += spd
            if p.y >= sh - size - 50:
                p.y = float(sh - size - 50)
                self.edge = "bottom"; self.dir = 1
            elif p.y <= margin:
                p.y = float(margin)
                self.edge = "top"; self.dir = -1

        # Squash/stretch nhẹ khi bước
        t = time.time()
        ph.sq = 1.0 + math.sin(t * 8) * 0.04
        ph.st = 1.0 - math.sin(t * 8) * 0.04
        ph.vx = 0; ph.vy = 0

        return p.x, p.y

    def _align_to_edge(self):
        p    = self.pet
        size = 80
        sw, sh = p.sw, p.sh
        margin = 4
        if self.edge == "bottom": p.y = float(sh - size - 50)
        elif self.edge == "top":  p.y = float(margin)
        elif self.edge == "left": p.x = float(margin)
        elif self.edge == "right":p.x = float(sw - size - margin)