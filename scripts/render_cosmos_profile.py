"""Render a cosmic deep-space + subtle terminal GitHub profile as self-contained animated SVGs.

No JavaScript, external fonts, or network services are required at render time.
The top animated profile terminal (assets/profile-terminal-v2.gif) is completely
independent and is never modified by this renderer.
"""
from html import escape
from io import BytesIO
from pathlib import Path
import base64
import math
import random
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'

BG = '#000000'
SURFACE = '#000000'
TEXT = '#edf1e9'
MUTED = '#c5c8c0'
DIM = '#a7ada2'
ACCENT = '#a8cf98'
LIME = '#82ed30'

_IMAGE_CACHE: dict[tuple[str, int, int], str] = {}


def cosmos_photo(image):
    """Grade photographic backdrops with the display theme's cold stellar colors."""
    from PIL import ImageOps
    return ImageOps.colorize(image.convert('L'), '#050608', '#f2f5f9', mid='#627e9b')


def encode_backdrop(asset_name: str, width: int, height: int, quality: int = 84) -> str:
    """Resize and JPEG-encode a space raster asset to keep SVGs crisp and lightweight."""
    from PIL import Image
    key = (asset_name, width, height)
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]
    with Image.open(ASSETS / asset_name) as img:
        rgb = cosmos_photo(img)
        src_w, src_h = rgb.size
        target_ratio = width / height
        src_ratio = src_w / src_h
        if src_ratio > target_ratio:
            crop_w = int(src_h * target_ratio)
            left = (src_w - crop_w) // 2
            rgb = rgb.crop((left, 0, left + crop_w, src_h))
        else:
            crop_h = int(src_w / target_ratio)
            top = (src_h - crop_h) // 2
            rgb = rgb.crop((0, top, src_w, top + crop_h))
        resized = rgb.resize((width, height), Image.Resampling.LANCZOS)
        buf = BytesIO()
        resized.save(buf, format='JPEG', quality=quality, optimize=True, progressive=True)
        encoded = base64.b64encode(buf.getvalue()).decode('ascii')
    _IMAGE_CACHE[key] = encoded
    return encoded


def text(x, y, value, size=18, color=TEXT, mono=False, extra=''):
    return f'<text x="{x}" y="{y}" font-size="{round(size * 1.06, 2) if size < 14 else size}" fill="{color}" class="{"mono" if mono else "ui"}" {extra}>{escape(value)}</text>'


def field(width, height, seed, count=110):
    rng = random.Random(seed)
    stars = []
    palette = ['#d7ffe3', '#96e6b3', '#a8cf98', '#b7f34a', '#7da88d']
    for i in range(count):
        x = rng.uniform(8, width - 8)
        y = rng.uniform(8, height - 8)
        r = rng.uniform(0.35, 1.35)
        color = rng.choice(palette)
        opacity = rng.uniform(0.18, 0.78)
        stars.append(
            f'<circle class="star s{i % 3}" cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" '
            f'fill="{color}" opacity="{opacity:.2f}"/>'
        )
    return ''.join(stars)


def flare(x, y, size=1):
    return (
        f'<g transform="translate({x} {y}) scale({size})">'
        '<circle class="breathe" r="18" fill="url(#starGlow)"/>'
        '<path d="M-9 0H9M0-9V9" stroke="#a2f7bd" stroke-width=".65" opacity=".75"/>'
        '<circle r="1.8" fill="#eaffef"/></g>'
    )


def galaxy(x, y, scale=1, seed=31, particles=900):
    rng = random.Random(seed)
    dust = []
    palette = ['#d7ffe3', '#65d993', '#a8cf98', '#82ed30', '#9cc9ad']
    for i in range(particles):
        reach = rng.random() ** 0.72
        angle = (i % 4) * math.tau / 4 + reach * 6.5 + rng.gauss(0, 0.16 + 0.12 * (1 - reach))
        distance = reach * 200
        px = math.cos(angle) * distance
        py = math.sin(angle) * distance
        color = rng.choice(palette)
        r = rng.uniform(0.35, 1.25)
        op = rng.uniform(0.16, 0.85) * (1 - reach * 0.48)
        dust.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.2f}" fill="{color}" opacity="{op:.2f}"/>')
    return (
        f'<g transform="translate({x} {y}) scale({scale})">'
        '<ellipse class="breathe" rx="265" ry="132" fill="url(#nebula)" transform="rotate(-22)"/>'
        '<g transform="rotate(-22) scale(1 .46)"><g class="galaxy-spin">'
        + ''.join(dust)
        + '</g></g>'
        '<ellipse rx="54" ry="24" fill="url(#core)" transform="rotate(-22)"/>'
        '<ellipse rx="12" ry="5.5" fill="url(#core)" transform="rotate(-22)"/></g>'
    )


