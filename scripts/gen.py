"""Generates the profile README art in PURABH'S WORLD colors (dusk sky, grass green, cream)."""
import os, random, re
from textpath import text, measure

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")

NAVY, PURPLE, MAUVE, PEACH = "#17123a", "#3d2466", "#8c4a60", "#d88a62"
GREEN, GREEN_D, CREAM, GOLD = "#46C95E", "#1d6b2c", "#fbf3e6", "#ffd183"


def save(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)


def icon_path(slug):
    s = open(os.path.join(HERE, "icons", slug + ".svg"), encoding="utf-8").read()
    return re.search(r'<path d="([^"]+)"', s).group(1)


def icon(slug, x, y, size, color):
    k = size / 24
    return f'<path transform="translate({x:.1f} {y:.1f}) scale({k:.4f})" fill="{color}" d="{icon_path(slug)}"/>'


def stars(w, h, n, seed, twinkle=True):
    r = random.Random(seed)
    out = []
    for i in range(n):
        x, y = r.uniform(0, w), r.uniform(0, h) ** 1.25 / h ** 0.25
        rad = r.choice([0.8, 1, 1.2, 1.6])
        cls = f' class="t{i % 3}"' if twinkle and r.random() < 0.45 else ""
        out.append(f'<circle{cls} cx="{x:.0f}" cy="{y:.0f}" r="{rad}" fill="{CREAM}" opacity="{r.uniform(.35, .9):.2f}"/>')
    return "".join(out)


TWINKLE = """<style>
.t0{animation:tw 3.2s ease-in-out infinite}.t1{animation:tw 4.1s ease-in-out 1s infinite}
.t2{animation:tw 2.6s ease-in-out .5s infinite}@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}
</style>"""


def sky_defs(id_, w, h):
    return f"""<linearGradient id="{id_}" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{NAVY}"/><stop offset=".42" stop-color="{PURPLE}"/>
<stop offset=".74" stop-color="{MAUVE}"/><stop offset="1" stop-color="{PEACH}"/></linearGradient>
<radialGradient id="{id_}v" cx=".5" cy=".55" r=".65"><stop offset="0" stop-color="#2a1530" stop-opacity=".55"/>
<stop offset="1" stop-color="#2a1530" stop-opacity="0"/></radialGradient>"""


# ---------- banner ----------
def voxel_town(w, ground):
    r = random.Random(7)
    dark, mid = "#1a1230", "#241838"
    parts = [f'<rect x="0" y="{ground}" width="{w}" height="60" fill="{dark}"/>']
    # rolling block hills
    x = 0
    while x < w:
        bw, bh = r.choice([40, 60, 80]), r.choice([8, 14, 20])
        parts.append(f'<rect x="{x}" y="{ground - bh}" width="{bw}" height="{bh + 1}" fill="{mid}"/>')
        x += bw
    # voxel trees
    for tx in [40, 120, 175, 700, 745, 905, 955]:
        s = r.choice([22, 26, 30])
        parts.append(f'<rect x="{tx + s / 2 - 3}" y="{ground - 22}" width="6" height="22" fill="{dark}"/>'
                     f'<rect x="{tx}" y="{ground - 22 - s}" width="{s}" height="{s}" fill="{dark}"/>'
                     f'<rect x="{tx + 5}" y="{ground - 30 - s}" width="{s - 10}" height="10" fill="{dark}"/>')
    # office building with lit windows, nod to the Azonix tower in the world
    bx, by, bw, bh = 800, ground - 74, 84, 74
    parts.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{dark}"/>'
                 f'<rect x="{bx - 4}" y="{by - 6}" width="{bw + 8}" height="8" fill="{dark}"/>')
    for row in range(4):
        for col in range(4):
            if r.random() < .7:
                parts.append(f'<rect x="{bx + 10 + col * 20}" y="{by + 10 + row * 17}" width="10" height="9" '
                             f'fill="{GOLD}" opacity="{r.uniform(.55, .95):.2f}"/>')
    # small R block, nod to the Rutgers sign
    parts.append(f'<rect x="250" y="{ground - 52}" width="120" height="52" fill="{dark}"/>')
    # lamp posts with glow
    for lx in [215, 420, 600, 880]:
        parts.append(f'<circle cx="{lx}" cy="{ground - 46}" r="16" fill="url(#glow)"/>'
                     f'<rect x="{lx - 1.5}" y="{ground - 44}" width="3" height="44" fill="{dark}"/>'
                     f'<rect x="{lx - 5}" y="{ground - 52}" width="10" height="9" rx="2" fill="{GOLD}"/>')
    return "".join(parts)


