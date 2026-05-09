"""
Bootstrap 5.3 HTML Renderer
===========================

Walks a JSON node tree (shape defined in ``component_catalogue.py``) and
emits valid, CDN-linked Bootstrap 5.3 HTML.

Used by:
  * ``GET /s/<subdomain>``                -- public published site
  * ``GET /api/websites/<id>/preview``    -- live preview for the editor
  * Starter-site templates                -- rendered the same way

The renderer is *authoritative over* the catalogue, meaning the catalogue's
prop values are taken as-is: if the catalogue stores ``bg = "bg-primary"``
the renderer drops that class in directly -- no re-mapping. Likewise many
compound props use ``::``-separated multi-line strings; we parse those here.
"""
from __future__ import annotations

import html
from typing import Any, Callable, Dict, List, Optional, Tuple

import bleach

from .bootstrap_themes import (
    BOOTSTRAP_CSS,
    BOOTSTRAP_ICONS_CSS,
    BOOTSTRAP_JS,
    theme_css_url,
    theme_exists,
)

# ---------------------------------------------------------------------------
# Safe-HTML allow-list for the "html" escape-hatch component
# ---------------------------------------------------------------------------
_SAFE_TAGS = [
    "a", "abbr", "b", "blockquote", "br", "cite", "code", "dd", "div", "dl",
    "dt", "em", "figcaption", "figure", "h1", "h2", "h3", "h4", "h5", "h6",
    "hr", "i", "img", "kbd", "li", "mark", "ol", "p", "pre", "s", "small",
    "span", "strong", "sub", "sup", "table", "tbody", "td", "tfoot", "th",
    "thead", "tr", "u", "ul",
]
_SAFE_ATTRS = {
    "*":   ["class", "id", "style", "title", "aria-label", "role"],
    "a":   ["href", "target", "rel"],
    "img": ["src", "alt", "width", "height", "loading"],
}


# ---------------------------------------------------------------------------
# Small pure helpers
# ---------------------------------------------------------------------------
def _e(value: Any) -> str:
    """HTML-escape a value. None/missing -> empty string."""
    return html.escape("" if value is None else str(value), quote=True)


def _classes(*parts: Any) -> str:
    """Build a space-separated, de-duplicated class list from heterogeneous input."""
    out: List[str] = []
    for p in parts:
        if not p:
            continue
        for token in str(p).split():
            if token and token not in out:
                out.append(token)
    return " ".join(out)


def _attr(name: str, value: Any) -> str:
    """Render a single HTML attribute, or '' if the value is empty."""
    if value is None or value == "" or value is False:
        return ""
    if value is True:
        return f" {name}"
    return f' {name}="{_e(value)}"'


def _bool(v: Any) -> bool:
    """Loose boolean coercion -- handles JSON 'true'/'false'/'1'."""
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.lower() in ("1", "true", "yes", "on")
    return bool(v)


