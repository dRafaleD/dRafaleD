"""Frame freshly generated snk SVGs without changing their activity data."""
from pathlib import Path
import argparse
import xml.etree.ElementTree as ET
from render_cosmos_profile import save, text, MUTED, ACCENT


def frame_file(path: Path, output_dir: Path | None = None):
    output_dir = output_dir or path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / path.name
    root = ET.parse(path).getroot()
    if root.get('data-cosmos-frame') == 'true':
        if destination != path:
            destination.write_bytes(path.read_bytes())
        return
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    # Preserve the inner viewBox, classes, keyframes and contribution geometry.
    root.set('x', '34')
    root.set('y', '27')
    root.set('width', '932')
    root.set('height', '204')
    original = ET.tostring(root, encoding='unicode')
    body = original
    body += text(34,254,'CONTRIBUTION TRACE',13,ACCENT,True)
    body += text(966,254,'dRafaleD / GITHUB',10,MUTED,True,'text-anchor="end"')
    save(path.name,277,'GitHub contribution trace',
         'The original animated GitHub contribution snake, with an ice-blue activity grid and mint cursor.',
         body,output_dir)
    framed = destination.read_text(encoding='utf-8').replace('<svg ', '<svg data-cosmos-frame="true" ', 1)
    # Include the contribution animation in the reduced-motion fallback.
    framed = framed.replace('</style>', '@media(prefers-reduced-motion:reduce){.c,.s{animation:none!important}}</style>',1)
    destination.write_text(framed,encoding='utf-8',newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory',type=Path,nargs='?',default=Path('dist'))
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    paths = sorted(args.directory.glob('github-contribution-grid-snake*.svg'))
    if not paths:
        raise SystemExit('No generated contribution snakes found')
    for path in paths:
        frame_file(path,args.output)
        print(f'Framed {path.name}')
