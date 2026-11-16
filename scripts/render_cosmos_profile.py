"""Render a living green universe as self-contained animated GitHub SVGs.

Space artwork is an embedded generated raster asset. No external runtime is needed. The large
terminal is independent and is never read or changed by this renderer.
"""
from html import escape
from pathlib import Path
import base64
import math
import random
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
BG, TEXT, MUTED, ACCENT = '#000000', '#f2f2f2', '#a3a3a3', '#a3e635'


def text(x, y, value, size=18, color=TEXT, mono=False, extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" class="{"mono" if mono else "ui"}" {extra}>{escape(value)}</text>'


def field(*args, **kwargs):
    return ''


def flare(*args, **kwargs):
    return ''


def galaxy(*args, **kwargs):
    return ''


STYLE = '''
.space-photo{animation:spaceDrift 30s ease-in-out infinite;transform-origin:75% 50%}@keyframes spaceDrift{0%,100%{transform:scale(1)}50%{transform:scale(1.045)}}
.ui{font-family:'Segoe UI',Ubuntu,Arial,sans-serif}.mono{font-family:Consolas,'DejaVu Sans Mono',monospace;letter-spacing:.5px}
.star{animation:twinkle 5s ease-in-out infinite}.s1{animation-delay:-1.8s;animation-duration:7s}.s2{animation-delay:-3.7s;animation-duration:9s}
.galaxy-spin{animation:spin 95s linear infinite;transform-origin:0 0}
.breathe{animation:breathe 8s ease-in-out infinite}
.nebula-drift{animation:nebulaDrift 24s ease-in-out infinite}
.stream{stroke-dasharray:3 18;animation:stream 12s linear infinite}
.link-flow{stroke-dasharray:2 80;animation:stream 7s linear infinite}
.meteor{animation:meteor 13s linear infinite}.meteor.second{animation-delay:-7s;animation-duration:19s}
@keyframes twinkle{0%,100%{opacity:.16}50%{opacity:.8}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes breathe{0%,100%{opacity:.55}50%{opacity:1}}
@keyframes nebulaDrift{0%,100%{transform:translate(0,0)}50%{transform:translate(-15px,7px)}}
@keyframes stream{to{stroke-dashoffset:-328}}
@keyframes meteor{0%,72%{opacity:0;transform:translate(-100px,-30px)}74%{opacity:.8}85%,100%{opacity:0;transform:translate(1150px,240px)}}
@media(prefers-reduced-motion:reduce){.space-photo,.star,.galaxy-spin,.breathe,.nebula-drift,.stream,.link-flow,.meteor{animation:none}.meteor{opacity:0}}
'''
DEFS = '''<defs>
<radialGradient id="nebula"><stop stop-color="#a3e635" stop-opacity=".24"/><stop offset=".42" stop-color="#14663d" stop-opacity=".16"/><stop offset="1" stop-color="#000000" stop-opacity="0"/></radialGradient>
<radialGradient id="core"><stop stop-color="#efffda" stop-opacity=".95"/><stop offset=".12" stop-color="#c6f5c5" stop-opacity=".7"/><stop offset=".42" stop-color="#a3e635" stop-opacity=".18"/><stop offset="1" stop-color="#a3e635" stop-opacity="0"/></radialGradient>
<radialGradient id="starGlow"><stop stop-color="#dfffea" stop-opacity=".85"/><stop offset=".12" stop-color="#a3e635" stop-opacity=".5"/><stop offset="1" stop-color="#a3e635" stop-opacity="0"/></radialGradient>
<linearGradient id="panel" x2="1" y2="1"><stop stop-color="#0a0a0a" stop-opacity=".94"/><stop offset="1" stop-color="#080808" stop-opacity=".82"/></linearGradient>
<linearGradient id="edge"><stop stop-color="#a3e635" stop-opacity=".55"/><stop offset=".55" stop-color="#a3e635" stop-opacity=".2"/><stop offset="1" stop-color="#a3e635" stop-opacity="0"/></linearGradient>
<linearGradient id="veil"><stop stop-color="#000000"/><stop offset=".48" stop-color="#000000" stop-opacity=".9"/><stop offset=".76" stop-color="#000000" stop-opacity="0"/></linearGradient>
<linearGradient id="meteor"><stop stop-color="#a3e635" stop-opacity="0"/><stop offset="1" stop-color="#e4ffec" stop-opacity=".9"/></linearGradient>
<radialGradient id="planet" cx="26%" cy="18%" r="86%"><stop stop-color="#5d8a6a"/><stop offset=".25" stop-color="#173d2b"/><stop offset=".63" stop-color="#071a11"/><stop offset="1" stop-color="#010503"/></radialGradient>
<radialGradient id="fogFade"><stop stop-color="white"/><stop offset=".5" stop-color="white" stop-opacity=".6"/><stop offset="1" stop-color="black"/></radialGradient>
<mask id="fogMask"><ellipse cx="760" cy="200" rx="480" ry="340" fill="url(#fogFade)"/></mask>
<filter id="spaceFog" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".008 .018" numOctaves="3" seed="17"/><feColorMatrix type="matrix" values="0 0 0 0 .06 0 0 0 0 .32 0 0 0 0 .17 0 0 0 .6 0"/></filter>
</defs>'''


def save(name, height, title, description, body, output_dir=ASSETS):
    strength = '.85' if name in ['cosmos-header.svg','cosmos-ethics.svg','cosmos-community.svg'] else '.38'
    photo = base64.b64encode((ASSETS/'deep-space-lime.png').read_bytes()).decode()
    backdrop = f'<image class="space-photo" href="data:image/png;base64,{photo}" width="1000" height="{height}" preserveAspectRatio="xMidYMid slice" opacity="{strength}"/>'
    clouds = ''
    meteors = ''
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>{DEFS}<style>{STYLE}</style>
<rect width="1000" height="{height}" rx="12" fill="{BG}"/>{clouds}{backdrop}{meteors}{body}</svg>'''
    (output_dir/name).write_text(svg,encoding='utf-8',newline='\n')


def heading(index, title, detail):
    return (text(34, 33, f'{index} / DEEP SPACE ARCHIVE', 11, ACCENT, True)
            + text(34, 73, title, 30, TEXT)
            + text(34, 101, detail, 15, MUTED)
            + '<path d="M34 119H966" stroke="url(#edge)" stroke-width=".8"/>')


def panel(x, y, width, height):
    return (f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="9" fill="url(#panel)" stroke="#424242" stroke-opacity=".6" stroke-width=".8"/>'
            f'<path d="M{x+12} {y+.5}H{x+width-12}" stroke="url(#edge)" stroke-width=".8"/>')


def cluster(*args, **kwargs):
    return ''


def planet(*args, **kwargs):
    return ''


def hero():
    body=planet(938,430,167)+galaxy(745,221,1.48,73,2800)
    body+='<rect width="1000" height="410" fill="url(#veil)"/>'
    body+=text(34,39,'dRafaleD / SIGNALS FROM THE UNKNOWN',11,ACCENT,True)
    body+=text(34,123,'Beyond the surface.',43,TEXT)
    body+=text(36,169,'Every binary has a story.',22,TEXT)
    body+=text(36,202,'Every signal is a place to begin.',20,MUTED)
    body+=text(36,254,'Exploring systems, tracing evidence,',17,MUTED)
    body+=text(36,280,'and building tools to make the unknown clearer.',17,MUTED)
    body+='<path class="stream" d="M36 321H425" stroke="#a3e635" stroke-opacity=".4"/>'
    body+=text(36,357,'OBSERVE  /  UNDERSTAND  /  BUILD',11,ACCENT,True)
    body+=text(964,382,'LOCAL TOOLS. WIDER HORIZONS.',10,MUTED,True,'text-anchor="end"')
    save('cosmos-header.svg',410,'Signals from the unknown','An animated, tilted spiral galaxy in green starlight. Exploring systems, tracing evidence, and building tools to make the unknown clearer.',body)


def projects():
    items=[
        ('01','Banshee','Offline analysis & evidence bundles','Inspect artifacts. Preserve the investigation.','OFFLINE ANALYSIS'),
        ('02','AsphDex','Static PE / ELF malware triage','Explore binaries. Explain suspicious signals.','BINARY TRIAGE'),
        ('03','FhniX','Explainable email triage','Review messages with local-first workflows.','EMAIL SECURITY'),
        ('04','The-Trackher','Own-account OSINT & privacy checks','Understand and reduce your digital footprint.','OSINT / PRIVACY'),
    ]
    body=heading('01','A constellation of investigations.','Four projects, connected by curiosity. Follow the signal from one field to the next.')
    paths=['M262 238C370 238 400 349 500 349S641 238 742 238','M262 462C370 462 400 349 500 349S641 462 742 462','M262 238C240 330 240 390 262 462','M742 238C764 330 764 390 742 462']
    for path in paths:
        body+=f'<path d="{path}" fill="none" stroke="#285e3e" stroke-width=".8" opacity=".7"/><path class="link-flow" d="{path}" fill="none" stroke="#83efac" stroke-width="1.3" opacity=".7"/>'
    body+=galaxy(500,349,.44,53,600)
    for i,(number,name,subtitle,detail,tag) in enumerate(items):
        x,y=34+(i%2)*482,144+(i//2)*223
        body+=panel(x,y,450,190)
        body+=cluster(x+390,y+48,number)
        body+=text(x+22,y+29,number+' / '+tag,10,ACCENT,True)
        body+=text(x+22,y+73,name,29,TEXT)
        body+=text(x+22,y+110,subtitle,17,TEXT)
        body+=text(x+22,y+145,detail,14,MUTED)
        body+=f'<path class="stream" d="M{x+22} {y+168}h180" stroke="#4dba79" opacity=".35"/>'
    body+=text(34,593,'INDEPENDENT PROJECTS / ONE CONTINUING EXPLORATION',10,MUTED,True)
    save('cosmos-projects.svg',618,'Project constellation','; '.join(f'{a[1]}: {a[2]}' for a in items),body)


def chips(x,y,width,names,highlights=()):
    start=x
    body=''
    for name in names:
        w=len(name)*8.1+26
        if x+w>start+width:
            x=start;y+=40
        active=name in highlights
        body+=f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="29" rx="5" fill="{"#253015" if active else "#080808"}" stroke="{"#a3e635" if active else "#333333"}" stroke-width=".7"/>'
        body+=text(round(x+13,1),y+20,name,13,ACCENT if active else '#b5b5b5',True)
        x+=w+8
    return body,y+29


def arsenal():
    rows=[('LANGUAGES',['Rust','YARA','YARA-X','Assembly','C','C++','Python','JavaScript']),('DATABASE',['PostgreSQL']),('PLATFORMS',['Kali Linux','Debian','Arch Linux'])]
    body=heading('02','The engineering spectrum.','Languages, rule engines and Linux systems behind the exploration.')
    body+=panel(34,143,932,170)
    for i,(label,names) in enumerate(rows):
        y=162+i*47
        body+=text(55,y+20,label,11,ACCENT,True)+chips(180,y,760,names,['Rust','YARA','YARA-X','C'])[0]
    body+='<path d="M55 348C240 321 420 375 595 348S805 330 945 347" fill="none" stroke="#285e3e" opacity=".6"/><path class="link-flow" d="M55 348C240 321 420 375 595 348S805 330 945 347" fill="none" stroke="#83efac" opacity=".7"/>'
    body+=flare(181,340,.5)+flare(595,348,.5)+flare(866,338,.5)
    save('cosmos-arsenal.svg',377,'Languages, rule engines and platforms','; '.join(a+': '+', '.join(b) for a,b in rows),body)


def toolkit():
    categories=[
        ('Recon & OSINT','Nmap,Shodan,theHarvester,Maltego,Tor,Amass,Recon-ng,SpiderFoot,Sherlock'),
        ('Web security','Burp Suite,OWASP ZAP,Nikto,sqlmap,Gobuster,ffuf,WPScan,Nuclei,dirsearch'),
        ('Offensive security','Metasploit,Hashcat,Hydra,John the Ripper,Aircrack-ng,Impacket,NetExec,Responder,BloodHound,Mimikatz,Evil-WinRM'),
        ('Defensive analysis','Wireshark,Snort,VirusTotal,Splunk,YARA,YARA-X,tcpdump,Zeek,Suricata,Sysmon,Velociraptor,Volatility,ELK and Elastic,Sigma'),
        ('Reverse engineering','Ghidra,IDA,radare2,Cutter,x64dbg,GDB,Binary Ninja,dnSpy,Frida,objdump,PE-bear,Detect It Easy,HxD,WinDbg,Procmon'),
    ]
    old=ET.parse(ASSETS/'security-toolkit-v3.svg')
    highlights=[n.text for n in old.iter() if n.tag.endswith('text') and 'hot' in n.get('class','').split()]
    highlights.append('YARA-X')
    body=heading('03','Instruments for the unknown.','A working reference across the security spectrum. Green marks the tools I use most.')
    y=144
    for index,(label,names) in enumerate(categories):
        labels,bottom=chips(61,y+51,878,names.split(','),highlights)
        body+=panel(34,y,932,bottom-y+19)
        body+=text(61,y+31,label,18,TEXT)+labels
        body+=cluster(925,y+24,index+17)
        y=bottom+35
    save('cosmos-toolkit.svg',y+10,'Security toolkit','; '.join(a+': '+b for a,b in categories),body)


def focus():
    columns=[
        (34,'CURRENT COORDINATES',['Web security & penetration testing','Vulnerability assessment & code review','OSINT & digital-footprint security','Malware, reverse engineering & binaries','Cryptography fundamentals','Linux, networks & backend development']),
        (516,'NEXT HORIZONS',['Advanced web application security','Malware analysis & reverse engineering','Linux hardening & network security','Secure APIs & backend architecture']),
    ]
    body=heading('04','There is always more to discover.','A flight plan through practical security research and secure backend development.')
    for x,label,lines in columns:
        body+=panel(x,144,450,247)
        body+=text(x+22,176,label,11,ACCENT,True)
        for i,value in enumerate(lines):
            body+=f'<circle cx="{x+24}" cy="{208+i*28}" r="1.6" fill="#71d999"/>'
            body+=text(x+38,213+i*28,value,16,MUTED)
    body+='<path d="M58 435C230 397 342 482 501 438S784 396 941 433" fill="none" stroke="#30543d" stroke-width="1"/><path class="link-flow" d="M58 435C230 397 342 482 501 438S784 396 941 433" fill="none" stroke="#a4efbd" stroke-width="1.2"/>'
    body+=flare(129,426,.65)+flare(501,438,.75)+flare(882,420,.5)
    body+=text(34,487,'LEARNING IS THE MISSION. CURIOSITY IS THE PROPULSION.',10,MUTED,True)
    save('cosmos-focus.svg',511,'Focus and learning','; '.join(label+': '+', '.join(lines) for _,label,lines in columns),body)


def about():
    body=heading('00','A little closer to the source.','Eren Erdoğan / backend development student / security tooling')
    body+=planet(914,242,121)
    lines=[
        'I study backend development and explore cybersecurity, Linux systems,',
        'and secure software development. My projects trace different signals:',
        'binaries, email, digital footprints, and the evidence they leave behind.',
        'I am learning penetration testing, OSINT, malware analysis, reverse',
        'engineering, and full-stack development through practical work.',
    ]
    for i,line in enumerate(lines):body+=text(36,156+i*30,line,17,MUTED)
    body+=text(36,334,'CURIOUS BY NATURE. PRACTICAL BY DESIGN.',10,ACCENT,True)
    save('cosmos-about.svg',363,'About Eren Erdoğan',' '.join(lines),body)


def certifications():
    items=[('Siber Vatan','Certificate verification','Sanayi ve Teknoloji Bakanlığı'),('Cisco','Introduction to Cybersecurity','Credly badge'),('Cisco','Network Defense','Credly badge'),('Cisco','Cyber Threat Management','Credly badge')]
    body=heading('05','Milestones along the journey.','Certifications and learning records. Original badges and verification links are below.')
    for i,(issuer,name,source) in enumerate(items):
        x,y=34+(i%2)*482,144+(i//2)*158
        body+=panel(x,y,450,133)+cluster(x+392,y+39,50+i)
        body+=text(x+21,y+28,issuer.upper(),10,ACCENT,True)
        body+=text(x+21,y+65,name,21,TEXT)
        body+=text(x+21,y+100,source,13,MUTED)
    save('cosmos-certifications.svg',477,'Certifications','Siber Vatan certificate; Cisco Introduction to Cybersecurity; Cisco Network Defense; Cisco Cyber Threat Management. Original verification links accompany this panel.',body)


def community():
    body=galaxy(844,133,.81,89,1050)
    body+='<rect width="1000" height="239" fill="url(#veil)"/>'
    body+=text(34,33,'06 / SHARED CONSTELLATIONS',11,ACCENT,True)
    body+=text(34,87,'Knowledge travels further together.',30)
    body+=text(36,133,'XERJ Corpus Hub',20)
    body+=text(36,166,'Community contributions / dRafaleD',16,MUTED)
    body+=text(36,208,'EXPLORE THE CONTRIBUTOR RECORD  →',10,ACCENT,True)
    save('cosmos-community.svg',239,'Community contributions','XERJ Corpus Hub contributor record for dRafaleD.',body)


def ethics():
    body=galaxy(853,201,.95,102,1400)
    body+='<rect width="1000" height="413" fill="url(#veil)"/>'
    body+=heading('07','Explore with a clear compass.','Curiosity opens the universe. Responsibility defines the route.')
    body+=text(36,160,'WHITE HAT / AUTHORIZED RESEARCH ONLY',11,ACCENT,True)
    body+=text(36,203,'Explore responsibly.',24)
    body+=text(36,241,'Report ethically. Strengthen securely.',24)
    body+=text(36,292,'All security research and testing is performed',17,MUTED)
    body+=text(36,320,'in authorized environments only.',17,MUTED)
    body+='<path class="link-flow" d="M36 365C270 345 398 389 630 362S866 346 966 358" fill="none" stroke="#84cfa2" opacity=".65"/>'
    body+=flare(490,370,.75)
    save('cosmos-ethics.svg',413,'Research ethics','White hat security. Authorized research only. Explore responsibly. Report ethically. Strengthen securely. All security research and testing is performed in authorized environments only.',body)


def connect():
    body=planet(926,208,111)
    body+=heading('08','Send a signal across the stars.','Find me on LinkedIn, explore my GitHub projects, or follow the work as it evolves.')
    body+=text(34,162,'THE LINKS BELOW ARE OPEN CHANNELS.',10,ACCENT,True)
    save('cosmos-connect.svg',190,'Connect with Eren Erdoğan','LinkedIn: Eren Erdoğan. GitHub: dRafaleD. Click the links beneath this panel.',body)
    # Separate image links remain clickable in GitHub's sanitized Markdown.
    for name,label,detail in [('linkedin','LinkedIn','Connect with Eren Erdoğan'),('github','GitHub','Explore dRafaleD repositories')]:
        body=galaxy(845,110,.61,19 if name=='linkedin' else 61,700)
        body+='<rect width="1000" height="178" fill="url(#veil)"/>'
        body+=text(36,45,'OPEN CHANNEL / '+label.upper(),11,ACCENT,True)
        body+=text(36,91,detail,31)
        body+=text(36,138,'FOLLOW THE SIGNAL  →',11,MUTED,True)
        save('cosmos-link-'+name+'.svg',178,label,detail,body)


def activity_header():
    body=heading('09','The journey leaves a trail.','GitHub activity, contribution streaks and a path through the contribution sky.')
    body+=galaxy(835,115,.65,27,800)
    body+='<path class="link-flow" d="M35 153C240 109 456 197 696 143S884 128 963 148" fill="none" stroke="#9fe1b5" opacity=".6"/>'
    body+=flare(235,145,.65)+flare(645,152,.65)
    save('cosmos-activity.svg',191,'GitHub activity','GitHub activity, contribution streaks, and an animated contribution snake follow.',body)


def streak_card(total,current,longest,total_range,current_range,longest_range):
    body=heading('LIVE','A record of continued exploration.','Contribution totals and streaks, refreshed from GitHub activity.')
    body+=galaxy(855,169,.68,87,700)
    for i,(value,label,dates) in enumerate([(f'{total:,}','Total contributions',total_range),(str(current),'Current streak',current_range),(str(longest),'Longest streak',longest_range)]):
        x=34+i*316
        body+=panel(x,143,300,157)
        body+=text(x+20,195,value,39,ACCENT)
        body+=text(x+20,236,label,17,TEXT)
        body+=text(x+20,272,dates,12,MUTED)
    save('github-streak.svg',327,'GitHub contribution streak statistics',f'{total} total contributions; {current} current streak; {longest} longest streak. {total_range}; {current_range}; {longest_range}.',body)


if __name__=='__main__':
    hero();about();projects();arsenal();toolkit();focus()
    certifications();community();ethics();connect();activity_header()
    print('Rendered the complete animated green-universe profile.')
