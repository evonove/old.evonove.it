# -*- encoding: utf-8 -*-

SITENAME = 'Evonove - '
WWW_ROOT = 'http://evonove.it/'
AUTHOR = 'staff'
EMAIL = 'info@evonove.it'
LANG = 'it'

VIEWS = {
    '/:lang/': {
        'view': 'e9home',
        'template': 'home.html',
    },

    '/blog/:year/:slug/:lang/': {
        'view': 'e9entry',
        'template': 'entry.html',
    },

    #'/tag/:name/': {'filters': 'summarize', 'view':'tag', 'pagination': '/tag/:name/:num'},

    # per tag Atom or RSS feed. Just uncomment to generate them.

    # '/tag/:name/atom/': {'filters': ['h2', 'nohyphenate'], 'view': 'atompertag'},
    # '/tag/:name/rss/': {'filters': ['h2', 'nohyphenate'], 'view': 'rsspertag'},

    #'/atom/': {'filters': ['h2', 'nohyphenate'], 'view': 'atom'},
    #'/rss/': {'filters': ['h2', 'nohyphenate'], 'view': 'rss'},

    '/blog/:lang/': {
        'view': 'e9index',
        'template': 'blog.html',
        'pagination': '/blog/page/:num/:lang/',
        'filters': 'intro',
    },

    '/sitemap.xml': {'view': 'sitemap'},

    # Here are some more examples

    # # '/:slug/' is a slugified url of your static page's title
    '/:slug/:lang/': {
        'view': 'pagebase',
        'if': lambda e: all(x not in e.filename for x in ('expertise','activities')),
        'template': 'page_base.html'
    },

    '/activities/:slug/:lang/': {
        'view': 'activitiespage',
        'template': 'page_activities.html'
    },

    '/expertise/:slug/:lang/': {
        'view': 'expertisepage',
        'template': 'page_expertise.html'
    },

    # # '/atom/full/' will give you a _complete_ feed of all your entries
    # '/atom/full/': {'filters': 'h2', 'view': 'atom', 'num_entries': 1000},

    # # a feed containing all entries tagges with 'python'
    # '/rss/python/': {'filters': 'h2', 'view': 'rss',
    #                  'if': lambda e: 'python' in e.tags}

    # # a full typography features entry including MathML and Footnotes
    # '/:year/:slug': {'filters': ['typography', 'Markdown+Footnotes+MathML'],
    #                  'view': 'entry'}
}

DEPLOYMENT = {
    "ls": "ls $OUTPUT_DIR",
    "echo": "echo '$OUTPUT_DIR'",
    "default": "rsync -av --delete $OUTPUT_DIR evonove@evonove.it:~/webapps/evostatic"
}

PAGE_PERMALINK = '/:slug/:lang/'
THEME = 'bizstrap'
ENGINE = 'acrylamid.templates.jinja2.Environment'
DATE_FORMAT = '%d.%m.%Y, %H:%M'
STATIC = ['static']
VIEWS_DIR = 'views'
FILTERS = ['rst', 'h1']
INTRO_LINK= ''

# Custom configuration
GRAVATAR_404 = 'http://beta.evonove.it/img/placeholder_60_60.png'
GRAVATAR_SIZE = 60
