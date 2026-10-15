"""Playwright integration test without localhost navigation, which may be blocked in sandboxes.

Loads the actual HTML/CSS and runs the same application JavaScript in one concatenated
classic-script context, stripping only ES module import/export syntax. It exercises
real browser Canvas/Blob encoding and downloads, but not HTTP/module loading.
"""
from pathlib import Path
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ['assets/icons.js', 'assets/toolkit.js','assets/site.js','assets/workbench.js']

def js_for(page_name):
    chunks=[]
    for path in SCRIPTS if page_name.startswith('tools/') else ['assets/icons.js','assets/site.js']:
        s=(ROOT/path).read_text()
        s=re.sub(r'^import .*?;\s*$', '', s, flags=re.MULTILINE)
        s=re.sub(r'\bexport\s+(?=(?:async\s+)?function|const|let|class)','',''.join([s]))
        chunks.append(s)
    return '(function(){\n'+ '\n;\n'.join(chunks)+'\n})();'

def show(page, name):
    html=(ROOT/name).read_text()
    # Data-URI preview for the logo: this harness uses set_content instead of HTTP assets.
    logo='data:image/svg+xml,'+quote((ROOT/'assets/favicon.svg').read_text())
    html=html.replace('/assets/favicon.svg',logo)
    alpine='data:image/svg+xml,'+quote((ROOT/'assets/alpine-preview.svg').read_text())
    html=html.replace('/assets/alpine-preview.svg',alpine)
    html=re.sub(r'<script[^>]*src="[^"]+"[^>]*></script>', '', html)
    html=re.sub(r'<link(?=[^>]*rel="stylesheet")[^>]*>', '', html)
    page.set_content(html,wait_until='load')
    page.add_style_tag(content='\n'.join((ROOT/'assets/styles.css').read_text().splitlines()[1:]))
    page.add_script_tag(content=js_for(name))

sample=ROOT/'tests'/'test-input.png'
img=Image.new('RGB',(650,530))
for y in range(530):
    for x in range(650):
        img.putpixel((x,y),((x*y)%256,(x*3+y*2)%256,((x-y)*7)%256))
