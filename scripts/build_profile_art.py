#!/usr/bin/env python3
"""Build local PNG/GIF artwork for the GitHub profile README."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

W = 1600
NAVY = (7, 11, 22)
WHITE = (248, 250, 252)
MUTED = (148, 163, 184)
SOFT = (203, 213, 225)
INDIGO = (99, 102, 241)
CYAN = (34, 211, 238)
VIOLET = (167, 139, 250)
LINE = (30, 41, 59)

SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf"
MONO_B = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def tracked_width(text: str, fnt: ImageFont.FreeTypeFont, tracking: int) -> int:
    if not text:
        return 0
    widths = [fnt.getlength(ch) for ch in text]
    return int(sum(widths) + tracking * (len(text) - 1))


def draw_tracked(draw: ImageDraw.ImageDraw, text: str, cx: int, y: int, fnt, fill, tracking=6, anchor="m"):
    total = tracked_width(text, fnt, tracking)
    x = cx - total // 2 if anchor == "m" else cx
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += fnt.getlength(ch) + tracking


def round_clip(im: Image.Image, radius: int) -> Image.Image:
    im = im.convert("RGBA")
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), radius, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, mask=mask)
    return out


def cover(src: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    sw, sh = src.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def vignette(size: tuple[int, int], strength: float = 0.55) -> Image.Image:
    small = Image.new("L", (80, 50), 0)
    px = small.load()
    cx, cy = 40, 25
    max_d = math.hypot(cx, cy)
    for y in range(50):
        for x in range(80):
            d = math.hypot(x - cx, y - cy) / max_d
            t = min(1.0, max(0.0, (d - 0.12) / 0.88))
            px[x, y] = int(255 * (1 - strength * (t**1.5)))
    shade = small.resize(size, Image.Resampling.LANCZOS).convert("RGB")
    return shade


def gradient_bar(width: int, height: int, t: float = 0.0) -> Image.Image:
    bar = Image.new("RGB", (width, height))
    px = bar.load()
    colors = [INDIGO, CYAN, VIOLET, INDIGO]
    for x in range(width):
        p = (x / max(width - 1, 1) + t) % 1.0
        seg = p * (len(colors) - 1)
        i = int(seg)
        f = seg - i
        c1, c2 = colors[i], colors[min(i + 1, len(colors) - 1)]
        c = tuple(int(c1[k] + (c2[k] - c1[k]) * f) for k in range(3))
        for y in range(height):
            px[x, y] = c
    return bar


def sheen(width: int, height: int, x0: int) -> Image.Image:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for i, alpha in enumerate((0, 40, 90, 40, 0)):
        draw.rectangle((x0 + i * 10, 0, x0 + 18 + i * 10, height), fill=(255, 255, 255, alpha))
    return layer.filter(ImageFilter.GaussianBlur(6))


def save_gif(frames: list[Image.Image], path: Path, duration: int) -> None:
    quantized = [im.convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for im in frames]
    quantized[0].save(
        path,
        save_all=True,
        append_images=quantized[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_w: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def build_banner() -> None:
    src = Image.open(ASSETS / "hero-bg.png").convert("RGB")
    base = cover(src, (W, 520))
    base = ImageChops.multiply(base, vignette((W, 520), 0.62))
    draw = ImageDraw.Draw(base)
    draw.rectangle((0, 0, W, 6), fill=INDIGO)
    bar = gradient_bar(W, 6, 0.08)
    base.paste(bar, (0, 0))

    # viewfinder corners
    for x, y, dx, dy in ((40, 40, 1, 1), (W - 40, 40, -1, 1), (40, 480, 1, -1), (W - 40, 480, -1, -1)):
        draw.line((x, y, x + 36 * dx, y), fill=CYAN, width=3)
        draw.line((x, y, x, y + 36 * dy), fill=CYAN, width=3)

    draw_tracked(draw, "FULL-STACK DEVELOPER  ·  SOFTWARE ENGINEERING", W // 2, 118, font(MONO, 22), MUTED, 4)
    draw_tracked(draw, "ALI YAQOUB", W // 2, 200, font(SANS_B, 86), WHITE, 14)
    underline = gradient_bar(280, 6)
    base.paste(underline, ((W - 280) // 2, 312))
    draw_tracked(draw, "React   Angular   Node.js   Laravel   Figma", W // 2, 350, font(SANS, 26), SOFT, 3)
    draw_tracked(draw, "AN-NAJAH NATIONAL UNIVERSITY  ·  PALESTINE", W // 2, 408, font(MONO, 18), (100, 116, 139), 3)

    out = round_clip(base, 36)
    out.save(ASSETS / "banner.png", optimize=True)


def build_available() -> None:
    frames = []
    for i in range(16):
        im = Image.new("RGB", (232, 56), (6, 40, 31))
        d = ImageDraw.Draw(im)
        pulse = 0.5 + 0.5 * math.sin(i / 16 * math.tau)
        cx, cy = 32, 28
        halo = 10 + int(5 * pulse)
        d.ellipse((cx - halo, cy - halo, cx + halo, cy + halo), fill=(6, 80, 55))
        d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(52, 211, 153))
        d.text((56, 28), "AVAILABLE FOR WORK", font=font(MONO_B, 16), fill=(167, 243, 208), anchor="lm")
        frames.append(im)
    save_gif(frames, ASSETS / "available.gif", 80)


def build_typing() -> None:
    lines = [
        "I build fast, accessible web applications",
        "React & Angular on the front end",
        "Node.js & Laravel on the back end",
        "Designed in Figma, shipped in TypeScript",
    ]
    w, h = 1100, 84
    fnt = font(SANS_B, 32)
    def frame(text: str, cursor: bool) -> Image.Image:
        im = Image.new("RGB", (w, h), NAVY)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((2, 2, w - 3, h - 3), 22, outline=(51, 65, 85), width=2)
        tw = d.textlength(text, font=fnt)
        x = (w - tw) / 2
        d.text((x, 24), text, font=fnt, fill=(165, 180, 252))
        if cursor:
            d.rectangle((x + tw + 6, 26, x + tw + 9, 58), fill=CYAN)
        return im

    frames = []
    for i, line in enumerate(lines):
        start = 0 if i else len(line)
        for idx in range(start, len(line) + 1, 2):
            frames.append(frame(line[:idx] or line[0], True))
        for blink in range(12):
            frames.append(frame(line, blink % 2 == 0))
    save_gif(frames, ASSETS / "typing.gif", 70)


def build_divider() -> None:
    frames = []
    for i in range(20):
        im = Image.new("RGB", (W, 36), NAVY)
        bar = gradient_bar(W - 160, 4, i / 20)
        im.paste(bar, (80, 16))
        shine = sheen(W, 36, int(-80 + (i / 20) * (W + 80)))
        im = Image.alpha_composite(im.convert("RGBA"), shine).convert("RGB")
        frames.append(im)
    save_gif(frames, ASSETS / "divider.gif", 70)


def button(label: str, color: tuple[int, int, int], path: Path) -> None:
    im = Image.new("RGB", (196, 56), NAVY)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, 194, 54), 16, fill=(15, 23, 42), outline=color, width=3)
    d.rectangle((1, 14, 7, 42), fill=color)
    d.text((104, 28), label, font=font(SANS_B, 18), fill=WHITE, anchor="mm")
    im.save(path)


def panel_from_card(size: tuple[int, int]) -> Image.Image:
    src = Image.open(ASSETS / "card-bg.png").convert("RGB")
    return cover(src, size)


def build_about() -> None:
    w, h = W, 340
    base = panel_from_card((w, h))
    d = ImageDraw.Draw(base)
    draw_tracked(d, "ABOUT", w // 2, 28, font(MONO_B, 18), CYAN, 8)
    cols = [
        ("01  DESIGN → CODE", "I design in Figma, then ship\nthe handoff myself."),
        ("02  WEB + MOBILE", "React, Angular, and Expo apps\nwith typed, reusable UI."),
        ("03  APIS & DATA", "Laravel and Node.js backends\nwith clean REST contracts."),
    ]
    gap = 36
    cw = (w - 80 - gap * 2) // 3
    for i, (title, body) in enumerate(cols):
        x = 40 + i * (cw + gap)
        y = 78
        d.rounded_rectangle((x, y, x + cw, h - 36), 22, outline=(51, 65, 85), width=2)
        d.rectangle((x, y, x + 8, h - 36), fill=[INDIGO, CYAN, VIOLET][i])
        d.text((x + 28, y + 28), title, font=font(MONO_B, 20), fill=WHITE)
        by = y + 84
        for line in body.split("\n"):
            d.text((x + 28, by), line, font=font(SANS, 22), fill=SOFT)
            by += 34
    round_clip(base, 32).save(ASSETS / "about.png", optimize=True)


def chip_row(draw, x, y, chips, fnt, max_w):
    cx, cy = x, y
    pad_x, pad_y = 16, 8
    for chip in chips:
        tw = draw.textlength(chip, font=fnt)
        ww, hh = tw + pad_x * 2, 36
        if cx + ww > x + max_w:
            cx = x
            cy += hh + 10
        draw.rounded_rectangle((cx, cy, cx + ww, cy + hh), 10, fill=(15, 23, 42), outline=(51, 65, 85))
        draw.text((cx + pad_x, cy + 7), chip, font=fnt, fill=SOFT)
        cx += ww + 10
    return cy + 46


def build_stack() -> None:
    w, h = W, 420
    base = panel_from_card((w, h))
    d = ImageDraw.Draw(base)
    draw_tracked(d, "STACK", w // 2, 22, font(MONO_B, 18), CYAN, 8)
    groups = [
        ("LANGUAGES", ["TypeScript", "JavaScript", "PHP", "Java", "C++", "Python", "HTML", "CSS"]),
        ("FRONT END", ["React", "Next.js", "Angular", "Vue", "Tailwind", "Vite", "Three.js"]),
        ("MOBILE + API", ["React Native", "Expo", "Node.js", "Laravel", "Firebase", "Supabase"]),
        ("DATA + QUALITY", ["MongoDB", "PostgreSQL", "MySQL", "Prisma", "Figma", "Cypress", "JUnit 5"]),
    ]
    fnt = font(SANS, 20)
    label = font(MONO_B, 16)
    col_w = (w - 120) // 2
    for i, (name, chips) in enumerate(groups):
        col = i % 2
        row = i // 2
        x = 50 + col * (col_w + 20)
        y = 72 + row * 160
        d.text((x, y), name, font=label, fill=MUTED)
        chip_row(d, x, y + 30, chips, fnt, col_w - 10)
    round_clip(base, 32).save(ASSETS / "stack.png", optimize=True)


def project_card(path: Path, eyebrow: str, title: str, body: str, chips: list[str], accent) -> None:
    w, h = 780, 300
    base = panel_from_card((w, h))
    orb = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(orb)
    od.ellipse((520, -40, 860, 300), fill=accent + (28,))
    od.ellipse((600, 40, 820, 260), fill=accent + (40,))
    base = Image.alpha_composite(base.convert("RGBA"), orb).convert("RGB")
    d = ImageDraw.Draw(base)
    d.rectangle((0, 0, 10, h), fill=accent)
    d.text((36, 28), eyebrow, font=font(MONO_B, 16), fill=accent)
    d.text((36, 62), title, font=font(SANS_B, 36), fill=WHITE)
    by = 120
    for line in wrap(d, body, font(SANS, 21), 470)[:3]:
        d.text((36, by), line, font=font(SANS, 21), fill=SOFT)
        by += 32
    chip_row(d, 36, h - 78, chips, font(SANS, 16), 520)
    round_clip(base, 28).save(path, optimize=True)


def build_projects() -> None:
    cards = [
        ("portfolio.png", "LIVE PRODUCT", "Portfolio", "3D personal site with particles, scroll-reveal, and glass UI.", ["React 18", "Three.js", "GSAP", "Tailwind"], INDIGO),
        ("thp.png", "PLATFORM", "THP Hiring", "Talent marketplace with bidding, auth, analytics, and export.", ["Angular 19", "Bootstrap 5", "Chart.js"], CYAN),
        ("thp-api.png", "API", "THP API", "OTP login, verification, jobs, bids, and admin moderation.", ["Laravel 12", "PHP 8.2", "Sanctum"], (251, 113, 133)),
        ("lumixy.png", "MOBILE", "Lumixy", "Service marketplace with search, onboarding, and dashboards.", ["Expo", "React Native", "TypeScript"], (52, 211, 153)),
        ("lumixy-api.png", "API", "Lumixy API", "31 endpoints, gated onboarding, gallery, and admin actions.", ["Laravel 12", "Sanctum", "MySQL"], (45, 212, 191)),
        ("dashboard.png", "WEB APP", "Account Dashboard", "Firebase Auth account app: profile, password, contacts, delete.", ["React 18", "Firebase", "MUI"], (251, 191, 36)),
        ("time4meds.png", "UI/UX", "Time4Meds", "Medication-reminder system designed to improve adherence.", ["Figma", "Design system"], VIOLET),
        ("qa.png", "QUALITY", "QA Automation", "JUnit 5 suites: parameterized tests, exceptions, lifecycle hooks.", ["Java", "JUnit 5"], (74, 222, 128)),
        ("dsa.png", "SYSTEMS", "Data Structures", "Templated Deque and LinkedList, polynomials, postfix evaluator.", ["C++", "Templates"], (96, 165, 250)),
        ("twist.png", "E-COMMERCE", "TWIST", "Arabic RTL storefront for custom embroidery and print on apparel.", ["Next.js", "TypeScript", "Supabase"], (244, 114, 182)),
        ("fatekit.png", "E-COMMERCE", "FATEKIT", "Luxury Arabic makeup shop plus admin dashboard for the Palestinian market.", ["Next.js 15", "Prisma", "PostgreSQL"], (212, 175, 150)),
        ("stockflow.png", "SAAS", "StockFlow", "Arabic-first inventory, POS, expenses, and reports for SMBs.", ["React 19", "Firebase", "Express"], (6, 182, 212)),
        ("restaurant.png", "PRODUCT", "Taste Menu", "Bilingual restaurant menu with admin, WhatsApp orders, and QR codes.", ["JavaScript", "Firebase", "Firestore"], (251, 146, 60)),
        ("kingpizza.png", "LIVE MENU", "King Pizza", "RTL digital menu for pizza, sandwiches, and sides.", ["HTML", "CSS", "JavaScript"], (196, 30, 58)),
        ("ecoswap-cart.png", "MICROFRONTEND", "EcoSwap Cart", "Cart, address, and checkout module for a second-hand marketplace.", ["Vue 3", "Vuetify", "Pinia"], (74, 222, 128)),
        ("ecoswap-shell.png", "MICROFRONTEND", "EcoSwap Shell", "Host shell that composes EcoSwap catalog, cart, and account apps.", ["JavaScript", "HTML", "CSS"], (16, 185, 129)),
        ("graduation.png", "PRODUCT", "Graduate Book", "Shareable digital graduation book that feels like a leather-bound album.", ["Next.js", "Three.js", "GSAP"], (196, 181, 253)),
        ("skyline.png", "COURSEWORK", "Skyline Auth", "JavaFX login, register, and password-reset module for a flight-booking app.", ["Java 20", "JavaFX", "Hibernate"], (56, 189, 248)),
        ("udacity.png", "LEARNING", "Udacity Projects", "Four course builds: sites, Sass portfolio, resume NLP, and a tested card game.", ["HTML", "Python", "Cypress"], (2, 167, 240)),
        ("hybrid.png", "MOBILE", "Hybrid Search", "Expo app that wraps Google Search in a full-screen native WebView.", ["Expo", "React Native", "WebView"], (99, 102, 241)),
    ]
    for name, *rest in cards:
        project_card(ASSETS / name, *rest)


def build_experience() -> None:
    w, h = W, 280
    base = panel_from_card((w, h))
    d = ImageDraw.Draw(base)
    draw_tracked(d, "EXPERIENCE  ·  EDUCATION", w // 2, 24, font(MONO_B, 18), CYAN, 6)
    blocks = [
        ((INDIGO), "SOFTWARE ENGINEERING INTERN", "ITG Software, Inc.", "Shipped client-facing features and learned how production code is reviewed, tested, and released."),
        ((CYAN), "B.SC. SOFTWARE ENGINEERING", "An-Najah National University", "Degree in progress, with DataCamp coursework in data analysis and Python."),
    ]
    gap = 28
    cw = (w - 80 - gap) // 2
    for i, (accent, title, org, body) in enumerate(blocks):
        x = 40 + i * (cw + gap)
        y = 72
        d.rounded_rectangle((x, y, x + cw, h - 28), 20, outline=(51, 65, 85), width=2)
        d.rectangle((x, y, x + 8, h - 28), fill=accent)
        d.text((x + 28, y + 22), title, font=font(MONO_B, 16), fill=accent)
        d.text((x + 28, y + 56), org, font=font(SANS_B, 26), fill=WHITE)
        by = y + 104
        for line in wrap(d, body, font(SANS, 20), cw - 56):
            d.text((x + 28, by), line, font=font(SANS, 20), fill=SOFT)
            by += 30
    round_clip(base, 32).save(ASSETS / "experience.png", optimize=True)


def build_stats() -> None:
    w, h = W, 220
    base = panel_from_card((w, h))
    d = ImageDraw.Draw(base)
    draw_tracked(d, "GITHUB", w // 2, 22, font(MONO_B, 18), CYAN, 8)
    items = [("22", "PUBLIC REPOS"), ("6", "FOLLOWERS"), ("2023", "JOINED")]
    for i, (num, label) in enumerate(items):
        x = 160 + i * 430
        d.text((x, 100), num, font=font(SANS_B, 64), fill=WHITE, anchor="mm")
        d.text((x, 160), label, font=font(MONO, 18), fill=MUTED, anchor="mm")
        if i < 2:
            d.line((x + 200, 80, x + 200, 170), fill=LINE, width=2)
    round_clip(base, 28).save(ASSETS / "stats.png", optimize=True)


def build_footer() -> None:
    src = Image.open(ASSETS / "hero-bg.png").convert("RGB")
    base = cover(src, (W, 200))
    base = ImageChops.multiply(base, vignette((W, 200), 0.5))
    d = ImageDraw.Draw(base)
    draw_tracked(d, "OPEN TO INTERNSHIPS  ·  FREELANCE  ·  OPEN SOURCE", W // 2, 58, font(MONO_B, 20), WHITE, 4)
    draw_tracked(d, "ali.yaqoub.software@gmail.com", W // 2, 112, font(SANS, 24), SOFT, 1)
    round_clip(base, 28).save(ASSETS / "footer.png", optimize=True)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    build_banner()
    build_available()
    build_typing()
    build_divider()
    button("Portfolio", (79, 70, 229), ASSETS / "btn-portfolio.png")
    button("LinkedIn", (10, 102, 194), ASSETS / "btn-linkedin.png")
    button("Email", (220, 38, 38), ASSETS / "btn-email.png")
    button("All Links", (5, 150, 105), ASSETS / "btn-links.png")
    button("Live site", (34, 211, 238), ASSETS / "btn-live.png")
    button("Case study", (167, 139, 250), ASSETS / "btn-case.png")
    build_about()
    build_stack()
    build_projects()
    build_experience()
    build_stats()
    build_footer()
    print("built", ASSETS)


if __name__ == "__main__":
    main()
