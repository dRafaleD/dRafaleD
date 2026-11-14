"""Build the profile's self-contained SVG cards; no network dependencies."""
from html import escape
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"
PROJECTS = [
    ("banshee", "01", "OFFLINE ANALYSIS", "Banshee", ["Inspect files. Decode suspicious values.", "Extract IOCs and preserve evidence.", "Local analysis, pipe-friendly workflow."], "RUST / YARA / ALPHA", '<path d="M12 7h19l8 8v31H12Z M31 7v9h8 M19 26h13 M19 33h13"/>'),
    ("asphdex", "02", "STATIC MALWARE TRIAGE", "AsphDex", ["PE/ELF inspection and YARA matches.", "Strings, entropy, explainable reports.", "Without intentionally running samples."], "ELECTRON / JAVASCRIPT / RUST / YARA", '<path d="m25 6 17 7v13c0 12-17 22-17 22S8 38 8 26V13Z M16 26l6 6 13-15"/>'),
    ("fhnix", "03", "EMAIL SECURITY", "FhniX", ["Explainable phishing email triage.", "Local scoring and optional classifier.", "Read-only IMAP. Links stay defanged."], "PYTHON / DESKTOP & CLI", '<rect x="6" y="12" width="39" height="28" rx="4"/><path d="m8 15 17 13 18-13 M8 38l12-12 M43 38 31 26"/>'),
    ("trackher", "04", "DIGITAL FOOTPRINT", "The-Trackher", ["OSINT for your own online accounts.", "Breach exposure and privacy checks.", "Local trace cleanup with dry-run."], "PYTHON / PRIVACY & OSINT", '<circle cx="23" cy="23" r="15"/><circle cx="23" cy="23" r="6"/><path d="m34 34 12 12 M23 3v8 M3 23h8"/>'),
]

for slug, number, category, title, lines, stack, icon in PROJECTS:
    text = "".join(f'<text x="30" y="{155+i*28}" class="body">{escape(line)}</text>' for i, line in enumerate(lines))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="290" viewBox="0 0 600 290" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)} — {escape(category)}</title>
<desc id="desc">{escape(" ".join(lines))} {escape(stack)}</desc>
<style>
text{{font-family:'Segoe UI',Ubuntu,Arial,sans-serif}}
.meta{{font-family:Consolas,'DejaVu Sans Mono',monospace;font-size:14px;letter-spacing:1.2px;fill:#90a69a}}
.body{{font-size:20px;fill:#b7c5bd}}
.scan{{animation:scan 9s ease-in-out infinite;animation-delay:-{int(number)*2}s}}
@keyframes scan{{0%,100%{{transform:translateX(0);opacity:.25}}50%{{transform:translateX(455px);opacity:.65}}}}
@media(prefers-reduced-motion:reduce){{.scan{{animation:none;opacity:.4}}}}
</style>
<rect x="1" y="1" width="598" height="288" rx="18" fill="#080d0b" stroke="#213a2b"/>
<path d="M30 62H570" stroke="#1b3024"/>
<text x="30" y="38" class="meta">{number} / {escape(category)}</text>
<text x="30" y="114" fill="#edfff4" font-size="38" font-weight="650">{escape(title)}</text>
<g transform="translate(516 78)" fill="none" stroke="#6bdc99" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{icon}</g>
{text}
<text x="30" y="255" class="meta" style="font-size:13px;fill:#71bd8d">{escape(stack)}</text>
<path d="M30 274H570" stroke="#15251b"/>
<g transform="translate(30 0)"><path class="scan" d="M0 274H55" stroke="#6bdc99" stroke-width="2"/></g>
</svg>'''
    (ASSETS / f"project-{slug}.svg").write_text(svg, encoding="utf-8")

(ASSETS / "profile-signal.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="70" viewBox="0 0 920 70" role="img" aria-labelledby="t d">
<title id="t">Build. Investigate. Document.</title><desc id="d">Cybersecurity, Linux, and secure software development.</desc>
<style>.signal{animation:breathe 5s ease-in-out infinite}@keyframes breathe{0%,100%{opacity:.35}50%{opacity:.95}}@media(prefers-reduced-motion:reduce){.signal{animation:none;opacity:.7}}</style>
<rect x="1" y="1" width="918" height="68" rx="12" fill="#080d0b" stroke="#213a2b"/>
<circle class="signal" cx="30" cy="35" r="4" fill="#6bdc99"/>
<g fill="#a7c0b0" font-family="Consolas,'DejaVu Sans Mono',monospace" font-size="15" letter-spacing="1.4"><text x="48" y="40">BUILD / INVESTIGATE / DOCUMENT</text></g>
<path d="M445 35H880" stroke="#1b3024"/><g class="signal" stroke="#6bdc99" fill="none" stroke-width="1.5"><path d="M735 35h25l6-7 9 15 9-20 9 12h30"/></g>
</svg>''', encoding="utf-8")
print("Rendered four project cards and the profile signal strip.")
