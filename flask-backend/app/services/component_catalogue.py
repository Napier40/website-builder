"""
Bootstrap 5.3 Component Schema
==============================

A page is stored as a **tree of nodes** (JSON). Each node has:

    {
      "type":     "<component-type>",   # e.g. "navbar", "card", "col", "heading"
      "props":    { ...any HTML attrs / Bootstrap options... },
      "children": [ <node>, ... ]        # optional, may be omitted for leaves
    }

Some nodes carry inline content in `props.text` (headings, paragraphs, buttons)
or `props.src/alt/href` (image, link).

The component TYPES dict below is the SINGLE SOURCE OF TRUTH for:
  - Which components exist (the palette)
  - What category each lives in (for the sidebar)
  - What props each accepts (for the properties panel)
  - What children are allowed (for drop-zone validation)
  - How to render each to Bootstrap 5.3 HTML

Categories match Bootstrap 5.3's docs: Layout / Content / Forms / Components / Helpers.
"""

# Property kinds used by the frontend properties panel
TEXT   = "text"      # free-form string
RICH   = "rich"      # longer text (textarea)
ENUM   = "enum"      # pick from list
BOOL   = "bool"
NUMBER = "number"
COLOR  = "color"     # Bootstrap colour token: primary/secondary/success/.../light/dark
URL    = "url"
ICON   = "icon"      # Bootstrap Icons name

# Bootstrap colour tokens
BS_COLORS = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]
BS_SIZES  = ["sm", "", "lg"]
BS_BREAKPOINTS = ["", "sm", "md", "lg", "xl", "xxl"]

