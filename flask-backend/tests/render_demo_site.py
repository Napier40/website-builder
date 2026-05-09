"""
Render a comprehensive demo page exercising *every* component and save it
to /workspace/demo-site.html for visual inspection in a browser.
"""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.services.component_catalogue import TYPES, new_node  # noqa: E402
from app.services.bootstrap_renderer import render_page  # noqa: E402


# Group every component by its category so the demo page is organised.
by_category: dict[str, list[str]] = {}
for name, spec in TYPES.items():
    by_category.setdefault(spec["category"], []).append(name)

# Build page -----------------------------------------------------------------
children: list[dict] = [
    new_node("navbar", **{}),
    {
        "type": "hero",
        "props": {
            "title": "Bootstrap 5.3 Component Showcase",
            "subtitle": "Every component in the catalogue, rendered from JSON by the Python renderer.",
            "buttonText": "View on GitHub",
            "buttonHref": "#",
            "variant": "light",
            "bg": "bg-primary",
            "textColor": "text-white",
            "align": "text-center",
            "classes": "p-5",
        },
    },
]

for category, names in by_category.items():
    children.append({
        "type": "section",
        "props": {"padding": "py-5", "bg": "", "classes": ""},
        "children": [
            {"type": "container", "props": {}, "children": [
                {"type": "heading", "props": {"level": "h2", "text": category, "display": "", "align": "text-center", "classes": "mb-5"}},
                *[
                    {
                        "type": "container",
                        "props": {"classes": "mb-5 pb-4 border-bottom"},
                        "children": [
                            {"type": "heading", "props": {"level": "h5", "text": f"{TYPES[name]['label']}  ({name})", "classes": "text-body-secondary mb-3"}},
                            new_node(name),
                        ],
                    }
                    for name in names
                ],
            ]},
        ],
    })

children.append(new_node("footer"))

tree = {"type": "page", "props": {}, "children": children}

# Render 3 variants: default theme + 2 Bootswatch themes
for theme in ("default", "cosmo", "darkly"):
    html = render_page(
        tree,
        title=f"Renderer Showcase — {theme}",
        theme=theme,
        description="Every Bootstrap 5.3 component produced by the Python renderer.",
    )
    out = Path(f"/workspace/demo-site-{theme}.html")
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({len(html):,} chars)")
