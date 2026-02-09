import tkinter as tk
from tkinter import Canvas
import json
import urllib.request
import urllib.parse

API_BASE = "https://todo-app-qko4.onrender.com/api/todos"
CATEGORIES = ["Ruofei", "Ruiqi", "Family"]


def _api(method, path="", body=None):
    """Call the remote API. Returns parsed JSON or None."""
    url = API_BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# --- Color Palette (warm light) ---
BG = "#faf8f5"           # warm cream
SURFACE = "#ffffff"       # white cards
SURFACE_HOVER = "#f5f0eb" # warm hover
BORDER = "#e8e0d8"        # warm border
TEXT = "#2c2418"          # warm dark brown
TEXT_SEC = "#8a7e72"      # warm medium
TEXT_DIM = "#b5aa9e"      # warm muted
ACCENT = "#d97706"        # amber
ACCENT_HOVER = "#b45309"  # darker amber
DONE = "#16a34a"          # green
DONE_DIM = "#22876a"
DANGER = "#dc2626"        # red
DANGER_HOVER = "#b91c1c"
TAB_BG = "#faf8f5"

FONT = "Segoe UI"


class RoundedFrame(Canvas):
    """A canvas that draws a rounded rectangle background."""

    def __init__(self, parent, bg_color, radius=14, border_color=None, **kwargs):
        super().__init__(parent, highlightthickness=0, bg=parent["bg"], **kwargs)
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius
        self._inner = tk.Frame(self, bg=bg_color)
        self.create_window(0, 0, window=self._inner, anchor="nw")
        self.bind("<Configure>", self._redraw)

    @property
    def inner(self):
        return self._inner

    def _redraw(self, event=None):
        self.delete("bg")
        w, h, r = self.winfo_width(), self.winfo_height(), self.radius
        if w < 2 or h < 2:
            return
        self._inner.configure(width=w - 2, height=h - 2)
        self.coords(self.find_all()[0] if self.find_all() else self.create_window(0, 0, window=self._inner, anchor="nw"), 1, 1)
        outline = self.border_color or self.bg_color
        self._round_rect(1, 1, w - 1, h - 1, r, fill=self.bg_color, outline=outline, tags="bg")
        self.tag_lower("bg")
        self._inner.place(x=1, y=1, width=w - 2, height=h - 2)

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r,
            x1, y1 + r, x1, y1,
        ]
        self.create_polygon(points, smooth=True, **kwargs)

    def set_bg(self, color):
        self.bg_color = color
        self._redraw()