# Complete catalogue. Each entry has:
#   category:   palette group
#   label:      display name
#   icon:       Bootstrap Icons class for palette
#   props:      dict of {prop_name: {kind, default, options?, label?}}
#   allows_children: True/False/list of allowed types
#   default_children: sensible defaults when dropped in
TYPES = {
    # ─────────────────────────────────────────────────────────────────────
    # LAYOUT
    # ─────────────────────────────────────────────────────────────────────
    "container": {
        "category": "Layout",
        "label":    "Container",
        "icon":     "bi-bounding-box",
        "props": {
            "fluid":   {"kind": ENUM,  "default": "",  "options": ["", "sm", "md", "lg", "xl", "xxl", "fluid"], "label": "Fluid at"},
            "classes": {"kind": TEXT,  "default": "",  "label": "Extra CSS classes"},
        },
        "allows_children": True,
    },
    "row": {
        "category": "Layout",
        "label":    "Row",
        "icon":     "bi-distribute-horizontal",
        "props": {
            "gutter":  {"kind": ENUM,  "default": "g-3", "options": ["g-0", "g-1", "g-2", "g-3", "g-4", "g-5"], "label": "Gutter"},
            "align":   {"kind": ENUM,  "default": "",    "options": ["", "align-items-start", "align-items-center", "align-items-end"], "label": "Align items"},
            "justify": {"kind": ENUM,  "default": "",    "options": ["", "justify-content-start", "justify-content-center", "justify-content-end", "justify-content-between", "justify-content-around", "justify-content-evenly"], "label": "Justify"},
            "classes": {"kind": TEXT,  "default": "",    "label": "Extra CSS classes"},
        },
        "allows_children": ["col"],
    },
    "col": {
        "category": "Layout",
        "label":    "Column",
        "icon":     "bi-layout-three-columns",
        "props": {
            "xs":      {"kind": ENUM, "default": "",  "options": ["", "auto", "1","2","3","4","5","6","7","8","9","10","11","12"], "label": "xs cols"},
            "sm":      {"kind": ENUM, "default": "",  "options": ["", "auto", "1","2","3","4","5","6","7","8","9","10","11","12"], "label": "sm cols"},
            "md":      {"kind": ENUM, "default": "6", "options": ["", "auto", "1","2","3","4","5","6","7","8","9","10","11","12"], "label": "md cols"},
            "lg":      {"kind": ENUM, "default": "",  "options": ["", "auto", "1","2","3","4","5","6","7","8","9","10","11","12"], "label": "lg cols"},
            "classes": {"kind": TEXT, "default": "",  "label": "Extra CSS classes"},
        },
        "allows_children": True,
    },
    "section": {
        "category": "Layout",
        "label":    "Section",
        "icon":     "bi-layout-wtf",
        "props": {
            "padding": {"kind": ENUM, "default": "py-5", "options": ["", "py-1", "py-2", "py-3", "py-4", "py-5"], "label": "Padding Y"},
            "bg":      {"kind": ENUM, "default": "",     "options": [""] + [f"bg-{c}" for c in BS_COLORS] + ["bg-body", "bg-body-tertiary"], "label": "Background"},
            "classes": {"kind": TEXT, "default": "",     "label": "Extra CSS classes"},
        },
        "allows_children": True,
    },
    "stack": {
        "category": "Layout",
        "label":    "Stack",
        "icon":     "bi-stack",
        "props": {
            "direction": {"kind": ENUM, "default": "vstack", "options": ["vstack", "hstack"], "label": "Direction"},
            "gap":       {"kind": ENUM, "default": "gap-3",  "options": ["gap-0","gap-1","gap-2","gap-3","gap-4","gap-5"], "label": "Gap"},
            "classes":   {"kind": TEXT, "default": "",       "label": "Extra CSS classes"},
        },
        "allows_children": True,
    },
    "grid": {
        "category": "Layout",
        "label":    "CSS Grid",
        "icon":     "bi-grid-3x3-gap",
        "props": {
            "cols":    {"kind": NUMBER, "default": 3, "label": "Columns"},
            "gap":     {"kind": ENUM,   "default": "gap-3", "options": ["gap-0","gap-1","gap-2","gap-3","gap-4","gap-5"], "label": "Gap"},
            "classes": {"kind": TEXT,   "default": "",  "label": "Extra CSS classes"},
        },
        "allows_children": True,
    },
    "divider": {
        "category": "Layout",
        "label":    "Divider (hr)",
        "icon":     "bi-hr",
        "props": {
            "classes": {"kind": TEXT, "default": "my-4", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "vr": {
        "category": "Layout",
        "label":    "Vertical Rule",
        "icon":     "bi-vr",
        "props": {"classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"}},
        "allows_children": False,
    },

    # ─────────────────────────────────────────────────────────────────────
    # CONTENT
    # ─────────────────────────────────────────────────────────────────────
    "heading": {
        "category": "Content",
        "label":    "Heading",
        "icon":     "bi-type-h1",
        "props": {
            "level":   {"kind": ENUM, "default": "h2", "options": ["h1","h2","h3","h4","h5","h6"], "label": "Level"},
            "text":    {"kind": TEXT, "default": "Heading text", "label": "Text"},
            "display": {"kind": ENUM, "default": "", "options": ["","display-1","display-2","display-3","display-4","display-5","display-6"], "label": "Display"},
            "align":   {"kind": ENUM, "default": "", "options": ["","text-start","text-center","text-end"], "label": "Alignment"},
            "classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "paragraph": {
        "category": "Content",
        "label":    "Paragraph",
        "icon":     "bi-paragraph",
        "props": {
            "text":    {"kind": RICH, "default": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "label": "Text"},
            "lead":    {"kind": BOOL, "default": False, "label": "Lead text"},
            "align":   {"kind": ENUM, "default": "", "options": ["","text-start","text-center","text-end","text-justify"], "label": "Alignment"},
            "classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "lead": {
        "category": "Content",
        "label":    "Lead Text",
        "icon":     "bi-file-text",
        "props": {
            "text":    {"kind": RICH, "default": "A lead paragraph stands out.", "label": "Text"},
            "classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "image": {
        "category": "Content",
        "label":    "Image",
        "icon":     "bi-image",
        "props": {
            "src":         {"kind": URL,  "default": "https://picsum.photos/800/450", "label": "Image URL"},
            "alt":         {"kind": TEXT, "default": "Placeholder image",             "label": "Alt text"},
            "fluid":       {"kind": BOOL, "default": True,  "label": "Fluid (responsive)"},
            "thumbnail":   {"kind": BOOL, "default": False, "label": "Thumbnail border"},
            "rounded":     {"kind": ENUM, "default": "",    "options": ["","rounded","rounded-1","rounded-2","rounded-3","rounded-circle","rounded-pill"], "label": "Rounded"},
            "classes":     {"kind": TEXT, "default": "",    "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "figure": {
        "category": "Content",
        "label":    "Figure",
        "icon":     "bi-card-image",
        "props": {
            "src":     {"kind": URL,  "default": "https://picsum.photos/600/400", "label": "Image URL"},
            "alt":     {"kind": TEXT, "default": "Figure",                         "label": "Alt text"},
            "caption": {"kind": TEXT, "default": "A caption for the above image.", "label": "Caption"},
            "classes": {"kind": TEXT, "default": "",                               "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "blockquote": {
        "category": "Content",
        "label":    "Blockquote",
        "icon":     "bi-chat-quote",
        "props": {
            "text":   {"kind": RICH, "default": "A well-known quote, contained in a blockquote element.", "label": "Quote"},
            "source": {"kind": TEXT, "default": "Someone famous", "label": "Source"},
            "cite":   {"kind": TEXT, "default": "Source Title",   "label": "Cite title"},
            "align":  {"kind": ENUM, "default": "", "options": ["", "text-center", "text-end"], "label": "Alignment"},
            "classes":{"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "list": {
        "category": "Content",
        "label":    "List",
        "icon":     "bi-list-ul",
        "props": {
            "ordered": {"kind": BOOL, "default": False, "label": "Ordered (numbered)"},
            "items":   {"kind": RICH, "default": "First item\nSecond item\nThird item", "label": "Items (one per line)"},
            "unstyled":{"kind": BOOL, "default": False, "label": "Unstyled"},
            "inline":  {"kind": BOOL, "default": False, "label": "Inline"},
            "classes": {"kind": TEXT, "default": "",    "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "dl": {
        "category": "Content",
        "label":    "Description List",
        "icon":     "bi-list-columns",
        "props": {
            "items":   {"kind": RICH, "default": "Term 1::Description 1\nTerm 2::Description 2", "label": "Items (term::description, one pair per line)"},
            "classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "code": {
        "category": "Content",
        "label":    "Code Block",
        "icon":     "bi-code-slash",
        "props": {
            "text":    {"kind": RICH, "default": "console.log('Hello, world!');", "label": "Code"},
            "inline":  {"kind": BOOL, "default": False, "label": "Inline <code>"},
            "classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "link": {
        "category": "Content",
        "label":    "Link",
        "icon":     "bi-link-45deg",
        "props": {
            "text":    {"kind": TEXT, "default": "Click here",  "label": "Text"},
            "href":    {"kind": URL,  "default": "#",           "label": "URL"},
            "target":  {"kind": ENUM, "default": "",            "options": ["", "_blank"], "label": "Target"},
            "classes": {"kind": TEXT, "default": "",            "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "icon": {
        "category": "Content",
        "label":    "Icon",
        "icon":     "bi-star-fill",
        "props": {
            "name":    {"kind": ICON, "default": "star",     "label": "Icon name (without bi- prefix)"},
            "size":    {"kind": ENUM, "default": "fs-3",     "options": ["fs-6","fs-5","fs-4","fs-3","fs-2","fs-1"], "label": "Size"},
            "color":   {"kind": ENUM, "default": "",         "options": [""] + [f"text-{c}" for c in BS_COLORS], "label": "Colour"},
            "classes": {"kind": TEXT, "default": "",         "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },

    # ─────────────────────────────────────────────────────────────────────
    # FORMS
    # ─────────────────────────────────────────────────────────────────────
    "form": {
        "category": "Forms",
        "label":    "Form",
        "icon":     "bi-ui-checks",
        "props": {
            "action":  {"kind": URL,  "default": "#",  "label": "Action URL"},
            "method":  {"kind": ENUM, "default": "post", "options": ["get", "post"], "label": "Method"},
            "classes": {"kind": TEXT, "default": "",   "label": "Extra CSS classes"},
        },
        "allows_children": True,
    },
    "input": {
        "category": "Forms",
        "label":    "Input",
        "icon":     "bi-input-cursor-text",
        "props": {
            "type":        {"kind": ENUM, "default": "text", "options": ["text","email","password","number","tel","url","search","date","time","datetime-local","month","week","color"], "label": "Type"},
            "name":        {"kind": TEXT, "default": "field", "label": "Name"},
            "label":       {"kind": TEXT, "default": "Label", "label": "Label"},
            "placeholder": {"kind": TEXT, "default": "",      "label": "Placeholder"},
            "helpText":    {"kind": TEXT, "default": "",      "label": "Help text"},
            "floating":    {"kind": BOOL, "default": False,   "label": "Floating label"},
            "size":        {"kind": ENUM, "default": "",      "options": ["","form-control-sm","form-control-lg"], "label": "Size"},
            "required":    {"kind": BOOL, "default": False,   "label": "Required"},
            "classes":     {"kind": TEXT, "default": "",      "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "textarea": {
        "category": "Forms",
        "label":    "Textarea",
        "icon":     "bi-textarea-t",
        "props": {
            "name":        {"kind": TEXT, "default": "message", "label": "Name"},
            "label":       {"kind": TEXT, "default": "Message", "label": "Label"},
            "placeholder": {"kind": TEXT, "default": "",        "label": "Placeholder"},
            "rows":        {"kind": NUMBER, "default": 3,       "label": "Rows"},
            "helpText":    {"kind": TEXT, "default": "",        "label": "Help text"},
            "floating":    {"kind": BOOL, "default": False,     "label": "Floating label"},
            "required":    {"kind": BOOL, "default": False,     "label": "Required"},
            "classes":     {"kind": TEXT, "default": "",        "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "select": {
        "category": "Forms",
        "label":    "Select",
        "icon":     "bi-menu-down",
        "props": {
            "name":      {"kind": TEXT, "default": "choice", "label": "Name"},
            "label":     {"kind": TEXT, "default": "Choose…", "label": "Label"},
            "options":   {"kind": RICH, "default": "Option 1\nOption 2\nOption 3", "label": "Options (one per line)"},
            "multiple":  {"kind": BOOL, "default": False, "label": "Multiple"},
            "size":      {"kind": ENUM, "default": "", "options": ["","form-select-sm","form-select-lg"], "label": "Size"},
            "floating":  {"kind": BOOL, "default": False, "label": "Floating label"},
            "classes":   {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "checkbox": {
        "category": "Forms",
        "label":    "Checkbox",
        "icon":     "bi-check-square",
        "props": {
            "name":    {"kind": TEXT, "default": "agree",     "label": "Name"},
            "label":   {"kind": TEXT, "default": "I agree",   "label": "Label"},
            "checked": {"kind": BOOL, "default": False,       "label": "Checked by default"},
            "classes": {"kind": TEXT, "default": "",          "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "radio": {
        "category": "Forms",
        "label":    "Radio Group",
        "icon":     "bi-record-circle",
        "props": {
            "name":    {"kind": TEXT, "default": "option",           "label": "Name"},
            "label":   {"kind": TEXT, "default": "Choose one",       "label": "Group label"},
            "options": {"kind": RICH, "default": "Option A\nOption B\nOption C", "label": "Options (one per line)"},
            "inline":  {"kind": BOOL, "default": False, "label": "Inline"},
            "classes": {"kind": TEXT, "default": "",    "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "switch": {
        "category": "Forms",
        "label":    "Switch",
        "icon":     "bi-toggle-on",
        "props": {
            "name":    {"kind": TEXT, "default": "enabled",           "label": "Name"},
            "label":   {"kind": TEXT, "default": "Enable notifications", "label": "Label"},
            "checked": {"kind": BOOL, "default": False,               "label": "Checked"},
            "classes": {"kind": TEXT, "default": "",                  "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "range": {
        "category": "Forms",
        "label":    "Range",
        "icon":     "bi-sliders",
        "props": {
            "name":    {"kind": TEXT,   "default": "range",   "label": "Name"},
            "label":   {"kind": TEXT,   "default": "Pick a value", "label": "Label"},
            "min":     {"kind": NUMBER, "default": 0,         "label": "Min"},
            "max":     {"kind": NUMBER, "default": 100,       "label": "Max"},
            "step":    {"kind": NUMBER, "default": 1,         "label": "Step"},
            "value":   {"kind": NUMBER, "default": 50,        "label": "Value"},
            "classes": {"kind": TEXT,   "default": "",        "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "file": {
        "category": "Forms",
        "label":    "File Upload",
        "icon":     "bi-paperclip",
        "props": {
            "name":     {"kind": TEXT, "default": "file",     "label": "Name"},
            "label":    {"kind": TEXT, "default": "Upload",   "label": "Label"},
            "multiple": {"kind": BOOL, "default": False,      "label": "Multiple"},
            "accept":   {"kind": TEXT, "default": "",         "label": "Accept (e.g. image/*)"},
            "classes":  {"kind": TEXT, "default": "",         "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "input-group": {
        "category": "Forms",
        "label":    "Input Group",
        "icon":     "bi-input-cursor",
        "props": {
            "prepend":     {"kind": TEXT, "default": "@",         "label": "Prepend text"},
            "append":      {"kind": TEXT, "default": "",          "label": "Append text"},
            "placeholder": {"kind": TEXT, "default": "Username",  "label": "Placeholder"},
            "name":        {"kind": TEXT, "default": "username",  "label": "Name"},
            "size":        {"kind": ENUM, "default": "", "options": ["","input-group-sm","input-group-lg"], "label": "Size"},
            "classes":     {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },

    # ─────────────────────────────────────────────────────────────────────
    # COMPONENTS
    # ─────────────────────────────────────────────────────────────────────
    "accordion": {
        "category": "Components",
        "label":    "Accordion",
        "icon":     "bi-list-nested",
        "props": {
            "items":   {"kind": RICH, "default": "First panel::Content of the first panel.\nSecond panel::Content of the second panel.\nThird panel::Content of the third panel.", "label": "Items (title::content, one per line)"},
            "flush":   {"kind": BOOL, "default": False, "label": "Flush"},
            "openFirst":{"kind":BOOL, "default": True,  "label": "First open"},
            "classes": {"kind": TEXT, "default": "",    "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "alert": {
        "category": "Components",
        "label":    "Alert",
        "icon":     "bi-exclamation-triangle",
        "props": {
            "variant":     {"kind": ENUM, "default": "primary",  "options": BS_COLORS, "label": "Variant"},
            "text":        {"kind": RICH, "default": "A simple alert—check it out!", "label": "Text"},
            "dismissible": {"kind": BOOL, "default": False,      "label": "Dismissible"},
            "classes":     {"kind": TEXT, "default": "",         "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "badge": {
        "category": "Components",
        "label":    "Badge",
        "icon":     "bi-award",
        "props": {
            "text":    {"kind": TEXT, "default": "New",     "label": "Text"},
            "variant": {"kind": ENUM, "default": "primary", "options": BS_COLORS, "label": "Variant"},
            "pill":    {"kind": BOOL, "default": False,     "label": "Pill"},
            "classes": {"kind": TEXT, "default": "",        "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "breadcrumb": {
        "category": "Components",
        "label":    "Breadcrumb",
        "icon":     "bi-chevron-right",
        "props": {
            "items":   {"kind": RICH, "default": "Home::/\nLibrary::/library\nData::", "label": "Items (label::href, blank href = active, one per line)"},
            "classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "button": {
        "category": "Components",
        "label":    "Button",
        "icon":     "bi-hand-index-thumb",
        "props": {
            "text":     {"kind": TEXT, "default": "Click me",   "label": "Text"},
            "variant":  {"kind": ENUM, "default": "primary",    "options": BS_COLORS + [f"outline-{c}" for c in BS_COLORS], "label": "Variant"},
            "size":     {"kind": ENUM, "default": "",           "options": ["", "btn-sm", "btn-lg"], "label": "Size"},
            "href":     {"kind": URL,  "default": "#",          "label": "Link URL"},
            "block":    {"kind": BOOL, "default": False,        "label": "Block (full width)"},
            "disabled": {"kind": BOOL, "default": False,        "label": "Disabled"},
            "icon":     {"kind": ICON, "default": "",           "label": "Icon (optional)"},
            "classes":  {"kind": TEXT, "default": "",           "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "button-group": {
        "category": "Components",
        "label":    "Button Group",
        "icon":     "bi-layout-three-columns",
        "props": {
            "size":     {"kind": ENUM, "default": "",  "options": ["","btn-group-sm","btn-group-lg"], "label": "Size"},
            "vertical": {"kind": BOOL, "default": False, "label": "Vertical"},
            "classes":  {"kind": TEXT, "default": "",  "label": "Extra CSS classes"},
        },
        "allows_children": ["button"],
    },
    "card": {
        "category": "Components",
        "label":    "Card",
        "icon":     "bi-card-heading",
        "props": {
            "title":     {"kind": TEXT, "default": "Card title",          "label": "Title"},
            "subtitle":  {"kind": TEXT, "default": "",                    "label": "Subtitle"},
            "text":      {"kind": RICH, "default": "Some quick example text to build on the card title and make up the bulk of the card's content.", "label": "Body text"},
            "image":     {"kind": URL,  "default": "",                    "label": "Header image URL"},
            "buttonText":{"kind": TEXT, "default": "",                    "label": "Button text (optional)"},
            "buttonHref":{"kind": URL,  "default": "#",                   "label": "Button URL"},
            "border":    {"kind": ENUM, "default": "",                    "options": [""] + [f"border-{c}" for c in BS_COLORS], "label": "Border"},
            "bg":        {"kind": ENUM, "default": "",                    "options": [""] + [f"bg-{c}" for c in BS_COLORS] + ["bg-body-tertiary"], "label": "Background"},
            "textColor": {"kind": ENUM, "default": "",                    "options": [""] + [f"text-{c}" for c in BS_COLORS], "label": "Text colour"},
            "classes":   {"kind": TEXT, "default": "",                    "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "carousel": {
        "category": "Components",
        "label":    "Carousel",
        "icon":     "bi-images",
        "props": {
            "slides":    {"kind": RICH, "default": "https://picsum.photos/1200/500?1::First slide::Nature is beautiful\nhttps://picsum.photos/1200/500?2::Second slide::Mountains and sky\nhttps://picsum.photos/1200/500?3::Third slide::Golden hour", "label": "Slides (image_url::title::caption, one per line)"},
            "controls":  {"kind": BOOL, "default": True,  "label": "Show controls"},
            "indicators":{"kind": BOOL, "default": True,  "label": "Show indicators"},
            "autoplay":  {"kind": BOOL, "default": True,  "label": "Autoplay"},
            "fade":      {"kind": BOOL, "default": False, "label": "Fade transition"},
            "classes":   {"kind": TEXT, "default": "",    "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "close-button": {
        "category": "Components",
        "label":    "Close Button",
        "icon":     "bi-x-lg",
        "props": {"classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"}},
        "allows_children": False,
    },
    "dropdown": {
        "category": "Components",
        "label":    "Dropdown",
        "icon":     "bi-caret-down-square",
        "props": {
            "label":   {"kind": TEXT, "default": "Dropdown",    "label": "Button text"},
            "items":   {"kind": RICH, "default": "Action::#\nAnother action::#\n---::\nSomething else::#", "label": "Items (label::href, --- for divider, one per line)"},
            "variant": {"kind": ENUM, "default": "primary",     "options": BS_COLORS + [f"outline-{c}" for c in BS_COLORS], "label": "Variant"},
            "split":   {"kind": BOOL, "default": False,         "label": "Split button"},
            "classes": {"kind": TEXT, "default": "",            "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "list-group": {
        "category": "Components",
        "label":    "List Group",
        "icon":     "bi-list-task",
        "props": {
            "items":      {"kind": RICH, "default": "Cras justo odio\nDapibus ac facilisis in\nMorbi leo risus\nPorta ac consectetur ac\nVestibulum at eros", "label": "Items (one per line)"},
            "flush":      {"kind": BOOL, "default": False, "label": "Flush"},
            "numbered":   {"kind": BOOL, "default": False, "label": "Numbered"},
            "horizontal": {"kind": BOOL, "default": False, "label": "Horizontal"},
            "classes":    {"kind": TEXT, "default": "",    "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "modal-trigger": {
        "category": "Components",
        "label":    "Modal (with trigger)",
        "icon":     "bi-window",
        "props": {
            "buttonText": {"kind": TEXT, "default": "Launch modal",     "label": "Trigger text"},
            "variant":    {"kind": ENUM, "default": "primary",          "options": BS_COLORS, "label": "Trigger variant"},
            "modalTitle": {"kind": TEXT, "default": "Modal title",      "label": "Modal title"},
            "modalBody":  {"kind": RICH, "default": "Modal body text goes here.", "label": "Body"},
            "size":       {"kind": ENUM, "default": "",                 "options": ["","modal-sm","modal-lg","modal-xl"], "label": "Size"},
            "centered":   {"kind": BOOL, "default": True,               "label": "Vertically centered"},
            "scrollable": {"kind": BOOL, "default": False,              "label": "Scrollable"},
            "classes":    {"kind": TEXT, "default": "",                 "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "navbar": {
        "category": "Components",
        "label":    "Navbar",
        "icon":     "bi-menu-button-wide",
        "props": {
            "brand":    {"kind": TEXT, "default": "Brand",                              "label": "Brand text"},
            "brandHref":{"kind": URL,  "default": "#",                                  "label": "Brand link"},
            "items":    {"kind": RICH, "default": "Home::/::active\nAbout::/about\nServices::/services\nContact::/contact", "label": "Items (label::href::active_flag, one per line)"},
            "variant":  {"kind": ENUM, "default": "light",                              "options": ["light", "dark"], "label": "Variant"},
            "bg":       {"kind": ENUM, "default": "bg-body-tertiary",                   "options": ["bg-body-tertiary"] + [f"bg-{c}" for c in BS_COLORS], "label": "Background"},
            "expand":   {"kind": ENUM, "default": "navbar-expand-lg",                   "options": ["navbar-expand-sm","navbar-expand-md","navbar-expand-lg","navbar-expand-xl","navbar-expand-xxl"], "label": "Expand at"},
            "sticky":   {"kind": BOOL, "default": False,                                "label": "Sticky top"},
            "container":{"kind": ENUM, "default": "container",                          "options": ["container","container-fluid"], "label": "Inner container"},
            "classes":  {"kind": TEXT, "default": "",                                   "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "nav-tabs": {
        "category": "Components",
        "label":    "Nav Tabs",
        "icon":     "bi-segmented-nav",
        "props": {
            "items":   {"kind": RICH, "default": "Home::Welcome to the home tab.\nProfile::This is the profile tab.\nContact::Contact info here.", "label": "Tabs (label::content, one per line)"},
            "style":   {"kind": ENUM, "default": "tabs", "options": ["tabs","pills","underline"], "label": "Style"},
            "fill":    {"kind": BOOL, "default": False, "label": "Fill"},
            "justified":{"kind":BOOL, "default": False, "label": "Justified"},
            "classes": {"kind": TEXT, "default": "",    "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "offcanvas-trigger": {
        "category": "Components",
        "label":    "Offcanvas (with trigger)",
        "icon":     "bi-layout-sidebar-inset",
        "props": {
            "buttonText": {"kind": TEXT, "default": "Open Offcanvas",  "label": "Trigger text"},
            "variant":    {"kind": ENUM, "default": "primary",         "options": BS_COLORS, "label": "Trigger variant"},
            "title":      {"kind": TEXT, "default": "Offcanvas",       "label": "Title"},
            "body":       {"kind": RICH, "default": "Content goes here.", "label": "Body"},
            "placement":  {"kind": ENUM, "default": "offcanvas-start", "options": ["offcanvas-start","offcanvas-end","offcanvas-top","offcanvas-bottom"], "label": "Placement"},
            "classes":    {"kind": TEXT, "default": "",                "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "pagination": {
        "category": "Components",
        "label":    "Pagination",
        "icon":     "bi-three-dots",
        "props": {
            "pages":    {"kind": NUMBER, "default": 5,    "label": "Total pages"},
            "active":   {"kind": NUMBER, "default": 1,    "label": "Active page"},
            "size":     {"kind": ENUM,   "default": "",   "options": ["","pagination-sm","pagination-lg"], "label": "Size"},
            "align":    {"kind": ENUM,   "default": "",   "options": ["","justify-content-center","justify-content-end"], "label": "Align"},
            "classes":  {"kind": TEXT,   "default": "",   "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "placeholder": {
        "category": "Components",
        "label":    "Placeholder",
        "icon":     "bi-file-earmark",
        "props": {
            "lines":    {"kind": NUMBER, "default": 3, "label": "Lines"},
            "animation":{"kind": ENUM,   "default": "placeholder-glow", "options": ["","placeholder-glow","placeholder-wave"], "label": "Animation"},
            "classes":  {"kind": TEXT,   "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "progress": {
        "category": "Components",
        "label":    "Progress",
        "icon":     "bi-bar-chart-line",
        "props": {
            "value":    {"kind": NUMBER, "default": 50, "label": "Value (0-100)"},
            "label":    {"kind": BOOL,   "default": True, "label": "Show label"},
            "variant":  {"kind": ENUM,   "default": "primary", "options": BS_COLORS, "label": "Variant"},
            "striped":  {"kind": BOOL,   "default": False, "label": "Striped"},
            "animated": {"kind": BOOL,   "default": False, "label": "Animated"},
            "classes":  {"kind": TEXT,   "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "spinner": {
        "category": "Components",
        "label":    "Spinner",
        "icon":     "bi-arrow-repeat",
        "props": {
            "variant":{"kind": ENUM, "default": "primary", "options": BS_COLORS, "label": "Variant"},
            "style":  {"kind": ENUM, "default": "border",  "options": ["border","grow"], "label": "Style"},
            "size":   {"kind": ENUM, "default": "",        "options": ["","spinner-border-sm","spinner-grow-sm"], "label": "Size"},
            "classes":{"kind": TEXT, "default": "",        "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "toast": {
        "category": "Components",
        "label":    "Toast (static)",
        "icon":     "bi-bell",
        "props": {
            "title":  {"kind": TEXT, "default": "Notification",         "label": "Title"},
            "time":   {"kind": TEXT, "default": "just now",             "label": "Time"},
            "body":   {"kind": RICH, "default": "Hello, world! This is a toast message.", "label": "Body"},
            "classes":{"kind": TEXT, "default": "",                     "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "footer": {
        "category": "Components",
        "label":    "Footer",
        "icon":     "bi-layout-text-sidebar-reverse",
        "props": {
            "text":     {"kind": RICH, "default": "© 2025 My Company. All rights reserved.", "label": "Text"},
            "bg":       {"kind": ENUM, "default": "bg-body-tertiary",   "options": ["bg-body-tertiary"] + [f"bg-{c}" for c in BS_COLORS], "label": "Background"},
            "textColor":{"kind": ENUM, "default": "",                   "options": [""] + [f"text-{c}" for c in BS_COLORS], "label": "Text colour"},
            "classes":  {"kind": TEXT, "default": "py-4 mt-5",          "label": "Extra CSS classes"},
        },
        "allows_children": True,
    },
    "hero": {
        "category": "Components",
        "label":    "Hero / Jumbotron",
        "icon":     "bi-hexagon-half",
        "props": {
            "title":     {"kind": TEXT, "default": "Hello, world!",        "label": "Title"},
            "subtitle":  {"kind": RICH, "default": "This is a simple hero unit, a simple jumbotron-style component for calling extra attention to featured content.", "label": "Subtitle"},
            "buttonText":{"kind": TEXT, "default": "Learn more",           "label": "Button text"},
            "buttonHref":{"kind": URL,  "default": "#",                    "label": "Button URL"},
            "variant":   {"kind": ENUM, "default": "primary",              "options": BS_COLORS, "label": "Button variant"},
            "bg":        {"kind": ENUM, "default": "bg-body-tertiary",     "options": ["bg-body-tertiary"] + [f"bg-{c}" for c in BS_COLORS], "label": "Background"},
            "textColor": {"kind": ENUM, "default": "",                     "options": [""] + [f"text-{c}" for c in BS_COLORS], "label": "Text colour"},
            "align":     {"kind": ENUM, "default": "text-center",          "options": ["text-start","text-center","text-end"], "label": "Align"},
            "classes":   {"kind": TEXT, "default": "p-5 rounded-3",        "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "embed": {
        "category": "Components",
        "label":    "Video / Embed",
        "icon":     "bi-play-btn",
        "props": {
            "src":      {"kind": URL,    "default": "https://www.youtube.com/embed/dQw4w9WgXcQ", "label": "Embed URL"},
            "ratio":    {"kind": ENUM,   "default": "ratio-16x9", "options": ["ratio-1x1","ratio-4x3","ratio-16x9","ratio-21x9"], "label": "Aspect ratio"},
            "title":    {"kind": TEXT,   "default": "Embedded content",  "label": "Title (a11y)"},
            "classes":  {"kind": TEXT,   "default": "",                  "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "html": {
        "category": "Helpers",
        "label":    "Raw HTML",
        "icon":     "bi-code",
        "props": {
            "html":    {"kind": RICH, "default": "<p>Your custom HTML here</p>", "label": "HTML"},
            "classes": {"kind": TEXT, "default": "",  "label": "Wrapper CSS classes"},
        },
        "allows_children": False,
    },

    # ─────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────
    "spacer": {
        "category": "Helpers",
        "label":    "Spacer",
        "icon":     "bi-arrows-vertical",
        "props": {
            "size":    {"kind": ENUM, "default": "my-5", "options": ["my-1","my-2","my-3","my-4","my-5"], "label": "Vertical spacing"},
            "classes": {"kind": TEXT, "default": "",     "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "ratio": {
        "category": "Helpers",
        "label":    "Aspect Ratio Wrapper",
        "icon":     "bi-aspect-ratio",
        "props": {
            "ratio":   {"kind": ENUM, "default": "ratio-16x9", "options": ["ratio-1x1","ratio-4x3","ratio-16x9","ratio-21x9"], "label": "Ratio"},
            "classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": True,
    },
    "visually-hidden": {
        "category": "Helpers",
        "label":    "Visually Hidden",
        "icon":     "bi-eye-slash",
        "props": {
            "text":    {"kind": TEXT, "default": "Screen-reader-only text", "label": "Text"},
            "classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "clearfix": {
        "category": "Helpers",
        "label":    "Clearfix",
        "icon":     "bi-arrows-collapse",
        "props": {
            "classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "stretched-link": {
        "category": "Helpers",
        "label":    "Stretched Link",
        "icon":     "bi-arrows-fullscreen",
        "props": {
            "text":    {"kind": TEXT, "default": "Go somewhere", "label": "Link text"},
            "href":    {"kind": URL,  "default": "#",            "label": "URL"},
            "classes": {"kind": TEXT, "default": "stretched-link", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "text-truncate": {
        "category": "Helpers",
        "label":    "Truncated Text",
        "icon":     "bi-text-paragraph",
        "props": {
            "text":    {"kind": RICH, "default": "Praeterea iter est quasdam res quas ex communi opinione bonas est", "label": "Text"},
            "width":   {"kind": TEXT, "default": "250px", "label": "Max width (CSS)"},
            "classes": {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "icon-link": {
        "category": "Helpers",
        "label":    "Icon Link",
        "icon":     "bi-link-45deg",
        "props": {
            "text":    {"kind": TEXT, "default": "Icon link", "label": "Text"},
            "icon":    {"kind": ICON, "default": "box-arrow-up-right", "label": "Icon"},
            "href":    {"kind": URL,  "default": "#",         "label": "URL"},
            "hover":   {"kind": BOOL, "default": True,        "label": "Hover effect"},
            "classes": {"kind": TEXT, "default": "",          "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # CONTENT (extras)
    # ─────────────────────────────────────────────────────────────────────────────
    "table": {
        "category": "Content",
        "label":    "Table",
        "icon":     "bi-table",
        "props": {
            "headers":   {"kind": RICH, "default": "Name\nRole\nCity", "label": "Header cells (one per line)"},
            "rows":      {"kind": RICH, "default": "Alice::Engineer::London\nBob::Designer::Berlin\nCarol::Manager::Paris", "label": "Rows (cell::cell::cell, one row per line)"},
            "variant":   {"kind": ENUM, "default": "", "options": ["", "table-primary", "table-secondary", "table-success", "table-danger", "table-warning", "table-info", "table-light", "table-dark"], "label": "Colour variant"},
            "striped":   {"kind": BOOL, "default": False, "label": "Striped rows"},
            "hover":     {"kind": BOOL, "default": True,  "label": "Hover highlight"},
            "bordered":  {"kind": BOOL, "default": False, "label": "Bordered"},
            "borderless":{"kind": BOOL, "default": False, "label": "Borderless"},
            "small":     {"kind": BOOL, "default": False, "label": "Small"},
            "responsive":{"kind": BOOL, "default": True,  "label": "Responsive wrapper"},
            "caption":   {"kind": TEXT, "default": "",    "label": "Caption (optional)"},
            "classes":   {"kind": TEXT, "default": "",    "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # COMPONENTS (extras — Collapse / Tooltip / Popover / Scrollspy / Navs /
    # Card group / Sticky header / Back-to-top)
    # ─────────────────────────────────────────────────────────────────────────────
    "collapse": {
        "category": "Components",
        "label":    "Collapse (toggle)",
        "icon":     "bi-chevron-expand",
        "props": {
            "buttonText": {"kind": TEXT, "default": "Toggle content", "label": "Button text"},
            "variant":    {"kind": ENUM, "default": "primary", "options": BS_COLORS + [f"outline-{c}" for c in BS_COLORS], "label": "Button variant"},
            "body":       {"kind": RICH, "default": "Some placeholder content for the collapse component. This panel is hidden by default but revealed when the user activates the relevant trigger.", "label": "Body"},
            "openByDefault": {"kind": BOOL, "default": False, "label": "Open by default"},
            "horizontal": {"kind": BOOL, "default": False, "label": "Horizontal"},
            "classes":    {"kind": TEXT, "default": "",    "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "tooltip": {
        "category": "Components",
        "label":    "Tooltip (on button)",
        "icon":     "bi-chat-square-text",
        "props": {
            "text":      {"kind": TEXT, "default": "Hover me",        "label": "Button text"},
            "tooltip":   {"kind": TEXT, "default": "Tooltip content", "label": "Tooltip content"},
            "placement": {"kind": ENUM, "default": "top", "options": ["top", "right", "bottom", "left"], "label": "Placement"},
            "variant":   {"kind": ENUM, "default": "secondary", "options": BS_COLORS + [f"outline-{c}" for c in BS_COLORS], "label": "Button variant"},
            "classes":   {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "popover": {
        "category": "Components",
        "label":    "Popover (on button)",
        "icon":     "bi-chat-right-text",
        "props": {
            "text":      {"kind": TEXT, "default": "Click me",                 "label": "Button text"},
            "title":     {"kind": TEXT, "default": "Popover title",            "label": "Popover title"},
            "body":      {"kind": RICH, "default": "And here's some amazing content. It's very engaging. Right?", "label": "Popover body"},
            "placement": {"kind": ENUM, "default": "right", "options": ["top", "right", "bottom", "left"], "label": "Placement"},
            "trigger":   {"kind": ENUM, "default": "click", "options": ["click", "hover", "focus"], "label": "Trigger"},
            "variant":   {"kind": ENUM, "default": "secondary", "options": BS_COLORS + [f"outline-{c}" for c in BS_COLORS], "label": "Button variant"},
            "classes":   {"kind": TEXT, "default": "", "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "scrollspy": {
        "category": "Components",
        "label":    "Scrollspy Nav",
        "icon":     "bi-list-ol",
        "props": {
            "items":   {"kind": RICH, "default": "First section::First section::Some text about the first section\nSecond section::Second section::Some text about the second section\nThird section::Third section::Some text about the third section", "label": "Sections (nav_label::heading::body, one per line)"},
            "height":  {"kind": TEXT, "default": "300px", "label": "Scroll container height"},
            "classes": {"kind": TEXT, "default": "",     "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "nav": {
        "category": "Components",
        "label":    "Nav (plain)",
        "icon":     "bi-list",
        "props": {
            "items":   {"kind": RICH, "default": "Active::/::active\nLink::/link1\nLink::/link2\nDisabled::#::disabled", "label": "Items (label::href::state, one per line)"},
            "style":   {"kind": ENUM, "default": "", "options": ["", "nav-pills", "nav-tabs", "nav-underline"], "label": "Style"},
            "align":   {"kind": ENUM, "default": "", "options": ["", "justify-content-center", "justify-content-end"], "label": "Align"},
            "vertical":{"kind": BOOL, "default": False, "label": "Vertical (flex-column)"},
            "fill":    {"kind": BOOL, "default": False, "label": "Fill"},
            "classes": {"kind": TEXT, "default": "",    "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "card-group": {
        "category": "Components",
        "label":    "Card Group",
        "icon":     "bi-grid-3x2-gap",
        "props": {
            "layout":  {"kind": ENUM, "default": "card-group", "options": ["card-group", "row-cards"], "label": "Layout"},
            "classes": {"kind": TEXT, "default": "",           "label": "Extra CSS classes"},
        },
        "allows_children": ["card"],
    },
    "back-to-top": {
        "category": "Components",
        "label":    "Back to Top Button",
        "icon":     "bi-arrow-up-circle",
        "props": {
            "label":   {"kind": TEXT, "default": "Back to top",      "label": "ARIA label"},
            "icon":    {"kind": ICON, "default": "arrow-up",         "label": "Icon"},
            "variant": {"kind": ENUM, "default": "primary",          "options": BS_COLORS, "label": "Colour"},
            "classes": {"kind": TEXT, "default": "",                 "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
    "header": {
        "category": "Components",
        "label":    "Page Header",
        "icon":     "bi-window-fullscreen",
        "props": {
            "title":    {"kind": TEXT, "default": "Welcome to our site", "label": "Title"},
            "subtitle": {"kind": RICH, "default": "A simple, bold header to introduce a page.", "label": "Subtitle"},
            "bg":       {"kind": ENUM, "default": "bg-body-tertiary", "options": ["bg-body-tertiary"] + [f"bg-{c}" for c in BS_COLORS], "label": "Background"},
            "textColor":{"kind": ENUM, "default": "",                 "options": [""] + [f"text-{c}" for c in BS_COLORS], "label": "Text colour"},
            "align":    {"kind": ENUM, "default": "text-center",      "options": ["text-start", "text-center", "text-end"], "label": "Align"},
            "classes":  {"kind": TEXT, "default": "py-4",             "label": "Extra CSS classes"},
        },
        "allows_children": False,
    },
}


def get_catalogue():
    """Return the full catalogue as list of dicts (stable order), for the frontend palette."""
    out = []
    for type_name, spec in TYPES.items():
        out.append({
            "type":     type_name,
            "category": spec["category"],
            "label":    spec["label"],
            "icon":     spec.get("icon", "bi-square"),
            "props":    spec["props"],
            "allowsChildren": spec.get("allows_children", False),
        })
    return out


def default_props(type_name: str) -> dict:
    """Build a default props dict for a newly-dropped component of this type."""
    spec = TYPES.get(type_name)
    if not spec:
        return {}
    return {k: v["default"] for k, v in spec["props"].items()}


def new_node(type_name: str, **overrides) -> dict:
    """Factory helper: create a new node with defaults, optionally overriding props."""
    spec = TYPES.get(type_name)
    if not spec:
        raise ValueError(f"Unknown component type: {type_name}")
    props = default_props(type_name)
    props.update(overrides)
    node = {"type": type_name, "props": props}
    if spec.get("allows_children"):
        node["children"] = []
    return node
