"""Render the profile's pixel-art static-analysis loop and project cartridges."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageOps
from render_cosmos_profile import cosmos_photo

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
INK, LINE, LIME, ICE, WHITE = '#0e0f12', '#3a3e46', '#98ecae', '#9fc4e8', '#e4e6ea'
BUG = [
    '  x       x  ', '   x xxx x   ', '    xxxxx    ', '   xx x xx   ',
    ' x  xxxxx  x ', '  xxxx xxxx  ', '   xxx xxx   ', 'xxx xx xx xxx',
    '   xxx xxx   ', '  xxxx xxxx  ', ' x  xx xx  x ', '   x xxx x   ',
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
                               fill=LIME if row == scan else ICE if row < scan else '#617488')


def hero():
    frames = []
    with Image.open(ASSETS / 'deep-space-lime.png') as space:
        sky = ImageOps.fit(cosmos_photo(space), (1070, 400))
    for i in range(48):
        phase = (1 - math.cos(2 * math.pi * i / 48)) / 2
        x = round(phase * 32)
        canvas = sky.crop((x, 0, x + 1000, 360))
        canvas = Image.blend(canvas, Image.new('RGB', canvas.size, INK), .32)
        d = ImageDraw.Draw(canvas)
        label(d,(43,42),'dRafaleD  ~/lab',19,ICE,True,True)
        label(d,(39,91),'Eren Erdoğan',65,WHITE,True)
        label(d,(43,190),'Malware analysis & digital forensics',26,WHITE)
        label(d,(43,241),'Rust  /  YARA-X  /  C',20,LIME,True,True)
        d.line((43,302,555,302),fill=LINE,width=2)
        label(d,(43,315),'LOCAL-FIRST SECURITY TOOLS',14,ICE,True,True)
        d.rounded_rectangle((613,24,975,335),radius=6,fill='#15171b',outline=LINE)
        d.line((614,75,974,75),fill=LINE)
        label(d,(633,44),'STATIC ANALYSIS  /  DEMO',18,ICE,True,True)
        for n in range(8):
            for m in range(13):
                d.point((638+m*25,92+n*20),fill='#46606b')
        scan = round(phase*13)
        specimen(d,736,91,10,scan)
        y = 89 + scan*10
        d.line((639,y,950,y),fill=LIME)
        d.line((633,y-3,633,y+3),fill=LIME,width=2)
        d.line((956,y-3,956,y+3),fill=LIME,width=2)
        label(d,(636,239),'4D 5A   50 45',16,ICE,False,True)
        label(d,(801,239),'4C 41 42',16,LIME if scan>=8 else ICE,True,True)
        label(d,(636,282),'YARA  /  '+('LAB marker matched' if scan>=8 else 'reading bytes...'),17,LIME if scan>=8 else ICE,True,True)
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


SCENES = {'asphdex':'eclipse', 'banshee':'supernova', 'flowscope':'comet',
          'sentinel':'planet', 'fhnix':'binary', 'trackher':'lens'}


def cards():
    for slug,name,category,detail,mark,accent in PROJECTS:
        with Image.open(ASSETS / f'deep-space-{SCENES[slug]}.jpg') as photo:
            thumbnail = ImageOps.fit(cosmos_photo(photo), (210,145))
        im = Image.new('RGB', (560,145), '#15171b')
        fade = Image.linear_gradient('L').rotate(90).resize(thumbnail.size)
        im.paste(thumbnail, (350,0), fade)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0,0,559,144),radius=6,outline=LINE)
        label(d,(23,18),category,16,ICE,True,True)
        label(d,(22,45),name,35,WHITE,True)
        label(d,(23,104),detail,19,'#cdd2da')
        d.rounded_rectangle((489,16,542,49),radius=5,fill=INK,outline=LINE)
        label(d,(498,23),mark,19,accent,True,True)
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
            active = 4 <= j <= 6 if i >= 20 else j == i // 3
            d.rounded_rectangle((x, 30, x+47, 69), radius=4, fill=(LIME if i >= 20 else ICE) if active else '#20262e')
            label(d, (x+10, 40), value, 20, INK if active else WHITE, True, True)
        label(d, (816, 39), 'MATCH: LAB' if i >= 20 else 'SCANNING', 20, LIME, True, True)
        frames.append(im)
    frames[-1].save(ASSETS/'lab-byte-trace.png')
    frames[0].save(ASSETS/'lab-byte-trace.gif',save_all=True,append_images=frames[1:],duration=160,loop=0)


if __name__ == '__main__':
    hero()
    cards()
    yara_trace()
