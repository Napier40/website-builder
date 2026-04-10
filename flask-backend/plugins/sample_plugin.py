"""
Sample Plugin
Demonstrates the plugin system architecture.
This plugin adds a watermark to new pages and logs website creation events.
"""
import logging

logger = logging.getLogger(__name__)

# Plugin metadata
PLUGIN_NAME = 'sample_plugin'
PLUGIN_VERSION = '1.0.0'

# ─── Hook handlers ────────────────────────────────────────────────────────────

def on_website_created(data: dict) -> dict:
    """
    Hook: website.created
    Called whenever a new website is created.
    Logs the event and adds metadata to the response.
    """
    logger.info(f"[SamplePlugin] New website created: {data.get('name', 'Unknown')}")
    # We could enrich the data here, e.g., send a welcome email
    data['_plugin_processed'] = True
    return data


def on_page_created(data: dict) -> dict:
    """
    Hook: page.created
    Called when a new page is added.
    """
    logger.info(f"[SamplePlugin] New page created: {data.get('title', 'Unknown')}")
    return data


def on_user_registered(data: dict) -> dict:
    """
    Hook: user.registered
    Called when a new user registers.
    """
    logger.info(f"[SamplePlugin] New user registered: {data.get('email', 'Unknown')}")
    return data


# ─── Hook registration ────────────────────────────────────────────────────────

# Maps hook names to handler functions
HOOKS = {
    'website.created': on_website_created,
    'page.created': on_page_created,
    'user.registered': on_user_registered,
}


def setup(settings: dict = None):
    """
    Called when the plugin is loaded/activated.
    settings: the plugin's saved configuration dict from the database.
    """
    settings = settings or {}
    logger.info(f"[SamplePlugin] Plugin initialized with settings: {settings}")


def teardown():
    """Called when the plugin is deactivated or the app shuts down."""
    logger.info("[SamplePlugin] Plugin deactivated.")