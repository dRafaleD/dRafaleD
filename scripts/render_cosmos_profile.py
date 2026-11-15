"""Build the animated Kozmos layout in the profile's original green palette.

Run from any directory with Python 3; no packages or network access required.
Text stays inside opaque panels. Only the header's galaxy uses a gradient.
"""
from html import escape
from pathlib import Path
import math
import random

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
BG, PANEL, LINE = "#070b09", "#0c1410", "#174c2b"
TEXT, MUTED, ACCENT = "#d7ffe3", "#86b697", "#39ff88"


def text(x, y, value, size=18, color=TEXT, mono=False, extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'class="{"mono" if mono else "ui"}" {extra}>{escape(value)}</text>')


def rect(x, y, w, h, fill=PANEL):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{LINE}"/>'


def save(name, height, title, description, body):
    rng = random.Random(name)
    stars = ""
    for i in range(30):
        x, y = rng.uniform(12, 988), rng.uniform(10, height-10)
        stars += f'<circle class="twinkle" style="animation-delay:-{i % 7}s" cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(.5,1.2):.1f}" fill="{ACCENT}" opacity=".24"/>'
    instrument = orbit(936, 35, 15)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<style>
.ui{{font-family:'Segoe UI',Ubuntu,Arial,sans-serif}}.mono{{font-family:Consolas,'DejaVu Sans Mono',monospace}}
.twinkle{{animation:twinkle 7s ease-in-out infinite}}
.orbit{{animation:orbit 28s linear infinite;transform-origin:0px 0px}}
.signal{{stroke-dasharray:3 170;animation:signal 22s linear infinite}}
.drift{{animation:drift 18s ease-in-out infinite}}
@keyframes twinkle{{0%,100%{{opacity:.12}}50%{{opacity:.52}}}}
@keyframes orbit{{to{{transform:rotate(360deg)}}}}
@keyframes signal{{to{{stroke-dashoffset:-346}}}}
@keyframes drift{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}
@media(prefers-reduced-motion:reduce){{.twinkle,.orbit,.signal,.drift{{animation:none}}}}
</style>
<rect x=".5" y=".5" width="999" height="{height-1}" rx="6" fill="{BG}" stroke="{LINE}"/>
{stars}{body}{instrument}</svg>'''
    (ASSETS / name).write_text(svg, encoding="utf-8", newline="\n")


def heading(index, title, detail):
    return (text(28, 35, index, 13, ACCENT, True)
            + text(64, 36, title, 19, TEXT, True)
            + text(28, 64, detail, 15, MUTED)
            + f'<path class="signal" d="M28 77H972" stroke="{ACCENT}" opacity=".24"/>')


def orbit(x, y, radius):
    return (f'<g transform="translate({x} {y})" fill="none" stroke="{ACCENT}" stroke-width=".8">'
            f'<circle r="{radius}" opacity=".22"/><ellipse rx="{radius+7}" ry="{radius*.4}" opacity=".25"/>'
            f'<g class="orbit"><circle cx="{radius}" r="2" fill="{ACCENT}" stroke="none"/></g></g>')


def hero():
    body = '''<defs><radialGradient id="core"><stop stop-color="#d7ffe3" stop-opacity=".30"/><stop offset=".35" stop-color="#39ff88" stop-opacity=".10"/><stop offset="1" stop-color="#050a07" stop-opacity="0"/></radialGradient>
