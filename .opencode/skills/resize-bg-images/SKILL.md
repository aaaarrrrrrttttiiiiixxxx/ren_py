---
name: resize-bg-images
description: Resize Ren'Py background images to 1920px width with Lanczos resampling and original backup
---

# Skill: Resize background images for Ren'Py

Check all background image dimensions:

```bash
python3 -c "
from PIL import Image
import os

d = 'game/images'
for f in sorted(os.listdir(d)):
    path = os.path.join(d, f)
    if os.path.isfile(path) and not f.startswith('.') and '_original' not in f:
        try:
            img = Image.open(path)
            print(f'{f}: {img.size[0]}x{img.size[1]}')
        except Exception as e:
            print(f'{f}: error ({e})')
"
```

Resize small images (< 1920px wide) to 1920px, Lanczos, keep aspect ratio, backup original:

```bash
python3 -c "
from PIL import Image
import os

d = 'game/images'
target_w = 1920

for f in ['file1.jpg', 'file2.jpg']:
    path = os.path.join(d, f)
    img = Image.open(path)
    w, h = img.size
    if w < target_w:
        ratio = target_w / w
        new_size = (target_w, int(h * ratio))
        base, ext = os.path.splitext(f)
        bak = os.path.join(d, f'{base}_original{ext}')
        os.rename(path, bak)
        img.resize(new_size, Image.LANCZOS).save(path, quality=95)
        print(f'{f}: {w}x{h} → {new_size[0]}x{new_size[1]}')
"
```

## Rules
- Target width: 1920px (maintain aspect ratio)
- Resampling: `Image.LANCZOS`
- Always backup originals with `_original` suffix
- Quality: 95 for JPEG
- Do NOT hardcode `_2`/`_3` variants in images.rpy — point to base filenames
