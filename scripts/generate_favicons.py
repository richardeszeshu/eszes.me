#!/usr/bin/env python3
"""
Generate multi-resolution favicons for eszes.me
Black rounded square with white "re" lowercase monogram
"""
import os
import sys

# Ensure python_modules is on path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(root_dir, "python_modules"))

from PIL import Image, ImageDraw, ImageFont

size = 512
img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

radius = 115
draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill="#000000")

font_path = "/System/Library/Fonts/Menlo.ttc"
font = ImageFont.truetype(font_path, 290, index=1)

bbox = draw.textbbox((0, 0), "re", font=font)
text_w = bbox[2] - bbox[0]
text_h = bbox[3] - bbox[1]

x = (size - text_w) / 2 - bbox[0]
y = (size - text_h) / 2 - bbox[1]

draw.text((x, y), "re", fill="#ffffff", font=font)

images_dir = os.path.join(root_dir, "assets", "images")
os.makedirs(images_dir, exist_ok=True)

# 1. 512x512 master PNG
img.save(os.path.join(images_dir, "android-chrome-512x512.png"), "PNG")

# 2. 192x192 Android Chrome
img_192 = img.resize((192, 192), Image.LANCZOS)
img_192.save(os.path.join(images_dir, "android-chrome-192x192.png"), "PNG")

# 3. 180x180 Apple Touch Icon
img_180 = img.resize((180, 180), Image.LANCZOS)
img_180.save(os.path.join(images_dir, "apple-touch-icon.png"), "PNG")

# 4. 32x32 Favicon PNG
img_32 = img.resize((32, 32), Image.LANCZOS)
img_32.save(os.path.join(images_dir, "favicon-32x32.png"), "PNG")

# 5. 16x16 Favicon PNG
img_16 = img.resize((16, 16), Image.LANCZOS)
img_16.save(os.path.join(images_dir, "favicon-16x16.png"), "PNG")

# 6. Multi-resolution favicon.ico in root
img.save(os.path.join(root_dir, "favicon.ico"), format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])

# 7. SVG Favicon
svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="115" fill="#000000"/>
  <text x="256" y="276" fill="#ffffff" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace" font-size="290" font-weight="700" text-anchor="middle" dominant-baseline="central">re</text>
</svg>
"""
with open(os.path.join(root_dir, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(svg)

print("Favicons successfully generated in root and assets/images/")