<clipPath id="space"><rect x="608" y="49" width="363" height="196" rx="6"/></clipPath></defs>'''
    body += text(28, 30, "MISSION LOG / dRafaleD", 13, ACCENT, True)
    body += f'<path d="M1 48H999" stroke="{LINE}"/>'
    body += '<g clip-path="url(#space)"><rect x="608" y="49" width="363" height="268" fill="#050a07"/>'
    body += '<g class="drift"><ellipse cx="798" cy="151" rx="217" ry="150" fill="url(#core)"/>'
    rng = random.Random(221)
    for _ in range(100):
        x, y = rng.uniform(609, 971), rng.uniform(49, 317)
        body += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(.4,1):.1f}" fill="#86b697" opacity="{rng.uniform(.15,.5):.2f}"/>'
    for _ in range(1700):
        reach = rng.random() ** 1.2
        angle = rng.randrange(4) * math.tau / 4 + reach * 5.4 + rng.gauss(0, .15)
        px, py = math.cos(angle) * reach * 188, math.sin(angle) * reach * 188 * .46
        x = 798 + px * .91 + py * .41
        y = 151 - px * .41 + py * .91
        color = rng.choice(["#d7ffe3", "#86b697", "#39ff88", "#b7f34a"])
        body += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(.35,1):.1f}" fill="{color}" opacity="{rng.uniform(.1,.65):.2f}"/>'
    body += '</g></g>'
    body += text(28, 111, "Follow the signal.", 35, TEXT, True)
    body += text(30, 151, "From unfamiliar binaries to clearer evidence.", 20)
    body += text(30, 183, "A learning journey through code, systems and security.", 17, MUTED)
    body += text(30, 224, "OBSERVE / UNDERSTAND / BUILD", 14, ACCENT, True)
    save("cosmos-header.svg", 262, "Mission log / dRafaleD", "Follow the signal. From unfamiliar binaries to clearer evidence. A learning journey through code, systems and security.", body)


def projects():
    items = [
        ("01", "Banshee", "Offline analysis & evidence bundles", "Inspect artifacts. Preserve the investigation.", "OFFLINE ANALYSIS"),
        ("02", "AsphDex", "Static PE / ELF malware triage", "Explore binaries and explain suspicious signals.", "BINARY TRIAGE"),
        ("03", "FhniX", "Explainable email triage", "Review messages with local-first workflows.", "EMAIL SECURITY"),
        ("04", "The-Trackher", "Own-account OSINT & privacy checks", "Understand and reduce your digital footprint.", "OSINT / PRIVACY"),
    ]
    body = heading("01", "Project constellation", "Four missions in one orbit: inspect the signal, explain it, preserve the evidence.")
    for i, (number, name, subtitle, detail, tag) in enumerate(items):
        x, y = 28 + (i % 2) * 480, 88 + (i // 2) * 169
        body += rect(x, y, 464, 153)
        body += orbit(x+422, y+54, 13)
        body += text(x+18, y+26, number + " / " + tag, 11, ACCENT, True)
        body += text(x+18, y+62, name, 27, TEXT, True)
        body += text(x+18, y+92, subtitle, 17)
        body += text(x+18, y+125, detail, 14, MUTED)
    save("cosmos-projects.svg", 436, "Selected projects", "; ".join(f"{i[1]}: {i[2]}" for i in items), body)


def chips(x, y, width, names, highlights=()):
    start = x
    body = ""
    for name in names:
        w = len(name) * 8.1 + 26
        if x + w > start + width:
            x = start
            y += 40
        active = name in highlights
        body += rect(round(x, 1), y, round(w, 1), 29, "#123020" if active else BG)
        body += text(round(x+13, 1), y+20, name, 13, ACCENT if active else MUTED, True)
        x += w + 8
    return body, y + 29


def arsenal():
    body = heading("02", "Engineering deck", "The building blocks aboard my workspace: languages, data and Linux systems.")
    rows = [
        ("LANGUAGES", ["Rust", "YARA", "Assembly", "C", "C++", "Python", "JavaScript"]),
        ("DATABASE", ["PostgreSQL"]),
        ("PLATFORMS", ["Kali Linux", "Debian", "Arch Linux"]),
    ]
    for i, (label, names) in enumerate(rows):
        y = 91 + i*49
        body += text(28, y+20, label, 12, ACCENT, True)
        body += chips(177, y, 795, names)[0]
    save("cosmos-arsenal.svg", 249, "Technical arsenal", "; ".join(label+": "+", ".join(names) for label, names in rows), body)


def toolkit():
    categories = [
        ("Recon & OSINT", "Nmap,Shodan,theHarvester,Maltego,Tor,Amass,Recon-ng,SpiderFoot,Sherlock"),
        ("Web security", "Burp Suite,OWASP ZAP,Nikto,sqlmap,Gobuster,ffuf,WPScan,Nuclei,dirsearch"),
        ("Offensive security", "Metasploit,Hashcat,Hydra,John the Ripper,Aircrack-ng,Impacket,NetExec,Responder,BloodHound,Mimikatz,Evil-WinRM"),
        ("Defensive analysis", "Wireshark,Snort,VirusTotal,Splunk,YARA,tcpdump,Zeek,Suricata,Sysmon,Velociraptor,Volatility,ELK and Elastic,Sigma"),
        ("Reverse engineering", "Ghidra,IDA,radare2,Cutter,x64dbg,GDB,Binary Ninja,dnSpy,Frida,objdump,PE-bear,Detect It Easy,HxD,WinDbg,Procmon"),
    ]
    # Preserve the user's existing highlighted tools.
    import xml.etree.ElementTree as ET
    old = ET.parse(ASSETS / "security-toolkit-v3.svg")
    highlights = [n.text for n in old.iter() if n.tag.endswith("text") and "hot" in n.get("class", "").split()]
    body = heading("03", "Instrument bay", "Tools for navigating the security landscape. Green marks my most-used instruments.")
    y = 88
    for label, names in categories:
        labels, bottom = chips(48, y+48, 904, names.split(","), highlights)
        body += rect(28, y, 944, bottom-y+18)
        body += text(48, y+29, label, 17, TEXT, True) + labels
        y = bottom+32
    save("cosmos-toolkit.svg", y+14, "Security toolkit", "; ".join(label+": "+names for label, names in categories), body)


def focus():
    body = heading("04", "Flight plan", "Current coordinates and the next frontiers in my security learning journey.")
    columns = [
        (28, "~/security/focus.txt", ["Web security & penetration testing", "Vulnerability assessment & code review", "OSINT & digital-footprint security", "Malware, reverse engineering & binaries", "Cryptography fundamentals", "Linux, networks & backend development"]),
        (508, "~/security/learning.txt", ["Advanced web application security", "Malware analysis & reverse engineering", "Linux hardening & network security", "Secure APIs & backend architecture"]),
    ]
    for x, label, lines in columns:
        body += rect(x, 88, 464, 246)
        body += text(x+18, 119, label, 14, ACCENT, True)
        body += f'<path d="M{x+18} 136h428" stroke="{LINE}"/>'
        for i, value in enumerate(lines):
            body += text(x+18, 166+i*28, "›", 16, ACCENT)
            body += text(x+36, 166+i*28, value, 16, MUTED)
    save("cosmos-focus.svg", 362, "Focus and learning", "; ".join(label+": "+", ".join(lines) for _, label, lines in columns), body)


if __name__ == "__main__":
    hero()
    projects()
    arsenal()
    toolkit()
    focus()
    print("Rendered five Kozmos profile assets.")
