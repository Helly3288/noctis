"""Собирает index.html для GitHub Pages из src/game.html (тело страницы для claude.ai)."""
from pathlib import Path

root = Path(__file__).resolve().parent.parent
lines = (root / 'src' / 'game.html').read_text(encoding='utf-8').split('\n')
head = []
while lines and (lines[0].startswith('<title>') or lines[0].startswith('<link ')):
    head.append(lines.pop(0))
html = ('<!doctype html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + '\n'.join(head) + '\n</head>\n<body>\n' + '\n'.join(lines) + '\n</body>\n</html>\n')
(root / 'index.html').write_text(html, encoding='utf-8')
print('index.html собран')
