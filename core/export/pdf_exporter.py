import base64
import io
import logging
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from svglib.svglib import svg2rlg

logger = logging.getLogger(__name__)

# ── Реєстрація шрифтів з підтримкою кирилиці ────────────────────────────────
def _register_fonts() -> None:
    """Реєструє DejaVuSans з папки fonts/ поруч з цим файлом."""
    import os
    fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
    variants = [
        ("DejaVuSans",            "DejaVuSans.ttf"),
        ("DejaVuSans-Bold",       "DejaVuSans-Bold.ttf"),
        ("DejaVuSans-Oblique",    "DejaVuSans-Oblique.ttf"),
        ("DejaVuSans-BoldOblique","DejaVuSans-BoldOblique.ttf"),
    ]
    for name, filename in variants:
        path = os.path.join(fonts_dir, filename)
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))
        else:
            logger.warning("Шрифт не знайдено: %s", path)

_register_fonts()

# Псевдоніми щоб код стилів не знав про конкретний шрифт
FONT_REGULAR  = "DejaVuSans"
FONT_BOLD     = "DejaVuSans-Bold"
FONT_ITALIC   = "DejaVuSans-Oblique"
FONT_MONO     = "DejaVuSans"          # моноширинний — теж DejaVu (достатньо для цифр)



# ── Кольори ──────────────────────────────────────────────────────────────────
PRIMARY     = colors.HexColor("#4f46e5")
PRIMARY_LT  = colors.HexColor("#ede9fe")
STEP_BG     = colors.HexColor("#f8fafc")
STEP_BORDER = colors.HexColor("#4f46e5")
RULE_BG     = colors.HexColor("#fffbeb")
RULE_BORDER = colors.HexColor("#fcd34d")
INTER_BG    = colors.HexColor("#f5f3ff")
INTER_BORDER= colors.HexColor("#a5b4fc")
RESULT_BG   = colors.HexColor("#ecfdf5")
RESULT_BORDER=colors.HexColor("#10b981")
HEADER_BG   = colors.HexColor("#4f46e5")
MUTED       = colors.HexColor("#6b7280")
DARK        = colors.HexColor("#1f2937")


# ── Назви фігур та задач ─────────────────────────────────────────────────────
FIGURE_NAMES = {
    "triangle":       "Трикутник",
    "circle":         "Коло",
    "sector":         "Сектор та Сегмент",
    "ellipse":        "Еліпс",
    "regular_polygon":"Правильний багатокутник",
    "quadrangle":     "Чотирикутник",
}

TASK_NAMES = {
    "RIGHT_LEGS":                   "За двома катетами",
    "RIGHT_LEG_HYPOTENUSE":         "За катетом і гіпотенузою",
    "SSS":                          "За трьома сторонами (SSS)",
    "SAS":                          "Дві сторони і кут між ними (SAS)",
    "ASA":                          "Сторона і два прилеглі кути (ASA)",
    "ISOSCELES_BASE_SIDE":          "За основою та бічною стороною",
    "EQUILATERAL_SIDE":             "За відомою стороною",
    "RADIUS":                       "За радіусом",
    "DIAMETER":                     "За діаметром",
    "CIRCUMFERENCE":                "За довжиною кола",
    "AREA":                         "За площею",
    "SECTOR_AND_ARC":               "За радіусом та центральним кутом",
    "ELLIPSE_AXES":                 "За піввісями a та b",
    "REGULAR_SIDE":                 "За стороною",
    "REGULAR_R_CIRCUM":             "За радіусом описаного кола (R)",
    "REGULAR_R_IN":                 "За радіусом вписаного кола (r)",
    "RECTANGLE_SIDES":              "Відомі обидві сторони",
    "RECTANGLE_AREA_SIDE":          "Через площу і сторону",
    "RECTANGLE_PERIMETER_SIDE":     "Через периметр і сторону",
    "RECTANGLE_DIAGONAL_SIDE":      "Через діагональ і сторону",
    "SQUARE_SIDE":                  "Відома сторона",
    "SQUARE_AREA":                  "Через площу",
    "SQUARE_PERIMETER":             "Через периметр",
    "SQUARE_DIAGONAL":              "Через діагональ",
    "RHOMBUS_DIAGONALS":            "Діагоналі",
    "RHOMBUS_SIDE_ANGLE":           "Сторона і кут",
    "RHOMBUS_AREA_SIDE":            "Площа і сторона",
    "RHOMBUS_DIAGONAL_SIDE":        "Діагональ і сторона",
    "PARALLELOGRAM_S_A":            "Дві сторони і кут",
    "PARALLELOGRAM_D_A":            "Діагоналі і кут між ними",
    "TRAPEZOID_ABH":                "Основи і висота",
    "TRAPEZOID_AREA_BASES":         "Площа і основи",
    "TRAPEZOID_MIDLINE_HEIGHT":     "Середня лінія і висота",
    "ISOSCELES_TRAPEZOID_BASES_LEG":"Рівнобічна: основи і бічна сторона",
    "ARB_SIDES_ANGLES":             "4 сторони та кут",
}


