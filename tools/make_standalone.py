"""Turn an `embed-resources: true` render into one HTML file that runs from disk.

Usage: python tools/make_standalone.py IN.html OUT.html

What Quarto's embedding misses, and what this fixes:
  * OJS refuses to run from file:// URLs -> remove that guard.
  * Libraries loaded at runtime from slides/vendor (OJS require, KaTeX loader)
    -> inline them as plain <script>s at the top of <head>, before the OJS
       runtime defines AMD `define`, so they become globals (window.d3, ...).
       _helpers.qmd picks those up via `window.X ?? require(...)`.
  * KaTeX CSS/fonts -> inline the CSS with woff2 fonts as data URIs.
"""
import base64
import re
import sys
from pathlib import Path

VENDOR = Path(__file__).resolve().parent.parent / "slides" / "vendor"
SCRIPTS = ["d3.min.js", "plot.umd.min.js", "plotly.min.js", "katex/katex.min.js"]


def must_replace(s, old, new):
    if old not in s:
        sys.exit(f"make_standalone: expected snippet not found (Quarto changed?):\n{old}")
    return s.replace(old, new)


def katex_css():
    css = (VENDOR / "katex/katex.min.css").read_text()

    def font(m):
        b64 = base64.b64encode((VENDOR / "katex" / m.group(1)).read_bytes()).decode()
        return f'url(data:font/woff2;base64,{b64}) format("woff2")'

    # keep only the woff2 source of each @font-face
    css = re.sub(r'url\((fonts/[^)]+\.woff2)\) format\("woff2"\)(,url\([^)]+\) format\("[a-z]+"\))*', font, css)
    return css


def main(src, dst):
    html = Path(src).read_text()

    html = must_replace(html, 'if (window.location.protocol === "file:") {', "if (false) {")

    # KaTeX loader: the library is already global, so render straight away
    html = must_replace(
        html,
        'var script = document.createElement("script");\n      script.src = "vendor/katex/katex.min.js";',
        'if (window.katex) { renderMathElements(); return; }\n'
        '      var script = document.createElement("script");\n      script.src = "vendor/katex/katex.min.js";',
    )
    html = must_replace(html, 'link.href = "vendor/katex/katex.min.css";\n      head.appendChild(link);',
                        'link.href = "vendor/katex/katex.min.css";')

    # charset must stay within the first 1024 bytes, ahead of the inlined libraries
    inline = ['<meta charset="utf-8">', f"<style>{katex_css()}</style>"]
    for name in SCRIPTS:
        js = (VENDOR / name).read_text().replace("</script", "<\\/script")
        inline.append(f"<script>{js}</script>")
    html = re.sub(r"<head[^>]*>", lambda m: m.group(0) + "\n" + "\n".join(inline), html, count=1)

    Path(dst).write_text(html)
    print(f"wrote {dst} ({Path(dst).stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main(*sys.argv[1:3])
