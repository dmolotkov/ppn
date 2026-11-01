#!/usr/bin/env python3
"""Generate a 2-week family football training PDF with visual exercise diagrams."""

from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
    Flowable,
)

# --- Fonts (Cyrillic) ---
pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

# --- Palette (grass / chalk / amber — clear sports look) ---
GREEN_DARK = HexColor("#1B5E3B")
GREEN_MID = HexColor("#2E7D4F")
GREEN_LIGHT = HexColor("#E8F5E9")
GREEN_FIELD = HexColor("#C8E6C9")
AMBER = HexColor("#E67E22")
AMBER_LIGHT = HexColor("#FEF5EB")
INK = HexColor("#1A2E1F")
MUTED = HexColor("#4A6354")
LINE = HexColor("#FFFFFF")
CARD_BG = HexColor("#FFFFFF")
PAGE_BG = HexColor("#F4F7F4")
BLUE_KID = HexColor("#1E88E5")
ORANGE_KID = HexColor("#FB8C00")
TEAL_KID = HexColor("#00897B")
RED_TAG = HexColor("#C62828")
PARENT = HexColor("#5D4037")

PAGE_W, PAGE_H = A4
MARGIN = 14 * mm


def styles():
    s = getSampleStyleSheet()
    s.add(
        ParagraphStyle(
            name="CoverTitle",
            fontName="DejaVuBold",
            fontSize=26,
            leading=32,
            textColor=white,
            alignment=TA_CENTER,
        )
    )
    s.add(
        ParagraphStyle(
            name="CoverSub",
            fontName="DejaVu",
            fontSize=12,
            leading=16,
            textColor=HexColor("#DCEEE0"),
            alignment=TA_CENTER,
        )
    )
    s.add(
        ParagraphStyle(
            name="H1",
            fontName="DejaVuBold",
            fontSize=16,
            leading=20,
            textColor=GREEN_DARK,
            spaceBefore=2,
            spaceAfter=6,
        )
    )
    s.add(
        ParagraphStyle(
            name="H2",
            fontName="DejaVuBold",
            fontSize=12,
            leading=15,
            textColor=GREEN_DARK,
            spaceBefore=0,
            spaceAfter=4,
        )
    )
    s.add(
        ParagraphStyle(
            name="Body",
            fontName="DejaVu",
            fontSize=9,
            leading=12,
            textColor=INK,
        )
    )
    s.add(
        ParagraphStyle(
            name="Small",
            fontName="DejaVu",
            fontSize=8,
            leading=10.5,
            textColor=MUTED,
        )
    )
    s.add(
        ParagraphStyle(
            name="Tip",
            fontName="DejaVu",
            fontSize=8.5,
            leading=11,
            textColor=HexColor("#6A3B0E"),
        )
    )
    s.add(
        ParagraphStyle(
            name="Phrase",
            fontName="DejaVuBold",
            fontSize=9.5,
            leading=12,
            textColor=GREEN_DARK,
            alignment=TA_CENTER,
        )
    )
    s.add(
        ParagraphStyle(
            name="Footer",
            fontName="DejaVu",
            fontSize=7.5,
            leading=9,
            textColor=MUTED,
            alignment=TA_CENTER,
        )
    )
    return s


class ColoredRect(Flowable):
    def __init__(self, width, height, fill, radius=6):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.fill = fill
        self.radius = radius

    def draw(self):
        self.canv.setFillColor(self.fill)
        self.canv.roundRect(0, 0, self.width, self.height, self.radius, fill=1, stroke=0)


class Diagram(Flowable):
    """Base canvas for a schematic; subclasses draw in draw_scene()."""

    def __init__(self, width=72 * mm, height=48 * mm, title=""):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.title = title

    def draw(self):
        c = self.canv
        # field background
        c.setFillColor(GREEN_FIELD)
        c.setStrokeColor(GREEN_MID)
        c.setLineWidth(1.2)
        c.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=1)
        # subtle grass stripes
        c.setFillColor(HexColor("#B7DEB9"))
        stripe_w = self.width / 8
        for i in range(0, 8, 2):
            c.rect(i * stripe_w, 0, stripe_w, self.height, fill=1, stroke=0)
        # redraw border
        c.setStrokeColor(GREEN_MID)
        c.setLineWidth(1.2)
        c.roundRect(0, 0, self.width, self.height, 5, fill=0, stroke=1)
        self.draw_scene(c)
        if self.title:
            c.setFillColor(GREEN_DARK)
            c.setFont("DejaVuBold", 7)
            c.drawCentredString(self.width / 2, self.height - 9, self.title)

    def draw_scene(self, c):
        pass

    # helpers
    def player(self, c, x, y, color, label="", r=6):
        c.setFillColor(color)
        c.setStrokeColor(white)
        c.setLineWidth(0.8)
        c.circle(x, y, r, fill=1, stroke=1)
        if label:
            c.setFillColor(white)
            c.setFont("DejaVuBold", 6)
            c.drawCentredString(x, y - 2, label)

    def cone(self, c, x, y):
        c.setFillColor(AMBER)
        path = c.beginPath()
        path.moveTo(x, y + 7)
        path.lineTo(x - 5, y - 3)
        path.lineTo(x + 5, y - 3)
        path.close()
        c.drawPath(path, fill=1, stroke=0)

    def ball(self, c, x, y, r=3.5):
        c.setFillColor(white)
        c.setStrokeColor(INK)
        c.setLineWidth(0.6)
        c.circle(x, y, r, fill=1, stroke=1)
        c.setStrokeColor(INK)
        c.line(x - r * 0.6, y, x + r * 0.6, y)
        c.line(x, y - r * 0.6, x, y + r * 0.6)

    def arrow(self, c, x1, y1, x2, y2, color=AMBER, width=1.5, dashed=False):
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(width)
        if dashed:
            c.setDash(3, 2)
        else:
            c.setDash()
        c.line(x1, y1, x2, y2)
        c.setDash()
        # arrowhead
        import math

        angle = math.atan2(y2 - y1, x2 - x1)
        size = 5
        a1 = angle + 2.6
        a2 = angle - 2.6
        path = c.beginPath()
        path.moveTo(x2, y2)
        path.lineTo(x2 + size * math.cos(a1), y2 + size * math.sin(a1))
        path.lineTo(x2 + size * math.cos(a2), y2 + size * math.sin(a2))
        path.close()
        c.drawPath(path, fill=1, stroke=0)

    def label(self, c, x, y, text, color=INK, size=6.5):
        c.setFillColor(color)
        c.setFont("DejaVu", size)
        c.drawString(x, y, text)

    def dashed_box(self, c, x, y, w, h):
        c.setStrokeColor(GREEN_DARK)
        c.setDash(2, 2)
        c.setLineWidth(1)
        c.rect(x, y, w, h, fill=0, stroke=1)
        c.setDash()


