"""Build pegasus_v44.html: the template with the live CSS, sprite and font inlined.

Run from v44_planning/:  python -X utf8 build/build-v44.py
The live files in build/live/ were read from Pegasus origin/dev (build/live/source.txt).
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
LIVE = ROOT / "live"
OUT = ROOT.parent / "pegasus_v44.html"


def read(name: str) -> str:
    return (LIVE / name).read_text(encoding="utf-8")


def css_without_font_face(css: str) -> str:
    # The font is inlined separately; the live @font-face points at a fingerprinted path.
    return re.sub(r"@font-face\{[^}]*\}", "", css)


def main() -> None:
    template = (ROOT / "template-v44.html").read_text(encoding="utf-8")
    sprite = read("lucide-sprite.svg").replace("<svg ", '<svg style="display:none" aria-hidden="true" ', 1)
    font = base64.b64encode((LIVE / "InterVariable.woff2").read_bytes()).decode("ascii")
    replacements = {
        "/*INTER_B64*/": font,
        "/*SITE_CSS*/": css_without_font_face(read("site.css")),
        "/*INBOX_CSS*/": read("inbox.css"),
        "<!--SPRITE-->": sprite,
    }
    for marker, value in replacements.items():
        if template.count(marker) != 1:
            raise SystemExit(f"marker {marker} must appear exactly once")
        template = template.replace(marker, value)
    OUT.write_text(template, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
