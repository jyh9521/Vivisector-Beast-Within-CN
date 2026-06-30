from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont


ATLAS_SIZE = 4096
CELL = 16

FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path(r"C:\Windows\Fonts\simsun.ttc"),
]


def write_tga_bottom_left(path: Path, image: Image.Image) -> None:
    image = image.convert("RGBA")
    w, h = image.size
    header = bytearray(18)
    header[2] = 2
    header[12:14] = w.to_bytes(2, "little")
    header[14:16] = h.to_bytes(2, "little")
    header[16] = 32
    header[17] = 8
    raw = bytearray()
    for y in range(h - 1, -1, -1):
        row = image.crop((0, y, w, y + 1)).tobytes("raw", "BGRA")
        raw.extend(row)
    path.write_bytes(bytes(header) + bytes(raw))


def load_original_font(font_tga: Path, font_backup: Path) -> Image.Image:
    source = font_backup if font_backup.exists() else font_tga
    return Image.open(source).convert("RGBA")


def select_font() -> Path:
    for candidate in FONT_CANDIDATES:
        if candidate.exists():
            return candidate
    raise SystemExit("No CJK font found in C:\\Windows\\Fonts")


def paste_original_ascii(atlas: Image.Image, original: Image.Image) -> None:
    for code in range(256):
        sx = (code & 0x0F) * CELL
        sy = (code >> 4) * CELL
        glyph = original.crop((sx, sy, sx + CELL, sy + CELL))
        dx = code * CELL
        atlas.alpha_composite(glyph, (dx, 0))


def render_gbk(atlas: Image.Image, font_path: Path) -> int:
    font = ImageFont.truetype(str(font_path), 16)
    draw_probe = ImageDraw.Draw(Image.new("L", (CELL, CELL)))
    rendered = 0

    for lead in range(0x81, 0xFF):
        for trail in range(0x40, 0xFF):
            if trail == 0x7F:
                continue
            try:
                char = bytes((lead, trail)).decode("gbk")
            except UnicodeDecodeError:
                continue
            if not char.strip():
                continue

            bbox = draw_probe.textbbox((0, 0), char, font=font)
            if bbox is None:
                continue
            gw = bbox[2] - bbox[0]
            gh = bbox[3] - bbox[1]
            if gw <= 0 or gh <= 0:
                continue

            mask = Image.new("L", (CELL, CELL), 0)
            draw = ImageDraw.Draw(mask)
            x = (CELL - gw) // 2 - bbox[0]
            y = (CELL - gh) // 2 - bbox[1]
            draw.text((x, y), char, font=font, fill=255)

            glyph = Image.new("RGBA", (CELL, CELL), (255, 255, 255, 0))
            glyph.putalpha(mask)
            atlas.alpha_composite(glyph, (trail * CELL, lead * CELL))
            rendered += 1
    return rendered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a 4096x4096 GBK bitmap font atlas for Vivisector.")
    parser.add_argument(
        "--game-dir",
        type=Path,
        default=Path.cwd(),
        help="Vivisector game directory. Defaults to the current working directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.game_dir.resolve()
    font_tga = root / "DATA" / "Textures" / "Interface" / "Text" / "EN" / "NewFont.tga"
    font_backup = font_tga.with_suffix(".tga.orig")
    if not font_tga.exists():
        raise SystemExit(f"NewFont.tga not found: {font_tga}")

    if not font_backup.exists():
        font_backup.write_bytes(font_tga.read_bytes())
        print(f"backup: {font_backup.name}")
    else:
        print(f"backup: {font_backup.name} already exists")

    original = load_original_font(font_tga, font_backup)
    atlas = Image.new("RGBA", (ATLAS_SIZE, ATLAS_SIZE), (255, 255, 255, 0))
    paste_original_ascii(atlas, original)

    font_path = select_font()
    count = render_gbk(atlas, font_path)
    write_tga_bottom_left(font_tga, atlas)
    print(f"font: {font_path}")
    print(f"rendered GBK glyphs: {count}")
    print(f"written: {font_tga}")


if __name__ == "__main__":
    main()
