from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import json
import os
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "github-streak.svg"
USERNAME = "dRafaleD"
GRAPHQL_URL = "https://api.github.com/graphql"


def graphql(query: str, variables: dict) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required")

    request = urllib.request.Request(
        GRAPHQL_URL,
        data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "dRafaleD-profile-streak",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)

    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]


def contribution_days() -> tuple[date, dict[date, int]]:
    profile_query = """
    query($login: String!) {
      user(login: $login) { createdAt }
    }
    """
    created_at = graphql(profile_query, {"login": USERNAME})["user"]["createdAt"]
    account_start = date.fromisoformat(created_at[:10])
    today = datetime.now(timezone.utc).date()
    counts: dict[date, int] = {}

    calendar_query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays { date contributionCount }
            }
          }
        }
      }
    }
    """

    window_start = account_start
    while window_start <= today:
        window_end = min(window_start + timedelta(days=364), today)
        variables = {
            "login": USERNAME,
            "from": f"{window_start.isoformat()}T00:00:00Z",
            "to": f"{window_end.isoformat()}T23:59:59Z",
        }
        data = graphql(calendar_query, variables)
        weeks = data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        for week in weeks:
            for item in week["contributionDays"]:
                day = date.fromisoformat(item["date"])
                if window_start <= day <= window_end:
                    counts[day] = item["contributionCount"]
        window_start = window_end + timedelta(days=1)

    return account_start, counts


def streaks(counts: dict[date, int]) -> tuple[int, date | None, date | None, int, date | None, date | None]:
    today = datetime.now(timezone.utc).date()
    anchor = today if counts.get(today, 0) > 0 else today - timedelta(days=1)

    current_end = anchor if counts.get(anchor, 0) > 0 else None
    current_start = current_end
    while current_start and counts.get(current_start - timedelta(days=1), 0) > 0:
        current_start -= timedelta(days=1)
    current_length = (current_end - current_start).days + 1 if current_start and current_end else 0

    longest_length = 0
    longest_start = None
    longest_end = None
    run_start = None
    previous = None

    for day in sorted(counts):
        if counts[day] <= 0:
            run_start = None
            previous = day
            continue
        if run_start is None or previous is None or day != previous + timedelta(days=1):
            run_start = day
        run_length = (day - run_start).days + 1
        if run_length > longest_length:
            longest_length = run_length
            longest_start = run_start
            longest_end = day
        previous = day

    return current_length, current_start, current_end, longest_length, longest_start, longest_end


def format_date(value: date) -> str:
    return f"{value.strftime('%b')} {value.day}, {value.year}"


def format_range(start: date | None, end: date | None) -> str:
    if not start or not end:
        return "No active streak"
    if start == end:
        return format_date(start)
    return f"{format_date(start)} - {format_date(end)}"


def render() -> None:
    account_start, counts = contribution_days()
    total = sum(counts.values())
    current, current_start, current_end, longest, longest_start, longest_end = streaks(counts)
    total_range = f"{format_date(account_start)} - Present"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 210" width="760" height="210" role="img" aria-label="GitHub contribution streak statistics">
  <style>
    text {{ font-family: "Segoe UI", Ubuntu, Arial, sans-serif; }}
    .value {{ fill: #D7FFE3; font-size: 40px; font-weight: 700; }}
    .label {{ fill: #39FF88; font-size: 17px; font-weight: 600; }}
    .date {{ fill: #6D9479; font-size: 13px; }}
    .ring {{ animation: pulse 3s ease-in-out infinite; transform-origin: 380px 82px; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: .78; }} 50% {{ opacity: 1; }} }}
  </style>
  <rect x="1" y="1" width="758" height="208" rx="12" fill="#070B09" stroke="#174C2B" stroke-width="2"/>
  <line x1="254" y1="30" x2="254" y2="180" stroke="#174C2B"/>
  <line x1="506" y1="30" x2="506" y2="180" stroke="#174C2B"/>

  <g text-anchor="middle">
    <text class="value" x="127" y="88">{total:,}</text>
    <text class="label" x="127" y="126">Total Contributions</text>
    <text class="date" x="127" y="158">{total_range}</text>

    <circle class="ring" cx="380" cy="82" r="52" fill="none" stroke="#39FF88" stroke-width="7"/>
    <text class="value" x="380" y="95">{current}</text>
    <text class="label" x="380" y="154">Current Streak</text>
    <text class="date" x="380" y="181">{format_range(current_start, current_end)}</text>

    <text class="value" x="633" y="88">{longest}</text>
    <text class="label" x="633" y="126">Longest Streak</text>
    <text class="date" x="633" y="158">{format_range(longest_start, longest_end)}</text>
  </g>
</svg>
"""

    OUTPUT.write_text(svg, encoding="utf-8", newline="\n")
    print(f"Rendered {OUTPUT} ({total} contributions, {current}-day current streak, {longest}-day longest streak)")


if __name__ == "__main__":
    render()
