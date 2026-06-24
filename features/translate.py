import threading
import tkinter as tk

# ── Cấu hình ─────────────────────────────────────────────────
ANTHROPIC_API_KEY = "YOUR_API_KEY_HERE"   # ← thay key vào đây
MODEL             = "claude-haiku-4-5"

class TranslatePopup:
    def __init__(self, root, x, y, col):
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.config(bg="#1a0a2e")

        frame = tk.Frame(self.win, bg=col, padx=2, pady=2); frame.pack()
        inner = tk.Frame(frame, bg="#1a0a2e", padx=14, pady=10); inner.pack()

        hdr = tk.Frame(inner, bg="#1a0a2e"); hdr.pack(fill="x")
        tk.Label(hdr, text="🌸 Lunara dịch", font=("Segoe UI", 9, "bold"),
                 bg="#1a0a2e", fg=col).pack(side="left")
        tk.Button(hdr, text="✕", font=("Segoe UI", 8), bg="#1a0a2e", fg="#aaaaaa",
                  relief="flat", cursor="hand2",
                  command=self.win.destroy).pack(side="right")

        self.txt = tk.Text(inner, width=38, height=5,
                           font=("Segoe UI", 10), bg="#0d0520", fg="#f0e6ff",
                           relief="flat", wrap="word", padx=8, pady=6,
                           state="disabled", cursor="arrow")
        self.txt.pack(pady=(6,0))

        self._result = ""
        self.copy_btn = tk.Button(inner, text="📋 Copy", font=("Segoe UI", 8),
                                  bg="#2d0850", fg="white", relief="flat",
                                  cursor="hand2", padx=8, pady=3,
                                  command=self._copy)
        self.copy_btn.pack(anchor="e", pady=(4,0))

        self.win.update_idletasks()
        sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
        self.win.geometry(f"+{min(x, sw-340)}+{min(y, sh-200)}")
        self.win.bind("<ButtonPress-1>", self._dp)
        self.win.bind("<B1-Motion>",     self._dm)

    def set_text(self, txt):
        self._result = txt
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.insert("end", txt)
        self.txt.config(state="disabled")
        self.txt.config(height=min(max(txt.count("\n")+1, 3), 10))

    def _copy(self):
        if self._result:
            import pyperclip; pyperclip.copy(self._result)
            self.copy_btn.config(text="✓ Đã copy!")
            self.win.after(1500, lambda: self.copy_btn.config(text="📋 Copy"))

    def _dp(self, e): self._ox=e.x_root; self._oy=e.y_root
    def _dm(self, e):
        self.win.geometry(f"+{self.win.winfo_x()+(e.x_root-self._ox)}+{self.win.winfo_y()+(e.y_root-self._oy)}")
        self._ox=e.x_root; self._oy=e.y_root


class TranslateFeature:
    def __init__(self, root, pet):
        self.root = root
        self.pet  = pet
        self.translating = False
        self._last_clip  = ""
        self._popup      = None

    def start_polling(self):
        self._poll()

    def _poll(self):
        try:
            import pyperclip
            clip = pyperclip.paste()
            if clip and clip != self._last_clip and len(clip.strip()) > 1 and not self.translating:
                self._last_clip = clip
                self.translate_now(clip.strip())
        except Exception:
            pass
        self.root.after(600, self._poll)

    def translate_now(self, text):
        if not text or self.translating:
            return
        if len(text) > 2000:
            text = text[:2000] + "…"
        self.translating = True
        self.pet.say("Đang dịch...")

        px = int(self.pet.x) + self.pet.W + 10
        py = int(self.pet.y)
        if self._popup and self._popup.win.winfo_exists():
            self._popup.win.destroy()
        popup = TranslatePopup(self.root, px, py, self.pet.mood.color)
        popup.set_text("⏳ Đang dịch...")
        self._popup = popup

        def run():
            result = self._call_api(text)
            def update():
                if popup.win.winfo_exists():
                    popup.set_text(result)
                self.translating = False
                self.pet.say("Dịch xong! ✓")
            self.root.after(0, update)
        threading.Thread(target=run, daemon=True).start()

    def _call_api(self, text):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            msg = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                messages=[{"role":"user","content":
                    "Dịch đoạn văn bản sau sang tiếng Việt tự nhiên, "
                    "giữ nguyên định dạng nếu có. "
                    "Chỉ trả về bản dịch, không giải thích thêm:\n\n" + text
                }]
            )
            return msg.content[0].text.strip()
        except Exception as e:
            err = str(e)
            if "credit" in err.lower():
                return "❌ Hết credit!\nVào console.anthropic.com\n→ Plans & Billing → Mua credit"
            if "auth" in err.lower() or "401" in err:
                return "❌ API key sai!\nKiểm tra ANTHROPIC_API_KEY\ntrong features/translate.py"
            return f"❌ Lỗi: {err[:100]}"
