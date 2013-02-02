# -*- encoding: utf-8 -*-

SITENAME = 'Evonove - Software'
WWW_ROOT = 'http://evonove.it/'
AUTHOR = 'staff'
EMAIL = 'info@evonove.it'
LANG = 'it'

VIEWS = {
    '/:lang/': {
        'view': 'e9home',
        'template': 'home.html'
    },

    '/:year/:slug/:lang/': {
        'view': 'entry',
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
    },

    #'/sitemap.xml': {'view': 'sitemap'},

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

PAGE_PERMALINK = '/:slug/:lang/'
THEME = 'bizstrap'
ENGINE = 'acrylamid.templates.jinja2.Environment'
DATE_FORMAT = '%d.%m.%Y, %H:%M'
STATIC = ['static']
VIEWS_DIR = 'views'
FILTERS_DIR = 'filters'
FILTERS = ['rst', 'h1']
