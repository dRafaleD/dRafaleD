"""Render the profile's pixel-art static-analysis loop and project cartridges."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
INK, LINE, LIME, PHOSPHOR, WHITE = '#030503', '#263522', '#82ed30', '#a8cf98', '#edf1e9'
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


def specimen(phase, reaction='idle'):
    """A socketed silicon skull with pulsing diagnostic LEDs."""
    sprite = Image.new('RGBA', (96, 68))
    draw = ImageDraw.Draw(sprite)
    shadow = '#364932'
    steel = '#94aa86'
    for y in range(18,44,6):
        draw.rectangle((18,y,77,y+2), fill=shadow)
        for x in (18,75):
            draw.rectangle((x,y,x+2,y+1), fill=PHOSPHOR)
    draw.polygon([(24,17),(32,8),(64,8),(72,17),(72,36),(66,45),
                  (61,46),(61,55),(55,61),(40,61),(34,55),(34,46),
                  (29,45),(24,37)], fill=shadow)
    draw.polygon([(26,18),(34,10),(62,10),(69,17),(69,35),(64,42),
                  (57,44),(57,51),(39,51),(39,44),(32,42),(26,35)], fill=steel)
    draw.polygon([(28,19),(35,12),(60,12),(64,15),(38,15),(31,22),(28,27)],fill='#d3e7bd')
    draw.line([(57,11),(54,16),(57,17),(50,23)],fill=shadow,width=2)
    for sign in (-1,1):
        socket = [(3,32),(18,27),(18,34),(14,39),(5,38)]
        draw.polygon([(48+sign*x,y) for x,y in socket],fill=INK)
        glow = '#77b995' if math.cos(phase)<0 else LIME
        if reaction == 'alert':
            draw.line([(48+sign*6,36),(48+sign*15,31)],fill='#b6ff57',width=2)
            draw.line([(48+sign*4,32),(48+sign*16,26)],fill='#59774b',width=3)
        elif reaction == 'offline':
            draw.line([(48+sign*7,35),(48+sign*14,35)],fill=shadow)
        else:
            draw.line([(48+sign*7,35),(48+sign*14,33)],fill=glow,width=2)
    draw.polygon([(47,38),(50,38),(53,44),(44,44)],fill=INK)
    draw.rectangle((39,50,57,56),fill=INK)
    for x in (39,44,50,55):
        draw.rectangle((x,48,x+2,54),fill='#d3e7bd')
    draw.line([(38,55),(42,58),(54,58),(58,55)],fill=steel,width=2)
    return sprite.resize((192,136),Image.Resampling.NEAREST)


def analysis_demos():
    frames = []
    for i in range(48):
        phase = math.tau*i/48
        im = Image.new('RGB', (1000,300), INK)
        d = ImageDraw.Draw(im)
        for left, title in [(0,'Static analysis'),(508,'Dynamic analysis')]:
            d.rounded_rectangle((left,0,left+491,299),radius=7,fill='#0a0e09',outline=LINE)
            label(d,(left+22,18),title,27,WHITE,True)
            label(d,(left+413,24),'DEMO',16,PHOSPHOR,True,True)
            d.line((left+1,61,left+490,61),fill=LINE)
        skull = specimen(0)
        im.paste(skull,(149,70),skull)
        y = 83 + round(105*(1-math.cos(phase))/2)
        d.line((47,y,444,y),fill='#689581')
        d.rectangle((43,y-2,47,y+2),fill=LIME)
        label(d,(22,216),'4D 5A    50 45    4C 41 42',20,PHOSPHOR,False,True)
        label(d,(22,254),'YARA  /  '+('LAB marker matched' if y>149 else 'scanning bytes'),20,LIME,True,True)

        stage = min(i//12,2)
        reaction = ('idle','alert','offline')[stage]
        skull = specimen(phase,reaction).resize((144,102),Image.Resampling.NEAREST)
        recoil = {12:-6,13:-4,14:-2}.get(i,0)
        im.paste(skull,(524+recoil,98+recoil),skull)
        if stage == 1:
            top = 80 + min(i-12,3)
            d.rounded_rectangle((629,top,655,top+28),radius=4,fill='#18280e',outline='#82ed30')
            d.polygon([(630,top+26),(626,top+32),(637,top+27)],fill='#82ed30')
            d.rectangle((640,top+5,644,top+16),fill='#d4ffc1')
            d.rectangle((640,top+20,644,top+23),fill='#d4ffc1')
        for j,event in enumerate(('Process start','File read','Process exit')):
            row = 99+j*38
            if j<2:
                d.line((697,row+5,697,row+38),fill=LINE,width=2)
            d.ellipse((692,row-4,702,row+6),fill=LIME if j==stage else '#586674')
            label(d,(718,row-7),event,19,WHITE if j<=stage else '#86909a',False,True)
        label(d,(530,216),'Synthetic event trace',20,PHOSPHOR,False,True)
        label(d,(530,254),('PID 104  /  started','PID 104  /  read 64 B','PID 104  /  exited')[stage],20,LIME,True,True)
        frames.append(im)
    frames[18].save(ASSETS/'malware-chip-skull.png')
    frames[0].save(ASSETS/'malware-chip-skull.gif',save_all=True,append_images=frames[1:],duration=150,loop=0)


def hero():
    frames = []
    with Image.open(ASSETS / 'operator-avatar.png') as source:
        avatar = source.resize((288,288),Image.Resampling.NEAREST)
    for i in range(48):
        canvas = Image.new('RGB',(1000,360), '#000000')
        canvas.paste(avatar,(655,41))
        d = ImageDraw.Draw(canvas)
        label(d,(42,35),'dRafaleD@lab  ~  $ whoami',18,LIME,True,True)
        label(d,(38,79),'Eren Erdoğan',65,WHITE,True)
        label(d,(42,173),'Malware analysis & reverse engineering',25,WHITE)
        label(d,(42,221),'Rust   /   YARA-X   /   C',19,LIME,True,True)
        d.line((42,271,555,271),fill=LINE)
        row = (i // 12) * 4
        label(d,(42,294),f'0x{row:04X}',16,PHOSPHOR,True,True)
        byte_rows = ('4D 5A 90 00','03 00 00 00','04 00 00 00','FF FF 00 00')
        label(d,(132,294),byte_rows[i//12],16,WHITE,False,True)
        if i % 12 < 8:
            d.rectangle((259,295,268,310),fill=LIME)
        for x,dx in ((638,1),(960,-1)):
            for y,dy in ((31,1),(333,-1)):
                d.line([(x+dx*17,y),(x,y),(x,y+dy*17)],fill=LIME,width=2)
        frames.append(canvas)
    frames[24].save(ASSETS/'lab-console.png')
    palette = frames[24].quantize(colors=160)
    frames = [f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    frames[0].save(ASSETS/'lab-console.gif',save_all=True,append_images=frames[1:],duration=140,loop=0)


PROJECTS = [
    ('asphdex','AsphDex','BINARY TRIAGE','Inspect PE / ELF files with YARA.','MZ',LIME),
    ('banshee','Banshee','EVIDENCE COLLECTION','Decode artifacts and bundle findings.','{}',PHOSPHOR),
    ('flowscope','flowscope','NETWORK FORENSICS','Follow traffic in offline captures.','~',PHOSPHOR),
    ('sentinel','sentinel-security','LINUX FORENSICS','Rebuild filesystem timelines.','t+',LIME),
    ('fhnix','FhniX','EMAIL TRIAGE','Inspect suspicious mail and its signals.','@',LIME),
    ('trackher','The-Trackher','ACCOUNT PRIVACY','Review your own digital footprint.','id',PHOSPHOR),
]


# One-bit project icons, drawn at native pixel resolution then enlarged.
ICONS = {
    'asphdex': ('01111100','01000110','01000010','01011010','01100110','01011010','01000010','01111110'),
    'banshee': ('00111100','01000010','10000001','10100101','10000001','10011001','10100101','11000011'),
    'flowscope': ('00000000','00100000','00100010','01010010','11010111','00010100','00001000','00000000'),
    'sentinel': ('01111110','01000010','00100100','00011000','00011000','00111100','01111110','01111110'),
    'fhnix': ('00000000','11111111','11000011','10100101','10011001','10000001','11111111','00000000'),
    'trackher': ('00111100','01000010','10011001','10100101','10110101','10100101','01001010','00110000'),
}


def cards():
    for slug,name,category,detail,mark,accent in PROJECTS:
        im = Image.new('RGB', (560,145), '#0a0e09')
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0,0,559,144),radius=6,outline=LINE)
        label(d,(23,18),category,16,PHOSPHOR,True,True)
        label(d,(22,45),name,35,WHITE,True)
        label(d,(23,104),detail,19,'#bdc8b7')
        for y,row in enumerate(ICONS[slug]):
            for x,bit in enumerate(row):
                if bit == '1':
                    d.rectangle((481+x*6,24+y*6,486+x*6,29+y*6),fill=LIME)
        im.save(ASSETS/f'lab-project-{slug}.png')


def yara_trace():
    frames = []
    for i in range(32):
        im = Image.new('RGB', (1000, 99), INK)
        d = ImageDraw.Draw(im)
        label(d, (25, 16), 'YARA / BYTE MATCH', 18, PHOSPHOR, True, True)
        label(d, (25, 55), 'Sample marker: LAB', 20, WHITE)
        for j, value in enumerate(['00','4D','5A','00','4C','41','42','00']):
            x = 336 + j * 56
            active = 4 <= j <= 6 if i >= 20 else j == i // 3
            d.rounded_rectangle((x, 30, x+47, 69), radius=4, fill=(LIME if i >= 20 else PHOSPHOR) if active else '#20301a')
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
