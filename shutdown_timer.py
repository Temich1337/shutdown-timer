import tkinter as tk
import subprocess
import threading
import time
import base64
import tempfile
import os

BG         = "#12121a"
SURFACE    = "#1e1e2a"
CARD       = "#252532"
CARD_HOVER = "#2e2e3e"
ACCENT     = "#4f8ef7"
ACCENT_DIM = "#3a6fd4"
DANGER     = "#e05555"
DANGER_DIM = "#b03e3e"
SUCCESS    = "#4caf7d"
TEXT1      = "#eeeef5"
TEXT2      = "#9898b0"
TEXT3      = "#5a5a78"
BORDER     = "#2e2e42"

WIN_W, WIN_H = 480, 620

ICON_B64 = """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"""

def extract_icon():
    try:
        data = base64.b64decode(ICON_B64)
        tmp = tempfile.NamedTemporaryFile(suffix=".ico", delete=False)
        tmp.write(data)
        tmp.close()
        return tmp.name
    except Exception:
        return None

def fmt(s):
    h, r = divmod(int(s), 3600)
    m, sec = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"

def do_shutdown(secs):
    try:
        subprocess.run(
            ["shutdown", "-s", "-t", str(secs)],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, ""
    except Exception as e:
        return False, str(e)

def do_abort():
    try:
        subprocess.run(
            ["shutdown", "-a"],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, ""
    except Exception as e:
        return False, str(e)


class FlatButton(tk.Canvas):
    def __init__(self, parent, text, cmd,
                 btn_w=200, btn_h=46,
                 fill=ACCENT, fill_hover=ACCENT_DIM,
                 fg=TEXT1, fnt=None, radius=12, **kw):
        super().__init__(parent,
                         width=btn_w, height=btn_h,
                         bg=BG, highlightthickness=0, **kw)
        self._fill   = fill
        self._fill_h = fill_hover
        self._fg     = fg
        self._text   = text
        self._fnt    = fnt or ("Segoe UI", 11, "bold")
        self._r      = radius
        self._cmd    = cmd
        self._bw     = btn_w
        self._bh     = btn_h
        self._draw(fill)
        self.bind("<Enter>",    lambda e: self._draw(self._fill_h))
        self.bind("<Leave>",    lambda e: self._draw(self._fill))
        self.bind("<Button-1>", lambda e: (self._draw(fill), self.after(80, cmd)))
        self.configure(cursor="hand2")

    def _draw(self, color):
        self.delete("all")
        w, h, r = self._bw, self._bh, self._r
        for x, y, a in [(0,0,90),(w-2*r,0,0),(0,h-2*r,180),(w-2*r,h-2*r,270)]:
            self.create_arc(x, y, x+2*r, y+2*r, start=a, extent=90,
                            fill=color, outline=color)
        self.create_rectangle(r, 0, w-r, h, fill=color, outline=color)
        self.create_rectangle(0, r, w, h-r, fill=color, outline=color)
        self.create_text(w//2, h//2, text=self._text,
                         fill=self._fg, font=self._fnt)

    def set_text(self, t):
        self._text = t
        self._draw(self._fill)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Таймер выключения")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._icon_path = extract_icon()
        if self._icon_path:
            try:
                self.iconbitmap(self._icon_path)
            except Exception:
                pass

        self._center()
        self._total   = 0
        self._remain  = 0
        self._running = False
        self._build()

    def __del__(self):
        if self._icon_path and os.path.exists(self._icon_path):
            try:
                os.unlink(self._icon_path)
            except Exception:
                pass

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - WIN_W) // 2
        y = (self.winfo_screenheight() - WIN_H) // 2
        self.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")

    def _build(self):
        self._build_header()
        self._divider()
        self._build_presets()
        self._divider()
        self._build_manual()
        self._divider()
        self._build_preview()
        self._build_countdown()
        self._build_actions()
        self._build_status()

    def _build_header(self):
        f = tk.Frame(self, bg=BG)
        f.pack(fill="x", padx=24, pady=(22, 0))
        tk.Label(f, text="⏻", font=("Segoe UI", 26),
                 bg=BG, fg=ACCENT).pack(side="left", padx=(0, 10))
        col = tk.Frame(f, bg=BG)
        col.pack(side="left")
        tk.Label(col, text="Таймер выключения",
                 font=("Segoe UI", 17, "bold"), bg=BG, fg=TEXT1).pack(anchor="w")
        tk.Label(col, text="Windows shutdown scheduler",
                 font=("Segoe UI", 9), bg=BG, fg=TEXT3).pack(anchor="w")

    def _divider(self):
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=10)

    def _build_presets(self):
        tk.Label(self, text="Быстрый выбор",
                 font=("Segoe UI", 9), bg=BG, fg=TEXT2).pack(anchor="w", padx=24)
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=24, pady=(6, 0))
        presets = [
            ("30 мин",   0, 30, 0),
            ("1 час",    1,  0, 0),
            ("2 часа",   2,  0, 0),
            ("3 часа",   3,  0, 0),
            ("6 часов",  6,  0, 0),
            ("12 часов", 12, 0, 0),
        ]
        self._preset_frames = []
        for label, h, m, s in presets:
            self._make_preset(row, label, h, m, s)

    def _make_preset(self, parent, label, h, m, s):
        f = tk.Frame(parent, bg=CARD, cursor="hand2")
        f.pack(side="left", expand=True, fill="x", padx=(0, 5))
        secs = h*3600 + m*60 + s
        top = tk.Label(f, text=label, font=("Segoe UI", 9, "bold"),
                       bg=CARD, fg=TEXT1)
        top.pack(pady=(9, 1))
        sub = tk.Label(f, text=f"{secs}с", font=("Segoe UI", 8),
                       bg=CARD, fg=TEXT3)
        sub.pack(pady=(0, 9))

        def click(_h=h, _m=m, _s=s, _f=f):
            self._h.set(str(_h))
            self._m.set(str(_m))
            self._s.set(str(_s))
            self._update_preview()
            for pf in self._preset_frames:
                col = CARD_HOVER if pf is _f else CARD
                pf.configure(bg=col)
                for c in pf.winfo_children():
                    c.configure(bg=col)

        for w in (f, top, sub):
            w.bind("<Button-1>", lambda e, c=click: c())
            w.bind("<Enter>", lambda e, fw=f: (
                fw.configure(bg=CARD_HOVER),
                [c.configure(bg=CARD_HOVER) for c in fw.winfo_children()]))
            w.bind("<Leave>", lambda e, fw=f: (
                fw.configure(bg=CARD),
                [c.configure(bg=CARD) for c in fw.winfo_children()]))
        self._preset_frames.append(f)

    def _build_manual(self):
        tk.Label(self, text="Ручной ввод",
                 font=("Segoe UI", 9), bg=BG, fg=TEXT2).pack(anchor="w", padx=24)
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=24, pady=(6, 0))
        self._h = tk.StringVar(value="0")
        self._m = tk.StringVar(value="0")
        self._s = tk.StringVar(value="0")
        for var, lbl in [(self._h, "Часы"), (self._m, "Минуты"), (self._s, "Секунды")]:
            col = tk.Frame(row, bg=BG)
            col.pack(side="left", expand=True, fill="x", padx=(0, 8))
            tk.Label(col, text=lbl, font=("Segoe UI", 9),
                     bg=BG, fg=TEXT2).pack(anchor="w")
            e = tk.Entry(col, textvariable=var, font=("Consolas", 18),
                         bg=CARD, fg=TEXT1, insertbackground=ACCENT,
                         relief="flat", bd=10, width=5, justify="center",
                         highlightthickness=1, highlightbackground=BORDER,
                         highlightcolor=ACCENT)
            e.pack(fill="x")
            var.trace_add("write", lambda *_: self._update_preview())

    def _build_preview(self):
        f = tk.Frame(self, bg=CARD)
        f.pack(fill="x", padx=24, pady=(8, 0))
        tk.Label(f, text="Команда:", font=("Segoe UI", 8),
                 bg=CARD, fg=TEXT3).pack(anchor="w", padx=12, pady=(8, 2))
        row = tk.Frame(f, bg=CARD)
        row.pack(fill="x", padx=12, pady=(0, 8))
        self._cmd_var = tk.StringVar(value="shutdown -s -t 0")
        tk.Label(row, textvariable=self._cmd_var,
                 font=("Consolas", 11), bg=CARD, fg=ACCENT).pack(side="left")
        copy_b = tk.Label(row, text="  📋 копировать",
                          font=("Segoe UI", 9), bg=CARD, fg=TEXT2, cursor="hand2")
        copy_b.pack(side="right")
        copy_b.bind("<Button-1>", lambda e: self._copy())

    def _build_countdown(self):
        self._cd_frame = tk.Frame(self, bg=SURFACE)
        self._cd_lbl = tk.Label(self._cd_frame, text="00:00:00",
                                font=("Consolas", 46, "bold"),
                                bg=SURFACE, fg=TEXT1)
        self._cd_lbl.pack(pady=(16, 2))
        self._cd_sub = tk.Label(self._cd_frame, text="до выключения",
                                font=("Segoe UI", 10), bg=SURFACE, fg=TEXT2)
        self._cd_sub.pack()
        pb_bg = tk.Frame(self._cd_frame, bg=BORDER, height=5)
        pb_bg.pack(fill="x", padx=24, pady=(10, 16))
        pb_bg.pack_propagate(False)
        self._pb = tk.Frame(pb_bg, bg=ACCENT, height=5)
        self._pb.place(x=0, y=0, relwidth=1.0, height=5)

    def _build_actions(self):
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=24, pady=(10, 0))
        inner_w = WIN_W - 48
        self._start_btn = FlatButton(
            btn_row, "▶   Запустить таймер",
            cmd=self._start,
            btn_w=inner_w, btn_h=48,
            fill=ACCENT, fill_hover=ACCENT_DIM,
            fnt=("Segoe UI", 13, "bold")
        )
        self._start_btn.pack()
        self._cancel_btn = FlatButton(
            btn_row, "✕   Отменить выключение",
            cmd=self._cancel,
            btn_w=inner_w, btn_h=48,
            fill=DANGER_DIM, fill_hover=DANGER,
            fg=TEXT1,
            fnt=("Segoe UI", 13, "bold")
        )

    def _build_status(self):
        self._status_var = tk.StringVar()
        self._st_lbl = tk.Label(self, textvariable=self._status_var,
                                font=("Segoe UI", 9), bg=BG, fg=TEXT2,
                                wraplength=432, justify="left")
        self._st_lbl.pack(anchor="w", padx=24, pady=(8, 4))

    def _get_secs(self):
        try:
            h = max(0, int(self._h.get() or 0))
            m = max(0, int(self._m.get() or 0))
            s = max(0, int(self._s.get() or 0))
            return h*3600 + m*60 + s
        except ValueError:
            return 0

    def _update_preview(self):
        self._cmd_var.set(f"shutdown -s -t {self._get_secs()}")

    def _copy(self):
        self.clipboard_clear()
        self.clipboard_append(self._cmd_var.get())
        self._status("Команда скопирована в буфер обмена ✓", SUCCESS)
        self.after(2500, lambda: self._status(""))

    def _status(self, msg, color=TEXT2):
        self._status_var.set(msg)
        self._st_lbl.configure(fg=color)

    def _start(self):
        secs = self._get_secs()
        if secs <= 0:
            self._status("Укажите время больше нуля", DANGER)
            return
        ok, err = do_shutdown(secs)
        if not ok:
            self._status(
                f"Ошибка: {err}  —  запустите от имени администратора", DANGER)
            return
        self._total   = secs
        self._remain  = secs
        self._running = True
        self._cd_frame.pack(fill="x", padx=24, pady=(8, 0))
        self._start_btn.pack_forget()
        self._cancel_btn.pack()
        self._status(f"Выключение через {fmt(secs)}  ·  команда принята Windows", SUCCESS)
        threading.Thread(target=self._tick, daemon=True).start()

    def _tick(self):
        while self._running and self._remain >= 0:
            self.after(0, self._refresh_cd)
            time.sleep(1)
            self._remain -= 1
        if self._running:
            self.after(0, self._done)

    def _refresh_cd(self):
        self._cd_lbl.configure(text=fmt(self._remain))
        ratio = max(0.0, self._remain / self._total) if self._total else 0
        self._pb.place(relwidth=ratio)

    def _done(self):
        self._cd_lbl.configure(text="00:00:00")
        self._cd_sub.configure(text="завершается…")
        self._pb.place(relwidth=0)
        self._status("Время вышло — Windows выключается.", DANGER)

    def _cancel(self):
        self._running = False
        ok, err = do_abort()
        self._cd_frame.pack_forget()
        self._cancel_btn.pack_forget()
        self._start_btn.pack()
        if ok:
            self._status("Выключение отменено (shutdown -a выполнен).", TEXT2)
        else:
            self._status(f"Не удалось отменить: {err}", DANGER)


if __name__ == "__main__":
    App().mainloop()
