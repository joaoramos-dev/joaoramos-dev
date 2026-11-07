"""Render the profile statistics as a self-contained CRT-style SVG."""

import html

from profile_stats.models import ProfileStats

WIDTH = 880
HEIGHT = 700
MONOSPACE = "'SFMono-Regular', Consolas, 'Liberation Mono', monospace"
METRIC_ICONS = (
    '<circle cx="8" cy="8" r="5.5"/><path d="M8 4.5V8l2.5 1.5"/>',
    '<path d="M2 5.5h5l1.5 1.5H14v6H2z"/><path d="M2 5.5V4h5l1.5 1.5"/>',
    '<circle cx="4" cy="4" r="1.5"/><circle cx="12" cy="12" r="1.5"/>'
    '<path d="M5.5 4H8a2 2 0 0 1 2 2v4a2 2 0 0 0 2 2"/>',
    '<path d="m8 1.5 1.9 4 4.4.6-3.2 3.1.8 4.4L8 11.5l-3.9 2.1.8-4.4-3.2-3.1 4.4-.6z" '
    'fill="#65D995"/>',
    '<path d="M3 4h10M3 8h6M3 12h10"/>',
)


def _render_definitions() -> list[str]:
    return [
        "<defs>",
        '<radialGradient id="screen" cx="50%" cy="45%" r="75%">'
        '<stop offset="0" stop-color="#0C1F18"/>'
        '<stop offset="0.7" stop-color="#07110D"/>'
        '<stop offset="1" stop-color="#030605"/>'
        "</radialGradient>",
        '<radialGradient id="vignette" cx="50%" cy="50%" r="72%">'
        '<stop offset="0.6" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000" stop-opacity="0.7"/>'
        "</radialGradient>",
        '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
        '<rect width="4" height="2" fill="#000" fill-opacity="0.28"/>'
        "</pattern>",
        '<filter id="glow" x="-5%" y="-5%" width="110%" height="110%">'
        '<feGaussianBlur stdDeviation="1.2" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        "</filter>",
        "</defs>",
    ]


def _render_introduction(user: str) -> list[str]:
    return [
        '<text x="48" y="56" font-size="15" fill="#E6A65C">'
        'joaoramos@dev:~$ <tspan fill="#65D995">whoami</tspan></text>',
        '<text x="48" y="94" font-size="26" font-weight="700" fill="#65D995">'
        'João Pedro da Cunha Ramos</text>',
        '<text x="48" y="132" font-size="15" fill="#E6A65C">'
        'joaoramos@dev:~$ <tspan fill="#65D995">roles</tspan></text>',
        '<text x="48" y="160" font-size="16" fill="#9CC9A7">&gt; software engineer</text>',
        '<text x="48" y="184" font-size="16" fill="#9CC9A7">&gt; data engineer</text>',
        '<text x="48" y="208" font-size="16" fill="#9CC9A7">&gt; AI engineer</text>',
        '<text x="48" y="248" font-size="15" fill="#E6A65C">'
        'joaoramos@dev:~$ <tspan fill="#65D995">whatido</tspan></text>',
        '<text x="48" y="276" font-size="14" fill="#9CC9A7">'
        'I transform disorganized business data into software capable of running</text>',
        '<text x="48" y="298" font-size="14" fill="#9CC9A7">'
        'in a production environment, and I apply AI where it truly saves effort.</text>',
        '<text x="48" y="320" font-size="14" fill="#9CC9A7">'
        'Worlds are born from ideas, and quality of life is born from technology.</text>',
        '<text x="48" y="404" font-size="15" fill="#E6A65C">'
        f'joaoramos@dev:~$ <tspan fill="#65D995">stats --user {html.escape(user)}</tspan></text>',
        '<line x1="48" y1="420" x2="832" y2="420" stroke="#9CC9A7" stroke-opacity="0.2"/>',
    ]


def _render_metrics(stats: ProfileStats) -> list[str]:
    metrics = (
        ("AGE", stats.age),
        ("REPOSITORIES", stats.repositories),
        ("COMMITS", stats.commits),
        ("STARS", stats.stars),
        ("LINES ADDED", stats.lines_added),
    )
    output: list[str] = []
    for index, (label, value) in enumerate(metrics):
        x = 48 + index * 156
        shown = "-" if value is None else f"{value:,}"
        value_color = "#65D995" if index == 0 else "#E8F1EA"
        output.extend([
            f'<text x="{x}" y="454" font-size="11" letter-spacing="1.5" '
            f'fill="#9CC9A7">{label}</text>',
            f'<rect x="{x}" y="476" width="20" height="20" rx="5" '
            'fill="#0C1F18" stroke="#1B3328"/>',
            f'<g transform="translate({x + 2} 478)" fill="none" stroke="#65D995" '
            f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">'
            f'{METRIC_ICONS[index]}</g>',
            f'<text x="{x + 27}" y="494" font-size="28" fill="{value_color}">{shown}</text>',
        ])
    return output


def _render_footer() -> list[str]:
    return [
        '<text x="48" y="552" font-size="15" fill="#E6A65C">'
        'joaoramos@dev:~$ <tspan fill="#65D995">links</tspan></text>',
        '<a href="https://github.com/joaoramos-dev" xlink:href="https://github.com/joaoramos-dev">'
        '<text x="48" y="584" font-size="14" fill="#65D995">github.com/joaoramos-dev</text></a>',
        '<a href="https://linkedin.com/in/joaoramos-dev" '
        'xlink:href="https://linkedin.com/in/joaoramos-dev">'
        '<text x="320" y="584" font-size="14" fill="#65D995">linkedin.com/in/joaoramos-dev</text></a>',
        '<text x="48" y="624" font-size="15" fill="#E6A65C">'
        'joaoramos@dev:~$ <tspan fill="#65D995">update</tspan></text>',
        '<text x="48" y="656" font-size="15" fill="#9CC9A7">loading'
        '<tspan>.</tspan>'
        '<tspan opacity="0"><animate attributeName="opacity" values="0;1;1;0" '
        'keyTimes="0;0.333;0.667;1" calcMode="discrete" dur="1.8s" '
        'repeatCount="indefinite"/>.</tspan>'
        '<tspan opacity="0"><animate attributeName="opacity" values="0;0;1;0" '
        'keyTimes="0;0.333;0.667;1" calcMode="discrete" dur="1.8s" '
        'repeatCount="indefinite"/>.</tspan></text>',
    ]


def render_profile(stats: ProfileStats, user: str) -> str:
    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        'aria-labelledby="title description">',
        "<title id=\"title\">João Pedro da Cunha Ramos — software, data and AI engineer</title>",
        '<desc id="description">A CRT-style terminal showing João’s introduction, live GitHub statistics, '
        'and links to GitHub and LinkedIn.</desc>',
        *_render_definitions(),
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#020403"/>',
        f'<rect x="12" y="12" width="{WIDTH - 24}" height="{HEIGHT - 24}" rx="18" '
        'fill="url(#screen)" stroke="#1B3328" stroke-width="2"/>',
        f'<g font-family="{MONOSPACE}" filter="url(#glow)">',
        *_render_introduction(user),
        *_render_metrics(stats),
        *_render_footer(),
        "</g>",
        f'<rect x="12" y="12" width="{WIDTH - 24}" height="{HEIGHT - 24}" rx="18" '
        'fill="url(#scan)" pointer-events="none"/>',
        f'<rect x="12" y="12" width="{WIDTH - 24}" height="{HEIGHT - 24}" rx="18" '
        'fill="url(#vignette)" pointer-events="none"/>',
        "</svg>",
    ]
    return "\n".join(output) + "\n"
