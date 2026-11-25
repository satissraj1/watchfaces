import sys
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
out, names = sys.argv[1], sys.argv[2:]
cols = 4 if len(names) > 3 else len(names)
rows = (len(names) + cols - 1) // cols
im = Image.new("RGB", (450 * cols, 450 * rows), "white")
for i, n in enumerate(names):
    im.paste(Image.open(f"shots/{n}.png").convert("RGB"), ((i % cols) * 450, (i // cols) * 450))
im.save(out)
