"""
Smoke test for the Bootstrap 5.3 renderer.

1. Every component type in the catalogue renders without error and produces
   non-empty, non-error-comment output.
2. Every theme slug resolves to a URL.
3. A realistic multi-component page parses as valid HTML.
4. The theme fallback works.
5. Unknown components are harmless.
6. The <html> escape-hatch sanitises dangerous input.
7. render_fragment returns body-only output.
"""
import sys
import html.parser
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.services.component_catalogue import TYPES, new_node  # noqa: E402
from app.services.bootstrap_renderer import render_page, render_fragment, Renderer  # noqa: E402
from app.services.bootstrap_themes import THEMES, theme_exists  # noqa: E402


# 1. Every type renders --------------------------------------------------
r = Renderer()
failures = []
for t_name in TYPES:
    node = new_node(t_name)
    try:
        out = r.render_node(node)
    except Exception as exc:
        failures.append((t_name, f"exception: {exc}"))
        continue
    if not out.strip():
        failures.append((t_name, "empty output"))
    elif out.lstrip().startswith("<!-- render error"):
        failures.append((t_name, f"render error comment: {out[:200]}"))

if failures:
    print("FAILURES:")
    for name, reason in failures:
        print(f"  - {name}: {reason}")
    sys.exit(1)
print(f"[ok] All {len(TYPES)} component types render cleanly.")

# 2. Themes --------------------------------------------------------------
for t in THEMES:
    assert theme_exists(t["slug"]), t["slug"]
print(f"[ok] All {len(THEMES)} themes registered.")

# 3. Realistic page ------------------------------------------------------
sample = {
    "type": "page",
    "props": {},
    "children": [
        new_node("navbar"),
        new_node("hero"),
        {
            "type": "section",
            "props": {"padding": "py-5"},
            "children": [
                {
                    "type": "container",
                    "props": {},
                    "children": [
                        new_node("heading"),
                        {
                            "type": "row",
                            "props": {"gutter": "g-4"},
                            "children": [
                                {"type": "col", "props": {"md": "4"}, "children": [new_node("card")]},
                                {"type": "col", "props": {"md": "4"}, "children": [new_node("card")]},
                                {"type": "col", "props": {"md": "4"}, "children": [new_node("card")]},
                            ],
                        },
                    ],
                },
            ],
        },
        new_node("accordion"),
        new_node("carousel"),
        new_node("footer"),
    ],
}

for theme in ("default", "cosmo", "darkly"):
    doc = render_page(sample, title="Acme Co", theme=theme, description="Test page.")
    assert "<!doctype html>" in doc
    assert "Acme Co" in doc
    if theme == "default":
        assert "bootswatch" not in doc
        assert "bootstrap.min.css" in doc
    else:
        assert f"bootswatch" in doc and theme in doc

    class _P(html.parser.HTMLParser):
        def __init__(self):
            super().__init__()
            self.errors = []

        def error(self, msg):
            self.errors.append(msg)

    p = _P()
    p.feed(doc)
    assert not p.errors, p.errors

print("[ok] Sample page renders across default + Bootswatch themes and parses.")

# 4. Invalid theme -> default -------------------------------------------
doc = render_page({"type": "paragraph", "props": {"text": "hi"}},
                  theme="does-not-exist")
assert "bootstrap.min.css" in doc and "bootswatch" not in doc
print("[ok] Invalid theme falls back to default.")

# 5. Unknown component is harmless --------------------------------------
weird = r.render_node({"type": "no-such-thing", "props": {}})
assert "<!-- unknown component" in weird
print("[ok] Unknown types rendered as comments (non-breaking).")

# 6. HTML escape-hatch sanitises dangerous input -------------------------
evil = r.render_node({"type": "html", "props": {
    "html": '<p>ok</p><script>alert(1)</script><a href="javascript:alert(1)">x</a>'
}})
assert "<script" not in evil.lower()
assert "javascript:" not in evil.lower()
assert "<p>ok</p>" in evil
print("[ok] Raw-HTML component sanitised via bleach.")

# 7. render_fragment ----------------------------------------------------
frag = render_fragment({"type": "page", "props": {}, "children": [new_node("alert")]})
assert "<!doctype" not in frag.lower()
assert "alert-primary" in frag
print("[ok] render_fragment returns body-only output.")