def cluster(x, y, seed):
    rng = random.Random(seed)
    dots = []
    for _ in range(28):
        angle = rng.random() * math.tau
        radius = (rng.random() ** 1.45) * 38
        cx = x + math.cos(angle) * radius
        cy = y + math.sin(angle) * radius * 0.55
        dots.append(
            f'<circle class="star s{rng.randrange(3)}" cx="{cx:.1f}" cy="{cy:.1f}" '
            f'r="{rng.uniform(0.35, 0.95):.1f}" fill="#b6e8c8" opacity=".52"/>'
        )
    return ''.join(dots) + flare(x, y, 0.55)


def planet(x, y, radius):
    return (
        f'<g transform="translate({x} {y})">'
        f'<circle class="breathe" r="{radius + 26}" fill="url(#nebula)"/>'
        f'<circle r="{radius}" fill="url(#planet)" stroke="#a8cf98" stroke-opacity=".28" stroke-width=".9"/>'
        f'<ellipse rx="{radius * 1.48:.1f}" ry="{radius * 0.3:.1f}" fill="none" stroke="#82ed30" stroke-opacity=".24" stroke-width="1" transform="rotate(-16)"/>'
        f'<ellipse rx="{radius * 1.65:.1f}" ry="{radius * 0.34:.1f}" fill="none" stroke="#a8cf98" stroke-opacity=".13" stroke-width=".7" stroke-dasharray="4 7" transform="rotate(-16)"/>'
        '</g>'
    )


STYLE = '''
.space-photo{animation:spaceDrift 22s ease-in-out infinite;transform-origin:75% 50%}
@keyframes spaceDrift{0%,100%{transform:scale(1)}50%{transform:translate(-8px,-3px) scale(1.045)}}
.ui{font-family:'Segoe UI',Ubuntu,Arial,sans-serif}
.mono{font-family:Consolas,'DejaVu Sans Mono',monospace;letter-spacing:.4px}
.star{animation:twinkle 5.5s ease-in-out infinite}
.s1{animation-delay:-1.9s;animation-duration:7.2s}
.s2{animation-delay:-3.8s;animation-duration:9.4s}
.galaxy-spin{animation:spin 100s linear infinite;transform-origin:0 0}
.breathe{animation:breathe 8s ease-in-out infinite}
.nebula-drift{animation:nebulaDrift 26s ease-in-out infinite}
.stream{stroke-dasharray:3 16;animation:stream 14s linear infinite}
.link-flow{stroke-dasharray:2 84;animation:stream 7.5s linear infinite}
.cursor{animation:blink 1.15s steps(2,start) infinite}
.scan{animation:scan 9s linear infinite;opacity:.75}
.meteor{animation:meteor 14s linear infinite}
.meteor.second{animation-delay:-7.5s;animation-duration:21s}
@keyframes twinkle{0%,100%{opacity:.16}50%{opacity:.86}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes breathe{0%,100%{opacity:.52}50%{opacity:1}}
@keyframes nebulaDrift{0%,100%{transform:translate(0,0)}50%{transform:translate(-14px,6px)}}
@keyframes stream{to{stroke-dashoffset:-328}}
@keyframes blink{0%,49%{opacity:.95}50%,100%{opacity:0}}
@keyframes scan{0%{transform:translateX(0);opacity:0}10%{opacity:.85}90%{opacity:.85}100%{transform:translateX(var(--end,360px));opacity:0}}
@keyframes meteor{0%,72%{opacity:0;transform:translate(-100px,-30px)}74%{opacity:.85}86%,100%{opacity:0;transform:translate(1160px,240px)}}
@media(prefers-reduced-motion:reduce){.space-photo,.star,.galaxy-spin,.breathe,.nebula-drift,.stream,.link-flow,.cursor,.scan,.meteor{animation:none}.meteor{opacity:0}}
'''

