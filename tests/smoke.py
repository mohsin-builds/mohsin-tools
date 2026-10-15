"""Local browser smoke tests; starts an isolated HTTP server automatically."""
import contextlib, http.server, io, os, socketserver, threading
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
 def log_message(self,*args):pass
class Server(socketserver.ThreadingMixIn,socketserver.TCPServer): allow_reuse_address=True
server=Server(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base=f'http://127.0.0.1:{server.server_address[1]}'
img=Image.new('RGB',(650,530))
for y in range(530):
 for x in range(650):img.putpixel((x,y),((x*y)%256,(x*3+y*2)%256,((x-y)*7)%256))
sample=root/'tests'/'test-input.png';img.save(sample)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=browser.new_page(accept_downloads=True,viewport={'width':1280,'height':900})
  errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
  page.goto(base+'/');assert page.locator('#hero-heading').count()==1
  assert len(page.locator('[data-tool-card]'))==3
  page.locator('#tool-search').fill('signature');assert page.locator('[data-tool-card]:visible').count()==1
  # JPG target 50 KB; output download must be within requested ceiling.
  page.goto(base+'/tools/compress-image.html')
  page.locator('#file-input').set_input_files(str(sample));assert page.locator('#process').is_enabled()
  page.locator('#target').fill('50');page.locator('#process').click();page.locator('#result.show').wait_for(timeout=30000)
  with page.expect_download() as di: page.locator('#download').click()
  dl=di.value;path=root/'tests'/'compressed-test.jpg';dl.save_as(path)
  assert path.stat().st_size<=50*1024,(path.stat().st_size,page.locator('#status').inner_text())
  with Image.open(path) as result:assert result.format=='JPEG'
  # Strict dimension tool
  page.goto(base+'/tools/photo-signature-resizer.html');page.locator('#file-input').set_input_files(str(sample));page.locator('#width').fill('200');page.locator('#height').fill('230');page.locator('#process').click();page.locator('#result.show').wait_for(timeout=30000)
  with page.expect_download() as di:page.locator('#download').click()
  path=root/'tests'/'resized-test.jpg';di.value.save_as(path)
  with Image.open(path) as result:assert result.size==(200,230)
  # image converter to WebP
  page.goto(base+'/tools/image-converter.html');page.locator('#file-input').set_input_files(str(sample));page.locator('#mime').select_option('image/webp');page.locator('#process').click();page.locator('#result.show').wait_for(timeout=30000)
  with page.expect_download() as di:page.locator('#download').click()
  path=root/'tests'/'converted-test.webp';di.value.save_as(path)
  with Image.open(path) as result:assert result.format=='WEBP'
  assert not errors,errors
  # Accessibility/layout smoke test mobile
  page.set_viewport_size({'width':375,'height':800});page.goto(base+'/');assert page.locator('body').evaluate('(e)=>e.scrollWidth <= innerWidth')
  browser.close()
 print('PASS: homepage search, compression ceiling, exact resize pixels, WebP conversion, mobile overflow, no JS exceptions')
finally:
 server.shutdown();server.server_close()
 for p in (root/'tests').glob('*-test.*'):p.unlink(missing_ok=True)
 sample.unlink(missing_ok=True)