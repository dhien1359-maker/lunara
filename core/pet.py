import tkinter as tk
import random, math

from core.physics  import Physics
from core.renderer import Renderer
from features.translate  import TranslateFeature
from features.mood       import MoodFeature
from features.scheduler  import SchedulerFeature
from features.walk       import WalkFeature

SIZE = 80
FPS  = 60

class CirclePet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "#010101")
        self.root.config(bg="#010101")

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self.W, self.H = SIZE + 80, SIZE + 70

        self.x = float(self.sw // 2)
        self.y = float(self.sh - SIZE - 100)
        self.bubble     = None
        self.bubble_tid = None

        self.mood      = MoodFeature()
        self.physics   = Physics(self.sw, self.sh, SIZE)
        self.renderer  = Renderer(self.root, self.W, self.H, self)
        self.translate = TranslateFeature(self.root, self)
        self.scheduler = SchedulerFeature(self.root, self)
        self.walk      = WalkFeature(self)

        self.root.geometry(f"{self.W}x{self.H}+{int(self.x)}+{int(self.y)}")
        self._bind_events()
        self.translate.start_polling()
        self._tick()

    def _bind_events(self):
        cv = self.renderer.canvas
        cv.bind("<ButtonPress-1>",   self._press)
        cv.bind("<B1-Motion>",       self._drag)
        cv.bind("<ButtonRelease-1>", self._release)
        cv.bind("<Double-Button-1>", self._double_click)
        cv.bind("<Button-3>",        self._right_click)

    def _press(self, e):
        self.physics.start_drag(e.x_root, e.y_root, self.x, self.y)

    def _drag(self, e):
        self.x, self.y = self.physics.update_drag(e.x_root, e.y_root)
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

    def _release(self, e):
        vx, vy = self.physics.end_drag()
        self.physics.vx = vx
        self.physics.vy = vy
        if math.hypot(vx, vy) > 10:
            self.say(random.choice(["Wheee~!", "Woah!", "Yay!"]))

    def _double_click(self, e):
        self.mood.next()
        self.say(self.mood.random_say())

    def _right_click(self, e):
        import pyperclip
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="🌐 Dịch clipboard",
                      command=lambda: self.translate.translate_now(pyperclip.paste()))
        m.add_command(label="📅 Lịch & Hẹn giờ",
                      command=lambda: self.scheduler.open_window())
        walk_label = "⏹ Dừng đi dạo" if self.walk.enabled else "🚶 Đi dạo viền màn hình"
        m.add_command(label=walk_label,
                      command=lambda: self.walk.toggle())
        m.add_separator()
        m.add_command(label="💬 Nói",
                      command=lambda: self.say(self.mood.random_say()))
        m.add_command(label="🎲 Đổi mood",
                      command=lambda: [self.mood.next(), self.say(self.mood.random_say())])
        m.add_command(label="⬆️  Tung lên",
                      command=lambda: [setattr(self.walk, 'enabled', False), setattr(self.physics, 'vy', -22.0)])
        m.add_command(label="💥 Ném mạnh",
                      command=lambda: [setattr(self.walk, 'enabled', False), self.physics.throw_random()])
        m.add_separator()
        m.add_command(label="❌ Thoát", command=self.root.destroy)
        m.tk_popup(e.x_root, e.y_root)

    def _tick(self):
        if not self.physics.dragging:
            if self.walk.enabled:
                # Luôn chạy physics trước (để nảy/rơi tự nhiên)
                self.x, self.y, hit = self.physics.step(self.x, self.y)
                # Walk step sẽ override vị trí khi đã ổn định về viền
                self.x, self.y = self.walk.step()
                self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
            else:
                self.x, self.y, hit = self.physics.step(self.x, self.y)
                self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
                if hit and not self.translate.translating:
                    self.say(random.choice(["Boing!", "Ow!", "●'◡'●"]))
        self.renderer.draw(self.x, self.y)
        self.root.after(1000 // FPS, self._tick)

    def say(self, txt):
        self.bubble = txt
        if self.bubble_tid:
            self.root.after_cancel(self.bubble_tid)
        self.bubble_tid = self.root.after(2200, lambda: setattr(self, "bubble", None))

    def run(self):
        self.root.mainloop()