DEFS = '''<defs>
<radialGradient id="nebula"><stop stop-color="#a8cf98" stop-opacity=".22"/><stop offset=".45" stop-color="#4a7fa8" stop-opacity=".14"/><stop offset="1" stop-color="#000000" stop-opacity="0"/></radialGradient>
<radialGradient id="nebulaLime"><stop stop-color="#82ed30" stop-opacity=".16"/><stop offset=".48" stop-color="#333d4c" stop-opacity=".12"/><stop offset="1" stop-color="#000000" stop-opacity="0"/></radialGradient>
<radialGradient id="core"><stop stop-color="#efffda" stop-opacity=".95"/><stop offset=".15" stop-color="#c6f5c5" stop-opacity=".7"/><stop offset=".45" stop-color="#a8cf98" stop-opacity=".18"/><stop offset="1" stop-color="#a8cf98" stop-opacity="0"/></radialGradient>
<radialGradient id="starGlow"><stop stop-color="#dfffea" stop-opacity=".85"/><stop offset=".18" stop-color="#a8cf98" stop-opacity=".45"/><stop offset="1" stop-color="#a8cf98" stop-opacity="0"/></radialGradient>
<linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#000000"/><stop offset=".6" stop-color="#000000"/><stop offset="1" stop-color="#000000"/></linearGradient>
<linearGradient id="panel" x2="1" y2="1"><stop stop-color="#1b1e23" stop-opacity=".92"/><stop offset="1" stop-color="#000000" stop-opacity=".84"/></linearGradient>
<linearGradient id="edge"><stop stop-color="#a8cf98" stop-opacity=".6"/><stop offset=".55" stop-color="#82ed30" stop-opacity=".28"/><stop offset="1" stop-color="#a8cf98" stop-opacity="0"/></linearGradient>
<linearGradient id="veil"><stop stop-color="#000000"/><stop offset=".46" stop-color="#000000" stop-opacity=".88"/><stop offset=".78" stop-color="#000000" stop-opacity=".24"/><stop offset="1" stop-color="#000000" stop-opacity=".08"/></linearGradient>
<linearGradient id="veilStrong"><stop stop-color="#000000" stop-opacity=".95"/><stop offset=".55" stop-color="#000000" stop-opacity=".82"/><stop offset="1" stop-color="#000000" stop-opacity=".5"/></linearGradient>
<linearGradient id="meteor"><stop stop-color="#a8cf98" stop-opacity="0"/><stop offset="1" stop-color="#e4ffec" stop-opacity=".92"/></linearGradient>
<radialGradient id="planet" cx="26%" cy="18%" r="86%"><stop stop-color="#5d8a6a"/><stop offset=".26" stop-color="#173d2b"/><stop offset=".64" stop-color="#071a11"/><stop offset="1" stop-color="#010503"/></radialGradient>
</defs>'''


def save(name, height, title, description, body, output_dir=ASSETS):
    outer_border = f'<rect x=".5" y=".5" width="999" height="{height - 1}" rx="12" fill="none" stroke="#2b2e31" stroke-width="1"/>'
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" '
        f'role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title)}</title>'
        f'<desc id="desc">{escape(description)}</desc>'
        f'{DEFS}<style>{STYLE}</style>'
        f'<rect width="1000" height="{height}" rx="12" fill="{BG}"/>'
        f'{body}{outer_border}</svg>'
    )
    (output_dir / name).write_text(svg, encoding='utf-8', newline='\n')


def terminal_chrome(prompt, sector_tag, y=28):
    dots = (
        f'<circle cx="38" cy="{y - 4}" r="3.6" fill="#545963"/>'
        f'<circle cx="52" cy="{y - 4}" r="3.6" fill="#263522"/>'
        f'<circle cx="66" cy="{y - 4}" r="3.6" fill="#a8cf98" opacity=".65"/>'
    )
    return (
        dots
        + text(82, y, prompt, 11.5, ACCENT, True)
        + text(966, y, sector_tag, 10, DIM, True, 'text-anchor="end"')
    )


def heading(index, command, title, detail, sector_tag=None):
    tag = sector_tag or f'SECTION {index}'
    return (
        terminal_chrome(f'dRafaleD@github:~$ {command}', tag, 30)
        + text(34, 72, title, 28, TEXT, True)
        + text(34, 100, detail, 14.5, MUTED)
        + '<path d="M34 118H966" stroke="url(#edge)" stroke-width=".9"/>'
    )


def panel(x, y, width, height):
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="6" fill="#000000" '
        f'stroke="#263522" stroke-opacity=".85" stroke-width=".9"/>'
        f'<path d="M{x + 14} {y + .5}H{x + width - 14}" stroke="url(#edge)" stroke-width=".9"/>'
    )


def hero():
    body = '<rect width="1000" height="398" fill="url(#veil)"/>'
    body += text(48, 53, 'dRafaleD@linux ~ $ whoami', 16, ACCENT, True)
    body += text(44, 155, 'Eren', 90, TEXT, extra='font-weight="700" letter-spacing="-4"')
    body += text(44, 243, 'Erdoğan.', 90, TEXT, extra='font-weight="700" letter-spacing="-4"')
    body += text(49, 289, 'I build tools for reading binaries and tracing evidence.', 19, TEXT)
    body += '<path d="M48 324H950" stroke="url(#edge)"/>'
    body += text(49, 361, 'Rust  /  YARA-X  /  C', 15, ACCENT, True)
    body += text(950, 361, 'Eskişehir, TR', 15, TEXT, True, 'text-anchor="end"')
    save('cosmos-header.svg', 398, 'Eren Erdoğan · dRafaleD',
         'Local-first security tools, binary analysis and detection engineering.', body)