# --- Concrete diagrams ---


class TagDiagram(Diagram):
    def draw_scene(self, c):
        self.player(c, 28, 22, RED_TAG, "В")
        self.player(c, 95, 55, BLUE_KID, "6")
        self.player(c, 130, 28, ORANGE_KID, "9")
        self.player(c, 160, 50, TEAL_KID, "11")
        self.arrow(c, 40, 28, 85, 48, RED_TAG)
        self.label(c, 8, 6, "В = водящий (касание рукой)")
        # home zone for 6yo
        c.setFillColor(HexColor("#FFF9C4"))
        c.setStrokeColor(AMBER)
        c.setDash(2, 2)
        c.roundRect(155, 8, 40, 18, 3, fill=1, stroke=1)
        c.setDash()
        self.label(c, 160, 14, "дом 6 лет", MUTED, 6)


class SprintDiagram(Diagram):
    def __init__(self, meters="10 м", **kw):
        self.meters = meters
        super().__init__(**kw)

    def draw_scene(self, c):
        self.cone(c, 35, 28)
        self.cone(c, 170, 28)
        self.player(c, 35, 48, ORANGE_KID, "→")
        self.arrow(c, 48, 48, 155, 48, AMBER, 2)
        self.arrow(c, 155, 22, 48, 22, MUTED, 1.2, dashed=True)
        self.label(c, 85, 54, f"рывок {self.meters}", GREEN_DARK, 7)
        self.label(c, 85, 10, "назад шагом", MUTED, 6.5)


class PushChaseDiagram(Diagram):
    def draw_scene(self, c):
        self.player(c, 40, 35, ORANGE_KID, "9")
        self.ball(c, 58, 35)
        self.arrow(c, 65, 35, 120, 35, AMBER, 1.5, dashed=True)
        self.ball(c, 130, 35)
        self.arrow(c, 48, 48, 120, 48, BLUE_KID, 2)
        self.label(c, 70, 54, "1. толкнул   2. догнал", GREEN_DARK, 7)
        self.cone(c, 155, 20)
        self.label(c, 8, 8, "потом остановить ногой", MUTED, 6.5)


class SquareNoStandDiagram(Diagram):
    def draw_scene(self, c):
        self.dashed_box(c, 35, 10, 140, 55)
        self.cone(c, 35, 12)
        self.cone(c, 175, 12)
        self.cone(c, 35, 62)
        self.cone(c, 175, 62)
        self.player(c, 70, 40, BLUE_KID, "6")
        self.player(c, 110, 28, ORANGE_KID, "9")
        self.player(c, 145, 48, TEAL_KID, "11")
        self.ball(c, 120, 32)
        self.arrow(c, 118, 35, 140, 45, AMBER, 1.5)
        self.label(c, 55, 68, "квадрат ~8×8 м  •  с мячом ≤ 2 сек", GREEN_DARK, 6.5)
        self.label(c, 40, 2, "пас или движение вперёд", MUTED, 6)


class ShotsDiagram(Diagram):
    def draw_scene(self, c):
        # goal
        c.setStrokeColor(INK)
        c.setLineWidth(2)
        c.line(160, 15, 160, 60)
        c.line(160, 15, 185, 15)
        c.line(160, 60, 185, 60)
        self.cone(c, 160, 12)
        self.cone(c, 160, 62)
        self.player(c, 55, 38, PARENT, "Р")
        self.ball(c, 70, 38)
        self.arrow(c, 75, 38, 110, 38, MUTED, 1.2, dashed=True)
        self.player(c, 115, 38, ORANGE_KID, "→")
        self.ball(c, 128, 38)
        self.arrow(c, 133, 38, 155, 38, AMBER, 2)
        self.label(c, 40, 8, "Р пасует → удар", MUTED, 6.5)


class TagWithBallDiagram(Diagram):
    def draw_scene(self, c):
        self.player(c, 40, 40, RED_TAG, "В")
        self.player(c, 100, 50, BLUE_KID, "6")
        self.ball(c, 112, 50)
        self.player(c, 145, 25, ORANGE_KID, "9")
        self.ball(c, 157, 25)
        self.arrow(c, 52, 40, 90, 48, RED_TAG)
        self.label(c, 8, 8, "водящий без мяча; у остальных мяч у ноги", MUTED, 6.5)


class ShuttleDiagram(Diagram):
    def draw_scene(self, c):
        self.cone(c, 40, 30)
        self.cone(c, 100, 30)
        self.cone(c, 170, 30)
        self.label(c, 32, 12, "старт", MUTED, 6)
        self.label(c, 92, 12, "5 м", MUTED, 6)
        self.label(c, 160, 12, "10 м", MUTED, 6)
        self.player(c, 40, 50, TEAL_KID, "→")
        self.arrow(c, 48, 50, 92, 50, AMBER, 1.5)
        self.arrow(c, 92, 42, 48, 42, MUTED, 1, dashed=True)
        self.arrow(c, 48, 58, 160, 58, AMBER, 1.5)
        self.label(c, 70, 64, "туда-обратно, потом до 10 м", GREEN_DARK, 6.5)


