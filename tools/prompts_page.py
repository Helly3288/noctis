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
NEG_INLINE = 'кадр без полей, без текста и логотипов, правильная анатомия, не 3D, не мультяшно, не комикс, без чёрных контуров'

# Где и когда происходит сцена. Хвост стиля подбирается под это, иначе генератор
# выносит людей на улицу под дождь, даже если сцена в комнате днём.
SETTING = {
    'out_night':   ('ночной мегаполис, непрерывный дождь, отражения на мокром асфальте, неоновые вывески, голографическая реклама, дроны и провода над улицей', 'тёплый янтарный свет натриевых фонарей'),
    'out_morning': ('раннее дождливое утро, серый свет, мокрый асфальт, погасший неон, голографическая реклама, провода и дроны над улицей', 'тёплый янтарный свет из окон'),
    'out_snow':    ('ночной мегаполис, мокрый снег, неоновые вывески, голографическая реклама, дроны над улицей', 'тёплый янтарный свет фонарей и гирлянд'),
    'out_day':     ('солнечный день, без дождя, футуристичные небоскрёбы, голографические панели, летающие дроны', 'тёплый янтарный солнечный свет'),
    'in_night':    ('интерьер, вечер, за окном неон и огни города, в комнате экраны, провода и самодельная техника', 'тёплый янтарный свет ламп'),
    'in_day':      ('интерьер, день, за окном пасмурно, в комнате экраны, провода и техника будущего', 'тёплый янтарный свет ламп'),
}
KIND = {
    # персонажи и события
    'char_nika': 'in_day', 'char_parents': 'in_day', 'char_dana': 'in_day', 'char_barro': 'in_night',
    'char_kit': 'out_night', 'char_teo': 'in_night', 'char_grach': 'in_night', 'char_miguel': 'in_night',
    'char_viv': 'out_day', 'char_sixth': 'in_night', 'char_sorel': 'in_night',
    'ev_reveal': 'in_day', 'ev_lamp': 'in_night', 'ev_stairs': 'in_night', 'ev_dana_rain': 'out_night',
    'ev_nika_found': 'out_night',
    'eve_dana': 'in_night', 'eve_nika': 'in_night', 'eve_teo': 'in_night', 'eve_family': 'in_night', 'eve_kit': 'out_night',
    # сцены
    's1': 'out_morning', 's3': 'in_day', 's4': 'in_night', 's7': 'out_morning', 's8': 'in_day', 's8h': 'in_night',
    's9a': 'in_night', 's9b': 'in_night', 's9d': 'in_night', 's11': 'in_night', 's12': 'in_night', 's14': 'in_day',
    's15a': 'in_day', 's15': 'out_morning', 's16': 'in_night', 'mon12': 'out_snow', 's17': 'in_day', 's18': 'in_night',
    's19': 'in_night', 's19d': 'in_day', 's20': 'out_day', 's21': 'in_night', 's22': 'in_night', 's25': 'in_night',
    'mon3': 'in_night', 's26': 'in_day', 's27': 'in_night', 'mon4': 'out_morning', 's28': 'in_night', 's30': 'in_night',
    'rd_train': 'in_night', 'rd_bus': 'in_night', 'rd_flood': 'in_night',
    'end_run': 'out_day', 'end_destroy': 'out_morning', 'end_viv': 'out_day', 'end_cer': 'in_night',
}
def style_for(pid):
    place, light = SETTING[KIND.get(pid, 'out_night')]
    return ('реалистичная цифровая живопись маслом, кинематографичный кадр, мир киберпанка, ' + place +
            ', бирюзово-асфальтовая палитра, ' + light + ' как акцент, пурпурный неон, атмосферная дымка')

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
    items.append({'id': pid, 'name': name, 'section': section, 'fmt': fmt,
                  'prompt': ('вид внутри помещения, ' if KIND.get(pid,'').startswith('in_') and not pid.startswith(('char_','ev_','eve_')) and not body.startswith(('внутри','вид внутри')) else '') + body.rstrip('.') + ', ' + style_for(pid) + ', ' + NEG_INLINE})

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
