"""Quiet Asterisk site engine (v2): a content layer plus a build pipeline.

The engine never writes HTML itself. It loads content, turns it into plain
data (see qa.pages), and hands that data to a theme (themes/<name>/), which
owns every template, stylesheet and script. Replace the theme folder and the
site looks completely different; content and engine stay untouched.
"""

__version__ = "2.0.0"
THEME_CONTRACT_VERSION = 2
