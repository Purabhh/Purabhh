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




# ---------- streak card: only on the profile while the streak is 3+ days ----------
MIN_STREAK = 3
README = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "README.md")
MARK_A, MARK_B = "<!-- streak -->", "<!-- /streak -->"


def flame(cx, base, s, delay, cls):
    """One flame tongue: outer orange, inner gold, core cream, flickering."""
    def tongue(k, fill):
        w, h = 26 * s * k, 70 * s * k
        return (f'<path fill="{fill}" d="M{cx} {base} C{cx - w} {base} {cx - w * 1.1} {base - h * .45} {cx - w * .35} {base - h * .7} '
                f'C{cx - w * .2} {base - h * .82} {cx + w * .05} {base - h * .9} {cx} {base - h} '
                f'C{cx + w * .3} {base - h * .75} {cx + w * 1.1} {base - h * .5} {cx + w} {base - h * .2} '
                f'C{cx + w * .9} {base - h * .05} {cx + w * .5} {base} {cx} {base}Z"/>')
    return (f'<g class="{cls}" style="animation-delay:{delay}s;transform-origin:{cx}px {base}px">'
            f'{tongue(1, "#ff6a2b")}{tongue(.72, "#ffb340")}{tongue(.42, "#fff1c9")}</g>')


def streak_card(n):
    w, h = 1000, 170
    r = __import__("random").Random(n)
    embers = "".join(
        f'<circle class="em" cx="{r.uniform(40, w - 40):.0f}" cy="{h - 10}" r="{r.choice([1.5, 2, 2.6])}" fill="{GOLD}" '
        f'style="animation-delay:{r.uniform(0, 4):.2f}s;animation-duration:{r.uniform(3, 5.5):.2f}s"/>' for _ in range(26))
    fires = "".join(flame(x, h + 4, sc, d, c) for x, sc, d, c in
                    [(60, 1.7, 0, "f1"), (140, 1.25, .3, "f2"), (870, 1.3, .5, "f1"), (945, 1.8, .1, "f2"), (330, .6, .4, "f1"), (680, .65, .6, "f2"),
                     (215, .85, .7, "f2"), (795, .9, .2, "f1")])
    big = f"{n} DAY STREAK"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<title>{n} day contribution streak</title><style>
.f1{{animation:fl 1.1s ease-in-out infinite alternate}}.f2{{animation:fl 1.5s ease-in-out infinite alternate-reverse}}
@keyframes fl{{0%{{transform:scale(1,1) skewX(0)}}50%{{transform:scale(1.06,.92) skewX(4deg)}}100%{{transform:scale(.95,1.1) skewX(-4deg)}}}}
.em{{animation:rise 4s linear infinite;opacity:0}}@keyframes rise{{0%{{transform:translateY(0);opacity:0}}15%{{opacity:1}}100%{{transform:translateY(-150px);opacity:0}}}}
.glow{{animation:pulse 2.2s ease-in-out infinite}}@keyframes pulse{{0%,100%{{opacity:.55}}50%{{opacity:.9}}}}
</style><defs>{sky_defs("sky", w, h)}
<radialGradient id="heat" cx=".5" cy="1.1" r=".8"><stop offset="0" stop-color="#ff6a2b" stop-opacity=".75"/><stop offset="1" stop-color="#ff6a2b" stop-opacity="0"/></radialGradient>
<clipPath id="c"><rect width="{w}" height="{h}" rx="22"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#sky)"/><rect class="glow" width="{w}" height="{h}" fill="url(#heat)"/>
{stars(w, 70, 20, 9)}{fires}{embers}
<path d="{text(big, w / 2, 96, 58, anchor="middle", spacing=1.5)}" transform="translate(0 5)" fill="#7a2a12"/>
<path d="{text(big, w / 2, 96, 58, anchor="middle", spacing=1.5)}" fill="{CREAM}"/>
<path d="{text("KEEP THE FIRE GOING", w / 2, 132, 16, "baloo600.ttf", "middle", 2)}" fill="{GOLD}"/></g></svg>"""


def sync_streak(n):
    s = open(README, encoding="utf-8").read()
    a, b = s.index(MARK_A) + len(MARK_A), s.index(MARK_B)
    block = (f'\n<a href="https://github.com/{USER}"><img src="assets/streak.svg" width="100%" alt="{n} day streak" /></a>\n'
             if n >= MIN_STREAK else "\n")
    if n >= MIN_STREAK:
        save("streak.svg", streak_card(n))
    open(README, "w", encoding="utf-8").write(s[:a] + block + s[b:])


if __name__ == "__main__":
    total, weeks = fetch()
    save("activity.svg", card(total, weeks))
    sync_streak(streaks([d for wk in weeks for d in wk])[0])
