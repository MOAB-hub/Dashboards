"""
Bundle hospital_dashboard.html into a single, fully self-contained file
that anyone can open in a browser -- no internet connection required.

It downloads the four CDN resources the dashboard currently relies on
(Bootstrap CSS, Bootstrap Icons CSS+fonts, Chart.js, SheetJS/xlsx),
inlines them directly into the HTML (<style>/<script> tags, icon font
as base64 data URIs), and writes the result to a new file so the
original is left untouched.
"""
import re
import base64
import urllib.request

SRC = "hospital_dashboard.html"
OUT = "hospital_dashboard_standalone.html"

CDN = {
    "bootstrap_css": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
    "icons_css":     "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css",
    "chartjs":       "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js",
    "xlsx":          "https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js",
}
ICON_FONT_BASE = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/"

def fetch_text(url):
    with urllib.request.urlopen(url) as r:
        return r.read().decode("utf-8")

def fetch_bytes(url):
    with urllib.request.urlopen(url) as r:
        return r.read()

print("Downloading Bootstrap CSS...")
bootstrap_css = fetch_text(CDN["bootstrap_css"])

print("Downloading Bootstrap Icons CSS...")
icons_css = fetch_text(CDN["icons_css"])

# Inline the icon font files referenced via url("./fonts/...") as base64 data URIs
print("Inlining icon font files (woff2/woff) as base64...")
def inline_font(match):
    rel_path = match.group(1)              # e.g. ./fonts/bootstrap-icons.woff2?HASH
    fmt = match.group(2)                   # woff2 / woff
    clean_path = rel_path.split("?")[0].lstrip("./")
    font_bytes = fetch_bytes(ICON_FONT_BASE + clean_path)
    mime = "font/woff2" if fmt == "woff2" else "font/woff"
    b64 = base64.b64encode(font_bytes).decode("ascii")
    return f'url("data:{mime};base64,{b64}") format("{fmt}")'

icons_css = re.sub(r'url\("(\./fonts/[^"]+)"\)\s*format\("(woff2?|woff)"\)', inline_font, icons_css)

print("Downloading Chart.js...")
chartjs = fetch_text(CDN["chartjs"])

print("Downloading SheetJS (xlsx)...")
xlsx = fetch_text(CDN["xlsx"])

print("Reading original dashboard HTML...")
with open(SRC, "r", encoding="utf-8") as f:
    html = f.read()

# Replace each <link>/<script> CDN tag with an inlined equivalent
html = html.replace(
    f'<link href="{CDN["bootstrap_css"]}" rel="stylesheet">',
    f'<style>\n{bootstrap_css}\n</style>'
)
html = html.replace(
    f'<link href="{CDN["icons_css"]}" rel="stylesheet">',
    f'<style>\n{icons_css}\n</style>'
)
html = html.replace(
    f'<script src="{CDN["chartjs"]}"></script>',
    f'<script>\n{chartjs}\n</script>'
)
html = html.replace(
    f'<script src="{CDN["xlsx"]}"></script>',
    f'<script>\n{xlsx}\n</script>'
)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\nDone! Wrote fully self-contained file: {OUT}")
print("This single file can be emailed or copied to any computer and opened")
print("directly in a browser -- no internet connection or server required.")
