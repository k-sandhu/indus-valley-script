"""Generate the 1200x630 social preview card for the public website."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / 'static/social-card.png'


def load_font(names: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for root in (Path('C:/Windows/Fonts'), Path('/usr/share/fonts/truetype/dejavu'), Path('/System/Library/Fonts')):
        for name in names:
            candidate = root / name
            if candidate.exists():
                return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def build_social_card(out: Path = OUT) -> Path:
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), '#143d40')
    draw = ImageDraw.Draw(img)

    # Geometric grid on the right panel.
    for x in range(750, 1220, 44):
        draw.line([(x, 0), (x, height)], fill='#1b4d50', width=1)
    for y in range(0, height + 44, 44):
        draw.line([(750, y), (width, y)], fill='#1b4d50', width=1)

    # Stylized seal-and-grid emblem.
    ex, ey = 975, 315
    draw.rounded_rectangle([ex - 138, ey - 138, ex + 138, ey + 138], radius=18,
                           fill='#103336', outline='#d99852', width=3)
    draw.rectangle([ex - 94, ey - 74, ex + 94, ey + 54], outline='#edf1e9', width=4)
    draw.line([(ex - 31, ey - 74), (ex - 31, ey + 54)], fill='#edf1e9', width=4)
    draw.line([(ex + 31, ey - 74), (ex + 31, ey + 54)], fill='#edf1e9', width=4)
    draw.line([(ex - 94, ey - 10), (ex + 94, ey - 10)], fill='#edf1e9', width=4)
    draw.line([(ex - 106, ey + 82), (ex + 106, ey + 82)], fill='#d99852', width=6)
    for mx, my, r in [(ex - 62, ey - 42, 6), (ex + 1, ey + 22, 7), (ex + 63, ey - 42, 5)]:
        draw.ellipse([mx - r, my - r, mx + r, my + r], fill='#d99852')

    # Top ochre rule.
    draw.rectangle([72, 62, 156, 68], fill='#d99852')

    f_eyebrow = load_font(['seguisb.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf'], 19)
    f_title = load_font(['georgiab.ttf', 'georgia.ttf', 'DejaVuSerif-Bold.ttf'], 56)
    f_sub = load_font(['segoeui.ttf', 'arial.ttf', 'DejaVuSans.ttf'], 25)
    f_stat = load_font(['georgiab.ttf', 'georgia.ttf', 'DejaVuSerif-Bold.ttf'], 34)
    f_stat_l = load_font(['segoeui.ttf', 'arial.ttf', 'DejaVuSans.ttf'], 16)
    f_url = load_font(['consola.ttf', 'segoeui.ttf', 'DejaVuSansMono.ttf'], 19)

    draw.text((72, 84), 'UNDECIPHERED SCRIPT · OPEN HUMAN & AI-AGENT RESEARCH', fill='#d99852', font=f_eyebrow)
    draw.text((72, 132), 'Indus Civilisation', fill='#f6f5ee', font=f_title)
    draw.text((72, 200), '& Script Research', fill='#f6f5ee', font=f_title)

    draw.text((72, 290), 'Source-linked findings, testable conjectures, interactive', fill='#c9d6ce', font=f_sub)
    draw.text((72, 326), 'atlases, and open tasks for humans and AI agents.', fill='#c9d6ce', font=f_sub)

    draw.line([(72, 400), (718, 400)], fill='#2b5d60', width=2)

    stats = [
        ('4,695', 'Register objects'),
        ('112', 'Located places'),
        ('7', '3D city models'),
        ('22', 'Conjectures'),
    ]
    for i, (val, lbl) in enumerate(stats):
        sx = 72 + i * 164
        draw.text((sx, 424), val, fill='#f6f5ee', font=f_stat)
        draw.text((sx, 470), lbl, fill='#9fb5b0', font=f_stat_l)

    draw.text((72, 546), 'k-sandhu.github.io/indus-valley-script', fill='#d99852', font=f_url)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, 'PNG', optimize=True)
    return out


if __name__ == '__main__':
    saved = build_social_card()
    print(f'Wrote {saved} ({saved.stat().st_size} bytes)')
