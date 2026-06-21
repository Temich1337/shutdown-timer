import tkinter as tk
from tkinter import font as tkfont
import subprocess
import threading
import time
import sys

# ── Colors ────────────────────────────────────────────────────────────────────
BG          = "#12121a"
SURFACE     = "#1e1e2a"
CARD        = "#252532"
CARD_HOVER  = "#2e2e3e"
ACCENT      = "#4f8ef7"
ACCENT_DIM  = "#3a6fd4"
DANGER      = "#e05555"
DANGER_DIM  = "#b03e3e"
SUCCESS     = "#4caf7d"
TEXT1       = "#eeeef5"
TEXT2       = "#9898b0"
TEXT3       = "#5a5a78"
BORDER      = "#2e2e42"

WIN_W, WIN_H = 480, 600

# ── Helpers ───────────────────────────────────────────────────────────────────
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

# ── Rounded canvas button ─────────────────────────────────────────────────────
class FlatButton(tk.Canvas):
    def __init__(self, parent, text, cmd, w=200, h=46,
                 fill=ACCENT, fill_hover=ACCENT_DIM,
                 fg=TEXT1, fnt=None, radius=12, **kw):
        super().__init__(parent, width=w, height=h,
                         bg=BG, highlightthickness=0, **kw)
        self._fill      = fill
        self._fill_h    = fill_hover
        self._fg        = fg
        self._text      = text
        self._fnt       = fnt or ("Segoe UI", 11, "bold")
        self._r         = radius
        self._cmd       = cmd
        self._w, self._h = w, h
        self._draw(fill)
        self.bind("<Enter>",        lambda e: self._draw(self._fill_h))
        self.bind("<Leave>",        lambda e: self._draw(self._fill))
        self.bind("<Button-1>",     lambda e: (self._draw(fill), self.after(80, cmd)))
        self.configure(cursor="hand2")

    def _draw(self, color):
        self.delete("all")
        w, h, r = self._w, self._h, self._r
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

    def recolor(self, fill, fill_h):
        self._fill, self._fill_h = fill, fill_h
        self._draw(fill)
        self.bind("<Enter>", lambda e: self._draw(fill_h))
        self.bind("<Leave>", lambda e: self._draw(fill))

# ── App ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Таймер выключения")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center()

        self._total   = 0
        self._remain  = 0
        self._running = False

        self._build()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - WIN_W) // 2
        y = (self.winfo_screenheight() - WIN_H) // 2
        self.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")

    # ── Build UI ───────────────────────────────────────────────────────────────
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
        f.pack(side="left", expand=True, fill="x", padx=(0, 6))
        secs = h*3600 + m*60 + s
        top  = tk.Label(f, text=label, font=("Segoe UI", 10, "bold"),
                        bg=CARD, fg=TEXT1, pady=0)
        top.pack(pady=(9, 1))
        sub  = tk.Label(f, text=f"{secs} с", font=("Segoe UI", 8),
                        bg=CARD, fg=TEXT3)
        sub.pack(pady=(0, 9))

        def click(_h=h, _m=m, _s=s, _f=f):
            self._h.set(str(_h)); self._m.set(str(_m)); self._s.set(str(_s))
            self._update_preview()
            for pf in self._preset_frames:
                col = CARD_HOVER if pf is _f else CARD
                pf.configure(bg=col)
                for c in pf.winfo_children(): c.configure(bg=col)

        for w in (f, top, sub):
            w.bind("<Button-1>", lambda e, c=click: c())
            w.bind("<Enter>", lambda e, fw=f: [fw.configure(bg=CARD_HOVER)] +
                   [c.configure(bg=CARD_HOVER) for c in fw.winfo_children()])
            w.bind("<Leave>", lambda e, fw=f: [fw.configure(bg=CARD)] +
                   [c.configure(bg=CARD) for c in fw.winfo_children()])
        self._preset_frames.append(f)

    def _build_manual(self):
        tk.Label(self, text="Ручной ввод",
                 font=("Segoe UI", 9), bg=BG, fg=TEXT2).pack(anchor="w", padx=24)
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=24, pady=(6, 0))
        self._h = tk.StringVar(value="0")
        self._m = tk.StringVar(value="0")
        self._s = tk.StringVar(value="0")
        for var, lbl in [(self._h,"Часы"),(self._m,"Минуты"),(self._s,"Секунды")]:
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
                 bg=CARD, fg=TEXT3).pack(anchor="w", padx=12, pady=(8,2))
        row = tk.Frame(f, bg=CARD)
        row.pack(fill="x", padx=12, pady=(0, 8))
        self._cmd_var = tk.StringVar(value="shutdown -s -t 0")
        tk.Label(row, textvariable=self._cmd_var,
                 font=("Consolas", 11), bg=CARD, fg=ACCENT).pack(side="left")
        copy_b = tk.Label(row, text="  📋 копировать",
                          font=("Segoe UI", 9), bg=CARD, fg=TEXT2,
                          cursor="hand2")
        copy_b.pack(side="right")
        copy_b.bind("<Button-1>", lambda e: self._copy())

    def _build_countdown(self):
        self._cd_frame = tk.Frame(self, bg=SURFACE)
        # hidden by default — shown when timer starts
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
        self._btn_row = tk.Frame(self, bg=BG)
        self._btn_row.pack(fill="x", padx=24, pady=(10, 0))
        self._start_btn = FlatButton(
            self._btn_row, "▶   Запустить таймер",
            cmd=self._start, w=432, h=48,
            fill=ACCENT, fill_hover=ACCENT_DIM,
            fnt=("Segoe UI", 13, "bold")
        )
        self._start_btn.pack()
        self._cancel_btn = FlatButton(
            self._btn_row, "✕   Отменить выключение",
            cmd=self._cancel, w=432, h=48,
            fill=DANGER_DIM, fill_hover=DANGER,
            fg=TEXT1, fnt=("Segoe UI", 13, "bold")
        )

    def _build_status(self):
        self._status_var = tk.StringVar()
        self._status_fg  = tk.StringVar(value=TEXT2)
        self._st_lbl = tk.Label(self, textvariable=self._status_var,
                                 font=("Segoe UI", 9), bg=BG, fg=TEXT2,
                                 wraplength=432, justify="left")
        self._st_lbl.pack(anchor="w", padx=24, pady=(8, 4))

    # ── Logic ──────────────────────────────────────────────────────────────────
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
                f"Ошибка: {err}\n"
                "Запустите программу от имени администратора (ПКМ → Запуск от имени администратора).",
                DANGER
            )
            return

        self._total  = secs
        self._remain = secs
        self._running = True

        self._cd_frame.pack(fill="x", padx=24, pady=(8, 0))
        self._start_btn.pack_forget()
        self._cancel_btn.pack()
        self._status(
            f"Выключение через {fmt(secs)} · команда принята Windows",
            SUCCESS
        )
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