def about():
    body = '<rect width="1000" height="368" fill="url(#veil)"/>'
    body += '<rect width="1000" height="48" fill="#000000" opacity=".48"/>'
    body += heading('00', 'cat about.md', 'About me.', 'Eren Erdoğan · Backend development student & security developer', 'PROFILE')
    lines = [
        'I study backend development and work on cybersecurity, Linux systems,',
        'and secure software engineering. My tools focus on verifiable,',
        'local-first analysis across binaries, emails, timelines, and traffic.',
        'Through practical projects and security labs, I work on malware triage,',
        'digital forensics, OSINT, penetration testing, and backend architecture.',
    ]
    for i, line in enumerate(lines):
        body += text(36, 158 + i * 30, line, 16.5, MUTED)
    body += '<path class="stream" d="M36 308H520" stroke="#a8cf98" stroke-opacity=".35"/>'
    body += text(36, 340, '> CURIOUS BY NATURE · PRACTICAL BY DESIGN', 10.5, ACCENT, True)
    save('cosmos-about.svg', 368, 'About Eren Erdoğan', ' '.join(lines), body)


def projects():
    items = [
        ('01', 'Banshee', 'Offline security analysis & evidence bundles', 'Decode artifacts, inspect PE/ELF, preserve findings.', 'RUST · OFFLINE ANALYSIS'),
        ('02', 'AsphDex', 'Static PE / ELF malware triage', 'Strings, entropy, YARA & IOC extraction — no execution.', 'JS / RUST · BINARY TRIAGE'),
        ('03', 'FhniX', 'Explainable phishing email triage', 'Desktop GUI, folder reports, IMAP scans & local ML.', 'PYTHON · EMAIL SECURITY'),
        ('04', 'The-Trackher', 'Digital footprint & own-account OSINT', 'Inspect exposed data and reduce privacy surface.', 'PYTHON · OSINT / PRIVACY'),
        ('05', 'sentinel-security', 'Linux MACB timeline forensic scanner', 'Live filesystem & TSK disk image artifact timelines.', 'RUST · LINUX FORENSICS'),
        ('06', 'flowscope', 'Offline PCAP / PCAPNG traffic analyzer', 'DNS, HTTP, TLS fingerprints, scan & beacon heuristics.', 'PYTHON · NETWORK TRIAGE'),
    ]
    height = 835
    body = f'<rect width="1000" height="{height}" fill="url(#veilStrong)"/>'
    body += heading('01', 'ls -la ~/projects', 'Selected projects.', 'Six local-first security tools built for analysis, triage, and forensics.', '6 PROJECTS')

    # Constellation network connecting all 6 project nodes around a central core
    cx, cy = 500, 446
    nodes = [
        (259, 232), (741, 232),
        (259, 446), (741, 446),
        (259, 660), (741, 660),
    ]
    paths = [
        f'M{nodes[0][0]} {nodes[0][1]} C370 232 400 {cy} {cx} {cy}',
        f'M{nodes[1][0]} {nodes[1][1]} C630 232 600 {cy} {cx} {cy}',
        f'M{nodes[2][0]} {nodes[2][1]} L{cx} {cy}',
        f'M{nodes[3][0]} {nodes[3][1]} L{cx} {cy}',
        f'M{nodes[4][0]} {nodes[4][1]} C370 660 400 {cy} {cx} {cy}',
        f'M{nodes[5][0]} {nodes[5][1]} C630 660 600 {cy} {cx} {cy}',
        f'M{nodes[0][0]} {nodes[0][1]} C232 340 232 550 {nodes[4][0]} {nodes[4][1]}',
        f'M{nodes[1][0]} {nodes[1][1]} C768 340 768 550 {nodes[5][0]} {nodes[5][1]}',
    ]
    for path in paths:
        body += f'<path d="{path}" fill="none" stroke="#3a4959" stroke-width=".9" opacity=".75"/>'
        body += f'<path class="link-flow" d="{path}" fill="none" stroke="#a8cf98" stroke-width="1.35" opacity=".75"/>'

    for i, (number, name, subtitle, detail, tag) in enumerate(items):
        x = 34 + (i % 2) * 482
        y = 144 + (i // 2) * 214
        body += panel(x, y, 450, 184)
        body += text(x + 22, y + 29, f'{number} / {tag}', 10, LIME if i % 2 else ACCENT, True)
        body += text(x + 22, y + 71, name, 27, TEXT)
        body += text(x + 22, y + 106, subtitle, 15.5, TEXT)
        body += text(x + 22, y + 136, detail, 13.5, MUTED)
        body += f'<path class="stream" d="M{x + 22} {y + 160}h195" stroke="#a8cf98" opacity=".4"/>'

    body += text(34, 804, '> OPEN-SOURCE SECURITY TOOLS', 10.5, MUTED, True)
    body += text(966, 804, 'STATUS: MAINTAINED', 10, ACCENT, True, 'text-anchor="end"')
    save('cosmos-projects.svg', height, 'Selected projects', '; '.join(f'{a[1]}: {a[2]}' for a in items), body)


def chips(x, y, width, names, highlights=()):
    start = x
    body = ''
    for name in names:
        w = len(name) * 8.9 + 22
        if x + w > start + width:
            x = start
            y += 40
        active = name in highlights
        fill = '#121c0e' if active else '#000000'
        stroke = '#a8cf98' if active else '#263522'
        color = LIME if active else '#edf1e9'
        body += f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="29" rx="5" fill="{fill}" stroke="{stroke}" stroke-width=".8"/>'
        body += text(round(x + 13, 1), y + 20, name, 14.5, color, True)
        x += w + 8
    return body, y + 29


def readable_cards(name, title, groups, highlights=()):
    """Flow each section to its actual reading width, including wrapped tool chips."""
    import textwrap
    for mode, width in [('mobile', 384)]:
        title_lines = textwrap.wrap(title, int((width-32)/18))
        parts = [text(16, 42+i*35, line, 29, TEXT, True) for i,line in enumerate(title_lines)]
        y = 68 + (len(title_lines)-1)*35
        for heading_text, lines, tools, icon in groups:
            top = y
            x = 22
            content = ''
            if icon:
                content += pixel_icon(x, y+18, icon, LIME)
                x += 36
            for line in textwrap.wrap(heading_text, max(12,int((width-x-20)/14.5))):
                y += 38
                content += text(x, y, line, 24, TEXT, True)
            y += 8
            for line in lines:
                for fragment in textwrap.wrap(line, int((width-48)/10.2)):
                    y += 26
                    content += text(22, y, fragment, 19, MUTED)
            if tools:
                y += 16
                x = 22
                for tool in tools:
                    w = len(tool)*12.3+20
                    if x+w > width-18:
                        x, y = 22, y+44
                    hot = tool in highlights
                    content += f'<rect x="{x}" y="{y}" width="{w}" height="35" rx="4" fill="{BG}" stroke="{LIME if hot else "#45533f"}"/>'
                    content += text(x+10,y+24,tool,19,LIME if hot else TEXT,True)
                    x += w+8
                y += 35
            y += 20
            parts.append(panel(6,top,width-12,y-top)+content)
            y += 12
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {y}">'
               f'<title>{escape(title)}</title>{DEFS}<style>{STYLE}</style>'
               f'<rect width="{width}" height="{y}" fill="{BG}"/>'
               + ''.join(parts) + '</svg>')
        (ASSETS/f'read-{name}-{mode}.svg').write_text(svg, encoding='utf8')


