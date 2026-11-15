"""Frame freshly generated snk SVGs without changing their activity data."""
from pathlib import Path
import argparse
import xml.etree.ElementTree as ET
from render_cosmos_profile import save, text, galaxy, MUTED, ACCENT


def frame_file(path: Path):
    root = ET.parse(path).getroot()
    if root.get('data-cosmos-frame') == 'true':
        return
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    # Preserve the inner viewBox, classes, keyframes and contribution geometry.
    root.set('x', '34')
    root.set('y', '27')
    root.set('width', '932')
    root.set('height', '204')
    original = ET.tostring(root, encoding='unicode')
    body = '<g opacity=".35">' + galaxy(865,202,.62,19,700) + '</g>'
    body += original
    body += text(34,254,'A PATH THROUGH THE CONTRIBUTION SKY',10,ACCENT,True)
    body += text(966,254,'dRafaleD / GITHUB',10,MUTED,True,'text-anchor="end"')
    save(path.name,277,'GitHub contribution sky',
         'The original animated GitHub contribution snake, framed by stars and a green galaxy.',
         body,path.parent)
    framed = path.read_text(encoding='utf-8').replace('<svg ', '<svg data-cosmos-frame="true" ', 1)
    # Include the contribution animation in the reduced-motion fallback.
    framed = framed.replace('</style>', '@media(prefers-reduced-motion:reduce){.c,.s{animation:none!important}}</style>',1)
    path.write_text(framed,encoding='utf-8',newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory',type=Path,nargs='?',default=Path('dist'))
    args = parser.parse_args()
    paths = sorted(args.directory.glob('github-contribution-grid-snake*.svg'))
    if not paths:
        raise SystemExit('No generated contribution snakes found')
    for path in paths:
        frame_file(path)
        print(f'Framed {path}')