class ReceivePassMoveDiagram(Diagram):
    def draw_scene(self, c):
        self.player(c, 40, 38, PARENT, "Р")
        self.ball(c, 55, 38)
        self.arrow(c, 60, 38, 100, 38, MUTED, 1.2, dashed=True)
        self.player(c, 110, 38, ORANGE_KID, "9")
        self.arrow(c, 118, 45, 150, 55, AMBER, 2)
        self.arrow(c, 110, 28, 55, 28, BLUE_KID, 1.2)
        self.label(c, 55, 60, "1 принять  2 отдать  3 сдвинуться", GREEN_DARK, 6.5)
        self.label(c, 8, 8, "3 шага в сторону / вперёд", MUTED, 6.5)


class TwoVOneDiagram(Diagram):
    def draw_scene(self, c):
        self.player(c, 60, 50, BLUE_KID, "6")
        self.player(c, 120, 50, TEAL_KID, "11")
        self.ball(c, 72, 50)
        self.arrow(c, 78, 50, 108, 50, AMBER, 1.5)
        self.player(c, 90, 22, ORANGE_KID, "9")
        self.arrow(c, 90, 30, 90, 42, RED_TAG, 1.2)
        self.label(c, 40, 64, "двое пасуют • один отбирает", GREEN_DARK, 6.5)
        self.label(c, 8, 6, "цель: 5 пасов подряд", MUTED, 6.5)


class SnakeRunDiagram(Diagram):
    def draw_scene(self, c):
        for x in (45, 85, 125, 165):
            self.cone(c, x, 28)
        self.player(c, 30, 48, ORANGE_KID, "→")
        # zigzag
        self.arrow(c, 38, 48, 45, 40, AMBER, 1.3)
        self.arrow(c, 45, 40, 85, 55, AMBER, 1.3)
        self.arrow(c, 85, 55, 125, 40, AMBER, 1.3)
        self.arrow(c, 125, 40, 165, 55, AMBER, 1.3)
        self.label(c, 50, 10, "змейка между ориентирами", MUTED, 6.5)


class StartsDiagram(Diagram):
    def draw_scene(self, c):
        poses = [("лицом", 35), ("боком", 75), ("спиной", 115), ("сидя", 155)]
        for i, (name, x) in enumerate(poses):
            self.player(c, x, 45, [BLUE_KID, ORANGE_KID, TEAL_KID, PARENT][i], str(i + 1))
            self.arrow(c, x, 55, x, 68, AMBER, 1.2)
            self.label(c, x - 12, 18, name, MUTED, 6)
        self.cone(c, 35, 70)
        self.cone(c, 155, 70)
        self.label(c, 55, 6, "свисток → рывок 8–10 м", GREEN_DARK, 6.5)


class PassAndSprintDiagram(Diagram):
    def draw_scene(self, c):
        self.player(c, 50, 30, PARENT, "Р")
        self.player(c, 50, 50, ORANGE_KID, "9")
        self.ball(c, 50, 40)
        self.arrow(c, 50, 45, 50, 36, MUTED, 1)
        self.arrow(c, 60, 50, 140, 50, AMBER, 2)
        self.cone(c, 155, 48)
        self.label(c, 70, 58, "пас → сразу рывок", GREEN_DARK, 7)
        self.label(c, 8, 8, "8–10 м к ориентиру, назад шагом", MUTED, 6.5)


class DribbleBeforeShotDiagram(Diagram):
    def draw_scene(self, c):
        self.dashed_box(c, 30, 12, 100, 50)
        self.player(c, 50, 35, TEAL_KID, "11")
        self.ball(c, 62, 35)
        self.arrow(c, 68, 35, 100, 35, AMBER, 1.5)
        self.ball(c, 110, 35)
        # goal
        c.setStrokeColor(INK)
        c.setLineWidth(2)
        c.line(155, 18, 155, 55)
        self.arrow(c, 118, 35, 150, 35, BLUE_KID, 1.5)
        self.label(c, 35, 58, "≥2 касания ведения → удар", GREEN_DARK, 6.5)


class ShortSprintsDiagram(Diagram):
    def draw_scene(self, c):
        y = 55
        for i in range(5):
            x0 = 25 + i * 32
            self.cone(c, x0, 22)
            self.arrow(c, x0, 40, x0 + 18, 40, AMBER, 1.3)
            self.label(c, x0 - 2, 10, f"{i+1}", MUTED, 6)
        self.player(c, 25, 40, ORANGE_KID, "→")
        self.label(c, 40, 62, "много коротких: 8–10 м, назад шагом", GREEN_DARK, 6.5)


class DribbleOutAndBackDiagram(Diagram):
    def draw_scene(self, c):
        self.cone(c, 40, 30)
        self.cone(c, 165, 30)
        self.player(c, 40, 48, BLUE_KID, "6")
        self.ball(c, 52, 48)
        self.arrow(c, 58, 48, 150, 48, AMBER, 2)
        self.arrow(c, 150, 22, 50, 22, MUTED, 1.2, dashed=True)
        self.label(c, 70, 56, "ведение туда 10 м", GREEN_DARK, 7)
        self.label(c, 70, 10, "назад шагом", MUTED, 6.5)


class KeepAwayDiagram(Diagram):
    def draw_scene(self, c):
        self.player(c, 55, 50, BLUE_KID, "6")
        self.player(c, 145, 50, ORANGE_KID, "9")
        self.player(c, 100, 20, TEAL_KID, "11")
        self.player(c, 100, 40, PARENT, "Р")
        self.ball(c, 67, 50)
        self.arrow(c, 72, 50, 132, 50, AMBER, 1.5)
        self.label(c, 35, 64, "трое пасуют • родитель слегка мешает", GREEN_DARK, 6.5)
        self.label(c, 8, 6, "цель: 8 пасов подряд", MUTED, 6.5)