def arsenal():
    rows = [
        ('LANGUAGES', ['Rust', 'YARA', 'YARA-X', 'Assembly', 'C', 'C++', 'Python', 'JavaScript']),
        ('DATABASE', ['PostgreSQL']),
        ('PLATFORMS', ['Kali Linux', 'Debian', 'Arch Linux']),
    ]
    readable_cards('arsenal','Technical stack',[(label.title(), [], tools, None)
                   for label,tools in rows], {'Rust','YARA','YARA-X','C'})

    body = heading('02', 'ls -la ~/stack', 'Technical stack.', 'Languages, rules and Linux.', 'TECH STACK')
    body += panel(34, 143, 932, 174)
    for i, (label, names) in enumerate(rows):
        y = 164 + i * 47
        body += text(55, y + 20, label, 11, LIME, True)
        body += chips(180, y, 760, names, ['Rust', 'YARA', 'YARA-X', 'C'])[0]
    save('cosmos-arsenal.svg', 385, 'Languages, rule engines and platforms', '; '.join(a + ': ' + ', '.join(b) for a, b in rows), body)


def pixel_icon(x, y, rows, color):
    tiles = ''.join(f'M{col} {row}h1v1h-1z' for row, bits in enumerate(rows)
                    for col, bit in enumerate(bits) if bit == '1')
    return f'<path transform="translate({x} {y}) scale(3)" fill="{color}" shape-rendering="crispEdges" d="{tiles}"/>'


