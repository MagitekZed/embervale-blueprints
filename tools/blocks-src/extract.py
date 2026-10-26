"""Extract block rows (name, icon, set, columns) from the wiki pages' wikitables."""
import json, re, sys, html
from html.parser import HTMLParser

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.section = None; self.heading = None; self.in_h = False; self.htext = ''
        self.tables = []  # stack of (is_wikitable, rows)
        self.out = []
        self.row = None; self.cell = None
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == 'article' and 'tabber__panel' in (a.get('class') or ''):
            self.section = a.get('id', '').replace('_-0', '').replace('_', ' ')
        if tag in ('h2', 'h3'):
            self.in_h = True; self.htext = ''
        if tag == 'table':
            self.tables.append('wikitable' in (a.get('class') or ''))
        if not self.tables or not self.tables[0]:
            return
        depth = len(self.tables)
        if tag == 'tr' and depth == 1:
            self.row = {'cells': [], 'imgs': [], 'section': self.section, 'heading': self.heading}
        if tag in ('td', 'th') and depth == 1 and self.row is not None:
            self.cell = ''
        if tag == 'img' and self.row is not None:
            w = int(a.get('width') or 0)
            self.row['imgs'].append((w, a.get('src'), a.get('alt')))
    def handle_endtag(self, tag):
        if tag in ('h2', 'h3') and self.in_h:
            self.in_h = False; self.heading = re.sub(r'\[.*', '', self.htext).strip()
        if tag == 'table' and self.tables:
            self.tables.pop()
        if not self.tables or not self.tables[0]:
            return
        depth = len(self.tables)
        if tag in ('td', 'th') and depth == 1 and self.row is not None and self.cell is not None:
            self.row['cells'].append(re.sub(r'\s+', ' ', self.cell).strip()); self.cell = None
        if tag == 'tr' and depth == 1 and self.row is not None:
            if self.row['cells']: self.out.append(self.row)
            self.row = None
    def handle_data(self, data):
        if self.in_h: self.htext += data
        if self.cell is not None: self.cell += data

res = {}
for f in sys.argv[2:]:
    d = json.load(open(f'{sys.argv[1]}/{f}.json', encoding='utf-8'))['parse']['text']
    p = P(); p.feed(d)
    res[f] = p.out
json.dump(res, open(f'{sys.argv[1]}/../extracted.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for f, rows in res.items():
    print('==', f, len(rows))
    for r in rows[:4] + rows[-2:]:
        big = [i for i in r['imgs'] if i[0] >= 50]
        print('  ', r['section'] or r['heading'], '|', r['cells'][:3], '|', big[:1])