def _split_lines(raw: Any) -> List[str]:
    """Split a RICH multi-line prop into trimmed, non-empty lines."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    return [ln.strip() for ln in str(raw).splitlines() if ln.strip()]


def _split_parts(line: str, n: int = 2) -> List[str]:
    """Split a ``::``-separated line, padding to *n* parts with empty strings."""
    parts = [p.strip() for p in line.split("::")]
    while len(parts) < n:
        parts.append("")
    return parts[:n] if n else parts


# Auto-increment id generator (scoped per render) -- used for ARIA targets
class _IdFactory:
    def __init__(self) -> None:
        self._counts: Dict[str, int] = {}

    def make(self, prefix: str) -> str:
        self._counts[prefix] = self._counts.get(prefix, 0) + 1
        return f"{prefix}-{self._counts[prefix]}"


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------
class Renderer:
    """Walks a node tree and produces Bootstrap 5.3 HTML. Stateful only for id generation."""

    def __init__(self) -> None:
        self.ids = _IdFactory()
        self._dispatch: Dict[str, Callable[[Dict[str, Any]], str]] = {
            # Layout
            "container":        self._r_container,
            "row":              self._r_row,
            "col":              self._r_col,
            "section":          self._r_section,
            "stack":            self._r_stack,
            "grid":             self._r_grid,
            "divider":          self._r_divider,
            "vr":               self._r_vr,
            # Content
            "heading":          self._r_heading,
            "paragraph":        self._r_paragraph,
            "lead":             self._r_lead,
            "image":            self._r_image,
            "figure":           self._r_figure,
            "blockquote":       self._r_blockquote,
            "list":             self._r_list,
            "dl":               self._r_dl,
            "code":             self._r_code,
            "link":             self._r_link,
            "icon":             self._r_icon,
            # Forms
            "form":             self._r_form,
            "input":            self._r_input,
            "textarea":         self._r_textarea,
            "select":           self._r_select,
            "checkbox":         self._r_checkbox,
            "radio":            self._r_radio,
            "switch":           self._r_switch,
            "range":            self._r_range,
            "file":             self._r_file,
            "input-group":      self._r_input_group,
            # Components
            "accordion":        self._r_accordion,
            "alert":            self._r_alert,
            "badge":            self._r_badge,
            "breadcrumb":       self._r_breadcrumb,
            "button":           self._r_button,
            "button-group":     self._r_button_group,
            "card":             self._r_card,
            "carousel":         self._r_carousel,
            "close-button":     self._r_close_button,
            "dropdown":         self._r_dropdown,
            "list-group":       self._r_list_group,
            "modal-trigger":    self._r_modal_trigger,
            "navbar":           self._r_navbar,
            "nav-tabs":         self._r_nav_tabs,
            "offcanvas-trigger": self._r_offcanvas_trigger,
            "pagination":       self._r_pagination,
            "placeholder":      self._r_placeholder,
            "progress":         self._r_progress,
            "spinner":          self._r_spinner,
            "toast":            self._r_toast,
            "footer":           self._r_footer,
            "hero":             self._r_hero,
            "embed":            self._r_embed,
            "html":             self._r_html,
            # Helpers
            "spacer":           self._r_spacer,
            "ratio":            self._r_ratio,
            "visually-hidden":  self._r_visually_hidden,
        }

    # -- public API -------------------------------------------------------
    def render_node(self, node: Optional[Dict[str, Any]]) -> str:
        if not node or not isinstance(node, dict):
            return ""
        t = node.get("type")
        if not t:
            return ""
        fn = self._dispatch.get(t)
        if fn is None:
            return f"<!-- unknown component: {_e(t)} -->"
        try:
            return fn(node)
        except Exception as exc:  # never break a published page
            return f"<!-- render error in {_e(t)}: {_e(exc)} -->"

    def render_children(self, node: Dict[str, Any]) -> str:
        return "".join(self.render_node(c) for c in (node.get("children") or []))

    @staticmethod
    def _p(node: Dict[str, Any]) -> Dict[str, Any]:
        return node.get("props") or {}

    # =====================================================================
    # LAYOUT
    # =====================================================================
    def _r_container(self, n):
        p = self._p(n)
        fluid = p.get("fluid", "")
        if fluid == "fluid":
            cls = "container-fluid"
        elif fluid:
            cls = f"container-{fluid}"
        else:
            cls = "container"
        return (
            f'<div class="{_classes(cls, p.get("classes"))}">'
            f"{self.render_children(n)}</div>"
        )

    def _r_row(self, n):
        p = self._p(n)
        cls = _classes("row", p.get("gutter"), p.get("align"), p.get("justify"), p.get("classes"))
        return f'<div class="{cls}">{self.render_children(n)}</div>'

    def _r_col(self, n):
        p = self._p(n)
        parts: List[str] = []
        # xs is unprefixed: col / col-auto / col-6
        xs = p.get("xs", "")
        if xs == "auto":
            parts.append("col-auto")
        elif xs:
            parts.append(f"col-{xs}")
        for bp in ("sm", "md", "lg", "xl", "xxl"):
            v = p.get(bp)
            if v == "auto":
                parts.append(f"col-{bp}-auto")
            elif v:
                parts.append(f"col-{bp}-{v}")
        if not parts:
            parts.append("col")  # bare column = flex-equal
        parts.append(p.get("classes", ""))
        return f'<div class="{_classes(*parts)}">{self.render_children(n)}</div>'

    def _r_section(self, n):
        p = self._p(n)
        return (
            f'<section class="{_classes(p.get("padding"), p.get("bg"), p.get("classes"))}">'
            f"{self.render_children(n)}</section>"
        )

    def _r_stack(self, n):
        p = self._p(n)
        return (
            f'<div class="{_classes(p.get("direction", "vstack"), p.get("gap"), p.get("classes"))}">'
            f"{self.render_children(n)}</div>"
        )

    def _r_grid(self, n):
        p = self._p(n)
        cols = int(p.get("cols") or 3)
        style = f"grid-template-columns: repeat({cols}, 1fr);"
        return (
            f'<div class="{_classes("d-grid", p.get("gap"), p.get("classes"))}"'
            f' style="{style}">{self.render_children(n)}</div>'
        )

    def _r_divider(self, n):
        p = self._p(n)
        return f'<hr class="{_classes(p.get("classes"))}">'

    def _r_vr(self, n):
        p = self._p(n)
        return f'<div class="{_classes("vr", p.get("classes"))}"></div>'

    # =====================================================================
    # CONTENT
    # =====================================================================
    @staticmethod
    def _heading_tag(raw: Any) -> str:
        """Accept 'h2' / 2 / '2' -> 'h2'. Clamps to h1..h6."""
        if raw is None:
            return "h2"
        s = str(raw).strip().lower()
        if not s.startswith("h"):
            s = "h" + s
        try:
            n = int(s[1:])
            n = max(1, min(6, n))
            return f"h{n}"
        except (ValueError, TypeError):
            return "h2"

    def _r_heading(self, n):
        p = self._p(n)
        tag = self._heading_tag(p.get("level"))
        return (
            f'<{tag} class="{_classes(p.get("display"), p.get("align"), p.get("classes"))}">'
            f"{_e(p.get('text', 'Heading'))}</{tag}>"
        )

    def _r_paragraph(self, n):
        p = self._p(n)
        lead_cls = "lead" if _bool(p.get("lead")) else ""
        return (
            f'<p class="{_classes(lead_cls, p.get("align"), p.get("classes"))}">'
            f"{_e(p.get('text', ''))}</p>"
        )

    def _r_lead(self, n):
        p = self._p(n)
        return (
            f'<p class="{_classes("lead", p.get("classes"))}">'
            f"{_e(p.get('text', ''))}</p>"
        )

    def _r_image(self, n):
        p = self._p(n)
        parts: List[str] = []
        if _bool(p.get("fluid", True)):
            parts.append("img-fluid")
        if _bool(p.get("thumbnail")):
            parts.append("img-thumbnail")
        rounded = p.get("rounded")
        if rounded:
            parts.append(rounded)
        parts.append(p.get("classes", ""))
        src = p.get("src") or "https://picsum.photos/800/450"
        return (
            f'<img src="{_e(src)}" alt="{_e(p.get("alt", ""))}" '
            f'class="{_classes(*parts)}" loading="lazy">'
        )

    def _r_figure(self, n):
        p = self._p(n)
        src = p.get("src") or "https://picsum.photos/600/400"
        return (
            f'<figure class="{_classes("figure", p.get("classes"))}">'
            f'<img src="{_e(src)}" alt="{_e(p.get("alt", ""))}" class="figure-img img-fluid rounded">'
            f'<figcaption class="figure-caption">{_e(p.get("caption", ""))}</figcaption>'
            f"</figure>"
        )

    def _r_blockquote(self, n):
        p = self._p(n)
        source = p.get("source")
        cite = p.get("cite")
        footer_html = ""
        if source or cite:
            cite_html = f' <cite title="{_e(cite)}">{_e(cite)}</cite>' if cite else ""
            footer_html = (
                f'<figcaption class="blockquote-footer">{_e(source)}{cite_html}</figcaption>'
            )
        return (
            f'<figure class="{_classes(p.get("align"), p.get("classes"))}">'
            f'<blockquote class="blockquote"><p>{_e(p.get("text", ""))}</p></blockquote>'
            f"{footer_html}</figure>"
        )

    def _r_list(self, n):
        p = self._p(n)
        tag = "ol" if _bool(p.get("ordered")) else "ul"
        parts: List[str] = []
        if _bool(p.get("unstyled")):
            parts.append("list-unstyled")
        if _bool(p.get("inline")):
            parts.append("list-inline")
        parts.append(p.get("classes", ""))
        item_cls = "list-inline-item" if _bool(p.get("inline")) else ""
        items = "".join(
            f'<li class="{item_cls}">{_e(it)}</li>' for it in _split_lines(p.get("items"))
        )
        return f'<{tag} class="{_classes(*parts)}">{items}</{tag}>'

    def _r_dl(self, n):
        p = self._p(n)
        body: List[str] = []
        for line in _split_lines(p.get("items")):
            term, desc = _split_parts(line, 2)
            body.append(f"<dt>{_e(term)}</dt><dd>{_e(desc)}</dd>")
        return f'<dl class="{_classes(p.get("classes"))}">{"".join(body)}</dl>'

    def _r_code(self, n):
        p = self._p(n)
        text = _e(p.get("text", ""))
        if _bool(p.get("inline")):
            return f'<code class="{_classes(p.get("classes"))}">{text}</code>'
        return f'<pre class="{_classes(p.get("classes"))}"><code>{text}</code></pre>'

    def _r_link(self, n):
        p = self._p(n)
        target = p.get("target") or ""
        rel = "noopener noreferrer" if target == "_blank" else ""
        return (
            f'<a href="{_e(p.get("href", "#"))}" class="{_classes(p.get("classes"))}"'
            f'{_attr("target", target)}{_attr("rel", rel)}>'
            f"{_e(p.get('text', 'Link'))}</a>"
        )

    def _r_icon(self, n):
        p = self._p(n)
        name = p.get("name") or "star"
        if not name.startswith("bi-"):
            name = "bi-" + name
        return (
            f'<i class="{_classes("bi", name, p.get("size"), p.get("color"), p.get("classes"))}"'
            f' aria-hidden="true"></i>'
        )

    # =====================================================================
    # FORMS
    # =====================================================================
    def _r_form(self, n):
        p = self._p(n)
        return (
            f'<form class="{_classes(p.get("classes"))}"'
            f'{_attr("action", p.get("action", "#"))}'
            f'{_attr("method", p.get("method", "post"))}>'
            f"{self.render_children(n)}</form>"
        )

    def _r_input(self, n):
        p = self._p(n)
        iid = p.get("id") or self.ids.make("input")
        floating = _bool(p.get("floating"))
        label_text = p.get("label", "")
        help_text = p.get("helpText", "") or p.get("help", "")
        size_cls = p.get("size", "")
        inp = (
            f'<input type="{_e(p.get("type", "text"))}" '
            f'class="{_classes("form-control", size_cls)}" id="{_e(iid)}"'
            f'{_attr("name", p.get("name"))}'
            f'{_attr("placeholder", p.get("placeholder") or (label_text if floating else None))}'
            f'{_attr("value", p.get("value"))}'
            f'{_attr("required", _bool(p.get("required")))}>'
        )
        help_html = (
            f'<div class="form-text">{_e(help_text)}</div>' if help_text else ""
        )
        if floating:
            return (
                f'<div class="{_classes("form-floating", "mb-3", p.get("classes"))}">'
                f'{inp}<label for="{_e(iid)}">{_e(label_text)}</label>{help_html}</div>'
            )
        label_html = (
            f'<label for="{_e(iid)}" class="form-label">{_e(label_text)}</label>'
            if label_text else ""
        )
        return (
            f'<div class="{_classes("mb-3", p.get("classes"))}">'
            f"{label_html}{inp}{help_html}</div>"
        )

    def _r_textarea(self, n):
        p = self._p(n)
        iid = p.get("id") or self.ids.make("textarea")
        floating = _bool(p.get("floating"))
        label_text = p.get("label", "")
        help_text = p.get("helpText", "")
        ta = (
            f'<textarea class="form-control" id="{_e(iid)}"'
            f'{_attr("name", p.get("name"))}'
            f'{_attr("rows", p.get("rows", 3))}'
            f'{_attr("placeholder", p.get("placeholder") or (label_text if floating else None))}'
            f'{_attr("required", _bool(p.get("required")))}>'
            f"{_e(p.get('value', ''))}</textarea>"
        )
        help_html = (
            f'<div class="form-text">{_e(help_text)}</div>' if help_text else ""
        )
        if floating:
            return (
                f'<div class="{_classes("form-floating", "mb-3", p.get("classes"))}">'
                f'{ta}<label for="{_e(iid)}">{_e(label_text)}</label>{help_html}</div>'
            )
        label_html = (
            f'<label for="{_e(iid)}" class="form-label">{_e(label_text)}</label>'
            if label_text else ""
        )
        return (
            f'<div class="{_classes("mb-3", p.get("classes"))}">'
            f"{label_html}{ta}{help_html}</div>"
        )

    def _r_select(self, n):
        p = self._p(n)
        iid = p.get("id") or self.ids.make("select")
        floating = _bool(p.get("floating"))
        label_text = p.get("label", "")
        size_cls = p.get("size", "")
        opts_html = "".join(
            f"<option>{_e(opt)}</option>" for opt in _split_lines(p.get("options"))
        )
        sel = (
            f'<select class="{_classes("form-select", size_cls)}" id="{_e(iid)}"'
            f'{_attr("name", p.get("name"))}'
            f'{_attr("multiple", _bool(p.get("multiple")))}>{opts_html}</select>'
        )
        if floating:
            return (
                f'<div class="{_classes("form-floating", "mb-3", p.get("classes"))}">'
                f'{sel}<label for="{_e(iid)}">{_e(label_text)}</label></div>'
            )
        label_html = (
            f'<label for="{_e(iid)}" class="form-label">{_e(label_text)}</label>'
            if label_text else ""
        )
        return (
            f'<div class="{_classes("mb-3", p.get("classes"))}">{label_html}{sel}</div>'
        )

    def _r_checkbox(self, n):
        return self._check_like(n, "checkbox", switch=False)

    def _r_switch(self, n):
        return self._check_like(n, "checkbox", switch=True)

    def _check_like(self, n, kind: str, switch: bool):
        p = self._p(n)
        iid = p.get("id") or self.ids.make(kind)
        wrap = "form-check" + (" form-switch" if switch else "")
        return (
            f'<div class="{_classes(wrap, p.get("classes"))}">'
            f'<input class="form-check-input" type="{kind}" id="{_e(iid)}"'
            f'{_attr("name", p.get("name"))}'
            f'{_attr("checked", _bool(p.get("checked")))}'
            f'{_attr("role", "switch" if switch else None)}>'
            f'<label class="form-check-label" for="{_e(iid)}">'
            f"{_e(p.get('label', 'Option'))}</label></div>"
        )

    def _r_radio(self, n):
        p = self._p(n)
        name = p.get("name") or "option"
        inline = _bool(p.get("inline"))
        options = _split_lines(p.get("options"))
        label_html = (
            f'<div class="form-label">{_e(p.get("label", ""))}</div>'
            if p.get("label") else ""
        )
        items: List[str] = []
        for i, opt in enumerate(options):
            rid = self.ids.make("radio")
            wrap = "form-check" + (" form-check-inline" if inline else "")
            checked = _attr("checked", i == 0)
            items.append(
                f'<div class="{wrap}">'
                f'<input class="form-check-input" type="radio" name="{_e(name)}" id="{rid}"'
                f' value="{_e(opt)}"{checked}>'
                f'<label class="form-check-label" for="{rid}">{_e(opt)}</label></div>'
            )
        return (
            f'<div class="{_classes("mb-3", p.get("classes"))}">'
            f"{label_html}{''.join(items)}</div>"
        )

    def _r_range(self, n):
        p = self._p(n)
        iid = p.get("id") or self.ids.make("range")
        label_text = p.get("label", "")
        label_html = (
            f'<label for="{_e(iid)}" class="form-label">{_e(label_text)}</label>'
            if label_text else ""
        )
        return (
            f'<div class="{_classes("mb-3", p.get("classes"))}">{label_html}'
            f'<input type="range" class="form-range" id="{_e(iid)}"'
            f'{_attr("name", p.get("name"))}'
            f'{_attr("min", p.get("min", 0))}{_attr("max", p.get("max", 100))}'
            f'{_attr("step", p.get("step", 1))}{_attr("value", p.get("value", 50))}>'
            f"</div>"
        )

    def _r_file(self, n):
        p = self._p(n)
        iid = p.get("id") or self.ids.make("file")
        label_text = p.get("label", "")
        label_html = (
            f'<label for="{_e(iid)}" class="form-label">{_e(label_text)}</label>'
            if label_text else ""
        )
        return (
            f'<div class="{_classes("mb-3", p.get("classes"))}">{label_html}'
            f'<input class="form-control" type="file" id="{_e(iid)}"'
            f'{_attr("name", p.get("name"))}'
            f'{_attr("accept", p.get("accept"))}'
            f'{_attr("multiple", _bool(p.get("multiple")))}></div>'
        )

    def _r_input_group(self, n):
        p = self._p(n)
        prepend = p.get("prepend")
        append = p.get("append")
        prepend_html = (
            f'<span class="input-group-text">{_e(prepend)}</span>' if prepend else ""
        )
        append_html = (
            f'<span class="input-group-text">{_e(append)}</span>' if append else ""
        )
        inner = self.render_children(n) or (
            f'<input type="text" class="form-control"'
            f'{_attr("name", p.get("name"))}'
            f'{_attr("placeholder", p.get("placeholder"))}>'
        )
        return (
            f'<div class="{_classes("input-group", "mb-3", p.get("size"), p.get("classes"))}">'
            f"{prepend_html}{inner}{append_html}</div>"
        )

    # =====================================================================
    # COMPONENTS
    # =====================================================================
    def _r_accordion(self, n):
        p = self._p(n)
        aid = self.ids.make("accordion")
        flush = " accordion-flush" if _bool(p.get("flush")) else ""
        open_first = _bool(p.get("openFirst", True))
        lines = _split_lines(p.get("items"))
        items: List[str] = []
        for i, line in enumerate(lines):
            title, body = _split_parts(line, 2)
            hid, cid = f"{aid}-h{i}", f"{aid}-c{i}"
            is_open = open_first and i == 0
            btn_cls = "accordion-button" if is_open else "accordion-button collapsed"
            col_cls = "accordion-collapse collapse" + (" show" if is_open else "")
            items.append(
                f'<div class="accordion-item">'
                f'<h2 class="accordion-header" id="{hid}">'
                f'<button class="{btn_cls}" type="button" data-bs-toggle="collapse"'
                f' data-bs-target="#{cid}" aria-expanded="{"true" if is_open else "false"}"'
                f' aria-controls="{cid}">{_e(title)}</button></h2>'
                f'<div id="{cid}" class="{col_cls}" aria-labelledby="{hid}"'
                f' data-bs-parent="#{aid}">'
                f'<div class="accordion-body">{_e(body)}</div></div></div>'
            )
        return (
            f'<div class="{_classes("accordion" + flush, p.get("classes"))}" id="{aid}">'
            f"{''.join(items)}</div>"
        )

    def _r_alert(self, n):
        p = self._p(n)
        variant = p.get("variant", "primary")
        dismissible = _bool(p.get("dismissible"))
        close_btn = (
            '<button type="button" class="btn-close" data-bs-dismiss="alert"'
            ' aria-label="Close"></button>' if dismissible else ""
        )
        extra = " alert-dismissible fade show" if dismissible else ""
        return (
            f'<div class="alert alert-{_e(variant)}{extra} {_classes(p.get("classes"))}"'
            f' role="alert">{_e(p.get("text", ""))}{close_btn}</div>'
        )

    def _r_badge(self, n):
        p = self._p(n)
        variant = p.get("variant", "secondary")
        pill = "rounded-pill" if _bool(p.get("pill")) else ""
        return (
            f'<span class="{_classes("badge", f"text-bg-{variant}", pill, p.get("classes"))}">'
            f"{_e(p.get('text', 'New'))}</span>"
        )

    def _r_breadcrumb(self, n):
        p = self._p(n)
        lines = _split_lines(p.get("items"))
        lis: List[str] = []
        for line in lines:
            label, href = _split_parts(line, 2)
            if not href:  # empty href => active (per catalogue convention)
                lis.append(
                    f'<li class="breadcrumb-item active" aria-current="page">{_e(label)}</li>'
                )
            else:
                lis.append(
                    f'<li class="breadcrumb-item"><a href="{_e(href)}">{_e(label)}</a></li>'
                )
        return (
            f'<nav aria-label="breadcrumb" class="{_classes(p.get("classes"))}">'
            f'<ol class="breadcrumb">{"".join(lis)}</ol></nav>'
        )

    def _r_button(self, n):
        p = self._p(n)
        variant = p.get("variant", "primary")
        parts = [f"btn btn-{variant}", p.get("size", "")]
        if _bool(p.get("block")):
            parts.append("w-100")
        if _bool(p.get("disabled")):
            parts.append("disabled")
        parts.append(p.get("classes", ""))
        icon = p.get("icon")
        icon_html = ""
        if icon:
            name = icon if str(icon).startswith("bi-") else f"bi-{icon}"
            icon_html = f'<i class="bi {name} me-1" aria-hidden="true"></i>'
        href = p.get("href")
        text_html = f"{icon_html}{_e(p.get('text', 'Button'))}"
        if href:
            disabled_attr = ' tabindex="-1" aria-disabled="true"' if _bool(p.get("disabled")) else ""
            return (
                f'<a href="{_e(href)}" class="{_classes(*parts)}" role="button"'
                f"{disabled_attr}>{text_html}</a>"
            )
        return (
            f'<button type="button" class="{_classes(*parts)}"'
            f'{_attr("disabled", _bool(p.get("disabled")))}>{text_html}</button>'
        )

    def _r_button_group(self, n):
        p = self._p(n)
        base = "btn-group-vertical" if _bool(p.get("vertical")) else "btn-group"
        return (
            f'<div class="{_classes(base, p.get("size"), p.get("classes"))}"'
            f' role="group">{self.render_children(n)}</div>'
        )

    def _r_card(self, n):
        p = self._p(n)
        parts = ["card", p.get("bg"), p.get("border"), p.get("textColor"), p.get("classes")]
        img_html = ""
        if p.get("image"):
            img_html = (
                f'<img src="{_e(p["image"])}" class="card-img-top"'
                f' alt="{_e(p.get("alt", ""))}" loading="lazy">'
            )
        body_parts: List[str] = []
        if p.get("title"):
            body_parts.append(f'<h5 class="card-title">{_e(p["title"])}</h5>')
        if p.get("subtitle"):
            body_parts.append(
                f'<h6 class="card-subtitle mb-2 text-body-secondary">{_e(p["subtitle"])}</h6>'
            )
        if p.get("text"):
            body_parts.append(f'<p class="card-text">{_e(p["text"])}</p>')
        if p.get("buttonText"):
            body_parts.append(
                f'<a href="{_e(p.get("buttonHref", "#"))}" class="btn btn-primary">'
                f'{_e(p["buttonText"])}</a>'
            )
        body_parts.append(self.render_children(n))
        return (
            f'<div class="{_classes(*parts)}">'
            f'{img_html}<div class="card-body">{"".join(body_parts)}</div></div>'
        )

    def _r_carousel(self, n):
        p = self._p(n)
        cid = self.ids.make("carousel")
        slides_lines = _split_lines(p.get("slides"))
        indicators: List[str] = []
        inner: List[str] = []
        for i, line in enumerate(slides_lines):
            src, title, caption = _split_parts(line, 3)
            active = " active" if i == 0 else ""
            aria = ' aria-current="true"' if i == 0 else ""
            indicators.append(
                f'<button type="button" data-bs-target="#{cid}" data-bs-slide-to="{i}"'
                f' class="{active.strip()}"{aria} aria-label="Slide {i + 1}"></button>'
            )
            cap_html = (
                f'<div class="carousel-caption d-none d-md-block">'
                f'<h5>{_e(title)}</h5><p>{_e(caption)}</p></div>'
                if title or caption else ""
            )
            inner.append(
                f'<div class="carousel-item{active}">'
                f'<img src="{_e(src or "https://picsum.photos/1200/500")}" '
                f'class="d-block w-100" alt="{_e(title)}" loading="lazy">'
                f"{cap_html}</div>"
            )
        controls_html = (
            f'<button class="carousel-control-prev" type="button"'
            f' data-bs-target="#{cid}" data-bs-slide="prev">'
            f'<span class="carousel-control-prev-icon" aria-hidden="true"></span>'
            f'<span class="visually-hidden">Previous</span></button>'
            f'<button class="carousel-control-next" type="button"'
            f' data-bs-target="#{cid}" data-bs-slide="next">'
            f'<span class="carousel-control-next-icon" aria-hidden="true"></span>'
            f'<span class="visually-hidden">Next</span></button>'
        ) if _bool(p.get("controls", True)) else ""
        ind_html = (
            f'<div class="carousel-indicators">{"".join(indicators)}</div>'
            if _bool(p.get("indicators", True)) else ""
        )
        fade = " carousel-fade" if _bool(p.get("fade")) else ""
        ride = "carousel" if _bool(p.get("autoplay", True)) else "false"
        return (
            f'<div id="{cid}" class="carousel slide{fade} {_classes(p.get("classes"))}"'
            f' data-bs-ride="{ride}">'
            f"{ind_html}"
            f'<div class="carousel-inner">{"".join(inner)}</div>'
            f"{controls_html}</div>"
        )

    def _r_close_button(self, n):
        p = self._p(n)
        return (
            f'<button type="button" class="{_classes("btn-close", p.get("classes"))}"'
            f' aria-label="Close"></button>'
        )

    def _r_dropdown(self, n):
        p = self._p(n)
        variant = p.get("variant", "primary")
        label = p.get("label", "Dropdown")
        split = _bool(p.get("split"))
        lis: List[str] = []
        for line in _split_lines(p.get("items")):
            item_label, href = _split_parts(line, 2)
            if item_label == "---":
                lis.append('<li><hr class="dropdown-divider"></li>')
            else:
                lis.append(
                    f'<li><a class="dropdown-item" href="{_e(href or "#")}">'
                    f"{_e(item_label)}</a></li>"
                )
        menu = f'<ul class="dropdown-menu">{"".join(lis)}</ul>'
        if split:
            inner = (
                f'<button type="button" class="btn btn-{_e(variant)}">{_e(label)}</button>'
                f'<button type="button" class="btn btn-{_e(variant)} dropdown-toggle dropdown-toggle-split"'
                f' data-bs-toggle="dropdown" aria-expanded="false">'
                f'<span class="visually-hidden">Toggle Dropdown</span></button>'
                f"{menu}"
            )
            return (
                f'<div class="{_classes("btn-group", p.get("classes"))}">{inner}</div>'
            )
        return (
            f'<div class="{_classes("dropdown", p.get("classes"))}">'
            f'<button class="btn btn-{_e(variant)} dropdown-toggle" type="button"'
            f' data-bs-toggle="dropdown" aria-expanded="false">{_e(label)}</button>'
            f"{menu}</div>"
        )

    def _r_list_group(self, n):
        p = self._p(n)
        tag = "ol" if _bool(p.get("numbered")) else "ul"
        parts = ["list-group"]
        if _bool(p.get("flush")):
            parts.append("list-group-flush")
        if _bool(p.get("numbered")):
            parts.append("list-group-numbered")
        if _bool(p.get("horizontal")):
            parts.append("list-group-horizontal")
        parts.append(p.get("classes", ""))
        items_html = "".join(
            f'<li class="list-group-item">{_e(it)}</li>'
            for it in _split_lines(p.get("items"))
        )
        return f'<{tag} class="{_classes(*parts)}">{items_html}</{tag}>'

    def _r_modal_trigger(self, n):
        p = self._p(n)
        mid = self.ids.make("modal")
        variant = p.get("variant", "primary")
        size = p.get("size", "")
        dialog_cls = ["modal-dialog", size]
        if _bool(p.get("centered", True)):
            dialog_cls.append("modal-dialog-centered")
        if _bool(p.get("scrollable")):
            dialog_cls.append("modal-dialog-scrollable")
        return (
            f'<button type="button" class="btn btn-{_e(variant)} {_classes(p.get("classes"))}"'
            f' data-bs-toggle="modal" data-bs-target="#{mid}">'
            f"{_e(p.get('buttonText', 'Launch modal'))}</button>"
            f'<div class="modal fade" id="{mid}" tabindex="-1" aria-hidden="true">'
            f'<div class="{_classes(*dialog_cls)}"><div class="modal-content">'
            f'<div class="modal-header">'
            f'<h1 class="modal-title fs-5">{_e(p.get("modalTitle", "Modal title"))}</h1>'
            f'<button type="button" class="btn-close" data-bs-dismiss="modal"'
            f' aria-label="Close"></button></div>'
            f'<div class="modal-body">{_e(p.get("modalBody", ""))}</div>'
            f'<div class="modal-footer">'
            f'<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>'
            f'<button type="button" class="btn btn-primary">Save changes</button>'
            f"</div></div></div></div>"
        )

    def _r_navbar(self, n):
        p = self._p(n)
        variant = p.get("variant", "light")
        bg = p.get("bg", "bg-body-tertiary")
        expand = p.get("expand", "navbar-expand-lg")
        container = p.get("container", "container")
        sticky = "sticky-top" if _bool(p.get("sticky")) else ""
        nid = self.ids.make("navbar")
        data_theme = ' data-bs-theme="dark"' if variant == "dark" else ""
        links_html: List[str] = []
        for line in _split_lines(p.get("items")):
            parts = _split_parts(line, 3)
            label, href, active_flag = parts[0], parts[1], parts[2]
            active = " active" if active_flag.lower() in ("active", "true", "1") else ""
            aria = ' aria-current="page"' if active else ""
            links_html.append(
                f'<li class="nav-item"><a class="nav-link{active}"{aria}'
                f' href="{_e(href or "#")}">{_e(label)}</a></li>'
            )
        return (
            f'<nav class="{_classes("navbar", expand, bg, sticky, p.get("classes"))}"{data_theme}>'
            f'<div class="{_e(container)}">'
            f'<a class="navbar-brand" href="{_e(p.get("brandHref", "#"))}">'
            f"{_e(p.get('brand', 'Brand'))}</a>"
            f'<button class="navbar-toggler" type="button" data-bs-toggle="collapse"'
            f' data-bs-target="#{nid}" aria-controls="{nid}" aria-expanded="false"'
            f' aria-label="Toggle navigation">'
            f'<span class="navbar-toggler-icon"></span></button>'
            f'<div class="collapse navbar-collapse" id="{nid}">'
            f'<ul class="navbar-nav ms-auto mb-2 mb-lg-0">{"".join(links_html)}</ul>'
            f"{self.render_children(n)}"
            f"</div></div></nav>"
        )

    def _r_nav_tabs(self, n):
        p = self._p(n)
        tid = self.ids.make("tabs")
        style = p.get("style", "tabs")  # tabs | pills | underline
        style_cls = {
            "tabs": "nav-tabs",
            "pills": "nav-pills",
            "underline": "nav-underline",
        }.get(style, "nav-tabs")
        nav_extra = []
        if _bool(p.get("fill")):
            nav_extra.append("nav-fill")
        if _bool(p.get("justified")):
            nav_extra.append("nav-justified")
        nav: List[str] = []
        panes: List[str] = []
        for i, line in enumerate(_split_lines(p.get("items"))):
            label, body = _split_parts(line, 2)
            pid, bid = f"{tid}-pane-{i}", f"{tid}-tab-{i}"
            active = i == 0
            nav.append(
                f'<li class="nav-item" role="presentation">'
                f'<button class="nav-link{" active" if active else ""}" id="{bid}"'
                f' data-bs-toggle="tab" data-bs-target="#{pid}" type="button" role="tab"'
                f' aria-controls="{pid}" aria-selected="{"true" if active else "false"}">'
                f"{_e(label)}</button></li>"
            )
            panes.append(
                f'<div class="tab-pane fade{" show active" if active else ""}" id="{pid}"'
                f' role="tabpanel" aria-labelledby="{bid}" tabindex="0">{_e(body)}</div>'
            )
        return (
            f'<ul class="{_classes("nav", style_cls, *nav_extra, p.get("classes"))}" id="{tid}"'
            f' role="tablist">{"".join(nav)}</ul>'
            f'<div class="tab-content pt-3">{"".join(panes)}</div>'
        )

    def _r_offcanvas_trigger(self, n):
        p = self._p(n)
        oid = self.ids.make("offcanvas")
        variant = p.get("variant", "primary")
        placement = p.get("placement", "offcanvas-start")
        return (
            f'<button class="btn btn-{_e(variant)} {_classes(p.get("classes"))}" type="button"'
            f' data-bs-toggle="offcanvas" data-bs-target="#{oid}" aria-controls="{oid}">'
            f"{_e(p.get('buttonText', 'Open'))}</button>"
            f'<div class="offcanvas {_e(placement)}" tabindex="-1" id="{oid}"'
            f' aria-labelledby="{oid}-label">'
            f'<div class="offcanvas-header">'
            f'<h5 class="offcanvas-title" id="{oid}-label">'
            f"{_e(p.get('title', 'Offcanvas'))}</h5>"
            f'<button type="button" class="btn-close" data-bs-dismiss="offcanvas"'
            f' aria-label="Close"></button></div>'
            f'<div class="offcanvas-body">{_e(p.get("body", ""))}</div></div>'
        )

    def _r_pagination(self, n):
        p = self._p(n)
        pages = max(1, int(p.get("pages") or 5))
        current = max(1, min(pages, int(p.get("active") or 1)))
        lis = [
            f'<li class="page-item{" disabled" if current == 1 else ""}">'
            f'<a class="page-link" href="#">Previous</a></li>'
        ]
        for i in range(1, pages + 1):
            active = " active" if i == current else ""
            aria = ' aria-current="page"' if i == current else ""
            lis.append(
                f'<li class="page-item{active}"{aria}>'
                f'<a class="page-link" href="#">{i}</a></li>'
            )
        lis.append(
            f'<li class="page-item{" disabled" if current == pages else ""}">'
            f'<a class="page-link" href="#">Next</a></li>'
        )
        cls = _classes("pagination", p.get("size"), p.get("align"), p.get("classes"))
        return f'<nav aria-label="pagination"><ul class="{cls}">{"".join(lis)}</ul></nav>'

    def _r_placeholder(self, n):
        p = self._p(n)
        lines = max(1, int(p.get("lines") or 3))
        animation = p.get("animation", "placeholder-glow")
        # Varying column widths for realism
        widths = ["col-7", "col-4", "col-6", "col-8", "col-10", "col-3", "col-5", "col-9"]
        bars = "".join(
            f'<span class="placeholder {widths[i % len(widths)]}"></span><br>'
            for i in range(lines)
        )
        return (
            f'<p class="{_classes(animation, p.get("classes"))}">{bars}</p>'
        )

    def _r_progress(self, n):
        p = self._p(n)
        value = max(0, min(100, int(p.get("value") or 50)))
        variant = p.get("variant", "primary")
        striped = " progress-bar-striped" if _bool(p.get("striped")) else ""
        animated = " progress-bar-animated" if _bool(p.get("animated")) else ""
        label = f"{value}%" if _bool(p.get("label", True)) else ""
        return (
            f'<div class="{_classes("progress", p.get("classes"))}" role="progressbar"'
            f' aria-valuenow="{value}" aria-valuemin="0" aria-valuemax="100">'
            f'<div class="progress-bar bg-{_e(variant)}{striped}{animated}"'
            f' style="width: {value}%">{_e(label)}</div></div>'
        )

    def _r_spinner(self, n):
        p = self._p(n)
        style = p.get("style", "border")
        variant = p.get("variant", "primary")
        size_cls = p.get("size", "")
        cls = _classes(f"spinner-{style}", f"text-{variant}", size_cls, p.get("classes"))
        return (
            f'<div class="{cls}" role="status">'
            f'<span class="visually-hidden">Loading...</span></div>'
        )

    def _r_toast(self, n):
        p = self._p(n)
        return (
            f'<div class="{_classes("toast", "show", p.get("classes"))}" role="alert"'
            f' aria-live="assertive" aria-atomic="true">'
            f'<div class="toast-header">'
            f'<strong class="me-auto">{_e(p.get("title", "Notification"))}</strong>'
            f'<small>{_e(p.get("time", ""))}</small>'
            f'<button type="button" class="btn-close" data-bs-dismiss="toast"'
            f' aria-label="Close"></button></div>'
            f'<div class="toast-body">{_e(p.get("body", ""))}</div></div>'
        )

    def _r_footer(self, n):
        p = self._p(n)
        children_html = self.render_children(n)
        inner = children_html or (
            f'<div class="container text-center">'
            f'<span class="text-body-secondary">{_e(p.get("text", ""))}</span></div>'
        )
        return (
            f'<footer class="{_classes(p.get("bg"), p.get("textColor"), p.get("classes"))}">'
            f"{inner}</footer>"
        )

    def _r_hero(self, n):
        p = self._p(n)
        variant = p.get("variant", "primary")
        section_cls = _classes(p.get("bg"), p.get("textColor"), p.get("align"), p.get("classes"))
        return (
            f'<section class="{section_cls}">'
            f'<div class="container text-center py-5">'
            f'<h1 class="display-4 fw-bold mb-3">{_e(p.get("title", "Welcome"))}</h1>'
            f'<p class="lead mb-4">{_e(p.get("subtitle", ""))}</p>'
            f'<a href="{_e(p.get("buttonHref", "#"))}" '
            f'class="btn btn-{_e(variant)} btn-lg">{_e(p.get("buttonText", "Learn more"))}</a>'
            f"</div></section>"
        )

    def _r_embed(self, n):
        p = self._p(n)
        ratio = p.get("ratio", "ratio-16x9")
        return (
            f'<div class="{_classes("ratio", ratio, p.get("classes"))}">'
            f'<iframe src="{_e(p.get("src", ""))}" '
            f'title="{_e(p.get("title", "Embedded content"))}" allowfullscreen></iframe>'
            f"</div>"
        )

    def _r_html(self, n):
        """Escape-hatch: user-supplied HTML, sanitised via bleach."""
        p = self._p(n)
        raw = p.get("html") or ""
        if not raw.strip():
            return "<!-- empty custom HTML block -->"
        cleaned = bleach.clean(
            raw, tags=_SAFE_TAGS, attributes=_SAFE_ATTRS, strip=True
        )
        if p.get("classes"):
            return f'<div class="{_classes(p.get("classes"))}">{cleaned}</div>'
        return cleaned

    # =====================================================================
    # HELPERS
    # =====================================================================
    def _r_spacer(self, n):
        p = self._p(n)
        return f'<div class="{_classes(p.get("size", "my-5"), p.get("classes"))}"></div>'

    def _r_ratio(self, n):
        p = self._p(n)
        return (
            f'<div class="{_classes("ratio", p.get("ratio", "ratio-16x9"), p.get("classes"))}">'
            f"{self.render_children(n)}</div>"
        )

    def _r_visually_hidden(self, n):
        p = self._p(n)
        return f'<span class="{_classes("visually-hidden", p.get("classes"))}">{_e(p.get("text", ""))}</span>'


# ---------------------------------------------------------------------------
# Top-level API
# ---------------------------------------------------------------------------
def render_page(
    tree: Dict[str, Any],
    *,
    title: str = "My Site",
    theme: str = "default",
    description: str = "",
    language: str = "en",
    color_mode: str = "light",
    extra_head: str = "",
    extra_body: str = "",
) -> str:
    """
    Render a complete, self-contained Bootstrap 5.3 HTML document.

    Parameters
    ----------
    tree
        Root node of the page tree. A ``"page"`` wrapper just renders its
        children; any other node is rendered directly.
    title
        ``<title>`` text.
    theme
        One of the slugs in ``bootstrap_themes.THEMES``. Invalid slugs fall
        back to the default theme.
    description
        Optional ``<meta name="description">`` content.
    language
        ``<html lang="...">``.
    color_mode
        ``"light"`` | ``"dark"`` | ``"auto"`` -- applied via ``data-bs-theme``.
    extra_head / extra_body
        Additional markup injected into ``<head>`` or just before ``</body>``.
    """
    r = Renderer()

    if tree and tree.get("type") == "page":
        body = r.render_children(tree)
    else:
        body = r.render_node(tree) if tree else ""

    # Theme CSS: default -> stock Bootstrap; Bootswatch -> swap stylesheet.
    if not theme or not theme_exists(theme):
        theme = "default"
    if theme == "default":
        theme_link = f'<link rel="stylesheet" href="{BOOTSTRAP_CSS}">'
    else:
        theme_link = f'<link rel="stylesheet" href="{theme_css_url(theme)}">'

    meta_desc = (
        f'<meta name="description" content="{_e(description)}">\n' if description else ""
    )

    return (
        f"<!doctype html>\n"
        f'<html lang="{_e(language)}" data-bs-theme="{_e(color_mode)}">\n'
        f"<head>\n"
        f'<meta charset="utf-8">\n'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{_e(title)}</title>\n"
        f"{meta_desc}"
        f"{theme_link}\n"
        f'<link rel="stylesheet" href="{BOOTSTRAP_ICONS_CSS}">\n'
        f"{extra_head}\n"
        f"</head>\n"
        f"<body>\n"
        f"{body}\n"
        f'<script src="{BOOTSTRAP_JS}"></script>\n'
        f"{extra_body}\n"
        f"</body>\n"
        f"</html>\n"
    )


def render_fragment(tree: Dict[str, Any]) -> str:
    """Render just the body fragment (for iframe ``srcdoc`` previews)."""
    r = Renderer()
    if tree and tree.get("type") == "page":
        return r.render_children(tree)
    return r.render_node(tree) if tree else ""


__all__ = ["Renderer", "render_page", "render_fragment"]