def toolkit():
    categories = [
        (
            'Recon & OSINT',
            'Discovery · intelligence · digital footprints',
            '~/toolkit/recon',
            '01110000 10001000 10101000 10001000 01110000 00001000 00000100 00000010'.split(),
            'Nmap,Shodan,theHarvester,Maltego,Tor,Amass,Recon-ng,SpiderFoot,Sherlock',
        ),
        (
            'Web security',
            'Application testing · auditing · assessment',
            '~/toolkit/web',
            '00111100 01000010 01000010 11111111 10011001 10011001 10000001 11111111'.split(),
            'Burp Suite,OWASP ZAP,Nikto,sqlmap,Gobuster,ffuf,WPScan,Nuclei,dirsearch',
        ),
        (
            'Offensive security',
            'Authorized testing · adversary simulation',
            '~/toolkit/offense',
            '00011000 00111100 01011010 11100111 11100111 01011010 00111100 00011000'.split(),
            'Metasploit,Hashcat,Hydra,John the Ripper,Aircrack-ng,Impacket,NetExec,Responder,BloodHound,Mimikatz,Evil-WinRM',
        ),
        (
            'Defensive analysis',
            'Detection · packet & artifact triage · IR',
            '~/toolkit/defense',
            '10000001 11111111 10000001 10011001 10100101 01000010 00100100 00011000'.split(),
            'Wireshark,Snort,VirusTotal,Splunk,YARA,YARA-X,tcpdump,Zeek,Suricata,Sysmon,Velociraptor,Volatility,ELK and Elastic,Sigma',
        ),
        (
            'Reverse engineering',
            'Binary inspection · debugging · dynamic instrumentation',
            '~/toolkit/reversing',
            '00100100 01111110 11000011 01011010 11011011 01000010 01111110 00100100'.split(),
            'Ghidra,IDA,radare2,Cutter,x64dbg,GDB,Binary Ninja,dnSpy,Frida,objdump,PE-bear,Detect It Easy,HxD,WinDbg,Procmon',
        ),
    ]
    old = ET.parse(ASSETS / 'security-toolkit-v3.svg')
    highlights = [n.text for n in old.iter() if n.tag.endswith('text') and 'hot' in n.get('class', '').split()]
    highlights.append('YARA-X')

    readable_cards('toolkit','Security toolkit',[
        (title,[subtitle],tools.split(','),icon)
        for title,subtitle,path,icon,tools in categories], highlights)

    body = '<rect width="1000" height="1068" fill="url(#veilStrong)"/>'
    body += heading('03', 'ls ~/security/toolkit --color=always', 'Security toolkit.', 'Green marks my primary tools.', '58 TOOLS // 5 CATEGORIES')

    def render_domain_card(idx, x, y, w, h, title, subtitle, path_label, icon_rows, tool_list):
        tools = tool_list.split(',')
        accent_col = LIME if idx in (1, 3) else ACCENT
        inner = panel(x, y, w, h)
        # Left glowing domain accent bar
        inner += f'<rect x="{x}" y="{y + 24}" width="3" height="34" rx="1.5" fill="{accent_col}" opacity=".9"/>'
        # Icon badge
        inner += f'<rect x="{x + 22}" y="{y + 20}" width="40" height="40" rx="10" fill="#121c0e" stroke="#263522" stroke-width=".9"/>'
        inner += pixel_icon(x+30, y+28, icon_rows, accent_col)
        inner += text(x + 74, y + 37, title, 20, TEXT)
        inner += text(x + 74, y + 56, f'{len(tools):02d} TOOLS  ·  {path_label}', 10.5, accent_col, True)
        inner += text(x + 22, y + 83, subtitle, 14, MUTED)

        # Animated scanner line
        line_w = w - 44
        inner += f'<path d="M{x + 22} {y + 98}H{x + w - 22}" stroke="#263522" stroke-width=".9"/>'
        inner += (
            f'<g class="scan" style="animation-delay:-{idx * 1.8:.1f}s;--end:{line_w - 22}px">'
            f'<rect x="{x + 22}" y="{y + 97}" width="20" height="2" rx="1" fill="{accent_col}" opacity=".35"/>'
            f'<circle cx="{x + 42}" cy="{y + 98}" r="2.1" fill="{accent_col}"/></g>'
        )

        labels, _ = chips(x + 22, y + 114, w - 44, tools, highlights)
        inner += labels
        return inner

    # Row 1: Recon & OSINT (left) + Web security (right)
    row1_h = 258
    body += render_domain_card(0, 34, 144, 454, row1_h, *categories[0])
    body += render_domain_card(1, 512, 144, 454, row1_h, *categories[1])

    # Row 2: Offensive security (left) + Defensive analysis (right)
    row2_y = 144 + row1_h + 24
    row2_h = 310
    body += render_domain_card(2, 34, row2_y, 454, row2_h, *categories[2])
    body += render_domain_card(3, 512, row2_y, 454, row2_h, *categories[3])

    # Row 3: Reverse engineering (full width)
    row3_y = row2_y + row2_h + 24
    row3_h = 212
    body += render_domain_card(4, 34, row3_y, 932, row3_h, *categories[4])

    footer_y = row3_y + row3_h + 34
    body += '<rect x="738" y="' + str(footer_y - 11) + '" width="10" height="10" rx="2.5" fill="#121c0e" stroke="#a8cf98" stroke-width=".9"/>'
    body += text(755, footer_y, 'PRIMARY', 10, ACCENT, True)
    body += '<rect x="838" y="' + str(footer_y - 11) + '" width="10" height="10" rx="2.5" fill="#000000" stroke="#263522" stroke-width=".9"/>'
    body += text(855, footer_y, 'REFERENCE', 10, MUTED, True)

    total_h = footer_y + 26
    body = body.replace('height="1068"', f'height="{total_h}"', 1)
    save('cosmos-toolkit.svg', total_h, 'Security toolkit', '; '.join(a + ': ' + e for a, _, _, _, e in categories), body)


