"""Fetch every skill page on enshrouded.tools and save the gear that raises each skill as gear.json.

Each skill page has a "Gear that raises it" list ("Arsonist: Elder Gloves +1, Mage Gloves drop +1, ..."). Items the
site has in two versions carry " drop" or " crafted" after the name.
Run: python -I scrape_gear.py <cache dir>    (pages are fetched with curl and cached; clear the cache to refresh)
"""
import html, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
cache = sys.argv[1]
os.makedirs(cache, exist_ok=True)


def get(url):
    path = os.path.join(cache, url.rstrip('/').rsplit('/', 1)[1] + '.html')
    if not os.path.exists(path) or not os.path.getsize(path):
        subprocess.run(['curl', '-s', '-A', 'Mozilla/5.0', url, '-o', path], check=True)
        time.sleep(0.2)
    return open(path, encoding='utf-8', errors='replace').read()


def text(t):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))


sitemap = get('https://www.enshrouded.tools/sitemap.xml')
urls = re.findall(r'<loc>(https://www\.enshrouded\.tools/skills/[^<]+)</loc>', sitemap)
out = {}
for u in urls:
    x = text(get(u))
    m = re.search(r'Skill tree / (.+?) Class ', x)
    g = re.search(r'Gear that raises it (\d+) (.*?) (?:Path from the start|Linked nodes|Enshrouded \. tools)', x)
    gear = []
    if g:
        for it, plus in re.findall(r'(.+?) \+(\d+)(?: |$)', g.group(2) + ' '):
            gear.append({'item': it.strip(), 'plus': int(plus)})
        if len(gear) != int(g.group(1)):
            print('count mismatch:', m and m.group(1), g.group(1), len(gear))
    if m and gear:
        out[m.group(1).strip()] = gear
json.dump({'source': 'https://www.enshrouded.tools/skills/*', 'fetched': time.strftime('%Y-%m-%d'), 'skills': out},
          open(os.path.join(HERE, 'gear.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f'{len(urls)} skill pages, {len(out)} with gear, {sum(len(v) for v in out.values())} entries -> gear.json')
