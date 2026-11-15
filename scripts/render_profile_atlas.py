"""Render the profile atlas as portable, self-contained animated SVG assets."""
from html import escape
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def text(x, y, value, size=18, color="#a5b9ac", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(value)}</text>'


def canvas(height, title, description, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img" aria-labelledby="t d">
<title id="t">{escape(title)}</title><desc id="d">{escape(description)}</desc>
<defs>
 <radialGradient id="halo"><stop stop-color="#39ff88" stop-opacity=".12"/><stop offset="1" stop-color="#39ff88" stop-opacity="0"/></radialGradient>
 <linearGradient id="fade"><stop stop-color="#39ff88" stop-opacity=".55"/><stop offset="1" stop-color="#39ff88" stop-opacity="0"/></linearGradient>
 <filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<style>
text{{font-family:'Segoe UI',Ubuntu,Arial,sans-serif}}
.mono{{font-family:Consolas,'DejaVu Sans Mono',monospace;letter-spacing:1.8px}}
.flow{{stroke-dasharray:3 22;animation:flow 9s linear infinite}}
.orbit{{animation:orbit 60s linear infinite;transform-origin:500px 370px}}
.pulse{{animation:pulse 5s ease-in-out infinite}}
@keyframes flow{{to{{stroke-dashoffset:-250}}}}
@keyframes orbit{{to{{transform:rotate(360deg)}}}}
@keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
@media(prefers-reduced-motion:reduce){{.flow,.orbit,.pulse{{animation:none}}}}
</style>
<rect width="1000" height="{height}" rx="20" fill="#070b09"/>
{body}
</svg>'''


def save(name, height, title, description, body):
    (ASSETS / name).write_text(canvas(height, title, description, body), encoding="utf-8")


# Four research disciplines meet in an animated evidence core. No invented metrics.
body = text(40, 45, "THE RESEARCH ATLAS", 13, "#39ff88", 'class="mono"')
body += text(40, 99, "From signal to evidence.", 43, "#e7ffef", 'font-weight="600"')
body += text(40, 132, "Four projects. One way of thinking: inspect, explain, preserve.", 18)
body += text(960, 45, "OPEN SOURCE / LOCAL FIRST", 10, "#79ad8b", 'class="mono" text-anchor="end"')
body += '<defs><radialGradient id="nebula"><stop stop-color="#39ff88" stop-opacity=".19"/><stop offset=".4" stop-color="#0b713e" stop-opacity=".11"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient></defs>'
body += '<ellipse cx="500" cy="370" rx="360" ry="270" fill="url(#nebula)"/>'
stars = random.Random(48)
for i in range(100):
    sx, sy = stars.uniform(25, 975), stars.uniform(155, 632)
    # Keep the project surfaces clear; stars live in the surrounding space.
    if (40 < sx < 370 or 630 < sx < 960) and (183 < sy < 356 or 441 < sy < 614):
        continue
    radius, opacity = stars.uniform(.5, 1.5), stars.uniform(.16, .55)
    body += f'<circle class="pulse" style="animation-delay:-{i % 5}s" cx="{sx:.1f}" cy="{sy:.1f}" r="{radius:.1f}" fill="#d7ffe3" opacity="{opacity:.2f}"/>'
for x, y in [(40, 183), (630, 183), (40, 441), (630, 441)]:
    body += f'<rect x="{x}" y="{y}" width="330" height="173" rx="16" fill="#030a05" stroke="#164d2b"/>'
    body += f'<path d="M{x+17} {y+36}h296" stroke="#123d22"/>'
    body += f'<circle cx="{x+296}" cy="{y+61}" r="27" fill="#031409"/>'
body += '<ellipse cx="500" cy="370" rx="235" ry="220" fill="url(#halo)"/>'
body += '<g fill="#39ff88" opacity=".2">'
for x, y in [(421,190),(488,207),(558,188),(430,560),(510,588),(575,550),(403,405),(603,414)]:
    body += f'<circle cx="{x}" cy="{y}" r="1.5"/>'
body += '</g>'
paths = ["M370 251C440 251 405 370 500 370", "M630 251C560 251 595 370 500 370", "M370 509C440 509 405 370 500 370", "M630 509C560 509 595 370 500 370"]
for i, p in enumerate(paths):
    body += f'<path d="{p}" fill="none" stroke="#1c422b" stroke-width="1.5"/><path class="flow" style="animation-delay:-{i*2}s" d="{p}" fill="none" stroke="#39ff88" stroke-width="2"/>'
body += '<circle cx="500" cy="370" r="104" fill="none" stroke="#173c25"/><g class="orbit"><circle cx="500" cy="370" r="91" fill="none" stroke="#39ff88" stroke-opacity=".5" stroke-dasharray="38 175 8 175"/><circle cx="500" cy="279" r="4" fill="#b7f34a"/></g>'
body += '<circle cx="500" cy="370" r="115" fill="none" stroke="#28673b" stroke-opacity=".45" stroke-dasharray="1 13"/>'
body += '<g class="orbit" style="animation-duration:80s"><ellipse cx="500" cy="370" rx="139" ry="50" transform="rotate(-28 500 370)" fill="none" stroke="#39ff88" stroke-opacity=".2"/><ellipse cx="500" cy="370" rx="139" ry="50" transform="rotate(28 500 370)" fill="none" stroke="#d7ffe3" stroke-opacity=".12"/></g>'
body += '<path class="pulse" d="m500 312 58 58-58 58-58-58Z" fill="none" stroke="#39ff88" stroke-width="2.5" filter="url(#glow)"/>'
body += '<path d="m500 312 58 58-58 58-58-58Z" fill="#0b1b10" stroke="#39ff88" stroke-opacity=".8"/><path d="m500 325 45 45-45 45-45-45Z" fill="none" stroke="#1b512c"/>'
body += text(500, 368, "EVIDENCE", 15, "#e0ffeb", 'text-anchor="middle" class="mono"')
body += text(500, 390, "LOCAL FIRST", 10, "#75a386", 'text-anchor="middle" class="mono"')
projects = [
 (40, 183, "01", "Banshee", "OFFLINE ANALYSIS", ["Decode values. Inspect files.", "Extract IOCs. Preserve evidence."], "RUST / YARA / ALPHA", 'M7 3h19l9 9v31H7Z M26 3v10h9 M14 23h14 M14 30h14'),
 (630, 183, "02", "AsphDex", "STATIC MALWARE TRIAGE", ["PE/ELF inspection. YARA matches.", "Explain findings. No execution."], "ELECTRON / JS / RUST / YARA", 'm22 2 17 7v13c0 12-17 23-17 23S5 34 5 22V9Z M13 23l7 7 12-16'),
 (40, 441, "03", "FhniX", "EMAIL SECURITY", ["Explainable phishing triage.", "Local scoring. Read-only IMAP."], "PYTHON / DESKTOP & CLI", 'M3 10h39v29H3Z m1 2 19 14 18-14 M4 38l13-14 M41 38 28 24'),
 (630, 441, "04", "The-Trackher", "DIGITAL FOOTPRINT", ["OSINT for your own accounts.", "Breach exposure. Privacy checks."], "PYTHON / PRIVACY & OSINT", 'M23 3v8 M3 23h8 M34 34l12 12 M38 23a15 15 0 1 0-30 0 15 15 0 0 0 30 0 M29 23a6 6 0 1 0-12 0 6 6 0 0 0 12 0'),
]
for x, y, n, name, category, lines, stack, icon in projects:
    body += f'<path d="M{x+1} {y+47}v32" stroke="#39ff88" stroke-width="2" stroke-linecap="round"/>'
    body += text(x+17, y+22, n+" / "+category, 11, "#7fa38a", 'class="mono"')
    body += text(x+17, y+65, name, 32, "#e6ffed", 'font-weight="600"')
    body += f'<g transform="translate({x+275} {y+37})" fill="none" stroke="#39ff88" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"> <path d="{icon}"/></g>'
    for j, line in enumerate(lines):
        body += text(x+17, y+99+j*25, line, 14)
    body += text(x+17, y+154, stack, 10, "#b7f34a", 'class="mono"')
body += '<path d="M40 649H960" stroke="#1b3d27"/>'
body += text(40, 677, "INSPECT", 11, "#76b98c", 'class="mono"')+text(426, 677, "EXPLAIN", 11, "#76b98c", 'class="mono"')+text(870, 677, "PRESERVE", 11, "#76b98c", 'class="mono"')
for old, new in {"#a5b9ac":"#d7ffe3", "#b7f34a":"#39ff88", "#e6ffed":"#39ff88", "#e7ffef":"#d7ffe3", "#7fa38a":"#86b697", "#79ad8b":"#86b697", "#76b98c":"#86b697", "#e0ffeb":"#d7ffe3", "#75a386":"#86b697"}.items():
    body = body.replace(old, new)
body += "<style>text{font-family:'Cascadia Mono','Cascadia Code',Consolas,Menlo,'DejaVu Sans Mono',monospace}</style>"
galaxy = canvas(704, "Research atlas — neon galaxy", "Four local security projects connected by flowing signals around a neon-green evidence core. Banshee, AsphDex, FhniX and The-Trackher.", body)
galaxy = galaxy.replace('rx="20" fill="#070b09"', 'rx="16" fill="#000"')
(ASSETS / "research-atlas-galaxy.svg").write_text(galaxy, encoding="utf-8")

# A single engineering surface replaces stacked miniature terminal windows.
body = text(40, 43, "ENGINEERING BASE", 13, "#39ff88", 'class="mono"')
body += text(40, 86, "Built close to the system.", 32, "#e6ffed", 'font-weight="600"')
groups=[(40,130,"LANGUAGES",["Rust · YARA · Assembly · C · C++", "Python · JavaScript"]), (560,130,"ENVIRONMENTS",["Kali Linux · Debian · Arch Linux", "PostgreSQL"])]
for x,y,title,lines in groups:
    body += f'<path d="M{x} {y-10}h375" stroke="url(#fade)"/>'
    body += text(x,y+20,title,12,"#7da58a",'class="mono"')
    for i,line in enumerate(lines): body += text(x,y+54+i*29,line,21,"#ccebd6")
body += '<circle class="pulse" cx="947" cy="42" r="4" fill="#39ff88"/>'
save("engineering-base.svg", 264, "Engineering base", "Languages: Rust, YARA, Assembly, C, C++, Python, JavaScript. Environments: Kali Linux, Debian, Arch Linux, PostgreSQL.",body)

tool_groups = [
 ("Recon & OSINT",["Nmap · Shodan · theHarvester · Maltego · Tor", "Amass · Recon-ng · SpiderFoot · Sherlock"]),
 ("Web security",["Burp Suite · OWASP ZAP · Nikto · sqlmap · Gobuster", "ffuf · WPScan · Nuclei · dirsearch"]),
 ("Authorized offensive testing",["Metasploit · Hashcat · Hydra · John the Ripper · Aircrack-ng", "Impacket · NetExec · Responder · BloodHound · Mimikatz · Evil-WinRM"]),
 ("Detection & analysis",["Wireshark · Snort · VirusTotal · Splunk · YARA · tcpdump · Zeek", "Suricata · Sysmon · Velociraptor · Volatility · ELK and Elastic · Sigma"]),
 ("Reverse engineering",["Ghidra · IDA · radare2 · Cutter · x64dbg · GDB · Binary Ninja · dnSpy", "Frida · objdump · PE-bear · Detect It Easy · HxD · WinDbg · Procmon"]),
]
body=text(40,43,"INVESTIGATION INSTRUMENTS",13,"#39ff88",'class="mono"')+text(40,87,"Different lenses. Same curiosity.",32,"#e6ffed",'font-weight="600"')
body += '<path d="M49 151V711" stroke="#1c422b" stroke-width="1.5"/><path class="flow" d="M49 151V711" stroke="#39ff88" stroke-width="2" fill="none"/>'
for i,(title,lines) in enumerate(tool_groups):
    y=145+i*133
    body+=f'<circle cx="49" cy="{y+8}" r="8" fill="#070b09" stroke="#39ff88"/><circle class="pulse" style="animation-delay:-{i}s" cx="49" cy="{y+8}" r="3" fill="#b7f34a"/>'
    body+=text(81,y+15,title,24,"#d3f5df",'font-weight="500"')
    for j,line in enumerate(lines):body+=text(81,y+49+j*25,line,18)
    if i<4:body+=f'<path d="M81 {y+98}H950" stroke="#142d1d"/>'
save("investigation-instruments.svg", 820, "Investigation instruments", "All security tools grouped by recon, web security, authorized offensive testing, detection and analysis, and reverse engineering. No hidden sections.", body)
print("Rendered the research atlas, engineering base and investigation instruments.")

# Show research interests beside the learning path, with every topic visible.
body = text(40, 43, "RESEARCH / NEXT HORIZON", 13, "#39ff88", 'class="mono"')
body += text(40, 88, "Curiosity, with a direction.", 34, "#e6ffed", 'font-weight="600"')
body += '<path d="M500 142V420" stroke="#20412c"/><path class="flow" d="M500 142V420" stroke="#39ff88" fill="none" stroke-width="2"/>'
body += text(40, 157, "INVESTIGATING", 12, "#b7f34a", 'class="mono"')
body += text(555, 157, "GOING DEEPER", 12, "#b7f34a", 'class="mono"')
focus = ["Web security & penetration testing", "Vulnerability assessment & code review", "OSINT & digital footprints", "Malware analysis & reverse engineering", "Cryptography & applied security", "Linux, networking & automation"]
learning = ["Advanced web application security", "Malware analysis & reverse engineering", "Linux hardening & network security", "Secure API & backend architecture"]
for i, value in enumerate(focus):
    body += text(40, 201 + i * 35, value, 19)
for i, value in enumerate(learning):
    y = 201 + i * 52
    body += f'<circle cx="561" cy="{y-6}" r="4" fill="#070b09" stroke="#39ff88"/>'
    body += text(580, y, value, 18)
body += '<path d="M40 432H960" stroke="#193723"/><path d="M40 432H240" stroke="#39ff88" stroke-opacity=".4"/>'
body += text(40, 466, "LEARN BY BUILDING. UNDERSTAND BY INVESTIGATING.", 11, "#7fa38a", 'class="mono"')
save("focus-learning-map.svg", 494, "Security focus and current learning", "Research: web security, vulnerability assessment, code review, OSINT, malware analysis, reverse engineering, cryptography, Linux and networking. Learning: advanced web security, malware analysis, Linux hardening and secure backend architecture.", body)
