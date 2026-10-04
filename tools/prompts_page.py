"""Собирает готовые промпты из docs/prompts.md:
- prompts.html — страница с кнопками «Скопировать» (GitHub Pages: /noctis/prompts.html)
- docs/prompts_ready.md — то же самое текстом
Промпт = описание картинки + блок «Стиль». Негатив отдельно, он один на все картинки.
"""
import html
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
md = (root / 'docs' / 'prompts.md').read_text(encoding='utf-8')

def block(title):
    m = re.search(r'^## ' + re.escape(title) + r'.*?\n(.*?)(?=\n## |\Z)', md, re.S | re.M)
    return m.group(1).strip()

style = block('Стиль').split('\n')[0].strip()
negative = block('Негатив').split('\n')[0].strip()
# Негатив встраивается в каждый промпт пожеланиями: отдельного поля в Kandinsky может не быть,
# а слова вроде «лишние пальцы» в самом промпте генератор иногда как раз рисует.
NEG_INLINE = 'чистое изображение без надписей, логотипов и водяных знаков, анатомически правильные руки и лица, естественные пропорции, не мультяшный рисунок, приглушённые цвета, чёткая детализация'
# Дневные картинки: без ночи и дождя в стиле, иначе промпт спорит сам с собой
DAY = {'char_viv', 's20', 'end_run', 'end_viv', 'end_destroy'}
style_day = style.replace('ночь, непрерывный дождь, отражения на мокром асфальте, ', '').replace('тёплый янтарный свет натриевых фонарей как главный акцент', 'тёплый янтарный солнечный свет как главный акцент')

items, section = [], ''
for line_block in re.split(r'\n(?=## |### )', md):
    head = line_block.split('\n', 1)[0]
    if head.startswith('## '):
        section = head[3:].strip()
        continue
    if not head.startswith('### '):
        continue
    m = re.match(r'### ([a-z0-9_]+) — (.+)', head)
    body = line_block.split('\n', 1)[1].strip() if '\n' in line_block else ''
    if not m or not body:
        continue
    pid, name = m.groups()
    fmt = '3:2' if pid.startswith(('char_', 'ev_', 'eve_')) else 'самый широкий (16:9 или 3:2)'
    st = style_day if pid in DAY else style
    items.append({'id': pid, 'name': name, 'section': section, 'fmt': fmt,
                  'prompt': body.rstrip('.') + ', ' + st + ', ' + NEG_INLINE})

too_long = [i['id'] for i in items if len(i['prompt']) > 1000]
assert not too_long, f'длиннее 1000 символов: {too_long}'

# Markdown
out = ['# Готовые промпты для Kandinsky', '',
       'Копируй промпт целиком и вставляй как есть: описание, стиль и запреты уже внутри.', '']
last = None
for i in items:
    if i['section'] != last:
        out += [f"## {i['section']}", '']
        last = i['section']
    out += [f"### {i['id']} — {i['name']}", f"Формат: {i['fmt']}. Файл: `{i['id']}.png`", '```', i['prompt'], '```', '']
(root / 'docs' / 'prompts_ready.md').write_text('\n'.join(out), encoding='utf-8')

# HTML page
cards, last = [], None
for i in items:
    if i['section'] != last:
        cards.append(f"<h2>{html.escape(i['section'])}</h2>")
        last = i['section']
    cards.append(f"""<section class="card" data-id="{i['id']}">
  <div class="top"><b>{i['id']}</b><span>{html.escape(i['name'])}</span><label><input type="checkbox"> готово</label></div>
  <div class="meta">Формат: {html.escape(i['fmt'])} · файл: {i['id']}.png</div>
  <p class="prompt">{html.escape(i['prompt'])}</p>
  <button type="button">Скопировать промпт</button>
</section>""")

page = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ноктис: промпты</title>
<style>
:root{{color-scheme:dark;--bg:#0E1316;--panel:#172026;--line:#28343C;--text:#E9E3D7;--muted:#8E9BA3;--amber:#F0A847;--good:#86C9A0}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:820px;margin:0 auto;padding:24px 16px 80px}}
h1{{font-size:22px;margin:0 0 8px}} h2{{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:32px 0 10px}}
.note{{color:var(--muted);margin:0 0 16px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:14px;margin:0 0 12px}}
.card.done{{opacity:.5}}
.top{{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}} .top b{{font-family:ui-monospace,monospace;color:var(--amber)}}
.top label{{margin-left:auto;color:var(--muted);font-size:13px;cursor:pointer}}
.meta{{color:var(--muted);font-size:12.5px;margin:4px 0 8px;font-family:ui-monospace,monospace}}
.prompt{{margin:0 0 10px;white-space:pre-wrap}}
button{{background:none;border:1px solid var(--amber);color:var(--amber);border-radius:4px;padding:8px 14px;font:inherit;cursor:pointer}}
button.ok{{border-color:var(--good);color:var(--good)}}
.neg{{border-color:var(--amber)}}
</style></head><body><main>
<h1>Ноктис: промпты для Kandinsky</h1>
<p class="note">Начни с этих: title, s1, s2, s3, char_nika, char_parents, char_dana. Нажми «Скопировать», вставь в Kandinsky как есть (стиль и запреты уже внутри), выбери формат. Сохрани картинку под именем из строки «файл» и пришли в чат. Галочка «готово» запоминается в этом браузере.</p>
{chr(10).join(cards)}
</main>
<script>
const KEY='noctis-prompts-done';
let done={{}}; try{{ done=JSON.parse(localStorage.getItem(KEY)||'{{}}'); }}catch(e){{}}
document.querySelectorAll('.card').forEach(card=>{{
  const id=card.dataset.id, btn=card.querySelector('button'), box=card.querySelector('input');
  if(box){{ box.checked=!!done[id]; card.classList.toggle('done', box.checked);
    box.addEventListener('change',()=>{{ done[id]=box.checked; card.classList.toggle('done', box.checked); try{{ localStorage.setItem(KEY, JSON.stringify(done)); }}catch(e){{}} }}); }}
  btn.addEventListener('click',async()=>{{
    const text=card.querySelector('.prompt').textContent; const label=btn.textContent;
    try{{ await navigator.clipboard.writeText(text); }}catch(e){{
      const t=document.createElement('textarea'); t.value=text; document.body.appendChild(t); t.select(); document.execCommand('copy'); t.remove(); }}
    btn.textContent='Скопировано'; btn.classList.add('ok'); setTimeout(()=>{{ btn.textContent=label; btn.classList.remove('ok'); }},1500);
  }});
}});
</script>
</body></html>
"""
(root / 'prompts.html').write_text(page, encoding='utf-8')
print(f'Промптов: {len(items)}, самый длинный: {max(len(i["prompt"]) for i in items)} символов')