class RollAndStopDiagram(Diagram):
    def draw_scene(self, c):
        self.player(c, 40, 40, PARENT, "Р")
        self.ball(c, 70, 40)
        self.arrow(c, 78, 40, 120, 40, MUTED, 1.2, dashed=True)
        self.player(c, 140, 40, ORANGE_KID, "9")
        self.arrow(c, 130, 40, 110, 40, AMBER, 2)
        self.ball(c, 125, 28)
        self.label(c, 45, 58, "Р откатил → дойти и остановить СТОЯ", GREEN_DARK, 6.5)
        self.label(c, 8, 8, "падение / подкат = повтор", HexColor("#8B1A1A"), 6.5)


class OneVOneDiagram(Diagram):
    def draw_scene(self, c):
        self.dashed_box(c, 40, 12, 130, 52)
        # mini goals
        c.setStrokeColor(INK)
        c.setLineWidth(1.5)
        c.line(40, 25, 40, 50)
        c.line(170, 25, 170, 50)
        self.player(c, 80, 38, ORANGE_KID, "9")
        self.player(c, 130, 38, TEAL_KID, "11")
        self.ball(c, 95, 38)
        self.arrow(c, 100, 38, 120, 38, AMBER, 1.5)
        self.label(c, 55, 60, "поле ~6×10 м  •  60–90 сек", GREEN_DARK, 6.5)
        self.label(c, 8, 2, "третий отдыхает / подаёт", MUTED, 6)


class ComboDiagram(Diagram):
    def draw_scene(self, c):
        self.player(c, 30, 38, PARENT, "Р")
        self.arrow(c, 40, 38, 60, 38, MUTED, 1, dashed=True)
        self.player(c, 70, 38, ORANGE_KID, "1")
        self.ball(c, 82, 38)
        self.arrow(c, 88, 38, 115, 38, AMBER, 1.5)  # 3 steps
        self.player(c, 125, 38, ORANGE_KID, "2")
        self.arrow(c, 125, 30, 125, 12, BLUE_KID, 1.2)  # pass down concept
        self.arrow(c, 135, 45, 170, 55, AMBER, 2)
        self.cone(c, 175, 52)
        self.label(c, 20, 62, "принять → 3 шага → пас → рывок 8 м", GREEN_DARK, 6.5)
        self.label(c, 8, 4, "связка как в игре", MUTED, 6.5)


class MatchDiagram(Diagram):
    def draw_scene(self, c):
        self.dashed_box(c, 25, 10, 160, 55)
        c.setStrokeColor(INK)
        c.setLineWidth(1.5)
        c.line(25, 22, 25, 52)
        c.line(185, 22, 185, 52)
        self.player(c, 60, 40, BLUE_KID, "6")
        self.player(c, 95, 28, ORANGE_KID, "9")
        self.player(c, 95, 52, TEAL_KID, "11")
        self.player(c, 145, 40, PARENT, "Р")
        self.ball(c, 72, 40)
        self.label(c, 45, 62, "мини-матч 10 мин • без стояния • без подкатов", GREEN_DARK, 6.5)


DIAGRAM_MAP = {
    "tag": TagDiagram,
    "sprint": SprintDiagram,
    "push_chase": PushChaseDiagram,
    "square": SquareNoStandDiagram,
    "shots": ShotsDiagram,
    "tag_ball": TagWithBallDiagram,
    "shuttle": ShuttleDiagram,
    "receive_move": ReceivePassMoveDiagram,
    "two_v_one": TwoVOneDiagram,
    "snake": SnakeRunDiagram,
    "starts": StartsDiagram,
    "pass_sprint": PassAndSprintDiagram,
    "dribble_shot": DribbleBeforeShotDiagram,
    "short_sprints": ShortSprintsDiagram,
    "dribble_ob": DribbleOutAndBackDiagram,
    "keepaway": KeepAwayDiagram,
    "roll_stop": RollAndStopDiagram,
    "one_v_one": OneVOneDiagram,
    "combo": ComboDiagram,
    "match": MatchDiagram,
}