# ── Стилі ────────────────────────────────────────────────────────────────────
def _make_styles() -> dict:
    def ps(name, **kw) -> ParagraphStyle:
        return ParagraphStyle(name, **kw)

    return {
        "title": ps("DocTitle",
            fontSize=20, leading=26, textColor=colors.white,
            fontName=FONT_BOLD, alignment=TA_CENTER, spaceAfter=0),
        "subtitle": ps("DocSubtitle",
            fontSize=11, leading=15, textColor=colors.HexColor("#c7d2fe"),
            fontName=FONT_REGULAR, alignment=TA_CENTER, spaceAfter=0),
        "section": ps("Section",
            fontSize=13, leading=17, textColor=PRIMARY,
            fontName=FONT_BOLD, spaceBefore=14, spaceAfter=6),
        "param_key": ps("ParamKey",
            fontSize=10, leading=14, textColor=MUTED,
            fontName=FONT_REGULAR),
        "param_val": ps("ParamVal",
            fontSize=10, leading=14, textColor=DARK,
            fontName=FONT_BOLD),
        "step_title": ps("StepTitle",
            fontSize=11, leading=15, textColor=PRIMARY,
            fontName=FONT_BOLD, spaceAfter=3),
        "inter_title": ps("InterTitle",
            fontSize=10, leading=14, textColor=colors.HexColor("#6366f1"),
            fontName=FONT_BOLD, spaceAfter=2),
        "formula": ps("Formula",
            fontSize=11, leading=15, textColor=PRIMARY,
            fontName=FONT_BOLD, alignment=TA_CENTER),
        "solution": ps("Solution",
            fontSize=10, leading=14, textColor=DARK,
            fontName=FONT_REGULAR),
        "rule": ps("Rule",
            fontSize=9, leading=13, textColor=colors.HexColor("#92400e"),
            fontName=FONT_ITALIC),
        "result_key": ps("ResultKey",
            fontSize=10, leading=14, textColor=colors.HexColor("#065f46"),
            fontName=FONT_BOLD),
        "result_val": ps("ResultVal",
            fontSize=11, leading=15, textColor=colors.HexColor("#047857"),
            fontName=FONT_BOLD),
        "info": ps("Info",
            fontSize=10, leading=14, textColor=DARK,
            fontName=FONT_REGULAR),
        "header_text": ps("HeaderText",
            fontSize=11, leading=15, textColor=PRIMARY,
            fontName=FONT_BOLD),
        "footer": ps("Footer",
            fontSize=8, leading=10, textColor=MUTED,
            fontName=FONT_REGULAR, alignment=TA_CENTER),
    }


