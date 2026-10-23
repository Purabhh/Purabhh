"""Builds assets/activity.svg: one card with the contribution grid and streak stats, in the banner's colors.

Run by .github/workflows/activity.yml every day. Needs GITHUB_TOKEN (any token that can read public profile data).
"""
import datetime as dt, json, os, urllib.request
from textpath import text, measure
from gen import NAVY, PURPLE, MAUVE, PEACH, GREEN, CREAM, GOLD, OUT, sky_defs, stars, save, TWINKLE

USER = os.environ.get("PROFILE_USER", "Purabhh")
QUERY = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
LEVELS = [None, "#1f6b2c", "#2f9a42", GREEN, "#8af09c"]


def fetch():
    req = urllib.request.Request("https://api.github.com/graphql",
                                 json.dumps({"query": QUERY, "variables": {"u": USER}}).encode(),
                                 {"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "User-Agent": USER})
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]


def streaks(days):
    cur = best = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        best = max(best, run)
    # today with no commits yet doesn't break the current streak
    tail = days[:-1] if days and days[-1][1] == 0 else days
    for _, n in reversed(tail):
        if not n:
            break
        cur += 1
    return cur, best


def level(n, top):
    if n == 0:
        return 0
    return min(4, 1 + int(3 * n / max(top, 1)))


def card(total, weeks):
    days = [d for w in weeks for d in w]
    cur, best = streaks(days)
    busiest = max(days, key=lambda d: d[1])
    top = sorted(n for _, n in days if n)[int(.9 * len([1 for _, n in days if n]))] if any(n for _, n in days) else 1

    w, cell, gap = 1000, 13, 4
    gx, gy = 62, 150
    h = gy + 7 * (cell + gap) + 46
    out = []

    stats = [(str(total), "CONTRIBUTIONS · LAST YEAR"), (f"{cur} day{'s' * (cur != 1)}", "CURRENT STREAK"),
             (f"{best} day{'s' * (best != 1)}", "LONGEST STREAK"),
             (str(busiest[1]), "BEST DAY · " + dt.date.fromisoformat(busiest[0]).strftime("%b %d").upper())]
    col = (w - 80) / len(stats)
    for i, (big, small) in enumerate(stats):
        cx = 40 + col * i + col / 2
        fill = GREEN if i == 1 else CREAM
        out.append(f'<path d="{text(big, cx, 72, 40, anchor="middle")}" fill="{fill}"/>'
                   f'<path d="{text(small, cx, 98, 13, "baloo600.ttf", "middle", 1.3)}" fill="{GOLD}"/>')
        if i:
            out.append(f'<rect x="{40 + col * i - 1}" y="38" width="2" height="62" rx="1" fill="{CREAM}" opacity=".14"/>')

    last_month, last_x = None, -99
    for i, wk in enumerate(weeks):
        x = gx + i * (cell + gap)
        m = dt.date.fromisoformat(wk[0][0]).month
        if m != last_month and x - last_x > 34 and i < len(weeks) - 2:
            out.append(f'<path d="{text(dt.date(2000, m, 1).strftime("%b"), x, gy - 10, 13, "baloo600.ttf")}" fill="{CREAM}" opacity=".7"/>')
            last_x = x
        last_month = m
        for d, n in wk:
            y = gy + dt.date.fromisoformat(d).isoweekday() % 7 * (cell + gap)
            lv = level(n, top)
            fill = f'fill="{LEVELS[lv]}"' if lv else f'fill="{CREAM}" fill-opacity=".08"'
            out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" {fill}><title>{d}: {n}</title></rect>')
            if lv:  # voxel highlight
                out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="4" rx="2" fill="#ffffff" opacity=".18"/>')
    for k, lab in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        out.append(f'<path d="{text(lab, gx - 10, gy + k * (cell + gap) + 11, 12, "baloo600.ttf", "end")}" fill="{CREAM}" opacity=".6"/>')

    lx = w - 40 - 5 * (cell + gap) - 70
    ly = h - 26
    out.append(f'<path d="{text("Less", lx - 8, ly + 11, 12, "baloo600.ttf", "end")}" fill="{CREAM}" opacity=".6"/>')
    for k in range(5):
        fill = f'fill="{LEVELS[k]}"' if k else f'fill="{CREAM}" fill-opacity=".08"'
        out.append(f'<rect x="{lx + k * (cell + gap)}" y="{ly}" width="{cell}" height="{cell}" rx="3" {fill}/>')
    out.append(f'<path d="{text("More", lx + 5 * (cell + gap) + 4, ly + 11, 12, "baloo600.ttf")}" fill="{CREAM}" opacity=".6"/>')
    stamp = "Updated " + dt.date.today().strftime("%b %d, %Y")
    out.append(f'<path d="{text(stamp, 40, ly + 11, 12, "baloo600.ttf")}" fill="{CREAM}" opacity=".45"/>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<title>{total} contributions in the last year, current streak {cur}, longest {best}</title>{TWINKLE}
<defs>{sky_defs("sky", w, h)}<clipPath id="c"><rect width="{w}" height="{h}" rx="22"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#sky)"/><rect width="{w}" height="{h}" fill="url(#skyv)"/>
{stars(w, 120, 30, 5)}{"".join(out)}</g></svg>"""


if __name__ == "__main__":
    save("activity.svg", card(*fetch()))