class ExerciseCard(Flowable):
    """Card with number, title, time, description, age notes, and diagram."""

    def __init__(self, number, title, minutes, steps, age_notes, diagram_key, diagram_kw=None, width=None):
        Flowable.__init__(self)
        self.number = number
        self.title = title
        self.minutes = minutes
        self.steps = steps
        self.age_notes = age_notes
        self.diagram_key = diagram_key
        self.diagram_kw = diagram_kw or {}
        self.card_width = width or (PAGE_W - 2 * MARGIN)
        self.diag_w = 72 * mm
        self.diag_h = 42 * mm
        self._height = None

    def wrap(self, availWidth, availHeight):
        self.card_width = min(self.card_width, availWidth)
        # estimate height from text only — keep cards compact
        lines = 1  # title row
        for step in self.steps:
            lines += max(1, 1 + len(step) // 48)
        for note in self.age_notes:
            lines += max(1, 1 + len(note) // 48)
        text_h = lines * 10.2 + 14
        # Fit to content; diagram sets a sensible minimum
        self._height = max(self.diag_h + 7 * mm, text_h + 5 * mm)
        return self.card_width, self._height

    def draw(self):
        c = self.canv
        w, h = self.card_width, self._height
        # card bg
        c.setFillColor(CARD_BG)
        c.setStrokeColor(HexColor("#D5E5D8"))
        c.setLineWidth(1)
        c.roundRect(0, 0, w, h, 7, fill=1, stroke=1)
        # left accent
        c.setFillColor(GREEN_MID)
        c.roundRect(0, 0, 3.5 * mm, h, 2, fill=1, stroke=0)
        c.rect(2 * mm, 0, 2 * mm, h, fill=1, stroke=0)

        # number badge
        c.setFillColor(AMBER)
        c.circle(9 * mm, h - 8 * mm, 5.5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("DejaVuBold", 9)
        c.drawCentredString(9 * mm, h - 9.5 * mm, str(self.number))

        # title + time
        c.setFillColor(GREEN_DARK)
        c.setFont("DejaVuBold", 10)
        c.drawString(15 * mm, h - 9 * mm, self.title)
        c.setFillColor(AMBER)
        c.setFont("DejaVuBold", 8)
        time_str = f"{self.minutes} мин"
        c.drawRightString(w - 4 * mm, h - 9 * mm, time_str)

        # diagram on the right
        diag_cls = DIAGRAM_MAP[self.diagram_key]
        diag = diag_cls(width=self.diag_w, height=self.diag_h, **self.diagram_kw)
        diag.canv = c
        c.saveState()
        c.translate(w - self.diag_w - 4 * mm, 4 * mm)
        diag.draw()
        c.restoreState()

        # text block
        text_x = 5 * mm
        text_top = h - 15 * mm
        y = text_top
        c.setFillColor(INK)
        c.setFont("DejaVu", 8)
        max_text_w = w - self.diag_w - 12 * mm

        def draw_wrapped(text, font="DejaVu", size=8, color=INK, leading=10.5):
            nonlocal y
            c.setFont(font, size)
            c.setFillColor(color)
            words = text.split()
            line = ""
            for word in words:
                test = (line + " " + word).strip()
                if c.stringWidth(test, font, size) <= max_text_w:
                    line = test
                else:
                    c.drawString(text_x, y, line)
                    y -= leading
                    line = word
            if line:
                c.drawString(text_x, y, line)
                y -= leading

        for step in self.steps:
            draw_wrapped("• " + step, "DejaVu", 8, INK, 10.2)
            y -= 1

        y -= 2
        if self.age_notes:
            c.setFillColor(AMBER_LIGHT)
            box_h = min(y - 3 * mm, len(self.age_notes) * 10 + 6)
            if box_h > 8:
                c.roundRect(text_x - 1 * mm, y - box_h + 8, max_text_w + 2 * mm, box_h, 3, fill=1, stroke=0)
            for note in self.age_notes:
                draw_wrapped(note, "DejaVu", 7.5, HexColor("#6A3B0E"), 9.5)


def make_styles_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAGE_BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    if doc.page > 1:
        canvas.setFillColor(GREEN_DARK)
        canvas.rect(0, PAGE_H - 8 * mm, PAGE_W, 8 * mm, fill=1, stroke=0)
        canvas.setFillColor(white)
        canvas.setFont("DejaVu", 7.5)
        canvas.drawString(MARGIN, PAGE_H - 5.2 * mm, "Семейный футбол • 6 / 9 / 11 лет • 2 недели")
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 5.2 * mm, f"стр. {doc.page}")
        canvas.setStrokeColor(HexColor("#D5E5D8"))
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, 10 * mm, PAGE_W - MARGIN, 10 * mm)
        canvas.setFillColor(MUTED)
        canvas.setFont("DejaVu", 7)
        canvas.drawCentredString(PAGE_W / 2, 5 * mm, "Подкаты запрещены  •  Не сравнивать детей  •  После тренировки — 1 похвала каждому")
    canvas.restoreState()


def cover_page(story, S):
    story.append(Spacer(1, 25 * mm))

    # big green banner via table
    banner_data = [
        [
            Paragraph("СЕМЕЙНЫЙ ФУТБОЛ", S["CoverTitle"]),
        ],
        [
            Paragraph("План на 2 недели • 3 тренировки в неделю", S["CoverSub"]),
        ],
        [
            Paragraph("25–30 минут • трое детей вместе • схемки к каждому упражнению", S["CoverSub"]),
        ],
    ]
    t = Table(banner_data, colWidths=[PAGE_W - 2 * MARGIN])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_DARK),
                ("TOPPADDING", (0, 0), (-1, 0), 18),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 16),
                ("BOTTOMPADDING", (0, 0), (-1, -2), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("ROUNDEDCORNERS", [10, 10, 10, 10]),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 10 * mm))

    kids = [
        ["Возраст", "Фокус на 2 недели"],
        ["6 лет", "Смелость касаться мяча, не стесняться, быть в игре"],
        ["9 лет", "Первый шаг / рывок без долгих раздумий, без подкатов"],
        ["11 лет", "Повторные ускорения + пас и открывание после передачи"],
    ]
    kt = Table(kids, colWidths=[28 * mm, PAGE_W - 2 * MARGIN - 28 * mm])
    kt.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN_MID),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTNAME", (0, 0), (-1, 0), "DejaVuBold"),
                ("FONTNAME", (0, 1), (-1, -1), "DejaVu"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 1), (-1, -1), INK),
                ("BACKGROUND", (0, 1), (-1, 1), HexColor("#E3F2FD")),
                ("BACKGROUND", (0, 2), (-1, 2), HexColor("#FFF3E0")),
                ("BACKGROUND", (0, 3), (-1, 3), HexColor("#E0F2F1")),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#C8DCCE")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(kt)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("Легенда на схемках", S["H2"]))
    legend = (
        "<b>Цветные кружки</b> — игроки (6 / 9 / 11) &nbsp;&nbsp; "
        "<b>Р</b> — родитель &nbsp;&nbsp; "
        "<b>В</b> — водящий &nbsp;&nbsp; "
        "<b>▲</b> — ориентир (конус/бутылка) &nbsp;&nbsp; "
        "<b>○</b> — мяч &nbsp;&nbsp; "
        "<b>→</b> — направление бега/паса"
    )
    story.append(Paragraph(legend, S["Body"]))
    story.append(Spacer(1, 6 * mm))

    rules = [
        "Подкаты запрещены на всех тренировках.",
        "Не сравнивать детей друг с другом.",
        "Младшему можно короче дистанцию и «безопасные» 2 секунды с мячом.",
        "Если очень устали — убрать 2 последних повтора.",
        "Лучшие дни: через день (Пн/Ср/Пт или Вт/Чт/Сб).",
        "В день матча лучше не ставить тяжёлую домашнюю тренировку.",
    ]
    story.append(Paragraph("Общие правила", S["H2"]))
    for r in rules:
        story.append(Paragraph("• " + r, S["Body"]))

    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Что нужно", S["H2"]))
    story.append(
        Paragraph(
            "1–2 мяча, 4 ориентира (конусы, бутылки или рюкзаки), ровная площадка ~15–20 метров.",
            S["Body"],
        )
    )
    story.append(PageBreak())


