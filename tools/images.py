"""Подключает картинки к игре.

Использование:
    python3 tools/images.py <папка с картинками>   # сжать новые картинки и положить в img/
    python3 tools/images.py                        # только обновить список в src/game.html

Имя файла = id картинки из docs/prompts.md (например s1.png, char_teo.jpg, title.webp).
Заставки сцен ужимаются до 1600 px по ширине, арты внутри сцен до 1200 px, формат webp.
"""
import re
import sys
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parent.parent
img_dir = root / 'img'
img_dir.mkdir(exist_ok=True)
src = root / 'src' / 'game.html'

if len(sys.argv) > 1:
    for f in sorted(Path(sys.argv[1]).iterdir()):
        if f.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp'}:
            continue
        key = f.stem.strip().lower()
        im = Image.open(f).convert('RGB')
        width = 1200 if key.startswith(('char_', 'ev_', 'eve_')) else 1600
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        out = img_dir / f'{key}.webp'
        im.save(out, 'WEBP', quality=80, method=6)
        print(f'{f.name} -> img/{out.name} ({out.stat().st_size // 1024} КБ)')

ids = sorted(p.stem for p in img_dir.glob('*.webp'))
html = src.read_text(encoding='utf-8')
line = 'const IMAGES = new Set([' + ', '.join(f"'{i}'" for i in ids) + ']);'
html, n = re.subn(r"const IMAGES = new Set\(\[.*?\]\);", line, html, count=1)
assert n == 1, 'не нашёл строку IMAGES в src/game.html'
src.write_text(html, encoding='utf-8')
print(f'В игре подключено картинок: {len(ids)}')