# ── Допоміжні функції ────────────────────────────────────────────────────────
def _card(content_rows: list, bg: colors.Color, border: colors.Color,
          col_widths=None, padding: int = 8) -> Table:
    """Картка з кольоровим фоном і лівою межею."""
    t = Table(content_rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), bg),
        ("LINECOLOR",    (0, 0), (-1, -1), border),
        ("LINEBEFORE",   (0, 0), (0,  -1), 3, border),
        ("TOPPADDING",   (0, 0), (-1, -1), padding),
        ("BOTTOMPADDING",(0, 0), (-1, -1), padding),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def _try_embed_image(image_b64: str, content_w: float) -> list:
    """
    Декодує SVG з base64 і вбудовує у PDF через svglib.
    svglib працює на всіх платформах без системних залежностей.
    Повертає список Flowable або порожній список якщо не вдалось.
    """
    try:
        svg_bytes = base64.b64decode(image_b64)
    except ValueError as decode_err:
        logger.debug("Не вдалося декодувати base64 зображення: %s", decode_err)
        return []

    try:
        drawing = svg2rlg(io.BytesIO(svg_bytes))
    except Exception as parse_err:
        logger.warning("Помилка парсингу SVG: %s", parse_err)
        return []

    if drawing is None:
        logger.warning("svg2rlg повернув None — SVG не вдалося розпарсити")
        return []

    # Масштабуємо малюнок під ширину контенту зберігаючи пропорції
    max_w = content_w
    max_h = 10 * cm
    scale = min(max_w / drawing.width, max_h / drawing.height)
    drawing.width  *= scale
    drawing.height *= scale
    drawing.transform = (scale, 0, 0, scale, 0, 0)

    img_table = Table([[drawing]], colWidths=[content_w])
    img_table.setStyle(TableStyle([
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ]))
    return [img_table, Spacer(1, 14)]


def _render_step(step: dict, styles: dict, page_w: float) -> list:
    """Перетворює один крок на список Flowable-елементів."""
    elems = []
    t = step.get("type", "")

    if t == "info":
        elems.append(_card(
            [[Paragraph(step.get("text", ""), styles["info"])]],
            bg=STEP_BG, border=MUTED,
        ))
        elems.append(Spacer(1, 5))

    elif t == "header":
        elems.append(Spacer(1, 6))
        elems.append(Paragraph(f"➤ {step.get('text', '')}", styles["header_text"]))
        elems.append(HRFlowable(width="100%", thickness=1,
                                color=PRIMARY_LT, spaceAfter=4))

    elif t == "rule":
        elems.append(_card(
            [[Paragraph(f"📌 {step.get('text', '')}", styles["rule"])]],
            bg=RULE_BG, border=RULE_BORDER,
        ))
        elems.append(Spacer(1, 5))

    elif t in ("step", "intermediate"):
        is_inter = t == "intermediate"
        title_style = styles["inter_title"] if is_inter else styles["step_title"]
        prefix = "↳ " if is_inter else "➤ "
        bg     = INTER_BG    if is_inter else STEP_BG
        border = INTER_BORDER if is_inter else STEP_BORDER

        # rows: list[list] — комірки таблиці (можуть містити Paragraph або Table)
        title_row: list = [Paragraph(f"{prefix}{step.get('title', '')}", title_style)]
        rows: list[list] = [title_row]

        if step.get("rule"):
            rows.append([_card(
                [[Paragraph(f"📌 {step['rule']}", styles["rule"])]],
                bg=RULE_BG, border=RULE_BORDER, padding=5,
            )])

        if step.get("formula"):
            rows.append([_card(
                [[Paragraph(step["formula"], styles["formula"])]],
                bg=colors.HexColor("#eef2ff"), border=PRIMARY, padding=6,
            )])

        value_str = step.get("value", "")
        sol_str   = step.get("solution", "")
        rows.append([Paragraph(
            f'{sol_str} = <font color="#4f46e5"><b>{value_str}</b></font>',
            styles["solution"],
        )])

        card = _card(rows, bg=bg, border=border)
        if is_inter:
            elems.append(Spacer(1, 2))
            wrapper = Table([[" ", card]], colWidths=[0.5 * cm, page_w - 0.5 * cm])
            wrapper.setStyle(TableStyle([
                ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING",   (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
                ("VALIGN",       (0, 0), (-1, -1), "TOP"),
            ]))
            elems.append(wrapper)
        else:
            elems.append(KeepTogether([card]))

        elems.append(Spacer(1, 6))

    return elems