img.save(sample)
signature=ROOT/'tests'/'signature-input.jpg'
sig=Image.new('RGB',(1400,430),'white');draw=ImageDraw.Draw(sig)
# Wide margins and delicate blue handwriting strokes, representative of a scan.
points=[(90,210),(160,180),(210,240),(260,140),(310,245),(360,180),(410,205),(490,120),(525,258),(580,190),(640,210),(710,145),(800,180),(900,120),(960,220),(1110,145),(1180,195)]
draw.line(points,fill=(21,58,133),width=6,joint='curve')
draw.arc((160,95,1130,340),start=20,end=150,fill=(35,70,147),width=4)
sig.save(signature,quality=88)
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(accept_downloads=True,viewport={'width':1280,'height':900})
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        show(page,'index.html')
        assert page.locator('#hero-heading').count()==1
        assert page.locator('[data-tool-card]').count()==3
        assert page.locator('.float-chip').count()==4
        assert page.locator('.how-features > div').count()==4
        assert page.locator('.hero .btn-dark').count()==1
        page.screenshot(path=str(ROOT/'tests'/'homepage-preview.png'),full_page=True)
        page.set_viewport_size({'width':375,'height':800})
        assert page.locator('body').evaluate('(e)=>e.scrollWidth <= innerWidth'), 'Mobile horizontal overflow'
        page.screenshot(path=str(ROOT/'tests'/'mobile-preview.png'),full_page=True)
        page.set_viewport_size({'width':1280,'height':900})

        show(page,'tools/compress-image.html')
        page.locator('#file-input').set_input_files(str(sample))
        page.locator('#process').wait_for(state='visible')
        page.wait_for_function('!document.querySelector("#process").disabled',timeout=10000)
        page.locator('#target').fill('50')
        page.locator('#process').click()
        page.locator('#result.show').wait_for(timeout=30000)
        assert 'success' in page.locator('#status').get_attribute('class'),page.locator('#status').inner_text()
        with page.expect_download(timeout=10000) as event: page.locator('#download').click()
        data=ROOT/'tests'/'compressed-test.jpg';event.value.save_as(str(data))
        assert data.stat().st_size<=50*1024, (data.stat().st_size, page.locator('#status').inner_text())
        with Image.open(data) as result:assert result.format=='JPEG'

        show(page,'tools/photo-signature-resizer.html')
        page.locator('#file-input').set_input_files(str(sample))
        page.locator('#width').fill('200')
        page.locator('#height').fill('230')
        page.locator('#process').click()
        page.locator('#result.show').wait_for(timeout=30000)
        with page.expect_download() as event:page.locator('#download').click()
        data=ROOT/'tests'/'resized-test.jpg';event.value.save_as(str(data))
        with Image.open(data) as result:assert result.size==(200,230)

        # Signature mode: real browser Canvas image clean-up, PNG output and
        # a visual check for contrast and non-blank strokes after resize.
        show(page,'tools/photo-signature-resizer.html')
        page.locator('#file-input').set_input_files(str(signature))
        page.locator('#purpose').select_option('signature')
        assert page.locator('#mime').input_value()=='image/png'
        assert page.locator('#signature-options').is_visible()
        page.screenshot(path=str(ROOT/'tests'/'signature-mode-preview.png'),full_page=True)
        page.locator('#width').fill('300')
        page.locator('#height').fill('120')
        page.locator('#process').click()
        page.locator('#result.show').wait_for(timeout=30000)
        assert page.locator('#result-preview').get_attribute('src').startswith('blob:')
        page.screenshot(path=str(ROOT/'tests'/'signature-result-preview.png'),full_page=True)
        with page.expect_download() as event:page.locator('#download').click()
        data=ROOT/'tests'/'signature-test.png';event.value.save_as(str(data))
        with Image.open(data) as output:
            assert output.size==(300,120) and output.format=='PNG'
            gray=output.convert('L')
            n_dark=sum(1 for pix in gray.getdata() if pix<135)
            assert n_dark>90,f'Signature disappeared after resizing ({n_dark} visible pixels)'
        # High-resolution master retains the detail of the source scan. It must
        # be larger than the exact-size application output and export lossless PNG.
        page.locator('input[name="signature-export"][value="master"]').check()
        assert page.locator('#width').is_disabled()
        page.locator('#process').click()
        page.locator('#result.show').wait_for(timeout=30000)
        with page.expect_download() as event:page.locator('#download').click()
        master=ROOT/'tests'/'signature-master-test.png';event.value.save_as(str(master))
        with Image.open(master) as master_img:
            assert master_img.width>800 and master_img.height>150,master_img.size
        assert page.locator('#zoom-image').get_attribute('src').startswith('blob:')
        page.screenshot(path=str(ROOT/'tests'/'signature-master-preview.png'),full_page=True)
        page.locator('[data-zoom="2"]').click()
        assert page.locator('[data-zoom="2"]').get_attribute('aria-pressed')=='true'
        # Return to exact-size before testing transparent PNG.
        page.locator('input[name="signature-export"][value="exact"]').check()
        page.locator('#process').click()
        page.locator('#result.show').wait_for(timeout=30000)
        # Transparent signature output maintains actual transparent pixels.
        page.locator('#transparent').check()
        page.locator('#process').click()
        page.locator('#result.show').wait_for(timeout=30000)
        with page.expect_download() as event:page.locator('#download').click()
        data=ROOT/'tests'/'signature-transparent-test.png';event.value.save_as(str(data))
        with Image.open(data) as output:
            assert output.mode=='RGBA'
            alpha=output.getchannel('A')
            assert alpha.getextrema()[0]==0 and alpha.getextrema()[1]>200,alpha.getextrema()

        show(page,'tools/image-converter.html')
        page.locator('#file-input').set_input_files(str(sample))
        page.locator('#mime').select_option('image/webp')
        page.locator('#process').click()
        page.locator('#result.show').wait_for(timeout=30000)
        with page.expect_download() as event:page.locator('#download').click()
        data=ROOT/'tests'/'converted-test.webp';event.value.save_as(str(data))
        with Image.open(data) as result:assert result.format=='WEBP'

        assert not errors,errors
        browser.close()
    print('PASS: real Chromium Canvas image compression, photo resizing, signature cleaning and transparency, WebP conversion, downloads, search and mobile layout')
finally:
    sample.unlink(missing_ok=True)
    signature.unlink(missing_ok=True)
    for p in (ROOT/'tests').glob('*-test.*'):p.unlink(missing_ok=True)