def banner():
    w, h = 1000, 300
    title = 82
    pw, sw = measure("PURABH ", title, spacing=1), measure("SINGH", title, spacing=1)
    x0 = (w - pw - sw) / 2
    ty = 136

    def shadowed(word, x, fill, shade):
        d = text(word, x, ty, title, spacing=1)
        return f'<path d="{d}" fill="{shade}" transform="translate(0 6)"/><path d="{d}" fill="{fill}"/>'

    sub = text("Backend & AI infrastructure engineer", w / 2, 182, 24, "lexend.ttf", "middle")
    sub2 = text("CS @ RUTGERS  ·  PREVIOUSLY BNY, ESSEX SECURITIES", w / 2, 214, 15, "baloo600.ttf", "middle", 1.6)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<title>Purabh Singh</title>{TWINKLE}<defs>{sky_defs("sky", w, h)}
<radialGradient id="glow"><stop offset="0" stop-color="{GOLD}" stop-opacity=".7"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>
<clipPath id="c"><rect width="{w}" height="{h}" rx="22"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#sky)"/><rect width="{w}" height="{h}" fill="url(#skyv)"/>
{stars(w, 170, 70, 3)}{voxel_town(w, h - 18)}
{shadowed("PURABH", x0, GREEN, GREEN_D)}{shadowed("SINGH", x0 + pw, CREAM, "#5f4a2c")}
<path d="{sub}" fill="{CREAM}" opacity=".95"/><path d="{sub2}" fill="{GOLD}"/></g></svg>"""


# ---------- section headers ----------
def header(label):
    w, h, size = 1000, 54, 26
    tw = measure(label.upper(), size, spacing=1.5)
    pill = tw + 76
    d = text(label.upper(), 50, 36, size, spacing=1.5)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<title>{label}</title><defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{NAVY}"/>
<stop offset=".6" stop-color="{PURPLE}"/><stop offset="1" stop-color="{MAUVE}"/></linearGradient>
<linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{PEACH}"/><stop offset="1" stop-color="{PEACH}" stop-opacity="0"/></linearGradient></defs>
<rect x="1" y="3" width="{pill}" height="48" rx="24" fill="url(#g)"/>
<rect x="24" y="20" width="14" height="14" rx="3" fill="{GREEN}"/><rect x="24" y="20" width="14" height="5" rx="2" fill="#6BE584"/>
<path d="{d}" fill="{CREAM}"/>
<rect x="{pill + 14}" y="26" width="{w - pill - 16}" height="3" rx="1.5" fill="url(#l)"/></svg>"""


# ---------- link buttons ----------
def button(label, slug, accent):
    size, h = 19, 48
    tw = measure(label, size, spacing=.5)
    w = tw + 84
    d = text(label, 62, 32, size, spacing=.5)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h}" width="{w:.0f}" height="{h}">
