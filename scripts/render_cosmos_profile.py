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

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'

BG = '#08090a'
SURFACE = '#111215'
TEXT = '#f2f2f2'
MUTED = '#b4b6ba'
DIM = '#a3a3a3'
ACCENT = '#bef264'
LIME = '#a3e635'

_IMAGE_CACHE: dict[tuple[str, int, int], str] = {}


def encode_backdrop(asset_name: str, width: int, height: int, quality: int = 84) -> str:
    """Resize and JPEG-encode a space raster asset to keep SVGs crisp and lightweight."""
    key = (asset_name, width, height)
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]
    with Image.open(ASSETS / asset_name) as img:
        rgb = img.convert('RGB')
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
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" class="{"mono" if mono else "ui"}" {extra}>{escape(value)}</text>'


def field(width, height, seed, count=110):
    rng = random.Random(seed)
    stars = []
    palette = ['#d7ffe3', '#96e6b3', '#bef264', '#b7f34a', '#7da88d']
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
    palette = ['#d7ffe3', '#65d993', '#bef264', '#a3e635', '#9cc9ad']
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
        f'<circle r="{radius}" fill="url(#planet)" stroke="#bef264" stroke-opacity=".28" stroke-width=".9"/>'
        f'<ellipse rx="{radius * 1.48:.1f}" ry="{radius * 0.3:.1f}" fill="none" stroke="#a3e635" stroke-opacity=".24" stroke-width="1" transform="rotate(-16)"/>'
        f'<ellipse rx="{radius * 1.65:.1f}" ry="{radius * 0.34:.1f}" fill="none" stroke="#bef264" stroke-opacity=".13" stroke-width=".7" stroke-dasharray="4 7" transform="rotate(-16)"/>'
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
<radialGradient id="nebula"><stop stop-color="#bef264" stop-opacity=".22"/><stop offset=".45" stop-color="#14663d" stop-opacity=".14"/><stop offset="1" stop-color="#08090a" stop-opacity="0"/></radialGradient>
<radialGradient id="nebulaLime"><stop stop-color="#a3e635" stop-opacity=".16"/><stop offset=".48" stop-color="#14532d" stop-opacity=".12"/><stop offset="1" stop-color="#08090a" stop-opacity="0"/></radialGradient>
<radialGradient id="core"><stop stop-color="#efffda" stop-opacity=".95"/><stop offset=".15" stop-color="#c6f5c5" stop-opacity=".7"/><stop offset=".45" stop-color="#bef264" stop-opacity=".18"/><stop offset="1" stop-color="#bef264" stop-opacity="0"/></radialGradient>
<radialGradient id="starGlow"><stop stop-color="#dfffea" stop-opacity=".85"/><stop offset=".18" stop-color="#bef264" stop-opacity=".45"/><stop offset="1" stop-color="#bef264" stop-opacity="0"/></radialGradient>
<linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#08090a"/><stop offset=".6" stop-color="#060c09"/><stop offset="1" stop-color="#08090a"/></linearGradient>
<linearGradient id="panel" x2="1" y2="1"><stop stop-color="#0b1510" stop-opacity=".92"/><stop offset="1" stop-color="#050a07" stop-opacity=".84"/></linearGradient>
<linearGradient id="edge"><stop stop-color="#bef264" stop-opacity=".6"/><stop offset=".55" stop-color="#a3e635" stop-opacity=".28"/><stop offset="1" stop-color="#bef264" stop-opacity="0"/></linearGradient>
<linearGradient id="veil"><stop stop-color="#08090a"/><stop offset=".46" stop-color="#08090a" stop-opacity=".88"/><stop offset=".78" stop-color="#08090a" stop-opacity=".24"/><stop offset="1" stop-color="#08090a" stop-opacity=".08"/></linearGradient>
<linearGradient id="veilStrong"><stop stop-color="#08090a" stop-opacity=".95"/><stop offset=".55" stop-color="#08090a" stop-opacity=".82"/><stop offset="1" stop-color="#08090a" stop-opacity=".5"/></linearGradient>
<linearGradient id="meteor"><stop stop-color="#bef264" stop-opacity="0"/><stop offset="1" stop-color="#e4ffec" stop-opacity=".92"/></linearGradient>
<radialGradient id="planet" cx="26%" cy="18%" r="86%"><stop stop-color="#5d8a6a"/><stop offset=".26" stop-color="#173d2b"/><stop offset=".64" stop-color="#071a11"/><stop offset="1" stop-color="#010503"/></radialGradient>
</defs>'''


def save(name, height, title, description, body, output_dir=ASSETS):
    scenes = {
        'cosmos-header.svg': ('deep-space-lime.png', '.88'),
        'cosmos-about.svg': ('deep-space-planet.jpg', '.95'),
        'cosmos-projects.svg': ('deep-space-nebula.png', '.74'),
        'cosmos-toolkit.svg': ('deep-space-nebula.png', '.42'),
        'cosmos-community.svg': ('deep-space-pulsar.jpg', '.94'),
        'cosmos-ethics.svg': ('deep-space-eclipse.jpg', '.95'),
        'cosmos-connect.svg': ('deep-space-horizon.png', '.85'),
        'cosmos-activity.svg': ('deep-space-comet.jpg', '.92'),
        'github-streak.svg': ('deep-space-supernova.jpg', '.82'),
    }
    if name in scenes:
        asset, strength = scenes[name]
        photo = encode_backdrop(asset, 1000, height)
        backdrop = (
            f'<image class="space-photo" href="data:image/jpeg;base64,{photo}" '
            f'width="1000" height="{height}" preserveAspectRatio="xMidYMid slice" opacity="{strength}"/>'
        )
        clouds = ''
        stars = field(1000, height, name, max(65, int(height * 0.14)))
    else:
        backdrop = f'<rect x=".5" y=".5" width="999" height="{height - 1}" rx="12" fill="url(#bgGrad)" stroke="#173825" stroke-width="1"/>'
        clouds = (
            f'<g class="nebula-drift">'
            f'<ellipse cx="835" cy="{height * 0.48:.1f}" rx="340" ry="{max(140, height * 0.46):.1f}" fill="url(#nebula)" opacity=".7"/>'
            f'<ellipse cx="145" cy="{height * 0.78:.1f}" rx="250" ry="{max(110, height * 0.38):.1f}" fill="url(#nebulaLime)" opacity=".45"/>'
            f'</g>'
        )
        stars = field(1000, height, name, max(75, min(220, int(height * 0.22))))

    meteors = ''
    if name in ('cosmos-header.svg', 'cosmos-projects.svg', 'cosmos-ethics.svg', 'cosmos-activity.svg', 'cosmos-connect.svg'):
        meteors = (
            '<g class="meteor"><path d="M0 0L95 22" stroke="url(#meteor)" stroke-width="1.3"/></g>'
            '<g class="meteor second"><path d="M0 120L70 136" stroke="url(#meteor)" stroke-width="1"/></g>'
        )

    outer_border = f'<rect x=".5" y=".5" width="999" height="{height - 1}" rx="12" fill="none" stroke="#2b2e31" stroke-width="1"/>'
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" '
        f'role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title)}</title>'
        f'<desc id="desc">{escape(description)}</desc>'
        f'{DEFS}<style>{STYLE}</style>'
        f'<rect width="1000" height="{height}" rx="12" fill="{BG}"/>'
        f'{backdrop}{clouds}{stars}{meteors}{body}{outer_border}</svg>'
    )
    (output_dir / name).write_text(svg, encoding='utf-8', newline='\n')


def terminal_chrome(prompt, sector_tag, y=28):
    dots = (
        f'<circle cx="38" cy="{y - 4}" r="3.6" fill="#2c593e"/>'
        f'<circle cx="52" cy="{y - 4}" r="3.6" fill="#214630"/>'
        f'<circle cx="66" cy="{y - 4}" r="3.6" fill="#bef264" opacity=".65"/>'
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
        + text(34, 72, title, 28, TEXT)
        + text(34, 100, detail, 14.5, MUTED)
        + '<path d="M34 118H966" stroke="url(#edge)" stroke-width=".9"/>'
    )


def panel(x, y, width, height):
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="10" fill="url(#panel)" '
        f'stroke="#393d40" stroke-opacity=".85" stroke-width=".9"/>'
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
    body += '<rect width="1000" height="48" fill="#08090a" opacity=".48"/>'
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
    body += '<path class="stream" d="M36 308H520" stroke="#bef264" stroke-opacity=".35"/>'
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
        body += f'<path d="{path}" fill="none" stroke="#225737" stroke-width=".9" opacity=".75"/>'
        body += f'<path class="link-flow" d="{path}" fill="none" stroke="#83efac" stroke-width="1.35" opacity=".75"/>'
    body += galaxy(cx, cy, 0.42, 53, 420)

    for i, (number, name, subtitle, detail, tag) in enumerate(items):
        x = 34 + (i % 2) * 482
        y = 144 + (i // 2) * 214
        body += panel(x, y, 450, 184)
        body += cluster(x + 394, y + 44, 10 + i)
        body += text(x + 22, y + 29, f'{number} / {tag}', 10, LIME if i % 2 else ACCENT, True)
        body += text(x + 22, y + 71, name, 27, TEXT)
        body += text(x + 22, y + 106, subtitle, 15.5, TEXT)
        body += text(x + 22, y + 136, detail, 13.5, MUTED)
        body += f'<path class="stream" d="M{x + 22} {y + 160}h195" stroke="#bef264" opacity=".4"/>'

    body += text(34, 804, '> OPEN-SOURCE SECURITY TOOLS', 10.5, MUTED, True)
    body += text(966, 804, 'STATUS: MAINTAINED', 10, ACCENT, True, 'text-anchor="end"')
    save('cosmos-projects.svg', height, 'Selected projects', '; '.join(f'{a[1]}: {a[2]}' for a in items), body)


def chips(x, y, width, names, highlights=()):
    start = x
    body = ''
    for name in names:
        w = len(name) * 8.1 + 26
        if x + w > start + width:
            x = start
            y += 40
        active = name in highlights
        fill = '#10291b' if active else '#060c08'
        stroke = '#bef264' if active else '#234230'
        color = ACCENT if active else '#bfd6c7'
        body += f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="29" rx="5" fill="{fill}" stroke="{stroke}" stroke-width=".8"/>'
        body += text(round(x + 13, 1), y + 20, name, 13, color, True)
        x += w + 8
    return body, y + 29


def arsenal():
    rows = [
        ('LANGUAGES', ['Rust', 'YARA', 'YARA-X', 'Assembly', 'C', 'C++', 'Python', 'JavaScript']),
        ('DATABASE', ['PostgreSQL']),
        ('PLATFORMS', ['Kali Linux', 'Debian', 'Arch Linux']),
    ]
    body = heading('02', 'ls -la ~/stack', 'Technical stack.', 'Languages, rule engines, and Linux environments I work with.', 'TECH STACK')
    body += panel(34, 143, 932, 174)
    body += cluster(915, 180, 99)
    for i, (label, names) in enumerate(rows):
        y = 164 + i * 47
        body += text(55, y + 20, label, 11, LIME, True)
        body += chips(180, y, 760, names, ['Rust', 'YARA', 'YARA-X', 'C'])[0]
    body += '<path d="M55 352C240 325 420 379 595 352S805 334 945 351" fill="none" stroke="#225737" opacity=".75"/><path class="link-flow" d="M55 352C240 325 420 379 595 352S805 334 945 351" fill="none" stroke="#83efac" opacity=".8"/>'
    body += flare(181, 344, 0.5) + flare(595, 352, 0.55) + flare(866, 342, 0.5)
    save('cosmos-arsenal.svg', 385, 'Languages, rule engines and platforms', '; '.join(a + ': ' + ', '.join(b) for a, b in rows), body)


def toolkit():
    categories = [
        (
            'Recon & OSINT',
            'Discovery · intelligence · digital footprints',
            '~/toolkit/recon',
            '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><path d="M12 12l6.5-6.5"/>',
            'Nmap,Shodan,theHarvester,Maltego,Tor,Amass,Recon-ng,SpiderFoot,Sherlock',
        ),
        (
            'Web security',
            'Application testing · auditing · assessment',
            '~/toolkit/web',
            '<path d="m12 2 8 4v6c0 5-8 10-8 10S4 17 4 12V6Z"/><path d="m8.5 12 2.5 2.5 4.5-5.5"/>',
            'Burp Suite,OWASP ZAP,Nikto,sqlmap,Gobuster,ffuf,WPScan,Nuclei,dirsearch',
        ),
        (
            'Offensive security',
            'Authorized testing · adversary simulation',
            '~/toolkit/offense',
            '<circle cx="12" cy="12" r="7.5"/><circle cx="12" cy="12" r="3"/><path d="M12 1.5v4m0 13v4M1.5 12h4m13 0h4"/>',
            'Metasploit,Hashcat,Hydra,John the Ripper,Aircrack-ng,Impacket,NetExec,Responder,BloodHound,Mimikatz,Evil-WinRM',
        ),
        (
            'Defensive analysis',
            'Detection · packet & artifact triage · IR',
            '~/toolkit/defense',
            '<path d="M1.5 12h4l2.8-7.5 4.4 15 2.8-7.5h7"/>',
            'Wireshark,Snort,VirusTotal,Splunk,YARA,YARA-X,tcpdump,Zeek,Suricata,Sysmon,Velociraptor,Volatility,ELK and Elastic,Sigma',
        ),
        (
            'Reverse engineering',
            'Binary inspection · debugging · dynamic instrumentation',
            '~/toolkit/reversing',
            '<path d="m8 6-5.5 6L8 18m8-12 5.5 6L16 18m-2.5-14-3 16"/>',
            'Ghidra,IDA,radare2,Cutter,x64dbg,GDB,Binary Ninja,dnSpy,Frida,objdump,PE-bear,Detect It Easy,HxD,WinDbg,Procmon',
        ),
    ]
    old = ET.parse(ASSETS / 'security-toolkit-v3.svg')
    highlights = [n.text for n in old.iter() if n.tag.endswith('text') and 'hot' in n.get('class', '').split()]
    highlights.append('YARA-X')

    body = '<rect width="1000" height="1068" fill="url(#veilStrong)"/>'
    body += heading('03', 'ls ~/security/toolkit --color=always', 'Security toolkit.', 'Tools across five security domains. Green highlights the ones I use most.', '58 TOOLS // 5 CATEGORIES')

    # Constellation arcs connecting the 5 security domains
    orbit_paths = [
        'M262 280C420 260 580 260 738 280',
        'M262 560C420 540 580 540 738 560',
        'M262 280C230 420 230 560 262 770',
        'M738 280C770 420 770 560 738 770',
    ]
    for op in orbit_paths:
        body += f'<path d="{op}" fill="none" stroke="#1d4d31" stroke-width=".9" opacity=".65"/>'
        body += f'<path class="link-flow" d="{op}" fill="none" stroke="#83efac" stroke-width="1.3" opacity=".7"/>'

    def render_domain_card(idx, x, y, w, h, title, subtitle, path_label, icon_svg, tool_list):
        tools = tool_list.split(',')
        accent_col = LIME if idx in (1, 3) else ACCENT
        inner = panel(x, y, w, h)
        # Left glowing domain accent bar
        inner += f'<rect x="{x}" y="{y + 24}" width="3" height="34" rx="1.5" fill="{accent_col}" opacity=".9"/>'
        # Icon badge
        inner += f'<rect x="{x + 22}" y="{y + 20}" width="40" height="40" rx="10" fill="#06160d" stroke="#235437" stroke-width=".9"/>'
        inner += (
            f'<g transform="translate({x + 30} {y + 28})" fill="none" stroke="{accent_col}" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{icon_svg}</g>'
        )
        inner += text(x + 74, y + 37, title, 18.5, TEXT)
        inner += text(x + 74, y + 56, f'{len(tools):02d} TOOLS  ·  {path_label}', 10.5, accent_col, True)
        inner += text(x + 22, y + 83, subtitle, 12.5, MUTED)
        inner += cluster(x + w - 34, y + 32, 70 + idx)

        # Animated scanner line
        line_w = w - 44
        inner += f'<path d="M{x + 22} {y + 98}H{x + w - 22}" stroke="#163b25" stroke-width=".9"/>'
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
    body += text(34, footer_y, '> 58 TOOLS ACROSS 5 CATEGORIES', 10.5, MUTED, True)
    body += '<rect x="738" y="' + str(footer_y - 11) + '" width="10" height="10" rx="2.5" fill="#10291b" stroke="#bef264" stroke-width=".9"/>'
    body += text(755, footer_y, 'PRIMARY', 10, ACCENT, True)
    body += '<rect x="838" y="' + str(footer_y - 11) + '" width="10" height="10" rx="2.5" fill="#060c08" stroke="#234230" stroke-width=".9"/>'
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
    body = heading('04', 'cat ~/learning.md', 'Focus & learning.', 'Areas I currently work on and topics I am studying next.', 'FOCUS')
    for idx, (x, label, lines) in enumerate(columns):
        body += panel(x, 144, 450, 247)
        body += cluster(x + 412, 174, 41 + idx)
        body += text(x + 22, 176, label, 11, LIME if idx else ACCENT, True)
        for i, value in enumerate(lines):
            body += f'<circle cx="{x + 24}" cy="{208 + i * 28}" r="1.8" fill="#bef264"/>'
            body += text(x + 38, 213 + i * 28, value, 15.5, MUTED)
    body += '<path d="M58 435C230 397 342 482 501 438S784 396 941 433" fill="none" stroke="#225737" stroke-width="1"/><path class="link-flow" d="M58 435C230 397 342 482 501 438S784 396 941 433" fill="none" stroke="#a4efbd" stroke-width="1.3"/>'
    body += flare(129, 426, 0.65) + flare(501, 438, 0.75) + flare(882, 420, 0.55)
    body += text(34, 487, '> HANDS-ON PRACTICE · CONTINUOUS LEARNING', 10.5, MUTED, True)
    save('cosmos-focus.svg', 512, 'Focus and learning', '; '.join(label + ': ' + ', '.join(lines) for _, label, lines in columns), body)


def certifications():
    items = [
        ('Siber Vatan', 'Certificate verification', 'Sanayi ve Teknoloji Bakanlığı'),
        ('Cisco', 'Introduction to Cybersecurity', 'Credly verified badge'),
        ('Cisco', 'Network Defense', 'Credly verified badge'),
        ('Cisco', 'Cyber Threat Management', 'Credly verified badge'),
    ]
    body = heading('05', 'ls ~/credentials', 'Certifications.', 'Verified certificates and training badges. Links are listed below.', '4 VERIFIED')
    for i, (issuer, name, source) in enumerate(items):
        x = 34 + (i % 2) * 482
        y = 144 + (i // 2) * 158
        body += panel(x, y, 450, 133) + cluster(x + 394, y + 39, 50 + i)
        body += text(x + 21, y + 29, issuer.upper(), 10.5, LIME if i == 0 else ACCENT, True)
        body += text(x + 21, y + 66, name, 20.5, TEXT)
        body += text(x + 21, y + 100, source, 13, MUTED)
    save('cosmos-certifications.svg', 474, 'Certifications', 'Siber Vatan certificate; Cisco Introduction to Cybersecurity; Cisco Network Defense; Cisco Cyber Threat Management.', body)


def community():
    body = '<rect width="1000" height="240" fill="url(#veil)"/>'
    body += terminal_chrome('dRafaleD@github:~$ curl https://hub.xerj.org/contributors/dRafaleD', 'COMMUNITY', 30)
    body += text(34, 86, 'Community contributions.', 29, TEXT)
    body += text(36, 132, 'XERJ Corpus Hub', 20, LIME)
    body += text(36, 165, 'Verified contributor profile / dRafaleD', 15.5, MUTED)
    body += text(36, 208, '> VIEW CONTRIBUTOR PROFILE  →', 10.5, ACCENT, True)
    save('cosmos-community.svg', 240, 'Community contributions', 'XERJ Corpus Hub contributor record for dRafaleD.', body)


def ethics():
    body = '<rect width="1000" height="398" fill="url(#veil)"/>'
    body += heading('06', 'cat /etc/ethics.conf', 'Research ethics.', 'Authorized testing and responsible security research.', 'WHITE HAT')
    body += text(36, 162, 'WHITE HAT // AUTHORIZED RESEARCH ONLY', 11, ACCENT, True)
    body += text(36, 205, 'Test responsibly.', 24, TEXT)
    body += text(36, 242, 'Report ethically. Build securely.', 24, TEXT)
    body += text(36, 290, 'All security research, analysis, and testing is performed', 16.5, MUTED)
    body += text(36, 318, 'strictly within authorized environments.', 16.5, MUTED)
    body += '<path d="M36 358C270 338 398 382 630 355S866 339 966 351" fill="none" stroke="#225737" stroke-width=".9"/><path class="link-flow" d="M36 358C270 338 398 382 630 355S866 339 966 351" fill="none" stroke="#84cfa2" stroke-width="1.2" opacity=".8"/>'
    body += flare(490, 363, 0.65)
    save('cosmos-ethics.svg', 398, 'Research ethics', 'White hat security. Authorized research only. Test responsibly. Report ethically. Build securely.', body)


def connect():
    body = f'<rect width="1000" height="196" fill="url(#veil)"/>'
    body += heading('07', './connect --links', 'Connect.', 'Find me on LinkedIn, browse my repositories on GitHub, or visit my portfolio.', 'LINKS')
    body += text(34, 166, '> LINKS BELOW', 10.5, ACCENT, True)
    save('cosmos-connect.svg', 196, 'Connect with Eren Erdoğan', 'LinkedIn: Eren Erdoğan. GitHub: dRafaleD. Portfolio: drafaled.github.io.', body)

    channels = [
        ('linkedin', 'LinkedIn', 'Connect with Eren Erdoğan', 'linkedin.com/in/eren-erdoğan', 'deep-space-lens.jpg'),
        ('github', 'GitHub', 'Explore dRafaleD repositories', 'github.com/dRafaleD', 'deep-space-binary.jpg'),
    ]
    for name, label, detail, sub, backdrop_asset in channels:
        w, h = 490, 160
        photo = encode_backdrop(backdrop_asset, w, h)
        cbody = (
            f'<image class="space-photo" href="data:image/jpeg;base64,{photo}" '
            f'width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" opacity=".92"/>'
        )
        cbody += field(w, h, f'link-{name}', 35)
        cbody += f'<rect width="{w}" height="{h}" fill="url(#veil)"/>'
        cbody += (
            '<circle cx="26" cy="24" r="3.2" fill="#2c593e"/>'
            '<circle cx="38" cy="24" r="3.2" fill="#214630"/>'
            '<circle cx="50" cy="24" r="3.2" fill="#bef264" opacity=".65"/>'
        )
        cbody += text(64, 28, f'> open {name}', 11, ACCENT, True)
        cbody += text(w - 22, 28, f'{label.upper()}', 10, DIM, True, 'text-anchor="end"')
        cbody += text(24, 78, detail, 22, TEXT)
        cbody += text(24, 106, sub, 12.5, MUTED, True)
        cbody += text(24, 138, f'> OPEN {label.upper()}  →', 10.5, ACCENT, True)
        cbody += f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="#2b2e31" stroke-width="1"/>'
        csvg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-labelledby="title desc">'
            f'<title id="title">{escape(label)}</title><desc id="desc">{escape(detail)}</desc>'
            f'{DEFS}<style>{STYLE}</style>'
            f'<rect width="{w}" height="{h}" rx="12" fill="{BG}"/>{cbody}</svg>'
        )
        (ASSETS / f'cosmos-link-{name}.svg').write_text(csvg, encoding='utf-8', newline='\n')


def activity_header():
    body = '<rect width="1000" height="196" fill="url(#veil)"/>'
    body += heading('08', 'git log --stat', 'GitHub activity.', 'Contribution streaks and recent commit activity.', 'ACTIVITY')
    body += '<path d="M35 156C240 112 456 200 696 146S884 131 963 151" fill="none" stroke="#225737" stroke-width=".9"/><path class="link-flow" d="M35 156C240 112 456 200 696 146S884 131 963 151" fill="none" stroke="#9fe1b5" stroke-width="1.2" opacity=".8"/>'
    body += flare(235, 148, 0.6) + flare(645, 155, 0.65)
    save('cosmos-activity.svg', 196, 'GitHub activity', 'GitHub activity, contribution streaks, and contribution graph.', body)


def streak_card(total, current, longest, total_range, current_range, longest_range):
    body = '<rect width="1000" height="327" fill="url(#veilStrong)"/>'
    body += heading('LIVE', 'git activity --summary', 'Contribution summary.', 'Totals and streaks, updated automatically from GitHub activity.', 'SYNCED')
    stats = [
        (f'{total:,}', 'Total contributions', total_range, ACCENT),
        (str(current), 'Current streak', current_range, LIME),
        (str(longest), 'Longest streak', longest_range, ACCENT),
    ]
    for i, (value, label, dates, col) in enumerate(stats):
        x = 34 + i * 316
        body += panel(x, 143, 300, 157)
        body += cluster(x + 258, 175, 200 + i)
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
