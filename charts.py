"""Beat 3 + Beat 5 charts for ch02_video1 — manim, brand colors, 1280x720."""
from manim import *
import json

data = json.load(open('/opt/kinocut-work/ch02_video1/chart_data.json'))
NAVY = "#0d1b2a"
ORANGE = "#E8552F"
SLATE = "#778da9"
OFFWHITE = "#e0e1dd"
GREEN = "#4ade80"
RED = "#f87171"


class Beat3GoldLine(Scene):
    def construct(self):
        self.camera.background_color = NAVY
        prices = data['gold']
        n = len(prices)
        lo, hi = min(prices), max(prices)

        title = Text("GOLD — 1 MONTH", font="monospace", color=OFFWHITE, weight=BOLD).scale(0.55)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.6)

        ax = Axes(
            x_range=[0, n - 1, 5], y_range=[lo - 20, hi + 20, 50],
            x_length=10, y_length=4.2,
            tips=False,
            axis_config={"color": SLATE, "stroke_width": 2},
        )
        ax.to_edge(DOWN, buff=0.5)
        self.play(Create(ax), run_time=0.8)

        pts = [ax.c2p(i, p) for i, p in enumerate(prices)]
        line = VMobject(color=ORANGE, stroke_width=5)
        line.set_points_smoothly(pts)
        self.play(Create(line), run_time=2.2, rate_func=linear)

        # record-zone marker
        last = pts[-1]
        dot = Dot(last, color=ORANGE, radius=0.09)
        label = Text("GOLD $4,477", font="monospace", color=ORANGE, weight=BOLD).scale(0.55)
        label.next_to(last, UP, buff=0.35)
        label2 = Text("+5.5% in 30 days", font="monospace", color=OFFWHITE).scale(0.45)
        label2.next_to(label, UP, buff=0.15)
        self.play(FadeIn(dot, scale=2), FadeIn(label), FadeIn(label2), run_time=0.8)

        sub = Text("RECORD ZONE — highest ever", font="monospace", color=SLATE).scale(0.5)
        sub.next_to(ax, DOWN, buff=0.3)
        self.play(FadeIn(sub), run_time=0.5)
        self.wait(0.8)


class Beat5Compare(Scene):
    def construct(self):
        self.camera.background_color = NAVY
        title = Text("THIS MONTH", font="monospace", color=OFFWHITE, weight=BOLD).scale(0.6)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.5)

        bars_data = [
            ("GOLD", data['gold_chg'], ORANGE),
            ("BTC", data['btc_chg'], GREEN),
            ("NIFTY", data['nifty_chg'], RED),
        ]
        # hand-rolled bars (BarChart needs latex; avoid)
        max_h = 3.2
        baseline_y = -2.6
        bar_rects = []
        labels = []
        for i, (name, val, color) in enumerate(bars_data):
            h = max(val, 0.3) / 26 * max_h
            rect = Rectangle(width=1.4, height=h, fill_color=color, fill_opacity=1, stroke_width=0)
            x = -3.6 + i * 3.0
            rect.move_to(np.array([x, baseline_y + h / 2, 0]))
            bar_rects.append(rect)
            nm = Text(name, font="monospace", color=OFFWHITE).scale(0.5)
            nm.move_to(np.array([x, baseline_y - 0.4, 0]))
            labels.append(nm)
        self.play(LaggedStart(*[GrowFromEdge(r, DOWN) for r in bar_rects], lag_ratio=0.2), run_time=1.4)
        self.play(LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.15), run_time=0.6)

        # value labels above bars
        for i, (name, val, color) in enumerate(bars_data):
            sign = "+" if val >= 0 else ""
            lbl = Text(f"{sign}{val}%", font="monospace", color=color, weight=BOLD).scale(0.55)
            lbl.next_to(bar_rects[i], UP, buff=0.15)
            self.play(FadeIn(lbl, shift=UP * 0.2), run_time=0.4)

        note = Text("gold moved while equities sat still", font="monospace", color=SLATE).scale(0.5)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note), run_time=0.5)
        self.wait(0.8)