# 8. Spot checks on a handful of tricky components ----------------------
acc = r.render_node(new_node("accordion"))
assert "accordion-item" in acc and "data-bs-toggle=\"collapse\"" in acc
assert acc.count("accordion-item") == 3  # default catalogue has 3 items

nav = r.render_node(new_node("navbar"))
assert "navbar-expand-lg" in nav and "navbar-brand" in nav
assert nav.count("nav-link") == 4  # Home/About/Services/Contact

bc = r.render_node(new_node("breadcrumb"))
# "Data" in default catalogue has empty href -> active
assert 'aria-current="page">Data</li>' in bc

btn = r.render_node(new_node("button"))
assert 'class="btn btn-primary' in btn

carousel_html = r.render_node(new_node("carousel"))
assert carousel_html.count("carousel-item") == 3
assert "carousel-control-prev" in carousel_html

tabs = r.render_node(new_node("nav-tabs"))
assert "nav-tabs" in tabs and tabs.count("tab-pane") == 3

modal = r.render_node(new_node("modal-trigger"))
assert 'data-bs-toggle="modal"' in modal and "modal-dialog" in modal

progress = r.render_node(new_node("progress"))
assert 'role="progressbar"' in progress and "50%" in progress

offcanvas = r.render_node(new_node("offcanvas-trigger"))
assert "offcanvas-start" in offcanvas

print("[ok] Spot-checks on accordion/navbar/breadcrumb/button/carousel/tabs/modal/progress/offcanvas all passed.")

# 9. New components added for Bootstrap 5.3 full coverage ---------------
table_html = r.render_node(new_node("table"))
assert "<table" in table_html and "<thead>" in table_html and "<tbody>" in table_html
assert "table-responsive" in table_html  # default wraps responsively
assert table_html.count("<tr>") == 4  # 1 header + 3 data rows

collapse_html = r.render_node(new_node("collapse"))
assert 'data-bs-toggle="collapse"' in collapse_html and 'class="collapse' in collapse_html

tooltip_html = r.render_node(new_node("tooltip"))
assert 'data-bs-toggle="tooltip"' in tooltip_html
assert 'data-bs-placement="top"' in tooltip_html

popover_html = r.render_node(new_node("popover"))
assert 'data-bs-toggle="popover"' in popover_html
assert 'data-bs-content=' in popover_html

scrollspy_html = r.render_node(new_node("scrollspy"))
assert 'data-bs-spy="scroll"' in scrollspy_html
assert scrollspy_html.count("<h4") == 3

nav_html = r.render_node(new_node("nav"))
assert '<ul class="nav' in nav_html and "nav-link active" in nav_html and "disabled" in nav_html

back_html = r.render_node(new_node("back-to-top"))
assert 'position-fixed' in back_html and 'bi-arrow-up' in back_html

header_html = r.render_node(new_node("header"))
assert "<header" in header_html and "display-5" in header_html

clearfix_html = r.render_node(new_node("clearfix"))
assert 'class="clearfix' in clearfix_html

stretched_html = r.render_node(new_node("stretched-link"))
assert "stretched-link" in stretched_html

truncate_html = r.render_node(new_node("text-truncate"))
assert "text-truncate" in truncate_html and "max-width:250px" in truncate_html

iconlink_html = r.render_node(new_node("icon-link"))
assert "icon-link" in iconlink_html and "bi-box-arrow-up-right" in iconlink_html

cardgroup_html = r.render_node({
    "type": "card-group", "props": {},
    "children": [new_node("card"), new_node("card"), new_node("card")]
})
assert "card-group" in cardgroup_html and cardgroup_html.count("class=\"card") >= 3

print("[ok] All 13 newly-added components render correctly.")

# 10. Generated pages include auto-init script for tooltips/popovers ----
full = render_page(
    {"type": "page", "props": {}, "children": [new_node("tooltip"), new_node("popover")]}
)
assert "new bootstrap.Tooltip" in full
assert "new bootstrap.Popover" in full
print("[ok] render_page injects auto-init JS for tooltips & popovers.")

print("\nALL RENDERER SMOKE TESTS PASSED")