class TodoApp:
    def __init__(self) -> None:
        self.current_category = CATEGORIES[0]

        self.root = tk.Tk()
        self.root.title("Todo")
        self.root.configure(bg=BG)
        self.root.geometry("500x680")
        self.root.minsize(400, 480)

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        # ── Header ──
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(24, 0))

        tk.Label(
            header, text="Todo", font=(FONT, 24, "bold"),
            bg=BG, fg=TEXT,
        ).pack(side="left")

        cat_label = tk.Label(
            header, text="", font=(FONT, 12),
            bg=BG, fg=TEXT_SEC,
        )
        cat_label.pack(side="right", pady=(8, 0))
        self._cat_label = cat_label

        # ── Tab Bar ──
        tab_bar = tk.Frame(self.root, bg=BG)
        tab_bar.pack(fill="x", padx=24, pady=(16, 0))

        self.tab_buttons = {}
        self.tab_indicators = {}
        for cat in CATEGORIES:
            frame = tk.Frame(tab_bar, bg=BG)
            frame.pack(side="left", padx=(0, 4), fill="x", expand=True)

            btn = tk.Label(
                frame, text=cat, font=(FONT, 12, "bold"),
                bg=TAB_BG, fg=TEXT_DIM, pady=10, cursor="hand2",
            )
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, c=cat: self.switch_category(c))
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=TEXT_SEC) if b != self.tab_buttons.get(self.current_category) else None)
            btn.bind("<Leave>", lambda e, b=btn, c=cat: b.config(fg=TEXT_DIM) if c != self.current_category else None)

            indicator = tk.Frame(frame, bg=BG, height=3)
            indicator.pack(fill="x")

            self.tab_buttons[cat] = btn
            self.tab_indicators[cat] = indicator

        # ── Divider ──
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 16))

        # ── Input Area ──
        input_area = tk.Frame(self.root, bg=BG)
        input_area.pack(fill="x", padx=24, pady=(0, 12))

        entry_wrap = RoundedFrame(input_area, SURFACE, radius=12, border_color=BORDER, height=48)
        entry_wrap.pack(side="left", fill="x", expand=True, padx=(0, 10))
        entry_wrap.inner.configure(bg=SURFACE)

        self.entry = tk.Entry(
            entry_wrap.inner, font=(FONT, 13), bg=SURFACE, fg=TEXT,
            insertbackground=ACCENT, relief="flat", bd=0,
            highlightthickness=0,
        )
        self.entry.place(relx=0, rely=0.5, anchor="w", x=14, relwidth=0.9)
        self.entry.insert(0, "What needs to be done?")
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)
        self.entry.bind("<Return>", lambda e: self.add_todo())
        self.entry.config(fg=TEXT_DIM)

        add_canvas = RoundedFrame(input_area, ACCENT, radius=12, height=48, width=72)
        add_canvas.pack(side="right")
        add_canvas.inner.configure(bg=ACCENT)
        add_label = tk.Label(
            add_canvas.inner, text="+", font=(FONT, 20, "bold"),
            bg=ACCENT, fg="#ffffff", cursor="hand2",
        )
        add_label.place(relx=0.5, rely=0.5, anchor="center")
        add_label.bind("<Button-1>", lambda e: self.add_todo())
        add_label.bind("<Enter>", lambda e: (add_canvas.set_bg(ACCENT_HOVER), add_label.config(bg=ACCENT_HOVER)))
        add_label.bind("<Leave>", lambda e: (add_canvas.set_bg(ACCENT), add_label.config(bg=ACCENT)))

        # ── Scrollable List ──
        list_outer = tk.Frame(self.root, bg=BG)
        list_outer.pack(fill="both", expand=True, padx=24, pady=(0, 0))

        self.canvas = tk.Canvas(list_outer, bg=BG, highlightthickness=0, bd=0)
        self.scroll_frame = tk.Frame(self.canvas, bg=BG)

        self.scroll_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self._canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._canvas_window, width=e.width))

        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # ── Status Bar ──
        self.status = tk.Label(
            self.root, text="", font=(FONT, 10),
            bg=SURFACE, fg=TEXT_DIM, anchor="center", pady=8,
        )
        self.status.pack(fill="x", side="bottom")

    # ── Tab Logic ──

    def _update_tabs(self) -> None:
        for cat, btn in self.tab_buttons.items():
            if cat == self.current_category:
                btn.config(bg=TAB_BG, fg=ACCENT)
                self.tab_indicators[cat].config(bg=ACCENT)
            else:
                btn.config(bg=TAB_BG, fg=TEXT_DIM)
                self.tab_indicators[cat].config(bg=BG)
        self._cat_label.config(text=self.current_category)

    def switch_category(self, category: str) -> None:
        self.current_category = category
        self.refresh()

    # ── Placeholder ──

    def _clear_placeholder(self, event):
        if self.entry.get() == "What needs to be done?":
            self.entry.delete(0, "end")
            self.entry.config(fg=TEXT)

    def _restore_placeholder(self, event):
        if not self.entry.get().strip():
            self.entry.delete(0, "end")
            self.entry.insert(0, "What needs to be done?")
            self.entry.config(fg=TEXT_DIM)

    # ── Refresh ──

    def refresh(self) -> None:
        self._update_tabs()

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        cat_param = urllib.parse.quote(self.current_category)
        todos = _api("GET", f"?category={cat_param}")

        if not todos:
            empty_frame = tk.Frame(self.scroll_frame, bg=BG)
            empty_frame.pack(fill="x", pady=60)
            tk.Label(
                empty_frame, text="\u2714", font=(FONT, 36),
                bg=BG, fg=TEXT_DIM,
            ).pack()
            tk.Label(
                empty_frame, text="All clear!", font=(FONT, 14),
                bg=BG, fg=TEXT_DIM,
            ).pack(pady=(4, 0))
            self.status.config(text="")
            return

        for todo in todos:
            self._make_row(todo)

        remaining = sum(1 for t in todos if not t["completed"])
        total = len(todos)
        self.status.config(text=f"{remaining} remaining  \u2022  {total} total")

        self.scroll_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # ── Row ──

    def _make_row(self, todo: dict) -> None:
        completed = bool(todo["completed"])

        row_canvas = RoundedFrame(
            self.scroll_frame, SURFACE, radius=12,
            border_color=BORDER if not completed else SURFACE,
            height=56,
        )
        row_canvas.pack(fill="x", pady=4)
        row = row_canvas.inner
        row.configure(bg=SURFACE)

        # Hover effect on the row
        def on_enter(e):
            row_canvas.set_bg(SURFACE_HOVER)
            for child in row.winfo_children():
                try:
                    child.config(bg=SURFACE_HOVER)
                except tk.TclError:
                    pass

        def on_leave(e):
            row_canvas.set_bg(SURFACE)
            for child in row.winfo_children():
                try:
                    child.config(bg=SURFACE)
                except tk.TclError:
                    pass

        row_canvas.bind("<Enter>", on_enter)
        row_canvas.bind("<Leave>", on_leave)

        # Checkbox circle
        check_size = 22
        check_canvas = tk.Canvas(
            row, width=check_size, height=check_size,
            bg=SURFACE, highlightthickness=0, cursor="hand2",
        )
        check_canvas.place(x=16, rely=0.5, anchor="w")

        if completed:
            check_canvas.create_oval(1, 1, check_size - 1, check_size - 1, fill=DONE, outline=DONE)
            check_canvas.create_text(
                check_size // 2, check_size // 2, text="\u2713",
                font=(FONT, 10, "bold"), fill="#ffffff",
            )
        else:
            check_canvas.create_oval(1, 1, check_size - 1, check_size - 1, fill="", outline=BORDER, width=2)

        check_canvas.bind("<Button-1>", lambda e, tid=todo["id"]: self.toggle_todo(tid))

        # Title
        title_text = todo["title"]
        title_fg = TEXT_DIM if completed else TEXT
        title_font = (FONT, 13, "overstrike") if completed else (FONT, 13)
        title = tk.Label(
            row, text=title_text, font=title_font, bg=SURFACE,
            fg=title_fg, anchor="w", cursor="hand2",
        )
        title.place(x=50, rely=0.5, anchor="w", relwidth=0.7)
        title.bind("<Button-1>", lambda e, tid=todo["id"]: self.toggle_todo(tid))

        # Delete button
        delete = tk.Label(
            row, text="\u2715", font=(FONT, 11), bg=SURFACE,
            fg=SURFACE, width=3, cursor="hand2",
        )
        delete.place(relx=1.0, rely=0.5, anchor="e", x=-10)
        delete.bind("<Enter>", lambda e: delete.config(fg=DANGER))
        delete.bind("<Leave>", lambda e: delete.config(fg=SURFACE))
        delete.bind("<Button-1>", lambda e, tid=todo["id"]: self.delete_todo(tid))

        # Show delete on row hover
        def row_enter(e, d=delete):
            on_enter(e)
            d.config(fg=TEXT_DIM)

        def row_leave(e, d=delete):
            on_leave(e)
            d.config(fg=SURFACE)

        row_canvas.bind("<Enter>", row_enter)
        row_canvas.bind("<Leave>", row_leave)

    # ── Actions ──

    def add_todo(self) -> None:
        title = self.entry.get().strip()
        if not title or title == "What needs to be done?":
            return
        _api("POST", "", {"title": title, "category": self.current_category})
        self.entry.delete(0, "end")
        self.refresh()
        self.entry.focus_set()

    def toggle_todo(self, todo_id: int) -> None:
        _api("PUT", f"/{todo_id}", {})
        self.refresh()

    def delete_todo(self, todo_id: int) -> None:
        _api("DELETE", f"/{todo_id}")
        self.refresh()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    TodoApp().run()