<title>{label}</title><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PURPLE}"/>
<stop offset="1" stop-color="{NAVY}"/></linearGradient></defs>
<rect x="1" y="1" width="{w - 2:.0f}" height="{h - 2}" rx="23" fill="url(#g)" stroke="{CREAM}" stroke-opacity=".22" stroke-width="1.5"/>
<circle cx="34" cy="24" r="15" fill="{accent}"/>{icon(slug, 25, 15, 18, "#ffffff")}
<path d="{d}" fill="{CREAM}"/></svg>"""


# ---------- tech stack ----------
STACK = [
    ("Languages", [("openjdk", "Java", "#f89820"), ("python", "Python", "#5a9fd4"), ("typescript", "TypeScript", "#4a8fe0"),
                   ("rust", "Rust", CREAM), ("cplusplus", "C++", "#6fa3dc")]),
    ("Backend & Infra", [("springboot", "Spring Boot", "#77c142"), ("nodedotjs", "Node.js", "#6cbf55"),
                         ("fastapi", "FastAPI", "#16c4a6"), ("apachekafka", "Kafka", CREAM), ("docker", "Docker", "#3fa3f5"),
                         ("kubernetes", "Kubernetes", "#6b96f5"), ("amazonwebservices", "AWS", "#ff9f1c")]),
    ("Data", [("postgresql", "PostgreSQL", "#7ea7e0"), ("redis", "Redis", "#ff5a4a"), ("sqlite", "SQLite", "#5cb8ea"),
              ("mongodb", "MongoDB", "#5cbf4f")]),
    ("AI / ML", [("langchain", "LangChain", "#5fd3b0"), ("ollama", "Ollama", CREAM), ("scikitlearn", "scikit-learn", "#f7a13e")]),
    ("Frontend", [("react", "React", "#61DAFB"), ("nextdotjs", "Next.js", CREAM), ("angular", "Angular", "#ff4f5e")]),
]


def stack():
    w, pad, row_h, tile, gap = 1000, 36, 142, 84, 16
    h = pad * 2 + row_h * len(STACK) - 12
    body = []
    for i, (cat, items) in enumerate(STACK):
        y = pad + i * row_h
        body.append(f'<path d="{text(cat.upper(), 40, y + 50, 19, spacing=1.2)}" fill="{GOLD}"/>')
        body.append(f'<rect x="40" y="{y + 61}" width="38" height="3" rx="1.5" fill="{GREEN}"/>')
        for j, (slug, label, color) in enumerate(items):
            x = 256 + j * (tile + gap)
            body.append(f'<rect x="{x}" y="{y}" width="{tile}" height="{tile}" rx="18" fill="{CREAM}" fill-opacity=".07" '
                        f'stroke="{CREAM}" stroke-opacity=".16" stroke-width="1.5"/>'
                        f'<circle cx="{x + tile / 2}" cy="{y + tile / 2}" r="31" fill="{color}" opacity=".13"/>'
                        f'{icon(slug, x + (tile - 40) / 2, y + (tile - 40) / 2, 40, color)}'
                        f'<path d="{text(label, x + tile / 2, y + tile + 24, 16, "baloo600.ttf", "middle")}" fill="{CREAM}" opacity=".88"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<title>Tech stack: {", ".join(l for _, its in STACK for _, l, _ in its)}</title>{TWINKLE}<defs>{sky_defs("sky", w, h)}
<clipPath id="c"><rect width="{w}" height="{h}" rx="22"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#sky)"/><rect width="{w}" height="{h}" fill="url(#skyv)"/>
{stars(w, h * .5, 40, 11)}{"".join(body)}</g></svg>"""


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    save("banner.svg", banner())
    save("stack.svg", stack())
    for name in ["Featured Projects", "Biggest Update", "Newest Creations", "Experience", "Education", "Tech Stack", "Activity", "Profile Views"]:
        save("h-" + name.lower().replace(" ", "-") + ".svg", header(name))
    save("btn-portfolio.svg", button("Portfolio", "googlechrome", GREEN))
    save("btn-linkedin.svg", button("LinkedIn", "linkedin", "#0A66C2"))
    save("btn-email.svg", button("Email", "gmail", "#D14836"))
    print(sorted(os.listdir(OUT)))
