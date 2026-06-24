"""
features/scheduler.py — Hẹn giờ, nhắc lịch, đồng hồ
"""
import tkinter as tk
from tkinter import ttk
import threading, time, datetime, json, os

SAVE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "reminders.json")

def _ensure_data_dir():
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)

# ── Cửa sổ quản lý lịch ─────────────────────────────────────────────────────
class SchedulerWindow:
    def __init__(self, root, pet):
        if hasattr(self, '_built'): return
        self._built = True
        self.root = root
        self.pet  = pet

        self.win = tk.Toplevel(root)
        self.win.title("🌸 Lunara — Lịch & Hẹn giờ")
        self.win.attributes("-topmost", True)
        self.win.config(bg="#0d0818")
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.win.withdraw)

        self._build_ui()
        self._position()
        self._tick_clock()

    def _position(self):
        self.win.update_idletasks()
        w = self.win.winfo_width() or 380
        h = self.win.winfo_height() or 520
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.win.geometry(f"{w}x{h}+{sw-w-20}+{sh-h-60}")

    def _build_ui(self):
        PAD = dict(padx=12, pady=6)
        BG  = "#0d0818"
        BG2 = "#1a0a2e"
        FG  = "#f0e6ff"
        ACC = "#FF9EC4"

        # ── Đồng hồ ──────────────────────────────────────────────────────────
        clock_frame = tk.Frame(self.win, bg=BG2, pady=10)
        clock_frame.pack(fill="x", padx=12, pady=(12,4))

        self.lbl_time = tk.Label(clock_frame, text="", font=("Segoe UI", 28, "bold"),
                                 bg=BG2, fg=ACC)
        self.lbl_time.pack()
        self.lbl_date = tk.Label(clock_frame, text="", font=("Segoe UI", 11),
                                 bg=BG2, fg="#c0a8e0")
        self.lbl_date.pack()

        # ── Tab: Hẹn giờ / Đếm ngược ────────────────────────────────────────
        nb = ttk.Notebook(self.win)
        nb.pack(fill="both", expand=True, padx=12, pady=6)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",        background=BG,  borderwidth=0)
        style.configure("TNotebook.Tab",    background=BG2, foreground=FG,
                        padding=[10,4], font=("Segoe UI", 9))
        style.map("TNotebook.Tab",
                  background=[("selected", "#3d1060")],
                  foreground=[("selected", ACC)])

        # Tab 1 — Nhắc lịch
        tab1 = tk.Frame(nb, bg=BG); nb.add(tab1, text="📅 Nhắc lịch")
        self._build_reminder_tab(tab1, BG, BG2, FG, ACC)

        # Tab 2 — Đếm ngược
        tab2 = tk.Frame(nb, bg=BG); nb.add(tab2, text="⏱ Đếm ngược")
        self._build_timer_tab(tab2, BG, BG2, FG, ACC)

        # Tab 3 — Danh sách nhắc
        tab3 = tk.Frame(nb, bg=BG); nb.add(tab3, text="📋 Danh sách")
        self._build_list_tab(tab3, BG, BG2, FG, ACC)

    # ── Tab nhắc lịch ────────────────────────────────────────────────────────
    def _build_reminder_tab(self, parent, BG, BG2, FG, ACC):
        def lbl(p, t, **kw):
            tk.Label(p, text=t, bg=BG, fg="#c0a8e0",
                     font=("Segoe UI", 9), **kw).pack(anchor="w", padx=4, pady=(6,0))

        lbl(parent, "Nội dung nhắc:")
        self.rem_text = tk.Entry(parent, font=("Segoe UI", 10),
                                 bg=BG2, fg=FG, insertbackground=FG,
                                 relief="flat", width=34)
        self.rem_text.pack(padx=4, pady=2, ipady=4)

        lbl(parent, "Ngày (DD/MM/YYYY) — bỏ trống = hôm nay:")
        self.rem_date = tk.Entry(parent, font=("Segoe UI", 10),
                                 bg=BG2, fg=FG, insertbackground=FG,
                                 relief="flat", width=20)
        self.rem_date.pack(padx=4, pady=2, anchor="w", ipady=4)

        lbl(parent, "Giờ (HH:MM):")
        time_frame = tk.Frame(parent, bg=BG)
        time_frame.pack(padx=4, pady=2, anchor="w")
        self.rem_hour = tk.Spinbox(time_frame, from_=0, to=23, width=4,
                                   format="%02.0f", font=("Segoe UI", 10),
                                   bg=BG2, fg=FG, buttonbackground=BG2,
                                   relief="flat", insertbackground=FG)
        self.rem_hour.pack(side="left")
        tk.Label(time_frame, text=" : ", bg=BG, fg=FG,
                 font=("Segoe UI", 12)).pack(side="left")
        self.rem_min = tk.Spinbox(time_frame, from_=0, to=59, width=4,
                                  format="%02.0f", font=("Segoe UI", 10),
                                  bg=BG2, fg=FG, buttonbackground=BG2,
                                  relief="flat", insertbackground=FG)
        self.rem_min.pack(side="left")

        # Preset nhanh
        lbl(parent, "Nhanh:")
        pf = tk.Frame(parent, bg=BG); pf.pack(padx=4, pady=2, anchor="w")
        for label, mins in [("5 phút",5),("15 phút",15),("30 phút",30),("1 giờ",60)]:
            tk.Button(pf, text=label, font=("Segoe UI", 8),
                      bg="#2d0850", fg=FG, relief="flat", cursor="hand2",
                      padx=6, pady=2,
                      command=lambda m=mins: self._quick_remind(m)
                      ).pack(side="left", padx=2)

        tk.Button(parent, text="➕ Thêm nhắc lịch",
                  font=("Segoe UI", 10, "bold"),
                  bg="#7b2fbe", fg="white", relief="flat",
                  cursor="hand2", padx=10, pady=6,
                  command=self._add_reminder
                  ).pack(pady=10)

        self.rem_status = tk.Label(parent, text="", bg=BG, fg=ACC,
                                   font=("Segoe UI", 9))
        self.rem_status.pack()

    # ── Tab đếm ngược ────────────────────────────────────────────────────────
    def _build_timer_tab(self, parent, BG, BG2, FG, ACC):
        tk.Label(parent, text="Đặt thời gian đếm ngược:",
                 bg=BG, fg="#c0a8e0", font=("Segoe UI", 9)
                 ).pack(anchor="w", padx=4, pady=(10,4))

        tf = tk.Frame(parent, bg=BG); tf.pack(padx=4)
        self.timer_h = tk.Spinbox(tf, from_=0, to=23, width=4, format="%02.0f",
                                  font=("Segoe UI", 14), bg=BG2, fg=FG,
                                  buttonbackground=BG2, relief="flat",
                                  insertbackground=FG)
        self.timer_h.pack(side="left")
        tk.Label(tf, text=" giờ  ", bg=BG, fg=FG, font=("Segoe UI",10)).pack(side="left")
        self.timer_m = tk.Spinbox(tf, from_=0, to=59, width=4, format="%02.0f",
                                  font=("Segoe UI", 14), bg=BG2, fg=FG,
                                  buttonbackground=BG2, relief="flat",
                                  insertbackground=FG)
        self.timer_m.pack(side="left")
        tk.Label(tf, text=" phút  ", bg=BG, fg=FG, font=("Segoe UI",10)).pack(side="left")
        self.timer_s = tk.Spinbox(tf, from_=0, to=59, width=4, format="%02.0f",
                                  font=("Segoe UI", 14), bg=BG2, fg=FG,
                                  buttonbackground=BG2, relief="flat",
                                  insertbackground=FG)
        self.timer_s.pack(side="left")
        tk.Label(tf, text=" giây", bg=BG, fg=FG, font=("Segoe UI",10)).pack(side="left")

        tk.Label(parent, text="Tên hẹn giờ (tùy chọn):",
                 bg=BG, fg="#c0a8e0", font=("Segoe UI", 9)
                 ).pack(anchor="w", padx=4, pady=(8,2))
        self.timer_name = tk.Entry(parent, font=("Segoe UI", 10),
                                   bg=BG2, fg=FG, insertbackground=FG,
                                   relief="flat", width=28)
        self.timer_name.pack(padx=4, ipady=4, anchor="w")

        bf = tk.Frame(parent, bg=BG); bf.pack(pady=10)
        self.btn_start = tk.Button(bf, text="▶ Bắt đầu",
                                   font=("Segoe UI", 10, "bold"),
                                   bg="#3aaa80", fg="white", relief="flat",
                                   cursor="hand2", padx=10, pady=6,
                                   command=self._start_timer)
        self.btn_start.pack(side="left", padx=4)
        self.btn_stop = tk.Button(bf, text="⏹ Dừng",
                                  font=("Segoe UI", 10),
                                  bg="#e0608a", fg="white", relief="flat",
                                  cursor="hand2", padx=10, pady=6,
                                  command=self._stop_timer,
                                  state="disabled")
        self.btn_stop.pack(side="left", padx=4)

        self.lbl_countdown = tk.Label(parent, text="--:--:--",
                                      font=("Segoe UI", 32, "bold"),
                                      bg=BG, fg=ACC)
        self.lbl_countdown.pack(pady=8)
        self.lbl_timer_name_disp = tk.Label(parent, text="",
                                            font=("Segoe UI", 10),
                                            bg=BG, fg="#c0a8e0")
        self.lbl_timer_name_disp.pack()

        self._timer_running   = False
        self._timer_end_time  = None
        self._timer_thread    = None

    # ── Tab danh sách ────────────────────────────────────────────────────────
    def _build_list_tab(self, parent, BG, BG2, FG, ACC):
        tk.Label(parent, text="Các nhắc lịch sắp tới:",
                 bg=BG, fg="#c0a8e0", font=("Segoe UI", 9)
                 ).pack(anchor="w", padx=4, pady=(8,2))

        frame = tk.Frame(parent, bg=BG2); frame.pack(fill="both", expand=True, padx=4, pady=4)
        self.list_box = tk.Listbox(frame, bg=BG2, fg=FG,
                                   font=("Segoe UI", 9),
                                   selectbackground="#3d1060",
                                   relief="flat", borderwidth=0,
                                   activestyle="none")
        self.list_box.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(frame, command=self.list_box.yview, bg=BG2)
        sb.pack(side="right", fill="y")
        self.list_box.config(yscrollcommand=sb.set)

        tk.Button(parent, text="🗑 Xoá mục chọn",
                  font=("Segoe UI", 9),
                  bg="#2d0850", fg=FG, relief="flat",
                  cursor="hand2", padx=8, pady=4,
                  command=self._delete_selected
                  ).pack(pady=6)

        self._refresh_list()

    # ── Logic ────────────────────────────────────────────────────────────────
    def _tick_clock(self):
        now = datetime.datetime.now()
        self.lbl_time.config(text=now.strftime("%H:%M:%S"))
        days = ["Thứ Hai","Thứ Ba","Thứ Tư","Thứ Năm","Thứ Sáu","Thứ Bảy","Chủ Nhật"]
        self.lbl_date.config(
            text=f"{days[now.weekday()]}, {now.strftime('%d/%m/%Y')}"
        )
        self.win.after(1000, self._tick_clock)

    def _quick_remind(self, minutes):
        now = datetime.datetime.now()
        target = now + datetime.timedelta(minutes=minutes)
        self.rem_hour.delete(0, "end"); self.rem_hour.insert(0, f"{target.hour:02d}")
        self.rem_min.delete(0, "end");  self.rem_min.insert(0, f"{target.minute:02d}")
        if not self.rem_text.get():
            self.rem_text.insert(0, f"Nhắc sau {minutes} phút")

    def _add_reminder(self):
        text = self.rem_text.get().strip()
        if not text:
            self.rem_status.config(text="⚠️ Nhập nội dung nhắc!", fg="#ffaa00")
            return
        try:
            hour = int(self.rem_hour.get())
            minute = int(self.rem_min.get())
        except ValueError:
            self.rem_status.config(text="⚠️ Giờ không hợp lệ!", fg="#ffaa00")
            return

        date_str = self.rem_date.get().strip()
        now = datetime.datetime.now()
        if date_str:
            try:
                d = datetime.datetime.strptime(date_str, "%d/%m/%Y")
                target = d.replace(hour=hour, minute=minute, second=0, microsecond=0)
            except ValueError:
                self.rem_status.config(text="⚠️ Ngày không hợp lệ! (DD/MM/YYYY)", fg="#ffaa00")
                return
        else:
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target <= now:
                target += datetime.timedelta(days=1)

        if target <= now:
            self.rem_status.config(text="⚠️ Thời gian phải trong tương lai!", fg="#ffaa00")
            return

        reminder = {
            "text":   text,
            "target": target.strftime("%Y-%m-%d %H:%M:%S"),
            "done":   False
        }
        self.pet.scheduler._reminders.append(reminder)
        self.pet.scheduler._save()
        self._refresh_list()

        delta = target - now
        h, rem = divmod(int(delta.total_seconds()), 3600)
        m, s   = divmod(rem, 60)
        self.rem_status.config(
            text=f"✓ Đã đặt! Còn {h}g {m}p {s}s", fg="#b5ead7"
        )
        self.rem_text.delete(0, "end")
        self.rem_date.delete(0, "end")

    def _start_timer(self):
        try:
            h = int(self.timer_h.get())
            m = int(self.timer_m.get())
            s = int(self.timer_s.get())
        except ValueError:
            return
        total = h*3600 + m*60 + s
        if total <= 0: return

        name = self.timer_name.get().strip() or "Hẹn giờ"
        self._timer_running  = True
        self._timer_end_time = time.time() + total
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.lbl_timer_name_disp.config(text=name)
        self._tick_timer(name)

    def _tick_timer(self, name):
        if not self._timer_running: return
        remaining = self._timer_end_time - time.time()
        if remaining <= 0:
            self.lbl_countdown.config(text="00:00:00", fg="#FF9EC4")
            self._timer_running = False
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.pet.scheduler._alert(f"⏰ {name} xong rồi!")
            return
        h, rem = divmod(int(remaining), 3600)
        m, s   = divmod(rem, 60)
        color = "#ff6b6b" if remaining <= 60 else "#FF9EC4"
        self.lbl_countdown.config(text=f"{h:02d}:{m:02d}:{s:02d}", fg=color)
        self.win.after(500, lambda: self._tick_timer(name))

    def _stop_timer(self):
        self._timer_running = False
        self.lbl_countdown.config(text="--:--:--", fg="#FF9EC4")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    def _refresh_list(self):
        self.list_box.delete(0, "end")
        now = datetime.datetime.now()
        reminders = sorted(
            [r for r in self.pet.scheduler._reminders if not r["done"]],
            key=lambda r: r["target"]
        )
        if not reminders:
            self.list_box.insert("end", "  (Chưa có lịch nào)")
            return
        for r in reminders:
            t = datetime.datetime.strptime(r["target"], "%Y-%m-%d %H:%M:%S")
            delta = t - now
            if delta.total_seconds() > 0:
                h, rem = divmod(int(delta.total_seconds()), 3600)
                m, _ = divmod(rem, 60)
                time_str = f"{h}g{m}p nữa" if h > 0 else f"{m}p nữa"
            else:
                time_str = "quá hạn"
            self.list_box.insert("end",
                f"  {t.strftime('%d/%m %H:%M')}  [{time_str}]  {r['text']}")

    def _delete_selected(self):
        sel = self.list_box.curselection()
        if not sel: return
        idx = sel[0]
        active = [r for r in self.pet.scheduler._reminders if not r["done"]]
        if idx < len(active):
            self.pet.scheduler._reminders.remove(active[idx])
            self.pet.scheduler._save()
            self._refresh_list()

    def show(self):
        self._refresh_list()
        self.win.deiconify()
        self.win.lift()


