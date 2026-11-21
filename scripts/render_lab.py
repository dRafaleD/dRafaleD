"""Render the profile's pixel-art static-analysis loop and project cartridges."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageOps
from render_cosmos_profile import cosmos_photo

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
INK, LINE, LIME, ICE, WHITE = '#0e0f12', '#3a3e46', '#98ecae', '#9fc4e8', '#e4e6ea'
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


def specimen(phase):
    """A socketed silicon skull with pulsing diagnostic LEDs."""
    sprite = Image.new('RGBA', (96, 68))
    draw = ImageDraw.Draw(sprite)
    shadow = '#37485a'
    steel = '#86a4be'
    for y in range(18,44,6):
        draw.rectangle((18,y,77,y+2), fill=shadow)
        for x in (18,75):
            draw.rectangle((x,y,x+2,y+1), fill=ICE)
    draw.polygon([(24,17),(32,8),(64,8),(72,17),(72,36),(66,45),
                  (61,46),(61,55),(55,61),(40,61),(34,55),(34,46),
                  (29,45),(24,37)], fill=shadow)
    draw.polygon([(26,18),(34,10),(62,10),(69,17),(69,35),(64,42),
                  (57,44),(57,51),(39,51),(39,44),(32,42),(26,35)], fill=steel)
    draw.polygon([(28,19),(35,12),(60,12),(64,15),(38,15),(31,22),(28,27)],fill='#c5d9e7')
    draw.line([(57,11),(54,16),(57,17),(50,23)],fill=shadow,width=2)
    for sign in (-1,1):
        socket = [(3,32),(18,27),(18,34),(14,39),(5,38)]
        draw.polygon([(48+sign*x,y) for x,y in socket],fill=INK)
        glow = '#77b995' if math.cos(phase)<0 else LIME
        draw.line([(48+sign*7,35),(48+sign*14,33)],fill=glow,width=2)
    draw.polygon([(47,38),(50,38),(53,44),(44,44)],fill=INK)
    draw.rectangle((39,50,57,56),fill=INK)
    for x in (39,44,50,55):
        draw.rectangle((x,48,x+2,54),fill='#c5d9e7')
    draw.line([(38,55),(42,58),(54,58),(58,55)],fill=steel,width=2)
    return sprite.resize((192,136),Image.Resampling.NEAREST)


def analysis_demos():
    frames = []
    for i in range(48):
        phase = math.tau*i/48
        im = Image.new('RGB', (1000,300), INK)
        d = ImageDraw.Draw(im)
        for left, title in [(0,'Static analysis'),(508,'Dynamic analysis')]:
            d.rounded_rectangle((left,0,left+491,299),radius=7,fill='#15171b',outline=LINE)
            label(d,(left+22,18),title,27,WHITE,True)
            label(d,(left+413,24),'DEMO',16,ICE,True,True)
            d.line((left+1,61,left+490,61),fill=LINE)
        skull = specimen(0)
        im.paste(skull,(149,70),skull)
        y = 83 + round(105*(1-math.cos(phase))/2)
        d.line((47,y,444,y),fill='#689581')
        d.rectangle((43,y-2,47,y+2),fill=LIME)
        label(d,(22,216),'4D 5A    50 45    4C 41 42',20,ICE,False,True)
        label(d,(22,254),'YARA  /  '+('LAB marker matched' if y>149 else 'scanning bytes'),20,LIME,True,True)

        skull = specimen(phase).resize((144,102),Image.Resampling.NEAREST)
        im.paste(skull,(524,98),skull)
        stage = min(i//12,2)
        for j,event in enumerate(('Process start','File read','Process exit')):
            row = 99+j*38
            if j<2:
                d.line((697,row+5,697,row+38),fill=LINE,width=2)
            d.ellipse((692,row-4,702,row+6),fill=LIME if j==stage else '#586674')
            label(d,(718,row-7),event,19,WHITE if j<=stage else '#86909a',False,True)
        label(d,(530,216),'Synthetic event trace',20,ICE,False,True)
        label(d,(530,254),('PID 104  /  started','PID 104  /  read 64 B','PID 104  /  exited')[stage],20,LIME,True,True)
        frames.append(im)
    frames[27].save(ASSETS/'lab-analysis.png')
    frames[0].save(ASSETS/'lab-analysis.gif',save_all=True,append_images=frames[1:],duration=150,loop=0)


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
    analysis_demos()
    cards()
    yara_trace()
