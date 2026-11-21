"""Bake space scene motion into GIF frames for GitHub image rendering.
Requires Pillow and Playwright; uses the installed Edge browser on Windows.
"""
from pathlib import Path
from io import BytesIO
import argparse
from PIL import Image
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]

def render():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='msedge',headless=True)
        for name in ['header','projects','connect']:
            path=ROOT/'assets'/f'cosmos-{name}.svg'
            svg=path.read_text(encoding='utf-8')
            height=int(ET.fromstring(svg).get('height'))
            page=browser.new_page(viewport={'width':1000,'height':height},device_scale_factor=1)
            page.set_content('<style>html,body{margin:0;background:black;overflow:hidden}</style>'+svg)
            page.wait_for_function("Array.from(document.querySelectorAll('image')).every(el=>!!el.href.baseVal)")
            page.wait_for_timeout(500)
            page.evaluate("document.getAnimations().forEach(a=>a.pause())")
            frames=[]
            for index in range(40):
                page.evaluate('(t)=>document.getAnimations().forEach(a=>a.currentTime=t)',index*200)
                frames.append(Image.open(BytesIO(page.screenshot())).convert('RGB'))
            palette=frames[0].quantize(colors=128)
            indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
            output=path.with_suffix('.gif')
            indexed[0].save(output,save_all=True,append_images=indexed[1:],duration=200,loop=0,optimize=True,disposal=1)
            print(f'{output.name}: {len(frames)} frames, {output.stat().st_size/1024/1024:.2f} MiB',flush=True)
            frames[0].save(ROOT/'assets'/f'cosmos-{name}-still.png')
            page.close()
        page=browser.new_page(viewport={'width':1000,'height':1500})
        parts=[(ROOT/'assets'/f'cosmos-{name}.svg').read_text(encoding='utf-8') for name in ['arsenal','toolkit']]
        page.set_content('<body style="margin:0;background:#08090b">'+''.join(parts))
        page.screenshot(path=str(Path.home()/'AppData/Local/Temp/console-preview.png'),full_page=True)
        browser.close()
if __name__=='__main__':render()