# ── Feature class (gắn vào pet) ──────────────────────────────────────────────
class SchedulerFeature:
    def __init__(self, root, pet):
        self.root = root
        self.pet  = pet
        self._reminders = []
        self._window    = None
        _ensure_data_dir()
        self._load()
        self._check_loop()

    def open_window(self):
        if self._window is None or not self._window.win.winfo_exists():
            self._window = SchedulerWindow(self.root, self.pet)
        else:
            self._window.show()

    def _check_loop(self):
        now = datetime.datetime.now()
        for r in self._reminders:
            if r["done"]: continue
            t = datetime.datetime.strptime(r["target"], "%Y-%m-%d %H:%M:%S")
            if now >= t:
                r["done"] = True
                self._save()
                self._alert(f"🔔 {r['text']}")
        self.root.after(10000, self._check_loop)

    def _alert(self, msg):
        self.pet.say(msg)
        # Popup cảnh báo
        popup = tk.Toplevel(self.root)
        popup.title("🌸 Lunara nhắc bạn!")
        popup.attributes("-topmost", True)
        popup.config(bg="#1a0a2e")
        popup.overrideredirect(False)

        tk.Label(popup, text="🔔", font=("Segoe UI Emoji", 36),
                 bg="#1a0a2e").pack(pady=(16,4))
        tk.Label(popup, text=msg, font=("Segoe UI", 13, "bold"),
                 bg="#1a0a2e", fg="#FF9EC4", wraplength=260).pack(padx=20, pady=6)
        tk.Label(popup, text=datetime.datetime.now().strftime("%H:%M  %d/%m/%Y"),
                 font=("Segoe UI", 9), bg="#1a0a2e", fg="#c0a8e0").pack(pady=(0,6))
        tk.Button(popup, text="OK!", font=("Segoe UI", 10, "bold"),
                  bg="#7b2fbe", fg="white", relief="flat",
                  cursor="hand2", padx=20, pady=6,
                  command=popup.destroy).pack(pady=(4,16))

        # Vị trí giữa màn hình
        popup.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        pw = popup.winfo_width() or 300
        ph = popup.winfo_height() or 200
        popup.geometry(f"+{(sw-pw)//2}+{(sh-ph)//2}")

        # Tự đóng sau 30 giây
        popup.after(30000, lambda: popup.destroy() if popup.winfo_exists() else None)

    def _save(self):
        try:
            _ensure_data_dir()
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._reminders, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load(self):
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, encoding="utf-8") as f:
                    self._reminders = json.load(f)
        except Exception:
            self._reminders = []
