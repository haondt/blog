AUTHOR = 'haondt'
SITENAME = 'haondt[blog]'
SITEURL = ""

PATH = "content"

TIMEZONE = 'America/Edmonton'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("Pelican", "https://getpelican.com/"),
    ("Python.org", "https://www.python.org/"),
    ("Jinja2", "https://palletsprojects.com/p/jinja/"),
    ("You can modify those links in your config file", "#"),
)

# Social widget
SOCIAL = (
    ("You can add links in your config file", "#"),
    ("Another social link", "#"),
)

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

THEME = 'themes/goldrush'

DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = False

MENUITEMS = [
    ("haondt", "https://haondt.dev"),
]

DEFAULT_DATE_FORMAT = "%b %-d, %Y"


# Theme specific settings

DISPLAY_ARCHIVES_ON_MENU = True
