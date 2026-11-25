"""Turn on-watch screenshots into picker previews: remove Samsung status icon (patched from a rotated copy), circle-mask."""
import sys
from PIL import Image, ImageDraw
for n in sys.argv[1:]:
    im = Image.open(f"shots/{n}.png").convert("RGBA")
    rot = im.rotate(-24, center=(225, 225), resample=Image.BICUBIC)
    m = Image.new("L", im.size, 0); dm = ImageDraw.Draw(m); dm.ellipse([198, 8, 252, 64], fill=255); dm.ellipse([-4, 211, 26, 239], fill=255)
    im.paste(rot, (0, 0), m)
    c = Image.new("L", im.size, 0); ImageDraw.Draw(c).ellipse([0, 0, 449, 449], fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.paste(im, (0, 0), c)
    out.save(f"previews/{n}.png")
