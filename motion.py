from manim import *
import json

NAVY = "#0d1b2a"; ORANGE = "#E8552F"; OFFWHITE = "#e0e1dd"; SLATE = "#778da9"

class BrandSting(Scene):
    def construct(self):
        self.camera.background_color = NAVY
        l1 = Text("BUILD  LEARN  AUTOMATE", font="monospace", color=OFFWHITE, weight=BOLD).scale(0.8)
        l2 = Text("GROW", font="monospace", color=ORANGE, weight=BOLD).scale(1.4)
        l2.next_to(l1, DOWN, buff=0.3)
        self.play(FadeIn(l1, shift=UP*0.3), run_time=0.7)
        self.play(Write(l2), run_time=0.9)
        self.wait(0.8)

class RulesBuild(Scene):
    def construct(self):
        self.camera.background_color = NAVY
        title = Text("3 RULES", font="monospace", color=ORANGE, weight=BOLD).scale(0.9)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.7)
        rules = [
            ("1. ONLY 5-10%", "of your portfolio"),
            ("2. SIP > LUMPSUM", "buy monthly, never all at a record"),
            ("3. ETF > JEWELLERY", "no making charges"),
        ]
        cards = VGroup()
        for i, (big, small) in enumerate(rules):
            card = RoundedRectangle(corner_radius=0.15, width=10, height=1.35,
                                    stroke_color=SLATE, stroke_width=1.5, fill_color="#1b263b", fill_opacity=0.7)
            card.move_to(UP * (1.6 - i * 1.7))
            big_t = Text(big, font="monospace", color=ORANGE, weight=BOLD).scale(0.65)
            big_t.move_to(card.get_center() + UP * 0.25)
            small_t = Text(small, font="monospace", color=OFFWHITE).scale(0.45)
            small_t.move_to(card.get_center() + DOWN * 0.3)
            g = VGroup(card, big_t, small_t)
            cards.add(g)
            self.play(FadeIn(g, shift=RIGHT * 0.5), run_time=0.8)
        self.wait(1.0)
