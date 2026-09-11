#!/usr/bin/env python3
"""図版HTML → PNG（余白を自動トリミング）"""
import re, subprocess, sys
from pathlib import Path
from PIL import Image

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
SRC = Path(__file__).resolve().parent
OUT = SRC.parent / "images"
OUT.mkdir(exist_ok=True)
PAD = 0  # トリミング後に残す余白(px, 2x scale)

def render(name: str):
    html = SRC / f"{name}.html"
    text = html.read_text(encoding="utf-8")
    m = re.search(r"\.sheet\s*\{[^}]*width:\s*(\d+)px", text)
    w = int(m.group(1)) if m else 1400
    png = OUT / f"{name}.png"
    subprocess.run([
        CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=2", f"--window-size={w},4200",
        "--default-background-color=FFFAF8F5",
        f"--screenshot={png}", f"file://{html}",
    ], check=True, capture_output=True)

    im = Image.open(png).convert("RGB")
    bg = im.getpixel((im.width - 4, im.height - 4))
    # 下から走査して、背景色以外が現れる行を探す
    px = im.load()
    step = max(1, im.width // 240)
    bottom = im.height
    for y in range(im.height - 1, -1, -1):
        row_bg = True
        for x in range(0, im.width, step):
            c = px[x, y]
            if abs(c[0]-bg[0]) > 6 or abs(c[1]-bg[1]) > 6 or abs(c[2]-bg[2]) > 6:
                row_bg = False
                break
        if not row_bg:
            bottom = min(im.height, y + 1 + 88)  # 44px 相当の下余白を残す
            break
    im.crop((0, 0, im.width, bottom)).save(png, optimize=True)
    size = png.stat().st_size
    print(f"  {name}.png  {im.width}x{bottom}  {size/1024:.0f}KB")

if __name__ == "__main__":
    for n in sys.argv[1:]:
        render(n.removesuffix(".html"))
