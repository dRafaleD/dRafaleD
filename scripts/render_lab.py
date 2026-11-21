"""Render the profile's pixel-art static-analysis loop and project cartridges."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
INK, LINE, LIME, ICE, WHITE = '#080d12', '#283941', '#c1ee76', '#87cdd9', '#edf1df'
BUG = [
    '   x     x   ', '    x   x    ', '   xxxxxxx   ', '  xxx x xxx  ',
    '   xxxxxxx   ', ' xxxxxxxxxxx ', 'xx xxxx xxxx ', '   xxxx xxx x',
    'xxx xxxx xxxx', '   xxxx xxx  ', ' xx xxxxx xx ', 'xx   xxx   xx',
]


def font(size, bold=False, mono=False):
    names = ('consolab.ttf' if bold else 'consola.ttf', 'DejaVuSansMono.ttf') if mono else (
        'segoeuib.ttf' if bold else 'segoeui.ttf', 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    raise RuntimeError(f'Missing font: {names}')


def label(draw, xy, value, size, color, bold=False, mono=False):
    draw.text(xy, value, font=font(size, bold, mono), fill=color, anchor='lt')


def specimen(draw, x, y, scale, scan):
    for row, pixels in enumerate(BUG):
        for column, pixel in enumerate(pixels):
            if pixel == 'x':
                left, top = x + column * scale, y + row * scale
                draw.rectangle((left, top, left + scale - 1, top + scale - 1),
                               fill=WHITE if row == scan else LIME if row < scan else '#588572')


def hero():
    frames = []
    space = Image.open(ASSETS / 'deep-space-lime.png').convert('RGB')
    from PIL import ImageOps
    sky = ImageOps.fit(space, (1070, 400))
    for i in range(48):
        phase = (1 - math.cos(2 * math.pi * i / 48)) / 2
        x = round(phase * 32)
        canvas = sky.crop((x, 0, x + 1000, 360))
        canvas = Image.blend(canvas, Image.new('RGB', canvas.size, INK), .63)
        d = ImageDraw.Draw(canvas)
        label(d,(43,42),'dRafaleD  ~/lab',19,LIME,True,True)
        label(d,(39,91),'Eren Erdoğan',65,WHITE,True)
        label(d,(43,190),'Malware analysis & digital forensics',26,WHITE)
        label(d,(43,241),'Rust  /  YARA-X  /  C',20,LIME,True,True)
        d.line((43,302,555,302),fill=LINE,width=2)
        label(d,(43,315),'LOCAL-FIRST SECURITY TOOLS',14,ICE,True,True)
        d.rectangle((613,24,975,335),fill=INK,outline=LINE,width=2)
        label(d,(633,44),'STATIC ANALYSIS  /  DEMO',18,ICE,True,True)
        for n in range(8):
            for m in range(13):
                d.point((638+m*25,92+n*20),fill='#46606b')
        scan = round(phase*13)
        specimen(d,736,91,10,scan)
        y = 89 + scan*10
        d.line((639,y,950,y),fill=ICE)
        label(d,(636,239),'4D 5A   50 45   4C 41 42',16,ICE,False,True)
        label(d,(636,282),'YARA  /  '+('LAB marker matched' if scan>=8 else 'reading bytes...'),17,LIME,True,True)
        frames.append(canvas)
    frames[24].save(ASSETS/'lab-console.png')
    palette = frames[24].quantize(colors=160)
    frames = [f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    frames[0].save(ASSETS/'lab-console.gif',save_all=True,append_images=frames[1:],duration=140,loop=0)


PROJECTS = [
    ('asphdex','AsphDex','BINARY TRIAGE','Inspect PE / ELF files with YARA.','MZ',LIME),
    ('banshee','Banshee','EVIDENCE COLLECTION','Decode artifacts and bundle findings.','{}',ICE),
    ('flowscope','flowscope','NETWORK FORENSICS','Follow traffic in offline captures.','~',ICE),
    ('sentinel','sentinel-security','LINUX FORENSICS','Rebuild filesystem timelines.','t+',LIME),
    ('fhnix','FhniX','EMAIL TRIAGE','Inspect suspicious mail and its signals.','@',LIME),
    ('trackher','The-Trackher','ACCOUNT PRIVACY','Review your own digital footprint.','id',ICE),
]


def cards():
    for slug,name,category,detail,mark,accent in PROJECTS:
        im=Image.new('RGB',(560,145),INK)
        d=ImageDraw.Draw(im)
        d.line([(1,144),(1,1),(541,1),(558,18),(558,144),(1,144)],fill=LINE,width=2)
        d.rectangle((17,22,21,51),fill=accent)
        label(d,(34,22),category,15,accent,True,True)
        label(d,(33,48),name,35,WHITE,True)
        label(d,(34,106),detail,19,'#c3cdd0')
        label(d,(481,48),mark,30,accent,True,True)
        im.save(ASSETS/f'lab-project-{slug}.png')


def yara_trace():
    frames = []
    for i in range(32):
        im = Image.new('RGB', (1000, 99), INK)
        d = ImageDraw.Draw(im)
        label(d, (25, 16), 'YARA / BYTE MATCH', 18, ICE, True, True)
        label(d, (25, 55), 'Sample marker: LAB', 20, WHITE)
        for j, value in enumerate(['00','4D','5A','00','4C','41','42','00']):
            x = 336 + j * 56
            active = j == min(i // 3, 7) or (i >= 20 and 4 <= j <= 6)
            d.rectangle((x, 30, x+47, 69), fill=LIME if active else LINE)
            label(d, (x+10, 40), value, 20, INK if active else WHITE, True, True)
        label(d, (816, 39), 'MATCH: LAB' if i >= 20 else 'SCANNING', 20, LIME, True, True)
        frames.append(im)
    frames[-1].save(ASSETS/'lab-byte-trace.png')
    frames[0].save(ASSETS/'lab-byte-trace.gif',save_all=True,append_images=frames[1:],duration=160,loop=0)


if __name__ == '__main__':
    hero()
    cards()
    yara_trace()