# ── Головна функція ───────────────────────────────────────────────────────────
def generate_pdf(solution: dict) -> bytes:
    """
    Генерує PDF з покроковим розв'язком.
    solution — dict з ключами: figure, task_type, params,
               targets, result, steps, image, created_at.
    Повертає bytes готового PDF.
    """
    buf = io.BytesIO()
    PAGE_W, _  = A4
    MARGIN     = 1.8 * cm
    CONTENT_W  = PAGE_W - 2 * MARGIN

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN,  bottomMargin=MARGIN,
        title="Розв'язок задачі з планіметрії",
        author="PlanimetrySolver",
    )

    styles = _make_styles()
    story  = []

    # ── Шапка ────────────────────────────────────────────────────────────────
    figure_name = FIGURE_NAMES.get(solution.get("figure", ""), solution.get("figure", ""))
    task_name   = TASK_NAMES.get(solution.get("task_type", ""), solution.get("task_type", ""))
    created_at  = solution.get("created_at",
                               datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M"))

    header_table = Table([
        [Paragraph("📐 PlanimetrySolver", styles["title"])],
        [Paragraph(f"Розв'язок задачі · {created_at}", styles["subtitle"])],
    ], colWidths=[CONTENT_W])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), HEADER_BG),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 14),
        ("LEFTPADDING",  (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    # ── Умова задачі ─────────────────────────────────────────────────────────
    story.append(Paragraph("Умова задачі", styles["section"]))

    params  = solution.get("params", {})
    targets = solution.get("targets", [])

    cond_rows = [
        [Paragraph("Фігура:",   styles["param_key"]),
         Paragraph(figure_name, styles["param_val"])],
        [Paragraph("Що відомо:",styles["param_key"]),
         Paragraph(task_name,   styles["param_val"])],
        *[
            [Paragraph(f"{k} =", styles["param_key"]),
             Paragraph(str(v),   styles["param_val"])]
            for k, v in params.items()
        ],
        [Paragraph("Знайти:",          styles["param_key"]),
         Paragraph(", ".join(targets), styles["param_val"])],
    ]

    cond_table = Table(cond_rows, colWidths=[3 * cm, CONTENT_W - 3 * cm])
    cond_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), STEP_BG),
        ("LINEBEFORE",    (0, 0), (0,  -1), 3, PRIMARY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [STEP_BG, colors.white]),
    ]))
    story.append(cond_table)
    story.append(Spacer(1, 14))

    # ── Результати ───────────────────────────────────────────────────────────
    result = solution.get("result", {})
    if result:
        story.append(Paragraph("Результати", styles["section"]))

        res_rows = [
            [Paragraph(f"{key}:", styles["result_key"]),
             Paragraph(str(val),  styles["result_val"])]
            for key, val in result.items()
        ]
        res_table = Table(res_rows, colWidths=[5 * cm, CONTENT_W - 5 * cm])
        res_table.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), RESULT_BG),
            ("LINEBEFORE",   (0, 0), (0,  -1), 3, RESULT_BORDER),
            ("TOPPADDING",   (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
            ("LEFTPADDING",  (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(res_table)
        story.append(Spacer(1, 14))

    # ── Малюнок ──────────────────────────────────────────────────────────────
    image_b64 = solution.get("image")
    if image_b64:
        image_flowables = _try_embed_image(image_b64, CONTENT_W)
        if image_flowables:
            story.append(Paragraph("Креслення", styles["section"]))
            story.extend(image_flowables)

    # ── Хід розв'язання ──────────────────────────────────────────────────────
    steps = solution.get("steps", [])
    if steps:
        story.append(Paragraph("Хід розв'язання", styles["section"]))
        story.append(HRFlowable(width="100%", thickness=2,
                                color=PRIMARY, spaceAfter=8))

        for step in steps:
            if isinstance(step, dict):
                story.extend(_render_step(step, styles, CONTENT_W))
            elif isinstance(step, str):
                story.append(Paragraph(step, styles["info"]))
                story.append(Spacer(1, 4))

    # ── Підвал ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Згенеровано PlanimetrySolver · "
        f"{datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M')}",
        styles["footer"],
    ))

    doc.build(story)
    return buf.getvalue()