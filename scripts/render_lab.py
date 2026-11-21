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


def specimen(reaction='idle'):
    """Pixel executable mascot with an expressive bug emblem on its cover."""
    sprite = Image.new('RGBA', (96,68))
    d = ImageDraw.Draw(sprite)
    page = [(23,3),(60,3),(75,18),(75,61),(72,64),(23,64),(20,61),(20,6)]
    d.polygon([(x+3,y+2) for x,y in page],fill='#24301d')
    d.polygon(page,fill='#192515',outline='#91ab7c')
    d.line([(23,58),(23,7),(26,6),(58,6)],fill='#43563b')
    d.polygon([(60,4),(74,18),(60,18)],fill='#526843',outline=PHOSPHOR)
    d.line([(61,20),(72,20)],fill=INK)
    # Short circuit-like legs keep the bug inside the file silhouette.
    for sign in (-1,1):
        for y,offset in ((24,-3),(31,0),(37,3)):
            d.line([(47+sign*10,y),(47+sign*15,y),(47+sign*18,y+offset)],
                   fill='#96ba7f',width=2)
        d.line([(47+sign*5,20),(47+sign*9,15),(47+sign*11,15)],fill=LIME)
    d.polygon([(36,22),(41,18),(53,18),(58,22),(58,36),(52,42),
               (42,42),(36,36)],fill='#080e07',outline='#749d59')
    d.line([(43,39),(47,40),(51,39)],fill='#4e7240')
    glow = '#506246' if reaction=='offline' else '#b6ff75'
    for sign in (-1,1):
        if reaction=='alert':
            eye = [(2,31),(9,26),(9,30),(4,33),(2,33)]
            d.line([(47+sign*2,28),(47+sign*9,23)],fill='#8cb072',width=2)
        else:
            eye = [(2,26),(8,25),(9,28),(8,32),(3,32),(2,31)]
        d.polygon([(47+sign*x,y) for x,y in eye],fill=glow)
        if reaction=='idle':
            d.line([(47+sign*5,27),(47+sign*5,30)],fill=INK)
    d.polygon([(17,45),(65,45),(69,49),(69,60),(17,60)],fill=LIME)
    label(d,(24,47),'.EXE',14,INK,True,True)
    return sprite.resize((192,136),Image.Resampling.NEAREST)


