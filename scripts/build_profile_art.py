#!/usr/bin/env python3
"""Build restrained, professional PNG artwork for the GitHub profile README."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

W = 1400
BG = (18, 20, 24)
PANEL = (24, 27, 33)
INK = (232, 234, 237)
MUTED = (138, 146, 158)
SOFT = (176, 183, 194)
LINE = (42, 47, 56)
ACCENT = (91, 141, 239)
ACCENT_DIM = (56, 97, 176)

SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf"


def fnt(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def round_clip(im: Image.Image, radius: int) -> Image.Image:
    im = im.convert("RGBA")
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), radius, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def solid(size: tuple[int, int], color=BG) -> Image.Image:
    return Image.new("RGB", size, color)


def hairline(draw: ImageDraw.ImageDraw, y: int, x0: int = 48, x1: int | None = None) -> None:
    draw.line((x0, y, x1 or (W - 48), y), fill=LINE, width=1)


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def build_banner() -> None:
    h = 320
    im = solid((W, h))
    d = ImageDraw.Draw(im)

    # Quiet left accent rail instead of neon orbs
    d.rectangle((0, 0, 8, h), fill=ACCENT)
    d.rectangle((8, 0, 10, h), fill=ACCENT_DIM)

    # Soft top rule
    d.line((48, 36, W - 48, 36), fill=LINE, width=1)

    d.text((48, 64), "FULL-STACK DEVELOPER", font=fnt(MONO, 18), fill=ACCENT)
    d.text((48, 108), "Ali Yaqoub", font=fnt(SERIF_B, 72), fill=INK)
    d.text(
        (48, 198),
        "I design and ship web products end to end — interfaces,",
        font=fnt(SANS, 26),
        fill=SOFT,
    )
    d.text(
        (48, 234),
        "APIs, and the systems that keep them reliable.",
        font=fnt(SANS, 26),
        fill=SOFT,
    )
    d.text(
        (48, 278),
        "An-Najah National University  ·  Palestine",
        font=fnt(MONO, 16),
        fill=MUTED,
    )

    round_clip(im, 20).save(ASSETS / "banner.png", optimize=True)


def build_section(title: str, path: Path, height: int = 72) -> None:
    im = solid((W, height), BG)
    d = ImageDraw.Draw(im)
    d.text((48, 22), title, font=fnt(MONO, 18), fill=ACCENT)
    hairline(d, height - 1)
    round_clip(im, 12).save(path, optimize=True)


def project_card(path: Path, kind: str, title: str, blurb: str, stack: list[str]) -> None:
    w, h = 680, 250
    im = solid((w, h), PANEL)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 5, h), fill=ACCENT)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 16, outline=LINE, width=1)

    d.text((28, 24), kind.upper(), font=fnt(MONO, 14), fill=ACCENT)
    d.text((28, 54), title, font=fnt(SANS_B, 30), fill=INK)

    y = 104
    for line in wrap(d, blurb, fnt(SANS, 18), w - 56)[:3]:
        d.text((28, y), line, font=fnt(SANS, 18), fill=SOFT)
        y += 28

    # Stack as quiet text, not neon pills
    chip_y = h - 42
    x = 28
    chip_font = fnt(MONO, 13)
    for i, chip in enumerate(stack):
        label = chip if i == 0 else f" · {chip}"
        d.text((x, chip_y), label, font=chip_font, fill=MUTED)
        x += int(d.textlength(label, font=chip_font))

    round_clip(im, 16).save(path, optimize=True)


def build_projects() -> None:
    cards = [
        ("portfolio.png", "Live site", "Portfolio", "3D personal site with scroll motion and a glass UI system.", ["React", "Three.js", "GSAP"]),
        ("twist.png", "E-commerce", "TWIST", "Arabic RTL storefront for custom embroidery and print.", ["Next.js", "TypeScript", "Supabase"]),
        ("fatekit.png", "E-commerce", "FATEKIT", "Luxury Arabic makeup shop with an admin dashboard.", ["Next.js", "Prisma", "PostgreSQL"]),
        ("stockflow.png", "SaaS", "StockFlow", "Arabic-first inventory, POS, expenses, and reporting.", ["React", "Firebase", "Express"]),
        ("restaurant.png", "Product", "Taste Menu", "Bilingual restaurant menu with admin and WhatsApp orders.", ["JavaScript", "Firebase"]),
        ("kingpizza.png", "Live menu", "King Pizza", "RTL digital menu for pizza, sandwiches, and sides.", ["HTML", "CSS", "JavaScript"]),
        ("thp.png", "Platform", "THP Hiring", "Talent marketplace with bidding, auth, and analytics.", ["Angular", "Bootstrap", "Chart.js"]),
        ("thp-api.png", "API", "THP API", "OTP auth, jobs, bids, and admin moderation endpoints.", ["Laravel", "PHP", "Sanctum"]),
        ("lumixy.png", "Mobile", "Lumixy", "Service marketplace with search, onboarding, and dashboards.", ["Expo", "React Native"]),
        ("lumixy-api.png", "API", "Lumixy API", "Onboarding gates, gallery flows, and admin actions.", ["Laravel", "MySQL", "Sanctum"]),
        ("ecoswap-cart.png", "Microfrontend", "EcoSwap Cart", "Cart, address, and checkout module for EcoSwap.", ["Vue 3", "Vuetify", "Pinia"]),
        ("ecoswap-shell.png", "Microfrontend", "EcoSwap Shell", "Host shell composing catalog, cart, and account apps.", ["JavaScript", "HTML", "CSS"]),
        ("graduation.png", "Product", "Graduate Book", "Shareable digital graduation book with book-like motion.", ["Next.js", "Three.js", "GSAP"]),
        ("dashboard.png", "Web app", "Account Dashboard", "Firebase Auth account flows: profile, password, contacts.", ["React", "Firebase", "MUI"]),
        ("time4meds.png", "UI/UX", "Time4Meds", "Medication-reminder system designed for adherence.", ["Figma", "Design system"]),
        ("skyline.png", "Coursework", "Skyline Auth", "Login, register, and password reset for a flight app.", ["Java", "JavaFX", "Hibernate"]),
        ("qa.png", "Quality", "QA Automation", "Parameterized suites, exceptions, and lifecycle hooks.", ["Java", "JUnit 5"]),
        ("dsa.png", "Systems", "Data Structures", "Templated containers, polynomials, and postfix evaluation.", ["C++", "Templates"]),
        ("udacity.png", "Learning", "Udacity Projects", "Sites, Sass portfolio, resume NLP, and a tested card game.", ["HTML", "Python", "Cypress"]),
        ("hybrid.png", "Mobile", "Hybrid Search", "Expo shell wrapping Google Search in a native WebView.", ["Expo", "React Native"]),
    ]
    for name, *rest in cards:
        project_card(ASSETS / name, *rest)


def build_footer() -> None:
    h = 120
    im = solid((W, h))
    d = ImageDraw.Draw(im)
    hairline(d, 1)
    d.text((48, 36), "Open to internships, freelance, and collaboration", font=fnt(SANS, 24), fill=INK)
    d.text((48, 76), "ali.yaqoub.software@gmail.com", font=fnt(MONO, 18), fill=ACCENT)
    round_clip(im, 16).save(ASSETS / "footer.png", optimize=True)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    # Remove gimmicky / unused assets from the previous design language
    for stale in (
        "available.gif",
        "typing.gif",
        "divider.gif",
        "stats.png",
        "about.png",
        "stack.png",
        "experience.png",
        "btn-portfolio.png",
        "btn-linkedin.png",
        "btn-email.png",
        "btn-links.png",
        "btn-live.png",
        "btn-case.png",
        "card-bg.png",
        "hero-bg.png",
        "more.png",
    ):
        path = ASSETS / stale
        if path.exists():
            path.unlink()

    build_banner()
    build_projects()
    build_footer()
    print("built clean assets in", ASSETS)


if __name__ == "__main__":
    main()
