#!/usr/bin/env python3
"""Deterministic 7 x 10 inch REVIEW books, never KDP upload masters.

Run only when the coordinating agent authorizes PDF generation. Importing this
module does not author files. Default invocation builds DE, EN, ES together.
Use --validate-only for source/schema checks without creating any artifacts.

Primary text contract: 01-concept/book-texts-v01.json, root C01..C06,
W01..W04, K01..K04, each {title:{de,en,es},panels:[{scene,lines:{de:[],
en:[],es:[]}}]}; ui contains localized fields; crafts maps B01..B08 to
{title:{de,en,es},instruction:{de,en,es}}. Speaker-prefixed strings are
printed with bold speaker names. The four front pages are derived from ui.
The following expanded schema is also accepted:
  ui: {de: {subtitle, edition, coloring, comic, jokes, mini, crafts, cut,
             fold, glue, review, ...}, en: {...}, es: {...}}
  front: {de: [{title,body}, ... exactly four], en: [...], es: [...]}
  specials: [{id, title:{de,en,es}, panels:[{dialogue:{de:[{speaker,text}],
             en:[...],es:[...]}}], instructions:{de:[...],en:[...],es:[...]}}]
  cover (optional): {base, lockup, inner_lockup, subtitle_box:[x,y,w,h]}
  craft_layouts: {B01: {image_box:[x,y,w,h], shapes:[...]}, ... B08}
Legacy craft layouts may still be supplied via --craft-layout and are validated;
built-in B01..B08 geometry is authoritative for this edition. B01/B02/B06/B07/B08
are native vector crafts and require no PNG. B03..B05 each place one intact 2:1
duo PNG over the lower halves of two separate rectangular tent cards; their
centre gutter must be blank. Legacy coordinates are normalized, top-left origin,
relative to the craft art box. Shapes: {kind:
cut|fold|glue, type:polyline|rect|ellipse, points:[[x,y],...], box:[x,y,w,h],
label:{de,en,es}}. Only explicit geometry is used. Entire generated PNGs are
contained inside image_box; source pixels are never cropped or transformed.
Composite panels are assumed equal height; speech bubbles follow the intact
placed strip in a separate right rail. Physical craft tests remain pending.

Outputs have a deterministic page/source manifest, SHA256 hashes, actual image
placement/DPI records and verification results. Existing outputs are protected.
All-page rendering, visual QA, monochrome checks and craft paper tests remain
the coordinating agent's responsibility and are marked pending in the manifest.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import re
from pathlib import Path
import tempfile
from xml.sax.saxutils import escape

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
W, H = 504.0, 720.0
LEFT, RIGHT = 45.0, 36.0  # content rectos: extra room at binding
CW = W - LEFT - RIGHT
LANGS = ("de", "en", "es")
EXPECTED = {"coloring": 30, "comic": 6, "jokes": 4, "mini": 4, "crafts": 8}
GROUPS = (("comic", "C", 6), ("jokes", "W", 4), ("mini", "K", 4), ("crafts", "B", 8))
NATIVE_CRAFTS = {"B01", "B02", "B06", "B07", "B08"}
TENT_CRAFTS = {"B03", "B04", "B05"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def localized(value, lang):
    if isinstance(value, dict) and lang in value:
        return value[lang]
    return value


def string(value, lang, context):
    value = localized(value, lang)
    require(isinstance(value, str) and value.strip(), f"Missing {lang} text: {context}")
    return value.strip()


def plain(value):
    return escape(str(value)).replace("\n", "<br/>")


def font_setup():
    runtime = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies"
    folder = runtime / "native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype"
    candidates = [folder, Path("/usr/share/fonts/truetype/dejavu"), Path("/Library/Fonts")]
    for folder in candidates:
        regular, bold = folder / "DejaVuSans.ttf", folder / "DejaVuSans-Bold.ttf"
        if regular.is_file() and bold.is_file():
            break
    else:
        raise FileNotFoundError("DejaVuSans.ttf and DejaVuSans-Bold.ttf required")
    pdfmetrics.registerFont(TTFont("Book", str(regular)))
    pdfmetrics.registerFont(TTFont("BookBold", str(bold)))
    pdfmetrics.registerFontFamily("Book", normal="Book", bold="BookBold", italic="Book", boldItalic="BookBold")
    display = Path("/System/Library/Fonts/Supplemental/Chalkboard.ttc")
    try:
        pdfmetrics.registerFont(TTFont("Display", str(display), subfontIndex=0))
    except Exception:
        display = bold
        pdfmetrics.registerFont(TTFont("Display", str(display)))
    return [regular, bold, display]


class Book:
    def __init__(self, root, texts_path, motifs_path, craft_path=None):
        self.root = root.resolve()
        self.texts_path, self.motifs_path = texts_path, motifs_path
        self.texts = read_json(texts_path)
        self.motifs = read_json(motifs_path)
        if isinstance(self.motifs, dict):
            self.motifs = self.motifs["motifs"]
        raw = self.texts.get("specials", [])
        if not raw:
            raw = [{"id": sid, **value} for sid, value in self.texts.items()
                   if len(sid) == 3 and sid[0] in "CWK" and sid[1:].isdigit()]
            raw += [{"id": sid, "instructions": value.get("instruction"), **value}
                    for sid, value in self.texts.get("crafts", {}).items()]
        self.specials = {v["id"]: v for v in raw} if isinstance(raw, list) else raw
        require(len(self.specials) == len(raw), "Duplicate special IDs")
        self.layouts = read_json(craft_path) if craft_path else self.texts.get("craft_layouts", {})
        self.craft_path = craft_path
        self.assets = {}
        self.placements = []
        self.plan = []
        self.lang = None
        self.c = None
        self.page = 0

    def path(self, value):
        path = (self.root / value).resolve()
        require(path.is_relative_to(self.root), f"Asset outside project: {value}")
        require(path.is_file(), f"Required asset is absent: {path}")
        require(path.suffix.lower() == ".png", f"Generated imagery must be PNG: {path}")
        if path not in self.assets:
            with Image.open(path) as im:
                require(im.format == "PNG", f"Not a PNG: {path}")
                im.verify()
            with Image.open(path) as im:
                self.assets[path] = {"path": str(path.relative_to(self.root)),
                                     "sha256": digest(path), "pixels": list(im.size), "mode": im.mode}
        return path

    def ui(self, key):
        ui = localized(self.texts["ui"], self.lang)
        aliases = {"review": "review_note"}
        key = aliases.get(key, key)
        section_names = {"coloring": ("Ausmalbilder", "Coloring pages", "Para colorear"),
                         "comic": ("Die Geschichte", "The story", "La historia"),
                         "jokes": ("Zum Kichern", "Time to giggle", "Para reír"),
                         "mini": ("Kleine Geschichten", "Little stories", "Pequeñas historias"),
                         "crafts": ("Bastelzeit", "Craft time", "Manualidades")}
        if key not in ui and key in section_names:
            return section_names[key][LANGS.index(self.lang)]
        require(key in ui, f"Missing ui.{self.lang}.{key}")
        return string(ui[key], self.lang, f"ui.{key}")

    def front(self, lang):
        if "front" not in self.texts:
            ui = localized(self.texts["ui"], lang)
            field = lambda key: string(ui[key], lang, f"ui.{key}")
            return [{"title": field("subtitle"), "body": [field("edition"), field("content_line")]},
                    {"title": field("edition"), "body": [field("imprint_note"), field("review_note")]},
                    {"title": field("welcome_title"), "body": [field("welcome_text"), field("belongs")], "name_line": True},
                    {"title": field("craft_intro_title"), "body": [field("craft_intro_text")]},
                    {"title": "Pips", "body": [
                        {"de": "Das ist Pips – unser kleiner Special-Gast! Pips ist ein freundliches Gespenst mit einer kleinen Locke und einem gewellten Saum. Pips erschreckt niemanden – Pips bringt lieber alle zum Lachen!", "en": "Meet Pips – our special guest! Pips is a friendly little ghost with one curl and a scalloped hem. Pips never scares anyone – Pips makes everyone giggle!", "es": "¡Conoce a Pips, nuestro invitado especial! Pips es un fantasmita amable con un pequeño rizo y un borde ondulado. Pips no asusta a nadie: ¡Pips hace reír a todos!"},
                    ]}]
        pages = localized(self.texts["front"], lang)
        require(isinstance(pages, list) and len(pages) == 4, f"Exactly four front pages needed: {lang}")
        return pages

    def special(self, sid):
        require(sid in self.specials, f"Missing special text: {sid}")
        return self.specials[sid]

    def dialogue(self, panel):
        value = localized(panel, self.lang)
        if isinstance(value, dict):
            value = localized(value.get("dialogue", value.get("lines", [])), self.lang)
        if isinstance(value, str):
            return plain(value)
        require(isinstance(value, list), f"Invalid dialogue: {value!r}")
        result = []
        for line in value:
            if isinstance(line, str):
                speaker, separator, words = line.partition(":")
                result.append(f"<b>{plain(speaker)}:</b> {plain(words.strip())}" if separator else plain(line))
            else:
                text = string(line["text"], self.lang, "dialogue")
                speaker = localized(line.get("speaker", ""), self.lang)
                require(isinstance(speaker, str), "Unlocalized speaker name")
                result.append((f"<b>{plain(speaker)}:</b> " if speaker else "") + plain(text))
        return "<br/>".join(result)

    def make_plan(self):
        content = []
        # Four brief interludes, each after six coloring motifs. Main comic stays
        # continuous; all expendable craft sheets are together at the back.
        for index, motif in enumerate(self.motifs, 1):
            content.append(("coloring", motif["id"]))
            if index in (6, 12, 18, 24):
                n = index // 6
                content.extend((("jokes", f"W{n:02}"), ("mini", f"K{n:02}")))
        content.extend(("comic", f"C{n:02}") for n in range(1, 7))
        content.extend(("crafts", f"B{n:02}") for n in range(1, 9))
        require(Counter(k for k, _ in content) == Counter(EXPECTED), "Content counts differ")
        self.plan = [{"pdf_page": 1, "interior_page": None, "kind": "cover", "id": "cover"}]
        for n in range(1, 6):
            self.plan.append({"pdf_page": n + 1, "interior_page": n, "kind": "front", "id": f"front{n}"})
        for index, (kind, sid) in enumerate(content):
            interior = 6 + 2 * index
            self.plan.append({"pdf_page": interior + 1, "interior_page": interior,
                              "kind": kind, "id": sid, "side": "recto"})
            self.plan.append({"pdf_page": interior + 2, "interior_page": interior + 1,
                              "kind": "blank", "id": f"reverse-{sid}", "side": "verso"})
        require(len(self.plan) == 110, "Review PDF must contain 110 pages")

    def validate(self, languages):
        require(len(self.motifs) == 30, "Exactly 30 motifs required")
        for field in ("id", "path"):
            require(len({m[field] for m in self.motifs}) == 30, f"Duplicate motif {field}")
        require({str(m["id"]) for m in self.motifs} == {f"{i:02}" for i in range(1, 31)}, "Motif IDs must be 01..30")
        expected_ids = {f"{prefix}{n:02}" for _, prefix, count in GROUPS for n in range(1, count + 1)}
        require(set(self.specials) == expected_ids, "Specials must contain exactly C01-C06, W01-W04, K01-K04, B01-B08")
        cover = self.texts.get("cover", {})
        self.path(cover.get("base", "04-cover/drafts/v01/cover-base.png"))
        self.path(cover.get("lockup", "04-cover/drafts/v01/title-lockup.png"))
        self.path(cover.get("inner_lockup", "04-cover/drafts/v01/title-inner-bw.png"))
        self.path("06-listing/publisher-mark/drafts/giggling-house-v01.png")
        for motif in self.motifs:
            self.path(motif["path"])
        require(len({self.assets[self.path(m["path"])]["sha256"] for m in self.motifs}) == 30,
                "Two motifs use identical image bytes")
        for sid in sorted(expected_ids):
            item = self.special(sid)
            if sid not in NATIVE_CRAFTS:
                asset = self.path(item.get("path", f"05-kdp/specials/v01/{sid}.png"))
                if sid in TENT_CRAFTS:
                    pw, ph = self.assets[asset]["pixels"]
                    require(abs(pw / ph - 2) < .03, f"{sid}: tent duo must be landscape 2:1")
            if sid.startswith("B"):
                # Built-in functional geometry is authoritative for this edition.
                # Keep validating supplied legacy geometry rather than silently
                # accepting malformed optional input; no external file is needed.
                layout = self.layouts.get(sid, item.get("geometry"))
                if layout is not None:
                    self.validate_geometry(layout, sid)
            else:
                expected_panels = 1 if sid.startswith("W") else (3 if sid in ("C04", "C05") else 4)
                for lang in languages:
                    panels = localized(item.get("panels"), lang)
                    require(isinstance(panels, list) and len(panels) == expected_panels,
                            f"{sid}/{lang} must have {expected_panels} panels")
        for lang in languages:
            self.lang = lang
            for key in ("subtitle", "edition", "coloring", "comic", "jokes", "mini", "crafts", "cut", "fold", "glue", "review"):
                self.ui(key)
            for page in self.front(lang):
                string(page["title"], lang, "front.title")
                require("body" in page, "Front page body missing")
            for motif in self.motifs:
                string(motif["title"], lang, motif["id"])
            for sid, item in self.specials.items():
                string(item["title"], lang, sid)
                if sid.startswith("B"):
                    instructions = localized(item.get("instructions"), lang)
                    require(isinstance(instructions, (list, str)) and instructions, f"Instructions absent: {sid}/{lang}")
                else:
                    for panel in localized(item["panels"], lang):
                        self.dialogue(panel)  # Silent panels intentionally allow [].
        self.make_plan()

    @staticmethod
    def validate_geometry(layout, sid):
        def box(values):
            require(isinstance(values, list) and len(values) == 4, f"Invalid box: {sid}")
            x, y, w, h = values
            require(0 <= x < 1 and 0 <= y < 1 and w > 0 and h > 0 and x + w <= 1.000001 and y + h <= 1.000001,
                    f"Geometry outside art area: {sid}")
        box(layout["image_box"])
        require(layout.get("shapes"), f"Craft must include explicit geometry: {sid}")
        for shape in layout["shapes"]:
            require(shape["kind"] in ("cut", "fold", "glue"), f"Invalid line kind: {sid}")
            require(shape["type"] in ("polyline", "rect", "ellipse"), f"Invalid shape: {sid}")
            if shape["type"] == "polyline":
                require(len(shape["points"]) >= 2, f"Too few points: {sid}")
                require(all(len(p) == 2 and all(0 <= v <= 1 for v in p) for p in shape["points"]), f"Invalid points: {sid}")
                require(not shape.get("label"), "Put labels on rectangular glue tabs, not polylines")
            else:
                box(shape["box"])

    def text(self, markup, x, top, width, height, size=12, minimum=None, align=0, font="Book"):
        if not markup:
            return 0
        minimum = size if minimum is None else minimum
        trial = size
        while trial >= minimum - .01:
            style = ParagraphStyle("book", fontName=font, fontSize=trial,
                                   leading=trial * 1.34, alignment=align, textColor=colors.black,
                                   splitLongWords=False, allowWidows=0, allowOrphans=0)
            paragraph = Paragraph(markup, style)
            aw, ah = paragraph.wrap(width, height)
            # Paragraph.wrap may silently let an indivisible word exceed width.
            longest = max((pdfmetrics.stringWidth(word, font, trial) for word in
                           re.sub("<[^>]+>", " ", markup).split()), default=0)
            if ah <= height + .01 and aw <= width + .01 and longest <= width + .01:
                paragraph.drawOn(self.c, x, top - ah)
                return ah
            trial -= .25
        raise ValueError(f"Text overflow {self.lang} PDF page {self.page}: {markup[:120]}")

    def image(self, value, x, y, width, height):
        path = self.path(value)
        pw, ph = self.assets[path]["pixels"]
        scale = min(width / pw, height / ph)
        dw, dh = pw * scale, ph * scale
        dx, dy = x + (width - dw) / 2, y + (height - dh) / 2
        self.c.drawImage(str(path), dx, dy, dw, dh, mask="auto")
        self.placements.append({"pdf_page": self.page, "path": str(path.relative_to(self.root)),
                                "box_pt": [round(v, 4) for v in (dx, dy, dw, dh)],
                                "effective_dpi": round(72 / scale, 2), "source_cropped": False})
        return dx, dy, dw, dh

    def chrome(self, title, category, interior):
        self.text(plain(category.upper()), LEFT, H - 29, CW, 18, size=8.5, font="BookBold")
        if title:
            self.text(plain(title), LEFT, H - 52, CW, 49, size=21, minimum=17, font="Display")
        self.c.setLineWidth(.65)
        self.c.line(LEFT, 27, W - RIGHT, 27)
        self.c.setFont("Book", 8)
        self.c.drawString(LEFT, 15, "Giggle Dumplings")
        self.c.drawRightString(W - RIGHT, 15, str(interior))

    def cover_page(self):
        cover = self.texts.get("cover", {})
        self.image(cover.get("base", "04-cover/drafts/v01/cover-base.png"), 0, 0, W, H)
        # Cream scalloped series plaque surrounds the intact wordmark layer.
        self.c.setFillColor(colors.HexColor("#fff9e8"))
        self.c.setStrokeColor(colors.HexColor("#ffc16a"))
        self.c.setLineWidth(1)
        p = self.c.beginPath()
        p.moveTo(29, 512)
        p.curveTo(3, 536, 10, 564, 28, 573)
        p.curveTo(8, 596, 17, 619, 40, 624)
        p.curveTo(26, 650, 45, 675, 74, 674)
        p.curveTo(83, 705, 121, 712, 147, 697)
        p.curveTo(176, 726, 221, 722, 252, 707)
        p.curveTo(285, 722, 330, 723, 355, 697)
        p.curveTo(385, 712, 425, 705, 434, 674)
        p.curveTo(459, 676, 481, 650, 466, 624)
        p.curveTo(490, 618, 497, 596, 478, 573)
        p.curveTo(498, 546, 490, 523, 473, 512)
        p.curveTo(405, 477, 99, 477, 29, 512)
        p.close()
        self.c.drawPath(p, stroke=1, fill=1)
        self.image(cover.get("lockup", "04-cover/drafts/v01/title-lockup.png"), 72, 505, 360, 170)
        # Local vector ribbon: illustration remains the untouched generated PNG.
        bx, by, bw, bh = cover.get("subtitle_box", [56, 470, 392, 50])
        self.c.setFillColor(colors.HexColor("#F5AA43"))
        self.c.setStrokeColor(colors.HexColor("#321A46"))
        self.c.setLineWidth(1.3)
        path = self.c.beginPath()
        for index, (x, y) in enumerate([(bx-15, by+bh-5), (bx, by+bh-5), (bx, by+bh),
                (bx+bw, by+bh), (bx+bw, by+bh-5), (bx+bw+15, by+bh-5),
                (bx+bw+8, by+bh/2), (bx+bw+15, by+5), (bx+bw, by+5),
                (bx+bw, by), (bx, by), (bx, by+5), (bx-15, by+5), (bx-8, by+bh/2)]):
            (path.moveTo if index == 0 else path.lineTo)(x, y)
        path.close()
        self.c.drawPath(path, stroke=1, fill=1)
        self.text(plain(self.ui("subtitle")), bx+12, by+bh-8, bw-24, bh-12,
                  size=18, minimum=14, align=1, font="Display")
        self.c.setFillColor(colors.white)
        self.c.roundRect(28, 12, 448, 43, 10, fill=1, stroke=0)
        tagline = {"de": "30 Ausmalbilder + Comics & Bastelspaß", "en": "30 coloring pictures + comics & crafts", "es": "30 dibujos para colorear + cómics y manualidades"}[self.lang]
        self.text(plain(tagline), 39, 47, 426, 20, size=13, minimum=11, align=1, font="Display")
        self.text(plain(self.ui("edition")), 39, 27, 426, 12, size=8, align=1)

    def front_page(self, item, interior):
        title = string(item["title"], self.lang, "front")
        self.chrome(title if interior != 1 else "", self.ui("edition"), interior)
        top = 594
        if interior == 1:
            lockup = self.texts.get("cover", {}).get("inner_lockup", "04-cover/drafts/v01/title-inner-bw.png")
            if lockup:
                self.image(lockup, LEFT, 402, CW, 185)
                self.c.setLineWidth(1)
                self.c.roundRect(LEFT+5, 340, CW-10, 50, 12, stroke=1, fill=0)
                self.text(plain(self.ui("subtitle")), LEFT+15, 377, CW-30, 35, size=20, minimum=17, align=1, font="Display")
                top = 313
            else:
                self.text("Giggle Dumplings", LEFT, 569, CW, 68, size=33, align=1, font="Display")
                self.text(plain(self.ui("subtitle")), LEFT, 492, CW, 65, size=22, minimum=18, align=1, font="Display")
                top = 391
        if interior == 2:
            imprint = string(item["body"][0], self.lang, "front.imprint")
            lines = imprint.split("\n")
            self.c.setFont("Book", 10.5)
            y = 82 + (len(lines)-1)*15
            for line in lines:
                self.c.drawString(LEFT+10, y, line); y -= 15
            self.image("06-listing/publisher-mark/drafts/giggling-house-v01.png", W-RIGHT-78, 72, 58, 58)
            return
        body = localized(item["body"], self.lang)
        body = body if isinstance(body, list) else [body]
        for paragraph in body:
            text = string(paragraph, self.lang, "front.body")
            used = self.text(plain(text), LEFT+10, top, CW-20, top-70, size=12.5)
            top -= used + 19
        if item.get("name_line"):
            require(top > 95, "No room for owner name line")
            self.c.setLineWidth(.8)
            self.c.line(LEFT+10, top-20, W-RIGHT-10, top-20)
        if interior in (1, 3, 4):
            asset = {1: "B03", 3: "B04", 4: "B05"}[interior]
            self.image(f"05-kdp/specials/v01/{asset}.png", LEFT+15, 60, CW-30, min(160, max(70, top-135)))
        if item.get("image"):
            require(top > 160, "Insufficient space for front illustration")
            self.image(item["image"], LEFT, 60, CW, top - 80)

    def coloring_page(self, item, interior):
        self.chrome(string(item["title"], self.lang, item["id"]), self.ui("coloring"), interior)
        x, y, w, h = self.image(item["path"], LEFT, 44, CW, 561.6)
        self.c.setLineWidth(1)
        self.c.rect(x, y, w, h, stroke=1, fill=0)

    def comic_page(self, item, kind, interior):
        self.chrome(string(item["title"], self.lang, item["id"]), self.ui(kind), interior)
        panels = localized(item["panels"], self.lang)
        if kind == "jokes":
            self.image(item.get("path", f"05-kdp/specials/v01/{item['id']}.png"), LEFT, 155, CW, 450)
            self.c.setLineWidth(1)
            self.c.roundRect(LEFT, 45, CW, 95, 16, stroke=1, fill=0)
            self.text(self.dialogue(panels[0]), LEFT+17, 126, CW-34, 74,
                      size=15, minimum=13, font="Display")
            return
        art_width, gap = CW * .62, 13
        x, y, width, height = self.image(item.get("path", f"05-kdp/specials/v01/{item['id']}.png"),
                                        LEFT, 44, art_width, 7.8 * 72)
        rail_x = LEFT + art_width + gap
        rail_w = CW - art_width - gap
        row_height = height / len(panels)
        for n, panel in enumerate(panels):
            top = y + height - n * row_height
            dialogue = self.dialogue(panel)
            if not dialogue:
                continue
            self.c.setLineWidth(.8)
            self.c.roundRect(rail_x, top-row_height+5, rail_w, row_height-10, 10, stroke=1, fill=0)
            # Tail stays entirely in the gutter, never over source panels/text.
            mid = top-row_height/2
            self.c.setFillColor(colors.white)
            p = self.c.beginPath()
            p.moveTo(rail_x+.5, mid+5)
            p.lineTo(x+width+2, mid-3)
            p.lineTo(rail_x+.5, mid-5)
            self.c.drawPath(p, stroke=0, fill=1)
            self.c.line(rail_x, mid+5, x+width+2, mid-3)
            self.c.line(x+width+2, mid-3, rail_x, mid-5)
            self.c.setFillColor(colors.black)
            self.text(dialogue, rail_x+8, top-13, rail_w-16, row_height-26,
                      size=12, minimum=11)

    def native_craft(self, sid, region, item):
        """Cuttable geometry in points, local bottom-left origin; paper QA pending.

        Native symbols are generic geometric crafts, not character illustrations.
        All bounds include cutting clearance inside the 423 x 388 pt art box.
        """
        c = self.c
        rx, ry, rw, rh = region
        c.saveState()
        c.translate(rx, ry)
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.black)
        c.setLineWidth(1.1)
        c.setDash([])

        def line(x1, y1, x2, y2, kind="cut"):
            c.setDash([5, 3] if kind == "fold" else ([1, 2] if kind == "glue" else []))
            c.line(x1, y1, x2, y2)
            c.setDash([])

        def outline(points):
            p = c.beginPath()
            p.moveTo(*points[0])
            for point in points[1:]:
                p.lineTo(*point)
            p.close()
            c.drawPath(p, stroke=1, fill=0)

        def face(x, y, scale=1):
            for dx in (-10, 10):
                c.circle(x+dx*scale, y+5*scale, 2.5*scale, stroke=1, fill=0)
            p = c.beginPath()
            p.moveTo(x-8*scale, y-6*scale)
            p.curveTo(x-4*scale, y-14*scale, x+4*scale, y-14*scale, x+8*scale, y-6*scale)
            c.drawPath(p, stroke=1, fill=0)

        def ghost(x, y, w, h):
            p = c.beginPath()
            p.moveTo(x, y+12)
            p.lineTo(x, y+h*.55)
            p.curveTo(x, y+h*1.15, x+w, y+h*1.15, x+w, y+h*.55)
            p.lineTo(x+w, y+12)
            for a in range(3):
                right = x+w-a*w/3
                p.curveTo(right-w/12, y-3, right-w/4, y-3, right-w/3, y+12)
            p.close()
            c.drawPath(p, stroke=1, fill=0)
            face(x+w/2, y+h*.56, min(w/55, 1.5))

        def symbol(kind, x, y):
            if kind == "ghost":
                ghost(x-27, y-34, 54, 70)
            elif kind == "pumpkin":
                c.ellipse(x-35, y-29, x+35, y+29, stroke=1, fill=0)
                c.ellipse(x-22, y-29, x+22, y+29, stroke=1, fill=0)
                c.rect(x-4, y+29, 8, 10, stroke=1, fill=0)
                face(x, y)
            elif kind == "bat":
                outline([(x-9,y+15),(x-16,y+27),(x-17,y+9),(x-43,y+19),
                         (x-37,y-8),(x-23,y-2),(x-16,y-16),(x,y-23),
                         (x+16,y-16),(x+23,y-2),(x+37,y-8),(x+43,y+19),
                         (x+17,y+9),(x+16,y+27),(x+9,y+15)])
                face(x, y, .7)
            else:
                c.ellipse(x-36, y-27, x+36, y+27, stroke=1, fill=0)
                for dx in (-15, 0, 15):
                    line(x+dx, y+24, x+dx*.65, y+14)
                face(x, y)

        if sid in ("B01", "B02"):
            # 140 mm total maximum width; photo prop, no wearable-fit promise.
            mw = 140 * 72 / 25.4
            ox, oy = (rw-mw)/2, 190
            c.saveState()
            c.translate(ox, oy)
            c.scale(mw/396, 1)
            p = c.beginPath()
            p.moveTo(0, 70)
            p.curveTo(0, 115, 35, 143, 70, 148)
            if sid == "B01":
                p.lineTo(94, 179)
                p.lineTo(119, 151)
                p.curveTo(165, 162, 231, 162, 277, 151)
                p.lineTo(302, 179)
                p.lineTo(326, 148)
            else:
                p.curveTo(115, 167, 162, 158, 184, 158)
                p.lineTo(184, 179)
                p.lineTo(210, 179)
                p.lineTo(210, 158)
                p.curveTo(265, 168, 298, 157, 326, 148)
            p.curveTo(361, 143, 396, 115, 396, 70)
            p.curveTo(396, 17, 316, 4, 232, 34)
            p.lineTo(214, 56)
            p.curveTo(205, 66, 191, 66, 182, 56)
            p.lineTo(164, 34)
            p.curveTo(80, 4, 0, 17, 0, 70)
            p.close()
            c.drawPath(p, stroke=1, fill=0)
            # Closed smooth eye cutouts, 29.6 x 15.5 mm, 62.2 mm centres.
            for ex in (110, 286):
                c.ellipse(ex-42, 68, ex+42, 112, stroke=1, fill=0)
            c.restoreState()
            # Separate wide card handle; dotted overlap attaches behind one cheek.
            c.rect(150, 12, 34, 145, stroke=1, fill=0)
            line(150, 122, 184, 122, "glue")
        elif sid in TENT_CRAFTS:
            # One intact duo image spans BOTH fronts; blank centre falls in the
            # 16 pt cut-away gutter. No clipping, splitting or pixel manipulation.
            span, gap = 392.0, 16.0
            x, y, half = (rw-span)/2, 8.0, 184.0
            c.saveState()
            c.translate(-rx, -ry)
            self.image(item.get("path", f"05-kdp/specials/v01/{sid}.png"),
                       rx+x, ry+y, span, half)
            c.restoreState()
            for xx in (x, x+(span+gap)/2):
                c.rect(xx, y, (span-gap)/2, 2*half, stroke=1, fill=0)
                line(xx, y+half, xx+(span-gap)/2, y+half, "fold")
        elif sid == "B06":
            # One-fold card as described in all three instruction texts.
            # Blank upper half folds behind illustrated lower half; reverse
            # of the sheet becomes the blank inside for the child's drawing.
            x, y, w, h = 71.5, 20, 280, 336
            c.rect(x, y, w, h, stroke=1, fill=0)
            line(x, y+h/2, x+w, y+h/2, "fold")
            c.saveState()
            c.translate(x+w/2, y+76)
            c.scale(1.65, 1.65)
            symbol("pumpkin", 0, 0)
            c.restoreState()
        elif sid == "B07":
            for i in range(3):
                x = 22+i*135
                ghost(x, 203, 105, 155)
                # Separate 38.8 x 9.9 mm adjustable ring, 7 mm overlap.
                c.rect(x-2, 112, 110, 28, stroke=1, fill=0)
                line(x+88, 112, x+88, 140, "glue")
        elif sid == "B08":
            for i, kind in enumerate(("pumpkin", "ghost", "bat", "dumpling")):
                x, y = 31.5+(i%2)*204, 12+(1-i//2)*190
                c.rect(x, y, 156, 170, stroke=1, fill=0)
                line(x, y+140, x+156, y+140, "fold")
                c.setDash([1, 2])
                c.rect(x+10, y+151, 136, 12, stroke=1, fill=0)
                c.setDash([])
                self.text(plain(self.ui("glue")), x+12, y+161, 132, 10, size=6, align=1)
                symbol(kind, x+78, y+70)
        else:
            raise ValueError(f"Unknown built-in craft: {sid}")
        c.restoreState()

    def craft_page(self, item, interior):
        self.chrome(string(item["title"], self.lang, item["id"]), self.ui("crafts"), interior)
        instructions = localized(item["instructions"], self.lang)
        if isinstance(instructions, list):
            instructions = "<br/>".join(f"<b>{i}.</b> {plain(string(s, self.lang, 'craft instruction'))}"
                                        for i, s in enumerate(instructions, 1))
        else:
            instructions = plain(instructions)
        self.text(instructions, LEFT, 607, CW, 132, size=11.5, minimum=11)
        region = (LEFT, 72, CW, 388)
        self.native_craft(item["id"], region, item)
        for i, key in enumerate(("cut", "fold", "glue")):
            x = LEFT + i * CW / 3
            self.c.setDash([5, 3] if key == "fold" else ([1, 2] if key == "glue" else []))
            self.c.line(x, 50, x+22, 50)
            self.c.setDash([])
            self.text(plain(self.ui(key)), x+28, 57, CW/3-30, 20, size=8)

    def build(self, lang, path):
        self.lang, self.page, self.placements = lang, 0, []
        self.c = canvas.Canvas(str(path), pagesize=(W, H), invariant=1, pageCompression=1)
        self.c.setTitle(f"Giggle Dumplings - {self.ui('subtitle')} - Review v01")
        self.c.setAuthor("Giggle Dumplings")
        self.c.setSubject("Review only; independent cover preview + 108-page interior; visual QA pending")
        motifs = {m["id"]: m for m in self.motifs}
        for page in self.plan:
            self.page = page["pdf_page"]
            self.c.setFillColor(colors.black)
            self.c.setStrokeColor(colors.black)
            kind, sid, interior = page["kind"], page["id"], page["interior_page"]
            if kind == "cover":
                self.cover_page()
            elif kind == "front":
                self.front_page(self.front(lang)[interior-1], interior)
            elif kind == "coloring":
                self.coloring_page(motifs[sid], interior)
            elif kind == "crafts":
                self.craft_page(self.special(sid), interior)
            elif kind != "blank":
                self.comic_page(self.special(sid), kind, interior)
            self.c.showPage()
        self.c.save()
        reader = PdfReader(path)
        require(len(reader.pages) == 109, "Generated PDF page count is not 109")
        for record, pdf_page in zip(self.plan, reader.pages):
            require(abs(float(pdf_page.mediabox.width)-W) < .01 and
                    abs(float(pdf_page.mediabox.height)-H) < .01, "Incorrect page dimensions")
            if record["kind"] == "blank":
                stream = pdf_page.get_contents()
                # Fonts and CTM setup are harmless; no painting or text permitted.
                forbidden = {b"Do", b"Tj", b"TJ", b"'", b'"', b"S", b"s", b"f", b"F", b"f*", b"B", b"B*", b"b", b"b*", b"sh"}
                require(not stream or not any(op in forbidden for _, op in stream.operations),
                        f"Reverse is not blank: PDF {record['pdf_page']}")
        return {"language": lang, "file": path.name, "sha256": digest(path),
                "pages": 109, "placements": list(self.placements),
                "checks": {"page_count": "passed", "page_dimensions": "passed", "blank_reverses": "passed",
                           "unique_motifs": "passed", "missing_assets": "passed", "text_fit": "passed"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--texts", type=Path, default=Path("01-concept/book-texts-v01.json"))
    parser.add_argument("--motifs", type=Path, default=Path("01-concept/motifs-v01.json"))
    parser.add_argument("--craft-layout", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("05-kdp/review/v01"))
    parser.add_argument("--languages", nargs="+", choices=LANGS, default=list(LANGS))
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    resolve = lambda p: (root / p).resolve() if p else None
    require(len(set(args.languages)) == len(args.languages), "Duplicate languages")
    book = Book(root, resolve(args.texts), resolve(args.motifs), resolve(args.craft_layout))
    book.validate(args.languages)
    fonts = font_setup()
    if args.validate_only:
        print("Source checks passed; 109 planned pages per language. No PDFs created; text layout/visual QA pending.")
        return
    output = resolve(args.output_dir)
    require(output.is_relative_to(root), "Output directory must be inside project")
    names = [f"giggle-dumplings-halloween-{lang}-review-v01.pdf" for lang in args.languages]
    manifest_name = "build-manifest-v01.json"
    for name in [*names, manifest_name]:
        require(not (output / name).exists(), f"Output exists; select a new version directory: {output/name}")
    output.mkdir(parents=True, exist_ok=True)
    # Do not publish partial language sets when layout validation fails.
    with tempfile.TemporaryDirectory(prefix=".build-v01-", dir=output) as staging:
        staged = Path(staging)
        editions = [book.build(lang, staged / name) for lang, name in zip(args.languages, names)]
        sources = [book.texts_path, book.motifs_path, Path(__file__).resolve()]
        if book.craft_path:
            sources.append(book.craft_path)
        manifest = {"schema_version": 1, "status": "review-draft", "trim_inches": [7, 10],
                    "bleed": False, "paper": "undecided", "upload_ready": False,
                    "cover_preview_independent": True, "interior_pages": 108, "review_pages": 109,
                    "content_counts": EXPECTED, "page_plan": book.plan,
                    "sources": [{"path": str(p.relative_to(root)) if p.is_relative_to(root) else str(p),
                                 "sha256": digest(p)} for p in sources],
                    "fonts": [{"path": str(p), "sha256": digest(p)} for p in fonts],
                    "assets": sorted(book.assets.values(), key=lambda a: a["path"]), "editions": editions,
                    "pending": ["Render and visually inspect every PDF page", "Source monochrome and contour QA",
                                "Effective image resolution acceptance", "Craft assembly at original size",
                                "B01/B02 140 mm photo-prop eye spacing and handle attachment physical test",
                                "B03-B05 blank image centre registration and tent stability physical test",
                                "B06 single-fold surprise card physical test",
                                "B07 three ghost ring fit and B08 hanging fold-tab physical tests",
                                "Interior title series-style adaptation if inner_lockup omitted",
                                "Editorial approval and official KDP preflight before upload"]}
        (staged / manifest_name).write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        for name in [*names, manifest_name]:
            # Exclusive create also prevents accidental overwrite during races.
            with (output / name).open("xb") as dest, (staged / name).open("rb") as source:
                for block in iter(lambda: source.read(1024*1024), b""):
                    dest.write(block)
    print(f"Built {len(editions)} review PDFs, 109 pages each, in {output}. All-page visual QA is still required.")


if __name__ == "__main__":
    main()
