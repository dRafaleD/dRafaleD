"""Build portable profile SVGs using BilTekMYO's Kozmos palette.

Run from any directory with Python 3; no packages or network access required.
Text stays inside opaque panels. Only the header's galaxy uses a gradient.
"""
from html import escape
from pathlib import Path
import math
import random

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
BG, PANEL, LINE = "#0e0f12", "#15171b", "#272a30"
TEXT, MUTED, ACCENT = "#e4e6ea", "#adb2ba", "#9fc4e8"


def text(x, y, value, size=18, color=TEXT, mono=False, extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'class="{"mono" if mono else "ui"}" {extra}>{escape(value)}</text>')


def rect(x, y, w, h, fill=PANEL):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{LINE}"/>'


def save(name, height, title, description, body):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<style>.ui{{font-family:'Segoe UI',Ubuntu,Arial,sans-serif}}.mono{{font-family:Consolas,'DejaVu Sans Mono',monospace}}</style>
<rect x=".5" y=".5" width="999" height="{height-1}" rx="6" fill="{BG}" stroke="{LINE}"/>
{body}</svg>'''
    (ASSETS / name).write_text(svg, encoding="utf-8", newline="\n")


def heading(index, title, detail):
    return (text(28, 35, index, 13, ACCENT, True)
            + text(64, 36, title, 19, TEXT, True)
            + text(28, 64, detail, 15, MUTED))


def hero():
    body = '''<defs><radialGradient id="core"><stop stop-color="#dfe6f0" stop-opacity=".30"/><stop offset=".35" stop-color="#6fb7e6" stop-opacity=".10"/><stop offset="1" stop-color="#050608" stop-opacity="0"/></radialGradient>
<clipPath id="space"><rect x="608" y="49" width="363" height="268" rx="6"/></clipPath></defs>'''
    body += text(28, 30, "dRafaleD / personal workspace", 13, MUTED, True)
    body += text(970, 30, "KOZMOS", 12, ACCENT, True, 'text-anchor="end"')
    body += f'<path d="M1 48H999" stroke="{LINE}"/>'
    body += '<g clip-path="url(#space)"><rect x="608" y="49" width="363" height="268" fill="#050608"/>'
    body += '<ellipse cx="798" cy="181" rx="217" ry="150" fill="url(#core)"/>'
    rng = random.Random(221)
    for _ in range(100):
        x, y = rng.uniform(609, 971), rng.uniform(49, 317)
        body += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(.4,1):.1f}" fill="#a8b8cc" opacity="{rng.uniform(.15,.5):.2f}"/>'
    for _ in range(1700):
        reach = rng.random() ** 1.2
        angle = rng.randrange(4) * math.tau / 4 + reach * 5.4 + rng.gauss(0, .15)
        px, py = math.cos(angle) * reach * 188, math.sin(angle) * reach * 188 * .46
        x = 798 + px * .91 + py * .41
        y = 181 - px * .41 + py * .91
        color = rng.choice(["#dfe6f0", "#a8b8cc", "#6fb7e6", "#9fd8ff"])
        body += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(.35,1):.1f}" fill="{color}" opacity="{rng.uniform(.1,.65):.2f}"/>'
    body += '</g>'
    body += text(28, 91, "~/whoami", 14, ACCENT, True)
    body += text(28, 143, "Eren Erdoğan", 43, TEXT, True)
    body += text(30, 180, "Backend development student · Security tooling", 19, MUTED)
    body += text(30, 219, "Inspect binaries. Understand systems.", 18)
    body += text(30, 246, "Build practical tools. Keep learning.", 18)
    body += rect(28, 278, 547, 37)
    body += text(42, 302, "REVERSE ENGINEERING  /  MALWARE ANALYSIS  /  LINUX", 12, ACCENT, True)
    body += text(28, 350, "Security is not a product, it's a process.", 14, MUTED, True)
    save("cosmos-header.svg", 376, "Eren Erdoğan / dRafaleD", "Backend development student focused on reverse engineering, malware analysis and security tooling. Kozmos: charcoal panels, ice-blue accents and a quiet galaxy.", body)


def projects():
    items = [
        ("01", "Banshee", "Offline analysis & evidence bundles", "Inspect artifacts. Preserve the investigation.", "OFFLINE ANALYSIS"),
        ("02", "AsphDex", "Static PE / ELF malware triage", "Explore binaries and explain suspicious signals.", "BINARY TRIAGE"),
        ("03", "FhniX", "Explainable email triage", "Review messages with local-first workflows.", "EMAIL SECURITY"),
        ("04", "The-Trackher", "Own-account OSINT & privacy checks", "Understand and reduce your digital footprint.", "OSINT / PRIVACY"),
    ]
    body = heading("01", "Selected projects", "Inspect, explain, preserve. Four areas of ongoing work.")
    for i, (number, name, subtitle, detail, tag) in enumerate(items):
        x, y = 28 + (i % 2) * 480, 88 + (i // 2) * 169
        body += rect(x, y, 464, 153)
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
        body += rect(round(x, 1), y, round(w, 1), 29, "#20262e" if active else BG)
        body += text(round(x+13, 1), y+20, name, 13, ACCENT if active else MUTED, True)
        x += w + 8
    return body, y + 29


def arsenal():
    body = heading("02", "Technical arsenal", "Languages, data and platforms in my learning and development workflow.")
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
    body = heading("03", "Security toolkit", "A working reference. Blue labels indicate the tools I use most.")
    y = 88
    for label, names in categories:
        labels, bottom = chips(48, y+48, 904, names.split(","), highlights)
        body += rect(28, y, 944, bottom-y+18)
        body += text(48, y+29, label, 17, TEXT, True) + labels
        y = bottom+32
    save("cosmos-toolkit.svg", y+14, "Security toolkit", "; ".join(label+": "+names for label, names in categories), body)


def focus():
    body = heading("04", "Focus & learning", "Practical security research alongside secure backend development.")
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