def focus():
    columns = [
        (34, '01 // CURRENT FOCUS', [
            'Web application security & pentesting',
            'Vulnerability assessment & code review',
            'OSINT & digital-footprint security',
            'Malware, reverse engineering & binaries',
            'Applied cryptography fundamentals',
            'Linux systems, networks & secure backend',
        ]),
        (516, '02 // CURRENTLY LEARNING', [
            'Advanced web application security',
            'Malware analysis & reverse engineering',
            'Linux hardening & network forensics',
            'Secure API & backend architecture',
            'Container & cloud security tooling',
        ]),
    ]
    readable_cards('focus','Focus & learning',[
        (label.split('// ')[1].title(), lines, [], None) for _,label,lines in columns])

    body = heading('04', 'cat ~/learning.md', 'Focus & learning.', 'Current work and studies.', 'FOCUS')
    for idx, (x, label, lines) in enumerate(columns):
        body += panel(x, 144, 450, 247)
        symbol = ('11110000 10001000 10100100 10001000 11110000 00000110 00001111 00000110'
                  if idx == 0 else '00000000 11100111 10011001 10011001 10011001 11111111 00011000 00000000')
        body += pixel_icon(x+400, 159, symbol.split(), ACCENT)
        body += text(x + 22, 176, label, 11, LIME if idx else ACCENT, True)
        for i, value in enumerate(lines):
            body += f'<circle cx="{x + 24}" cy="{208 + i * 28}" r="1.8" fill="#a8cf98"/>'
            body += text(x + 38, 213 + i * 28, value, 15.5, MUTED)
    save('cosmos-focus.svg', 512, 'Focus and learning', '; '.join(label + ': ' + ', '.join(lines) for _, label, lines in columns), body)


