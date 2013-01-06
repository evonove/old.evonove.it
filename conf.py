# -*- encoding: utf-8 -*-
# This is your configuration file.  Please write valid python!
# See http://posativ.org/acrylamid/conf.py.html

SITENAME = 'Evonove - Software'
WWW_ROOT = 'http://evonove.it/'
AUTHOR = 'staff'
EMAIL = 'info@evonove.it'

VIEWS = {
    '/': {'view': 'homepage', 'template': 'home.html'},

    #'/:year/:slug/': {'view': 'entry'},

    #'/tag/:name/': {'filters': 'summarize', 'view':'tag', 'pagination': '/tag/:name/:num'},

    # per tag Atom or RSS feed. Just uncomment to generate them.

    # '/tag/:name/atom/': {'filters': ['h2', 'nohyphenate'], 'view': 'atompertag'},
    # '/tag/:name/rss/': {'filters': ['h2', 'nohyphenate'], 'view': 'rsspertag'},

    #'/atom/': {'filters': ['h2', 'nohyphenate'], 'view': 'atom'},
    #'/rss/': {'filters': ['h2', 'nohyphenate'], 'view': 'rss'},

    #'/articles/': {'view': 'articles'},

    #'/sitemap.xml': {'view': 'sitemap'},

    # Here are some more examples

    # # '/:slug/' is a slugified url of your static page's title
    #'/:slug/': {'view': 'page'}

    # # '/atom/full/' will give you a _complete_ feed of all your entries
    # '/atom/full/': {'filters': 'h2', 'view': 'atom', 'num_entries': 1000},

    # # a feed containing all entries tagges with 'python'
    # '/rss/python/': {'filters': 'h2', 'view': 'rss',
    #                  'if': lambda e: 'python' in e.tags}

    # # a full typography features entry including MathML and Footnotes
    # '/:year/:slug': {'filters': ['typography', 'Markdown+Footnotes+MathML'],
    #                  'view': 'entry'}
}

FILTERS = ['rst', 'hyphenate', 'h1']
THEME = 'bizstrap'
ENGINE = 'acrylamid.templates.jinja2.Environment'
DATE_FORMAT = '%d.%m.%Y, %H:%M'
STATIC = ['static']
VIEWS_DIR = 'views'
