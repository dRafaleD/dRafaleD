from pathlib import Path
import os
import urllib.request
import json
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
USERNAME = "dRafaleD"
API_BASE = "https://api.github.com"
MASK_SOURCE = ROOT / "assets" / "profile-terminal-mask.png"
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
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except OSError:
        if not shutil.which("gh"):
            raise
        # Use the authenticated CLI if the local Python HTTPS transport fails.
        result = subprocess.run(["gh", "api", path], check=True, capture_output=True, text=True)
        return json.loads(result.stdout)


def fetch_stats():
    try:
        user = github_api(f"/users/{USERNAME}")
        repos = github_api(f"/users/{USERNAME}/repos?type=owner&per_page=100")
        search = github_api(f"/search/commits?q=author%3A{USERNAME}&per_page=1")
        return {
            "repos": user["public_repos"],
            "followers": user["followers"],
            "stars": sum(repo.get("stargazers_count", 0) for repo in repos),
            "commits": search["total_count"],
        }
    except Exception as error:
        raise RuntimeError("GitHub stats unavailable; keeping the existing terminal asset.") from error


STATS = fetch_stats()
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

W, H = 920, 900
BG = "#0e0f12"
HEADER = "#15171b"
BORDER = "#272a30"
GREEN = "#9fc4e8"
LIME = "#b9d5f0"
TEXT = "#e4e6ea"
MUTED = "#adb2ba"

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


def load_terminal_mask() -> Image.Image:
    # Keep the original terminal mask independent of the GitHub profile photo.
    # This checked-in crop preserves the historic mask's shape and placement.
    original = Image.open(MASK_SOURCE).convert("RGBA")
    # Keep the historic mask's shape, detail and position. Map its green
    # intensity to Kozmos blue, including the original opaque background.
    intensity = original.getchannel("G").point(lambda value: max(0, min(255, round((value - 11) * 255 / 213))))
    recolored = ImageOps.colorize(intensity, BG, GREEN).convert("RGBA")
    recolored.putalpha(original.getchannel("A"))
    return recolored


TERMINAL_MASK = load_terminal_mask()


def render(visible_chars: int, cursor_strength: float, scanline_y: int) -> Image.Image:
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((22, 22, 898, 878), outline=BORDER, width=2)
    draw.rectangle((22, 22, 898, 64), fill=HEADER)
    draw.line((22, 64, 898, 64), fill=BORDER, width=2)
    draw.line((24, scanline_y, 896, scanline_y), fill="#171c24", width=1)
    draw.ellipse((40, 36, 54, 50), fill="#3a3e46")
    draw.ellipse((62, 36, 76, 50), fill="#6c7f98")
    draw.ellipse((84, 36, 98, 50), fill=GREEN)
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
        image.paste(TERMINAL_MASK, (52, 318), TERMINAL_MASK)

    if visible_chars >= TOTAL_CHARS:
        draw.ellipse((44, 802, 54, 812), fill=GREEN)
    cursor = (
        int(50 + 109 * cursor_strength),
        int(65 + 131 * cursor_strength),
        int(82 + 150 * cursor_strength),
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
