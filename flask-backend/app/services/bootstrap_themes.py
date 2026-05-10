"""
Bootstrap 5.3 themes catalogue.

All Bootswatch themes (v5.3) via jsdelivr CDN, plus the stock default.
Used by:
  - The frontend editor preview (to load the correct CSS)
  - The public site renderer (to emit the correct <link> tag)

Source: https://bootswatch.com/  (MIT licensed)
"""

BOOTSTRAP_VERSION = "5.3.8"

# Direct-from-CDN assets (jsdelivr mirrors npm)
BOOTSTRAP_CSS = f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css"
BOOTSTRAP_JS  = f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/bootstrap.bundle.min.js"
BOOTSTRAP_ICONS_CSS = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"

BOOTSWATCH_VERSION = "5.3.8"
BOOTSWATCH_BASE    = f"https://cdn.jsdelivr.net/npm/bootswatch@{BOOTSWATCH_VERSION}/dist"


# All Bootswatch 5.3 themes. Keep slugs URL/DB-safe (lowercase).
# Human-friendly name + one-line description for the UI.
THEMES = [
    {"slug": "default",   "name": "Default",   "description": "Bootstrap's classic look.",          "is_dark": False},
    {"slug": "cerulean",  "name": "Cerulean",  "description": "A calm blue sky.",                   "is_dark": False},
    {"slug": "cosmo",     "name": "Cosmo",     "description": "An ode to Metro.",                   "is_dark": False},
    {"slug": "cyborg",    "name": "Cyborg",    "description": "Jet black and electric blue.",       "is_dark": True},
    {"slug": "darkly",    "name": "Darkly",    "description": "Flatly in night mode.",              "is_dark": True},
    {"slug": "flatly",    "name": "Flatly",    "description": "Flat and modern.",                   "is_dark": False},
    {"slug": "journal",   "name": "Journal",   "description": "Crisp like a new sheet of paper.",   "is_dark": False},
    {"slug": "litera",    "name": "Litera",    "description": "The medium is the message.",         "is_dark": False},
    {"slug": "lumen",     "name": "Lumen",     "description": "Light and shadow.",                  "is_dark": False},
    {"slug": "lux",       "name": "Lux",       "description": "A touch of class.",                  "is_dark": False},
    {"slug": "materia",   "name": "Materia",   "description": "Material is the metaphor.",          "is_dark": False},
    {"slug": "minty",     "name": "Minty",     "description": "A fresh feel.",                      "is_dark": False},
    {"slug": "morph",     "name": "Morph",     "description": "A neumorphic layer.",                "is_dark": False},
    {"slug": "pulse",     "name": "Pulse",     "description": "A trace of purple.",                 "is_dark": False},
    {"slug": "quartz",    "name": "Quartz",    "description": "A glassmorphic layer.",              "is_dark": True},
    {"slug": "sandstone", "name": "Sandstone", "description": "A touch of warmth.",                 "is_dark": False},
    {"slug": "simplex",   "name": "Simplex",   "description": "Mini and minimalist.",               "is_dark": False},
    {"slug": "sketchy",   "name": "Sketchy",   "description": "A hand-drawn look for mockups.",     "is_dark": False},
    {"slug": "slate",     "name": "Slate",     "description": "Shades of gunmetal grey.",           "is_dark": True},
    {"slug": "solar",     "name": "Solar",     "description": "A spin on Solarized.",               "is_dark": True},
    {"slug": "spacelab",  "name": "Spacelab",  "description": "Silvery and sleek.",                 "is_dark": False},
    {"slug": "superhero", "name": "Superhero", "description": "The brave and the blue.",            "is_dark": True},
    {"slug": "united",    "name": "United",    "description": "Ubuntu orange and unique font.",     "is_dark": False},
    {"slug": "vapor",     "name": "Vapor",     "description": "A cyberpunk aesthetic.",             "is_dark": True},
    {"slug": "yeti",      "name": "Yeti",      "description": "A friendly foundation.",             "is_dark": False},
    {"slug": "zephyr",    "name": "Zephyr",    "description": "Breezy and beautiful.",              "is_dark": False},
    {"slug": "brite",     "name": "Brite",     "description": "Bright and electric.",               "is_dark": False},
]

THEME_SLUGS = [t["slug"] for t in THEMES]


def theme_css_url(slug: str) -> str:
    """Return the CDN URL for a given theme, or the default Bootstrap CSS."""
    if slug in (None, "", "default"):
        return BOOTSTRAP_CSS
    if slug not in THEME_SLUGS:
        return BOOTSTRAP_CSS
    return f"{BOOTSWATCH_BASE}/{slug}/bootstrap.min.css"


def theme_exists(slug: str) -> bool:
    return slug in THEME_SLUGS or slug in (None, "", "default")
