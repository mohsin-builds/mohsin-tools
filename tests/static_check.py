"""Validate deployable assets, no external file processors, and local links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
root=Path(__file__).resolve().parents[1]/'dist'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  for k in ('href','src'):
   if k in d:self.urls.append((tag,d[k]))
assert (root/'index.html').exists()
pages=list(root.rglob('*.html'))
assert len(pages)==5,(len(pages),pages)
for page in pages:
 p=Links();p.feed(page.read_text(encoding='utf-8'))
 for tag,raw in p.urls:
  parsed=urlsplit(raw)
  if parsed.scheme or parsed.netloc or raw.startswith('#') or raw.startswith('mailto:'):continue
  path=unquote(parsed.path)
  if not path:continue
  target=(root/path.removeprefix('/')) if path.startswith('/') else (page.parent/path)
  if path.endswith('/'):target=target/'index.html'
  assert target.exists(),f'{page.relative_to(root)}: broken local URL {raw}'
assert not list(root.rglob('test*')),'Test files should not be deployed'
assert not (root/'README.md').exists(),'README should not be deployed'
print(f'PASS: {len(pages)} HTML pages and local asset links, clean production output')