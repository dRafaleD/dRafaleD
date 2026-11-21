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
    """Front-facing armored beetle with hooked limbs and articulated mandibles."""
    sprite = Image.new('RGBA', (96,68))
    d = ImageDraw.Draw(sprite)
    alert = reaction == 'alert'
    dark, shell, ridge = '#283723', '#526749', '#a0b78c'
    eye = '#53624c' if reaction == 'offline' else LIME
    twitch = 0 if reaction == 'offline' else round(2 * math.sin(phase * 3))
    for side in (-1, 1):
        def mirror(points):
            return [(48 + side * x, y) for x, y in points]

        for joint, knee, ankle, tip in [
            ((11,19),(25,9),(33,15),(39,12)),
            ((13,29),(31,21),(37,31),(44,32)),
            ((12,38),(27,37),(36,51),(42,48)),
        ]:
            leg = mirror([joint, knee, ankle, (tip[0], tip[1]+twitch)])
            d.line(leg, fill=shell, width=3)
            d.line(leg[:2], fill=ridge)
            d.point(leg[2], fill=LIME)
        d.polygon(mirror([(1,33),(1,8),(5,4),(12,11),(15,20),(13,32),(8,38)]),
                  fill=shell, outline=dark)
        d.line(mirror([(3,25),(4,11),(6,8),(11,14)]),fill=ridge)
        for y in (14,19,24):
            d.line(mirror([(6,y),(10,y+3)]),fill='#30402c')
        d.line(mirror([(9,38),(20,24),(26,18+twitch),(29,9+twitch)]),fill=PHOSPHOR)
    d.polygon([(34,32),(40,26),(56,26),(62,32),(64,42),(58,51),
               (51,55),(45,55),(38,51),(32,42)],fill=dark,outline=ridge)
    for side in (-1, 1):
        def face(points):
            return [(48+side*x,y) for x,y in points]

        d.polygon(face([(2,37),(14,32),(14,41),(8,46),(2,44)]),fill=INK)
        if alert:
            d.polygon(face([(3,42),(13,35),(12,40),(5,45)]),fill=eye)
            d.line(face([(2,39),(12,32),(15,32)]),fill=ridge,width=2)
        else:
            d.polygon(face([(4,37),(11,35),(12,39),(9,43),(4,43)]),fill=eye)
            d.line(face([(8,37),(8,41)]),fill=dark)
        spread = 4 if alert else 0
        d.polygon(face([(8,47),(12,49),(12+spread,56),(8+spread,63),(4,65),
                        (8+spread,57),(6,52)]),fill=shell,outline=ridge)
    d.line([(45,49),(48,47),(51,49)],fill=INK,width=2)
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
        sample = specimen(0)
        im.paste(sample,(149,70),sample)
        y = 83 + round(105*(1-math.cos(phase))/2)
        d.line((47,y,444,y),fill='#689581')
        d.rectangle((43,y-2,47,y+2),fill=LIME)
        label(d,(22,216),'4D 5A    50 45    4C 41 42',20,PHOSPHOR,False,True)
        label(d,(22,254),'YARA  /  '+('LAB marker matched' if y>149 else 'scanning bytes'),20,LIME,True,True)

        stage = min(i//12,2)
        reaction = ('idle','alert','offline')[stage]
        sample = specimen(phase,reaction).resize((144,102),Image.Resampling.NEAREST)
        recoil = {12:-6,13:-4,14:-2}.get(i,0)
        im.paste(sample,(524+recoil,98+recoil),sample)
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
    frames[18].save(ASSETS/'malware-beetle.png')
    frames[0].save(ASSETS/'malware-beetle.gif',save_all=True,append_images=frames[1:],duration=150,loop=0)


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
        frames = []
        signals = {
            'asphdex': ('4D 5A', 'PE', 'YARA'),
            'banshee': ('READ', 'HASH', 'PACK'),
            'flowscope': ('DNS', 'TCP', 'TLS'),
            'sentinel': ('MTIME', 'CTIME', 'ATIME'),
            'fhnix': ('FROM', 'LINK', 'SCORE'),
            'trackher': ('ID', 'ALIAS', 'MATCH'),
        }
        for i in range(18):
            frame = im.copy()
            draw = ImageDraw.Draw(frame)
            scan = 25 + round(45*(1-math.cos(math.tau*i/18))/2)
            draw.line((475,scan,533,scan),fill='#a6ff59')
            label(draw,(480,88),signals[slug][i//6],13,LIME,True,True)
            frames.append(frame)
        frames[6].save(ASSETS/f'trace-{slug}.png')
        frames[0].save(ASSETS/f'trace-{slug}.gif', save_all=True,
                       append_images=frames[1:], duration=160, loop=0)


def disassembly():
    frames = []
    rows = [('0000','31 C0','xor eax, eax'),('0002','FF C0','inc eax'),
            ('0004','83 F8 01','cmp eax, 1'),('0007','C3','ret')]
    for i in range(4):
        frame = Image.new('RGB',(1000,235),INK)
        draw = ImageDraw.Draw(frame)
        label(draw,(28,18),'Disassembly',24,WHITE,True)
        label(draw,(663,23),'REGISTER WATCH',16,LIME,True,True)
        for j,(offset,raw,instruction) in enumerate(rows):
            y = 70+j*37
            if i == j:
                draw.rectangle((20,y-9,610,y+24),fill='#16280d')
                draw.rectangle((20,y-9,23,y+24),fill=LIME)
            for x,value in [(39,offset),(151,raw),(346,instruction)]:
                label(draw,(x,y),value,19,LIME if i==j else PHOSPHOR,False,True)
        label(draw,(663,83),'EAX',17,PHOSPHOR,True,True)
        label(draw,(663,116),'00000000' if i==0 else '00000001',31,WHITE,True,True)
        label(draw,(663,182),('zero register','increment','compare','return')[i],17,LIME,False,True)
        frames.append(frame)
    frames[2].save(ASSETS/'instruction-trace.png')
    frames[0].save(ASSETS/'instruction-trace.gif',save_all=True,append_images=frames[1:],duration=800,loop=0)


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
    disassembly()
    cards()
    yara_trace()