def training_block(story, S, week, num, title, phrase, exercises):
    story.append(Paragraph(f"Неделя {week} • Тренировка {num}", S["H1"]))
    story.append(Paragraph(title, S["H2"]))
    story.append(Spacer(1, 2 * mm))

    # phrase banner
    phrase_t = Table(
        [[Paragraph(f"Фраза дня: «{phrase}»", S["Phrase"])]],
        colWidths=[PAGE_W - 2 * MARGIN],
    )
    phrase_t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), AMBER_LIGHT),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("BOX", (0, 0), (-1, -1), 1, AMBER),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(phrase_t)
    story.append(Spacer(1, 4 * mm))

    for i, ex in enumerate(exercises, 1):
        card = ExerciseCard(
            number=i,
            title=ex["title"],
            minutes=ex["min"],
            steps=ex["steps"],
            age_notes=ex.get("ages", []),
            diagram_key=ex["diagram"],
            diagram_kw=ex.get("diagram_kw", {}),
        )
        story.append(KeepTogether([card, Spacer(1, 2.2 * mm)]))

    # praise line
    story.append(Spacer(1, 1 * mm))
    story.append(Paragraph("После тренировки — похвала", S["H2"]))
    story.append(
        Paragraph(
            "6 лет: смелость / касания мяча &nbsp;•&nbsp; "
            "9 лет: первые шаги вперёд / к мячу &nbsp;•&nbsp; "
            "11 лет: пас и работа без остановки",
            S["Small"],
        )
    )


