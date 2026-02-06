# PS2 XMB Cover Generator

This project is a small Python utility that generates PS3-compatible `ICON0.PNG` files
using official PlayStation 2 box art.

It is designed for use on **CFW PlayStation 3 systems** where PS2 games are launched via
multiMAN, webMAN MOD, or PS2 Classics workflows.

The goal is to preserve full portrait box art (no cropping) while fitting cleanly into
the PS3 XMB icon system.

---

## What This Tool Does

- Downloads PS2 cover art by serial number
- Preserves the full portrait box art
- Fits the cover into a PS3-friendly portrait canvas
- Adds a very subtle drop shadow for depth
- Outputs a ready-to-use `ICON0.PNG` per game

No image editors are required.

---

## Output Format

For each serial, the script creates:

```text
output/
└── SLUS-20312/
    └── ICON0.PNG
```

These `ICON0.PNG` files can then be copied into the appropriate PS3 directory depending
on how the game is launched.

---

## Requirements

- Python 3.10 or newer
- Python packages:
  - requests
  - Pillow

Install dependencies:

```bash
pip install requests pillow
```

---

## Usage

1. Create a file named `serials.txt`

2. Add one PS2 serial per line:

```text
SLUS-20312
SLES-50355
SLPM-65051
```

3. Run the script:

```bash
python make_icons.py
```

4. Check the `output/` folder for generated icons

If a serial is missing from the cover repository, it will be logged in `missing.txt`.

---

## Image Behavior

- Box art is never cropped
- Aspect ratio is preserved
- Padding is added only when necessary
- A very light drop shadow is applied to give the icon subtle depth in XMB (this is a test I very well may not keep this)

The cover image itself is not altered.

---

## Cover Art Source

All cover images are pulled from:

https://github.com/xlenore/ps2-covers

This project does not include or redistribute cover art directly.

---

## Notes

- This tool only generates icons. It does not modify PS3 system files.
- Placement of `ICON0.PNG` depends on your PS3 setup (multiMAN, webMAN, or PKG-based).
- The script is intentionally minimal and easy to modify.

---

## License

This project is provided as-is for educational and personal use.
