from pathlib import Path
import os
import tempfile
import urllib.request
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
USERNAME = "dRafaleD"
API_BASE = "https://api.github.com"
AVATAR_SOURCE = Path(tempfile.gettempdir()) / "drafaled-github-avatar.png"
OUTPUT = ROOT / "assets" / "profile-terminal-v2.gif"
FONT = Path(r"C:\Windows\Fonts\CascadiaMono.ttf")

if not FONT.exists():
    FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")


def github_api(path: str):
    headers = {"User-Agent": "dRafaleD-profile-terminal"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(API_BASE + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_stats():
    fallback = {"repos": 7, "followers": 27, "stars": 4, "commits": 123}
    try:
        user = github_api(f"/users/{USERNAME}")
        repos = github_api(f"/users/{USERNAME}/repos?type=owner&per_page=100")
        search = github_api(f"/search/commits?q=author%3A{USERNAME}&per_page=1")
        return {
            "repos": user.get("public_repos", fallback["repos"]),
            "followers": user.get("followers", fallback["followers"]),
            "stars": sum(repo.get("stargazers_count", 0) for repo in repos),
            "commits": search.get("total_count", fallback["commits"]),
        }
    except Exception as error:
        print(f"GitHub stats unavailable, using fallback values: {error}")
        return fallback


def download_avatar():
    urllib.request.urlretrieve(f"https://github.com/{USERNAME}.png?size=512", AVATAR_SOURCE)


STATS = fetch_stats()
download_avatar()
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

W, H = 920, 900
BG = "#070b09"
HEADER = "#0c1410"
BORDER = "#174c2b"
GREEN = "#39ff88"
LIME = "#b7f34a"
TEXT = "#d7ffe3"
MUTED = "#6d9479"

prompt_font = ImageFont.truetype(str(FONT), 16)
body_font = ImageFont.truetype(str(FONT), 15)
small_font = ImageFont.truetype(str(FONT), 14)

entries = [
    ("dRafaleD@github:~$", 44, 94, prompt_font, GREEN),
    ("whoami", 320, 94, prompt_font, LIME),
    ("Eren Erdogan", 44, 124, body_font, TEXT),
    ("dRafaleD@github:~$", 44, 160, prompt_font, GREEN),
    ("./profile --summary", 320, 160, prompt_font, LIME),
    ("Focus: Cybersecurity and secure software", 44, 190, body_font, TEXT),
    ("Secondary: Full Stack Development", 44, 216, body_font, TEXT),
    ("Status: Learning - building - testing", 44, 242, body_font, TEXT),
    ("dRafaleD@github:~$", 44, 278, prompt_font, GREEN),
    ("neofetch", 320, 278, prompt_font, LIME),
    ("dRafaleD @github.com", 350, 320, body_font, GREEN),
    ("--------------------", 350, 346, body_font, MUTED),
    ("OS:         GitHub", 350, 378, body_font, TEXT),
    ("Focus:      Cybersecurity", 350, 406, body_font, TEXT),
    (f"Repos:      {STATS['repos']} public repositories", 350, 434, body_font, TEXT),
    (f"Followers:  {STATS['followers']}", 350, 462, body_font, TEXT),
    (f"Stars:      {STATS['stars']}", 350, 490, body_font, TEXT),
    (f"Commits:    {STATS['commits']} public commits", 350, 518, body_font, TEXT),
    ("Location:   Eskisehir, Turkiye", 350, 546, body_font, TEXT),
    ("dRafaleD@github:~$", 44, 630, prompt_font, GREEN),
    ("cat about.txt", 320, 630, prompt_font, LIME),
    ("Focused on cybersecurity, Linux systems,", 44, 660, body_font, TEXT),
    ("and secure backend development.", 44, 686, body_font, TEXT),
    ("Building tools for OSINT, malware analysis, and email security.", 44, 712, body_font, TEXT),
    ("dRafaleD@github:~$", 44, 768, prompt_font, GREEN),
    ("status", 320, 768, prompt_font, LIME),
    ("SYSTEM ONLINE  |  SECURITY MONITORING  |  BUILD ACTIVE", 64, 796, body_font, TEXT),
    ("dRafaleD@github:~$", 44, 850, prompt_font, GREEN),
    ("exit", 320, 850, prompt_font, LIME),
]
TOTAL_CHARS = sum(len(item[0]) for item in entries)


def crop_avatar() -> Image.Image:
    source = Image.open(AVATAR_SOURCE).convert("RGBA")
    # The workflow downloads the avatar directly from GitHub, so use the
    # complete square image instead of the old screenshot crop.
    avatar = source

    # Keep only the green ASCII mask pixels. The circular avatar background,
    # border and surrounding black area become fully transparent.
    pixels = avatar.load()
    for y in range(avatar.height):
        for x in range(avatar.width):
            red, green, blue, _ = pixels[x, y]
            green_signal = green - max(red, blue)
            alpha = min(255, max(0, (green_signal - 4) * 5)) if green > 18 else 0
            pixels[x, y] = (red, green, blue, alpha)

    return avatar.resize((245, 245), Image.Resampling.LANCZOS)


AVATAR = crop_avatar()


def render(visible_chars: int, cursor_strength: float, scanline_y: int) -> Image.Image:
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((22, 22, 898, 878), outline=BORDER, width=2)
    draw.rectangle((22, 22, 898, 64), fill=HEADER)
    draw.line((22, 64, 898, 64), fill=BORDER, width=2)
    draw.line((24, scanline_y, 896, scanline_y), fill="#0a160f", width=1)
    draw.ellipse((40, 36, 54, 50), fill="#ff5f57")
    draw.ellipse((62, 36, 76, 50), fill="#ffbd2e")
    draw.ellipse((84, 36, 98, 50), fill="#28c840")
    draw.text((115, 38), "dRafaleD@github: ~/profile", font=small_font, fill=MUTED)

    progress = visible_chars
    avatar_visible = False
    for text, x, y, font, color in entries:
        count = max(0, min(len(text), progress))
        if count:
            draw.text((x, y), text[:count], font=font, fill=color)
        if progress >= len(text):
            progress -= len(text)
            if text == "neofetch":
                avatar_visible = True
        else:
            break

    if avatar_visible:
        image.paste(AVATAR, (52, 318), AVATAR)

    if visible_chars >= TOTAL_CHARS:
        draw.ellipse((44, 802, 54, 812), fill=GREEN)
    cursor = (
        int(20 + 37 * cursor_strength),
        int(70 + 185 * cursor_strength),
        int(45 + 91 * cursor_strength),
    )
    draw.rectangle((366, 832, 376, 852), fill=cursor)
    return image


frames = []
durations = []
typing_steps = 190
for step in range(typing_steps):
    visible = int(TOTAL_CHARS * (step + 1) / typing_steps)
    phase = (step % 18) / 18
    cursor_strength = 0.35 + 0.65 * abs(phase * 2 - 1)
    frames.append(render(visible, cursor_strength, 82 + (step * 5) % 780))
    durations.append(60)

final_frame = render(TOTAL_CHARS, 1.0, 82)
for _ in range(6):
    frames.append(final_frame.copy())
    durations.append(10_000)

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0,
    optimize=False,
    disposal=1,
)
print(OUTPUT)