def build():
    out = Path("/workspace/family_football_2weeks.pdf")
    S = styles()
    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Семейный футбол — план на 2 недели",
        author="Family Football Plan",
    )
    story = []
    cover_page(story, S)

    # ===== WEEK 1 =====
    training_block(
        story,
        S,
        week=1,
        num=1,
        title="«Первый шаг» — ~26 мин",
        phrase="Побеждает тот, кто первым делает шаги к мячу",
        exercises=[
            {
                "title": "Догонялки",
                "min": 3,
                "diagram": "tag",
                "steps": [
                    "Один водящий без мяча.",
                    "Кого коснулись рукой — тот становится водящим.",
                    "Бегать можно в любую сторону на площадке.",
                ],
                "ages": ["6 лет: зона «дом» у родителя на 3 секунды отдыха."],
            },
            {
                "title": "Рывки к ориентиру",
                "min": 6,
                "diagram": "sprint",
                "diagram_kw": {"meters": "10 м"},
                "steps": [
                    "Два ориентира на 10 метров.",
                    "По команде — рывок к дальнему, коснуться рукой.",
                    "Назад — спокойным шагом. Сделать 8 раз.",
                ],
                "ages": ["6 лет: дистанция 8 м.", "9 и 11 лет: 10–12 м."],
            },
            {
                "title": "Толкни мяч — догони — останови",
                "min": 6,
                "diagram": "push_chase",
                "steps": [
                    "Лёгкий толчок мяча вперёд на 3–5 м.",
                    "Сразу бегом догнать и остановить ногой.",
                    "Принести обратно шагом. По 7 раз каждому.",
                ],
                "ages": [
                    "6 лет: толкать слабо, главное — побежал.",
                    "9 лет: после остановки ещё 3 шага вперёд с мячом.",
                    "11 лет: остановил → пас родителю → открылся.",
                ],
            },
            {
                "title": "Квадрат: нельзя стоять",
                "min": 7,
                "diagram": "square",
                "steps": [
                    "Квадрат ~8×8 м (4 ориентира).",
                    "С мячом стоять не больше 2 секунд.",
                    "Нужно отдать пас или пойти вперёд. Подкаты запрещены.",
                ],
                "ages": ["6 лет: после приёма 2 секунды его не отбирают."],
            },
            {
                "title": "Удары по воротам",
                "min": 4,
                "diagram": "shots",
                "steps": [
                    "Ворота = 2 бутылки / конуса.",
                    "Родитель пасует — ребёнок бьёт. По 6 ударов.",
                    "Без оценок «слабо/криво».",
                ],
                "ages": [],
            },
        ],
    )
    story.append(PageBreak())

    training_block(
        story,
        S,
        week=1,
        num=2,
        title="«Догони и отдай» — ~26 мин",
        phrase="Отдал — сразу сдвинулся",
        exercises=[
            {
                "title": "Догонялки с мячом у ноги",
                "min": 3,
                "diagram": "tag_ball",
                "steps": [
                    "Водящий без мяча.",
                    "У остальных мяч у ноги — ведут и убегают.",
                    "Потерял контроль мяча — можно пятнать.",
                ],
                "ages": [],
            },
            {
                "title": "Челноки",
                "min": 6,
                "diagram": "shuttle",
                "steps": [
                    "Ориентиры: старт — 5 м — 10 м.",
                    "До 5 м и назад, потом до 10 м и назад шагом.",
                    "6 повторов.",
                ],
                "ages": ["6 лет: только до 5 м и назад, 6 раз."],
            },
            {
                "title": "Прими — отдай — сдвинься",
                "min": 7,
                "diagram": "receive_move",
                "steps": [
                    "Родитель пасует каждому по кругу.",
                    "Принять → отдать обратно → 3 шага в сторону/вперёд.",
                    "По 8 касаний каждому.",
                ],
                "ages": [],
            },
            {
                "title": "Игра 2 на 1",
                "min": 7,
                "diagram": "two_v_one",
                "steps": [
                    "Двое держат мяч пасами, один отбирает.",
                    "Каждые 1–1,5 мин меняете отбирающего.",
                    "Цель атакующих: 5 пасов подряд.",
                ],
                "ages": ["6 лет чаще в атаке, реже один в отборе."],
            },
            {
                "title": "Свободные удары",
                "min": 3,
                "diagram": "shots",
                "steps": [
                    "Кто куда хочет бьёт по воротам.",
                    "Без очереди и оценок — закончить на удовольствии.",
                ],
                "ages": [],
            },
        ],
    )
    story.append(PageBreak())

    training_block(
        story,
        S,
        week=1,
        num=3,
        title="«Ускорение после паса» — ~26 мин",
        phrase="Отдал — ускорился",
        exercises=[
            {
                "title": "Бег змейкой",
                "min": 3,
                "diagram": "snake",
                "steps": [
                    "4 ориентира в линию.",
                    "Лёгкий бег змейкой туда-обратно 3 раза.",
                    "Потом 3 раза чуть быстрее.",
                ],
                "ages": [],
            },
            {
                "title": "Рывки из разных стартов",
                "min": 6,
                "diagram": "starts",
                "steps": [
                    "Старты: лицом, боком, спиной, сидя — по 2 раза (всего 8).",
                    "По свистку/команде — рывок 8–10 м к ориентиру.",
                ],
                "ages": ["6 лет: можно 8 м и без старта «сидя»."],
            },
            {
                "title": "Пас + рывок",
                "min": 7,
                "diagram": "pass_sprint",
                "steps": [
                    "Отдал пас родителю/в стенку.",
                    "Сразу ускорение 8–10 м к ориентиру.",
                    "Назад шагом. По 6 раз каждому.",
                ],
                "ages": [],
            },
            {
                "title": "Квадрат: гол после ведения",
                "min": 7,
                "diagram": "dribble_shot",
                "steps": [
                    "Перед ударом минимум 2 касания своим ведением.",
                    "Маленькие ворота из 2 ориентиров.",
                    "Играют все вместе.",
                ],
                "ages": [],
            },
            {
                "title": "Удары с места",
                "min": 3,
                "diagram": "shots",
                "steps": ["По 3 удара каждому.", "Закончить на эмоции, без критики."],
                "ages": [],
            },
        ],
    )
    story.append(PageBreak())

    # ===== WEEK 2 =====
    training_block(
        story,
        S,
        week=2,
        num=4,
        title="«Много коротких включений» — ~27 мин",
        phrase="Короткий рывок лучше, чем долгое стояние",
        exercises=[
            {
                "title": "Догонялки",
                "min": 3,
                "diagram": "tag",
                "steps": ["Как в тренировке 1: водящий пятнает рукой."],
                "ages": ["6 лет: можно «дом» на 3 секунды."],
            },
            {
                "title": "Серия коротких рывков",
                "min": 7,
                "diagram": "short_sprints",
                "steps": [
                    "10 рывков по 8–10 м.",
                    "Между ними только шаг назад.",
                    "Если к 8-му уже «нет ног» — остановиться раньше.",
                ],
                "ages": ["6 лет: 8 × 8 м."],
            },
            {
                "title": "Ведение до ориентира и назад",
                "min": 6,
                "diagram": "dribble_ob",
                "steps": [
                    "10 м с мячом туда (без остановки, не обязательно быстро).",
                    "Назад шагом. По 5 раз.",
                ],
                "ages": [
                    "9 лет: на последних 3 м чуть ускориться.",
                    "11 лет: на обратном пути — пас родителю с 5–6 м.",
                ],
            },
            {
                "title": "Удержание мяча (3 на родителя)",
                "min": 7,
                "diagram": "keepaway",
                "steps": [
                    "Трое детей передают между собой.",
                    "Родитель слегка мешает (не в полную силу).",
                    "Цель: 8 пасов подряд.",
                ],
                "ages": ["Младшему всегда можно отдать «лёгкий» пас."],
            },
            {
                "title": "Удары после паса",
                "min": 4,
                "diagram": "shots",
                "steps": ["Пас вдоль от родителя → удар.", "По 5 раз каждому."],
                "ages": [],
            },
        ],
    )
    story.append(PageBreak())

    training_block(
        story,
        S,
        week=2,
        num=5,
        title="«Забрать стоя» — ~26 мин",
        phrase="Сначала ноги и 2 шага, потом борьба",
        exercises=[
            {
                "title": "Догонялки в квадрате",
                "min": 3,
                "diagram": "tag",
                "steps": ["Все в квадрате 8×8 м, выходить нельзя."],
                "ages": [],
            },
            {
                "title": "Рывок к мячу (только стоя)",
                "min": 6,
                "diagram": "roll_stop",
                "steps": [
                    "Родитель откатывает мяч в сторону.",
                    "Ребёнок доходит и останавливает СТОЯ, без падения.",
                    "Каждому по 6 мячей. Упал или подкат — повтор.",
                ],
                "ages": ["Важно для 9 лет: убрать привычку «падать в подкате»."],
            },
            {
                "title": "1 на 1 на крошечном поле",
                "min": 8,
                "diagram": "one_v_one",
                "steps": [
                    "Поле ~6×10 м, маленькие ворота с двух сторон.",
                    "Пары по 60–90 сек, третий отдыхает/подаёт.",
                    "Потом смена.",
                ],
                "ages": ["Родитель может играть, если нужен партнёр."],
            },
            {
                "title": "Общий квадрат без стояния",
                "min": 6,
                "diagram": "square",
                "steps": [
                    "Снова правило 2 секунд с мячом.",
                    "Отбор только стоя, без подкатов.",
                ],
                "ages": [],
            },
            {
                "title": "Удары на точность",
                "min": 3,
                "diagram": "shots",
                "steps": ["Попасть между двумя бутылками с 6–8 м.", "По 4 попытки."],
                "ages": [],
            },
        ],
    )
    story.append(PageBreak())

    training_block(
        story,
        S,
        week=2,
        num=6,
        title="«Как в игре» — ~27 мин",
        phrase="Играем в движение, не в стояние",
        exercises=[
            {
                "title": "Лёгкие догонялки",
                "min": 2,
                "diagram": "tag",
                "steps": ["Короткий разогрев 2 минуты."],
                "ages": [],
            },
            {
                "title": "Рывки 6 × 12 м",
                "min": 5,
                "diagram": "sprint",
                "diagram_kw": {"meters": "12 м"},
                "steps": [
                    "6 рывков по 12 м.",
                    "После каждого — 20 сек спокойной ходьбы.",
                ],
                "ages": ["6 лет: 6 × 8–10 м."],
            },
            {
                "title": "Связка: прими — 3 шага — пас — рывок",
                "min": 7,
                "diagram": "combo",
                "steps": [
                    "Принять от родителя.",
                    "3 шага вперёд с мячом.",
                    "Отдать пас.",
                    "Ускориться 8 м к ориентиру. По 5 раз каждому.",
                ],
                "ages": [],
            },
            {
                "title": "Мини-матч",
                "min": 10,
                "diagram": "match",
                "steps": [
                    "3 на родителя или 2 на 1 с помощью родителя.",
                    "Нельзя стоять с мячом. Подкатов нет.",
                    "После потери — сразу попытка вернуть.",
                ],
                "ages": ["Счёт можно вести мягко, без давления."],
            },
            {
                "title": "Удары «на десерт»",
                "min": 3,
                "diagram": "shots",
                "steps": ["Каждый сам выбирает способ удара.", "Закончить улыбкой."],
                "ages": [],
            },
        ],
    )
    story.append(PageBreak())

    # Final page — match goals + schedule
    story.append(Paragraph("Мини-цели на матчи этих 2 недель", S["H1"]))
    goals = [
        ["Кто", "Цель на игру", "Как хвалить"],
        [
            "6 лет",
            "Не прятаться — минимум 5 касаний",
            "«Ты не стеснялся и трогал мяч»",
        ],
        [
            "9 лет",
            "6 раз побежал к мячу / открылся",
            "«Ты сразу пошёл вперёд — вот это нужно»",
        ],
        [
            "11 лет",
            "После каждого паса — сдвинуться",
            "«Хороший пас и сразу открылся»",
        ],
    ]
    gt = Table(goals, colWidths=[22 * mm, 75 * mm, PAGE_W - 2 * MARGIN - 97 * mm])
    gt.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN_DARK),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTNAME", (0, 0), (-1, 0), "DejaVuBold"),
                ("FONTNAME", (0, 1), (-1, -1), "DejaVu"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("TEXTCOLOR", (0, 1), (-1, -1), INK),
                ("BACKGROUND", (0, 1), (-1, 1), HexColor("#E3F2FD")),
                ("BACKGROUND", (0, 2), (-1, 2), HexColor("#FFF3E0")),
                ("BACKGROUND", (0, 3), (-1, 3), HexColor("#E0F2F1")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#C8DCCE")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(gt)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("Расписание (пример)", S["H2"]))
    sched = [
        ["День", "Неделя 1", "Неделя 2"],
        ["Пн / Вт", "Тренировка 1 — Первый шаг", "Тренировка 4 — Короткие включения"],
        ["Ср / Чт", "Тренировка 2 — Догони и отдай", "Тренировка 5 — Забрать стоя"],
        ["Пт / Сб", "Тренировка 3 — Ускорение после паса", "Тренировка 6 — Как в игре"],
    ]
    st = Table(sched, colWidths=[22 * mm, (PAGE_W - 2 * MARGIN - 22 * mm) / 2] * 1 + [])
    # fix widths
    st = Table(
        sched,
        colWidths=[
            22 * mm,
            (PAGE_W - 2 * MARGIN - 22 * mm) / 2,
            (PAGE_W - 2 * MARGIN - 22 * mm) / 2,
        ],
    )
    st.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN_MID),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTNAME", (0, 0), (-1, 0), "DejaVuBold"),
                ("FONTNAME", (0, 1), (-1, -1), "DejaVu"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TEXTCOLOR", (0, 1), (-1, -1), INK),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#C8DCCE")),
                ("BACKGROUND", (0, 1), (-1, -1), GREEN_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(st)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("После матча", S["H2"]))
    story.append(
        Paragraph(
            "Сначала вода и тепло. Разбор — только если ребёнок готов, "
            "и максимум: один плюс + одно «попробуем в следующий раз». "
            "Не разбирать игру в машине сразу после финального свистка.",
            S["Body"],
        )
    )
    story.append(Spacer(1, 6 * mm))
    story.append(
        Paragraph(
            "Откройте нужную тренировку на телефоне/планшете прямо на поле — "
            "схема справа от описания показывает, как встать и куда бежать.",
            S["Tip"],
        )
    )

    doc.build(story, onFirstPage=make_styles_header_footer, onLaterPages=make_styles_header_footer)
    print(f"Wrote {out}")
    return out


if __name__ == "__main__":
    build()