def certifications():
    items = [
        ('Siber Vatan', 'Certificate verification', 'Sanayi ve Teknoloji Bakanlığı'),
        ('Cisco', 'Introduction to Cybersecurity', 'Credly verified badge'),
        ('Cisco', 'Network Defense', 'Credly verified badge'),
        ('Cisco', 'Cyber Threat Management', 'Credly verified badge'),
    ]
    readable_cards('certifications','Certifications',[
        (name,[issuer,source],[],None) for issuer,name,source in items])

    body = heading('05', 'ls ~/credentials', 'Certifications.', 'Verified training and certificates.', '4 VERIFIED')
    for i, (issuer, name, source) in enumerate(items):
        x = 34 + (i % 2) * 482
        y = 144 + (i // 2) * 158
        body += panel(x, y, 450, 133)
        body += text(x + 21, y + 29, issuer.upper(), 10.5, LIME if i == 0 else ACCENT, True)
        body += text(x + 21, y + 66, name, 20.5, TEXT)
        body += text(x + 21, y + 100, source, 13, MUTED)
    save('cosmos-certifications.svg', 474, 'Certifications', 'Siber Vatan certificate; Cisco Introduction to Cybersecurity; Cisco Network Defense; Cisco Cyber Threat Management.', body)


def community():
    readable_cards('community','Community contributions',[
        ('XERJ Corpus Hub',['Verified contributor profile.'],[],None),
        ('PE signature',['0000   4D 5A   MZ','003C   80 00 00 00','0080   50 45 00 00   PE'],[],None)])

    body = '<rect width="1000" height="240" fill="url(#veil)"/>'
    body += terminal_chrome('dRafaleD@github:~$ curl https://hub.xerj.org/contributors/dRafaleD', 'COMMUNITY', 30)
    body += text(34, 86, 'Community contributions.', 29, TEXT)
    body += text(36, 132, 'XERJ Corpus Hub', 20, LIME)
    body += text(36, 165, 'Verified contributor profile / dRafaleD', 15.5, MUTED)
    body += text(36, 208, '> VIEW CONTRIBUTOR PROFILE  →', 10.5, ACCENT, True)
    body += panel(565, 56, 398, 158)
    body += text(586, 85, 'HEX VIEW   /   PE signature', 16, ACCENT, True)
    for i, (offset, values, ascii_view) in enumerate([
        ('0000', '4D 5A', 'MZ'), ('003C', '80 00 00 00', '....'),
        ('0080', '50 45 00 00', 'PE..')
    ]):
        y = 119 + 32*i
        body += text(586, y, offset, 15, MUTED, True)
        body += text(664, y, values, 16, TEXT, True)
        body += text(886, y, ascii_view, 16, LIME, True)
    save('cosmos-community.svg', 240, 'Community contributions', 'XERJ Corpus Hub contributor record for dRafaleD.', body)


def ethics():
    readable_cards('ethics','Research ethics',[
        ('Authorized research',['Test responsibly. Report ethically. Build securely.',
          'All testing takes place in authorized environments.'],[],None),
        ('Analysis scope',['Isolated sample copy. Read-only inspection.',
          'Execution off. Network offline.'],[],None)])

    body = '<rect width="1000" height="398" fill="url(#veil)"/>'
    body += heading('06', 'cat /etc/ethics.conf', 'Research ethics.', 'Authorized testing and responsible security research.', 'WHITE HAT')
    body += text(36, 162, 'WHITE HAT // AUTHORIZED RESEARCH ONLY', 11, ACCENT, True)
    body += text(36, 205, 'Test responsibly.', 24, TEXT)
    body += text(36, 242, 'Report ethically. Build securely.', 24, TEXT)
    body += text(36, 290, 'All security research, analysis, and testing is performed', 16.5, MUTED)
    body += text(36, 318, 'strictly within authorized environments.', 16.5, MUTED)
    body += panel(574, 144, 392, 213)
    body += text(595, 178, 'ANALYSIS SCOPE', 16, ACCENT, True)
    for i, (key, value) in enumerate([
        ('sample', 'isolated copy'), ('inspection', 'read-only'),
        ('execution', 'off'), ('network', 'offline')
    ]):
        y = 217 + 34*i
        body += text(595, y, key, 16, MUTED, True)
        body += text(755, y, value, 16, LIME if i == 2 else TEXT, True)
    save('cosmos-ethics.svg', 398, 'Research ethics', 'White hat security. Authorized research only. Test responsibly. Report ethically. Build securely.', body)


def connect():
    channels = [
        ('linkedin', 'LinkedIn', 'Connect with Eren Erdoğan', 'in'),
        ('github', 'GitHub', 'Explore my repositories', '>_'),
        ('portfolio', 'Portfolio', 'Visit dRafaleD.github.io', '//'),
    ]
    for name, title, action, icon in channels:
        for mode, width in [('wide', 800), ('mobile', 400)]:
            svg = (
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 96">'
                f'<title>{title} — {action}</title>'
                f'<rect x="1" y="1" width="{width-2}" height="94" rx="6" fill="#000000" stroke="#374a2e"/>'
                '<rect x="15" y="23" width="50" height="50" rx="3" fill="#192711"/>'
                f'<text x="40" y="56" text-anchor="middle" fill="#82ed30" font-family="monospace" font-weight="bold" font-size="24">{escape(icon)}</text>'
                f'<text x="82" y="43" font-family="monospace" font-weight="bold" font-size="30" fill="#edf1e9">{title}</text>'
                f'<text x="82" y="72" font-family="Arial,sans-serif" font-size="21" fill="#edf1e9">{action}</text>'
                f'<path d="M{width-49} 58l19-19m-17 0h17v17" fill="none" stroke="#82ed30" stroke-width="4"/>'
                '</svg>'
            )
            (ASSETS / f'contact-{name}-{mode}.svg').write_text(svg, encoding='utf8')


def activity_header():
    readable_cards('activity','GitHub activity',[
        ('Contribution trace',['Contribution streaks and recent commit activity.'],['entry','decode','return'],None)])

    body = '<rect width="1000" height="196" fill="url(#veil)"/>'
    body += heading('08', 'git log --stat', 'GitHub activity.', 'Contribution streaks and recent commit activity.', 'ACTIVITY')
    body += text(36, 165, 'TRACE VIEW', 13, ACCENT, True)
    for i, step in enumerate(('entry', 'decode', 'return')):
        x = 572 + i*134
        body += panel(x, 137, 113, 38)
        body += text(x+16, 162, step, 16, LIME if i == 1 else TEXT, True)
        if i < 2:
            body += f'<path d="M{x+113} 156h20m-5 -4 5 4 -5 4" fill="none" stroke="{ACCENT}"/>'
    save('cosmos-activity.svg', 196, 'GitHub activity', 'GitHub activity, contribution streaks, and contribution graph.', body)


def streak_card(total, current, longest, total_range, current_range, longest_range):
    body = '<rect width="1000" height="327" fill="url(#veilStrong)"/>'
    body += heading('LIVE', 'git activity --summary', 'Contribution summary.', 'GitHub totals and streaks.', 'SYNCED')
    stats = [
        (f'{total:,}', 'Total contributions', total_range, ACCENT),
        (str(current), 'Current streak', current_range, LIME),
        (str(longest), 'Longest streak', longest_range, ACCENT),
    ]
    readable_cards('streak','Contribution summary',[
        (value+' · '+label,[dates],[],None) for value,label,dates,_ in stats])
    for i, (value, label, dates, col) in enumerate(stats):
        x = 34 + i * 316
        body += panel(x, 143, 300, 157)
        body += text(x + 219, 176, ('COUNT', 'CURRENT', 'MAX')[i], 12, MUTED, True)
        body += text(x + 20, 196, value, 39, col)
        body += text(x + 20, 236, label, 16.5, TEXT)
        body += text(x + 20, 272, dates, 12, MUTED, True)
    save(
        'github-streak.svg',
        327,
        'GitHub contribution streak statistics',
        f'{total} total contributions; {current} current streak; {longest} longest streak. {total_range}; {current_range}; {longest_range}.',
        body,
    )


if __name__ == '__main__':
    hero()
    about()
    projects()
    arsenal()
    toolkit()
    focus()
    certifications()
    community()
    ethics()
    connect()
    activity_header()
    print('Rendered the cosmic-terminal profile SVGs.')
