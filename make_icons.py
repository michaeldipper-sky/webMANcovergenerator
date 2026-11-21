import io
import os
import re
from pathlib import Path

import requests
from PIL import Image, ImageFilter

# Source: PS2 covers indexed by serial (e.g., SLUS-20312)
BASE_URL = "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{serial}.jpg"

GAME_ID_REGEX = r'[a-zA-Z]{3}[a-zA-Z]?[-]\d{3}\d?\d?'

# Portrait canvas for box art style icons
TARGET_W = 268
TARGET_H = 268

TIMEOUT_SECONDS = 20


def load_serials_from_txt(path: Path) -> list[str]:
    """Read serials (one per line) from serials.txt. Supports comments with #."""
    serials: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        serials.append(s)
    return serials


def load_serials_from_isos(path: Path) -> list[str]:
    """Parse serials from ISO files in path."""
    game_id_pattern = re.compile(GAME_ID_REGEX)

    serials: list[str] = []
    for file_path in os.listdir(path):
        file_name, file_ext = os.path.splitext(file_path)
        if file_ext.lower() == ".iso":
            match = re.search(game_id_pattern, file_name)
            if match is not None:
                serials.append(match.group())
    return serials


def download_cover(serial: str) -> bytes | None:
    """Download cover JPEG bytes for a given PS2 serial."""
    url = BASE_URL.format(serial=serial)
    r = requests.get(url, timeout=TIMEOUT_SECONDS)
    if r.status_code == 200 and r.content:
        return r.content
    return None


def fit_full_art(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """
    Fit entire cover into a portrait canvas with no crop.
    Any leftover space becomes black padding.
    """
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    art = img.copy().convert("RGBA")
    art.thumbnail((target_w, target_h), Image.LANCZOS)

    x = (target_w - art.size[0]) // 2
    y = (target_h - art.size[1]) // 2
    canvas.paste(art, (x, y), art)
    return canvas


def add_drop_shadow(
    art: Image.Image,
    offset: tuple[int, int] = (2, 2),
    blur_radius: int = 3,
    shadow_color: tuple[int, int, int, int] = (0, 0, 0, 100),
) -> Image.Image:
    """
    Adds a subtle soft drop shadow to the provided RGBA image.
    Tuned for small XMB-scale icons.
    """
    w, h = art.size
    ox, oy = offset

    # Create a shadow mask by using the alpha of the art
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", (w, h), shadow_color)

    # Paste shadow layer where art is opaque (using art as alpha mask)
    shadow.paste(shadow_layer, (0, 0), art)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

    # Composite: shadow behind, then art on top
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    result.paste(shadow, (ox, oy), shadow)
    result.paste(art, (0, 0), art)

    return result


def make_icon(serial: str, out_dir: Path) -> None:
    """Create output/<SERIAL>/ICON0.PNG with full-art + subtle shadow."""
    data = download_cover(serial)
    if data is None:
        raise FileNotFoundError(serial)

    icon_path = out_dir / "{0}.PNG".format(serial)

    with Image.open(io.BytesIO(data)) as img:
        img = img.convert("RGBA")

        base = fit_full_art(img, TARGET_W, TARGET_H)
        final_img = add_drop_shadow(
            base,
            offset=(2, 2),
            blur_radius=3,
            shadow_color=(0, 0, 0, 100),
        )

        final_img.save(icon_path, format="PNG", optimize=True)


def main() -> None:
    root = Path(__file__).resolve().parent

    mode = input("1. Read serials from serials.txt\n2. Parse serials from ISOs\nSelect mode: ").strip()

    if mode not in ["1", "2"]:
        print("Invalid mode. Exiting...")
        return

    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)

    if mode == "1":
        serials_file = root / "serials.txt"
        serials = load_serials_from_txt(serials_file)
    else:
        serials = load_serials_from_isos(root)
    
    print(f"Found {len(serials)} serials")

    missing: list[str] = []

    for s in serials:
        try:
            make_icon(s, output_dir)
            print(f"OK   {s}")
        except FileNotFoundError:
            print(f"MISS {s}")
            missing.append(s)
        except Exception as e:
            print(f"ERR  {s}: {e}")
            missing.append(s)

    if missing:
        (root / "missing.txt").write_text("\n".join(missing) + "\n", encoding="utf-8")
        print(f"\nMissing or failed: {len(missing)}. See missing.txt")
    else:
        print("\nAll covers downloaded and converted successfully.")


if __name__ == "__main__":
    main()
