"""Assemble the GitHub Pages site from the built pages.

The pages are written for claude.ai artifacts, which wrap each file in a document skeleton (doctype, charset,
viewport and a small reset). For Pages they get that skeleton here, and their links to each other (written as
the artifacts' claude.ai links) point at the pages beside them instead.

Run (after building the pages): python tools/site/build_site.py <out dir>
  index.html          the planner (tools/embervale-blueprints.html)
  build-tester.html   the Flameborn Build Tester (tools/flameborn-build-tester.html)
  build-guide.html    the Build guide (tools/build-guide.html)
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
# each tool's claude.ai artifact, and where it sits on the site (only href="…" links are changed, so the Build
# Tester's share-link fallback keeps its artifact address)
LINKS = {'https://claude.ai/artifact/QbEiF3vGnAfXo3K2GeAiLS': './', 'https://claude.ai/artifact/9bvTQYyRwNJ7LUobdViRkW': 'build-tester.html',
         'https://claude.ai/artifact/8jei2C8pV8hJiZm5aKsxxR': 'build-guide.html'}
PAGES = [('embervale-blueprints.html', 'index.html'), ('flameborn-build-tester.html', 'build-tester.html'), ('build-guide.html', 'build-guide.html')]
# what the artifact skeleton gives every page
HEAD = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
        'body{margin:0;font:14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>\n'
        '</head>\n<body>\n')


def main(out):
    os.makedirs(out, exist_ok=True)
    for src, dst in PAGES:
        page = open(os.path.join(TOOLS, src), encoding='utf-8').read()
        for url, rel in LINKS.items():
            page = page.replace(f'href="{url}"', f'href="{rel}"')
        if not page.lstrip().lower().startswith('<!doctype'):
            page = HEAD + page + '\n</body>\n</html>\n'
        open(os.path.join(out, dst), 'w', encoding='utf-8').write(page)
        print(f'{dst}: {len(page) // 1024} KB')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '_site')