def analysis_demos():
    right = 508
    sprite_x, sprite_y = 22, 69
    height = 328
    frames = []
    stacked_frames = []
    for i in range(48):
        phase = math.tau*i/48
        im = Image.new('RGB', (1000,height), INK)
        d = ImageDraw.Draw(im)
        for left, title in [(0,'Static analysis'),(508,'Dynamic analysis')]:
            d.rounded_rectangle((left,0,left+491,height-1),radius=7,fill='#0a0e09',outline=LINE)
            label(d,(left+22,18),title,31,WHITE,True)
            label(d,(left+413,24),'DEMO',18,PHOSPHOR,True,True)
            d.line((left+1,61,left+490,61),fill=LINE)
        sample = specimen()
        im.paste(sample,(sprite_x,sprite_y),sample)
        y = 83 + round(105*(1-math.cos(phase))/2)
        d.line((22,y,216,y),fill='#689581')
        d.rectangle((22,y-2,26,y+2),fill=LIME)
        for j, value in enumerate(('4D 5A   MZ', '50 45   PE', '4C 41 42   LAB')):
            label(d,(246,92+j*38),value,23,LIME if y>149 and j==2 else PHOSPHOR,False,True)
        label(d,(22,225),'Static byte scan',23,PHOSPHOR,False,True)
        label(d,(22,273),'YARA  /  '+('LAB marker matched' if y>149 else 'scanning bytes'),23,LIME,True,True)

        stage = min(i//12,2)
        reaction = ('idle','alert','offline')[stage]
        sample = specimen(reaction)
        recoil = {12:-6,13:-4,14:-2}.get(i,0)
        im.paste(sample,(right+sprite_x+recoil,sprite_y+recoil),sample)
        if stage == 1:
            top = 67 + min(i-12,3)
            d.rounded_rectangle((691,top,717,top+28),radius=4,fill='#18280e',outline='#82ed30')
            d.polygon([(692,top+26),(688,top+32),(699,top+27)],fill='#82ed30')
            d.rectangle((702,top+5,706,top+16),fill='#d4ffc1')
            d.rectangle((702,top+20,706,top+23),fill='#d4ffc1')
        for j,event in enumerate(('Process start','File read','Process exit')):
            row = 99+j*38
            if j<2:
                d.line((739,row+5,739,row+38),fill=LINE,width=2)
            d.ellipse((734,row-4,744,row+6),fill=LIME if j==stage else '#586674')
            label(d,(754,row-7),event,23,WHITE if j<=stage else '#86909a',False,True)
        label(d,(530,225),'Synthetic event trace',23,PHOSPHOR,False,True)
        label(d,(530,273),('PID 104  /  started','PID 104  /  read 64 B','PID 104  /  exited')[stage],23,LIME,True,True)
        frames.append(im)
        stacked = Image.new('RGB', (492, height*2+12), INK)
        stacked.paste(im.crop((0,0,492,height)), (0,0))
        stacked.paste(im.crop((right,0,1000,height)), (0,height+12))
        stacked_frames.append(stacked)
    for layout, sequence in [('wide', frames), ('stacked', stacked_frames)]:
        base = ASSETS / f'exe-mascot-{layout}'
        sequence[18].save(base.with_suffix('.png'))
        sequence[0].save(base.with_suffix('.gif'), save_all=True,
                         append_images=sequence[1:], duration=150, loop=0)


def hero():
    frames = []
    with Image.open(ASSETS / 'operator-avatar.png') as source:
        avatar = source.convert("RGB").resize((288, 288), Image.Resampling.LANCZOS)
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
    frames[24].save(ASSETS/'operator-profile-card.png')
    palette = frames[24].quantize(colors=256)
    frames = [f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    frames[0].save(ASSETS/'operator-profile-card.gif',save_all=True,append_images=frames[1:],duration=140,loop=0)


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
        import textwrap
        mobile_frames = []
        for frame in frames:
            mobile = Image.new('RGB',(352,146),'#0a0e09')
            pen = ImageDraw.Draw(mobile)
            pen.rectangle((0,0,351,145),outline=LINE)
            label(pen,(12,12),category,16,PHOSPHOR,True,True)
            label(pen,(12,39),name,27,WHITE,True)
            for line_no,line in enumerate(textwrap.wrap(detail,28)):
                label(pen,(12,86+line_no*24),line,20,WHITE)
            mobile.paste(frame.crop((474,20,548,105)).resize((55,64)),(286,10))
            mobile_frames.append(mobile)
        save_trace(f'trace-{slug}-mobile',mobile_frames,6,160)
        frames[6].save(ASSETS/f'trace-{slug}.png')
        frames[0].save(ASSETS/f'trace-{slug}.gif', save_all=True,
                       append_images=frames[1:], duration=160, loop=0)


def save_trace(name, frames, still, duration):
    frames[still].save(ASSETS/f'{name}.png')
    frames[0].save(ASSETS/f'{name}.gif', save_all=True, append_images=frames[1:], duration=duration, loop=0)


def disassembly():
    rows = [('0000','31 C0','xor eax, eax'),('0002','FF C0','inc eax'),
            ('0004','83 F8 01','cmp eax, 1'),('0007','C3','ret')]
    for mode,width in [('mobile',352),('wide',720)]:
        frames = []
        for i in range(4):
            im = Image.new('RGB',(width,282),INK)
            d = ImageDraw.Draw(im)
            label(d,(16,18),'Disassembly',28,WHITE,True)
            for j,(offset,raw,instruction) in enumerate(rows):
                y = 68+j*38
                if i == j:
                    d.rectangle((8,y-7,width-8,y+26),fill='#16280d')
                for x,value in [(16,offset),(85,raw),(178,instruction)]:
                    label(d,(x,y),value,19,LIME if i==j else PHOSPHOR,False,True)
            label(d,(16,238),'EAX  '+('00000000' if i==0 else '00000001'),23,LIME,True,True)
            frames.append(im)
        save_trace('register-'+mode,frames,2,800)


def yara_trace():
    for mode,width in [('mobile',352),('wide',720)]:
        frames=[]
        for i in range(32):
            im=Image.new('RGB',(width,170),INK)
            d=ImageDraw.Draw(im)
            label(d,(14,13),'YARA / BYTE MATCH',23,WHITE,True,True)
            for j,value in enumerate(('00','4D','5A','00','4C','41','42','00')):
                x=13+j*((width-24)//8)
                active=4<=j<=6 if i>=20 else j==i//3
                d.rectangle((x,58,x+(width-24)//8-5,97),fill=LIME if active else '#20301a')
                label(d,(x+5,67),value,20,INK if active else WHITE,True,True)
            label(d,(14,120),'MATCH: LAB' if i>=20 else 'Scanning for LAB',22,LIME,True,True)
            frames.append(im)
        save_trace('byte-scan-'+mode,frames,-1,160)


if __name__ == '__main__':
    hero()
    analysis_demos()
    disassembly()
    cards()
    yara_trace()
