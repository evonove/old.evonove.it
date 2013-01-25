# -*- coding: utf-8 -*-
from collections import defaultdict
from acrylamid import AcrylamidException
from acrylamid.views.entry import Base
from acrylamid.helpers import union, joinurl, expand
import os
from datetime import datetime


class TranslationNotFound(Exception):
    pass


def entry_for_lang(request, lang, entry):
    for t in request['translations']:
        if t.identifier == entry.identifier and t.lang == lang:
            return t
    raise TranslationNotFound()


class E9Base(Base):
    """Base class for views in this site.

    The view collects common data needed to *every* site page and push it in
    the global context (e.g. menubar, footer, etc...)

    """
    def __init__(self, conf, env, **kwargs):
        if not 'langs' in env:
            env['langs'] = set()
        Base.__init__(self, conf, env, **kwargs)

    def _strip_default_lang(self, url):
        """Strip the part of the url containing default language code. In this
        way, default lang will not have postfix in urls (e.g. blog/ instead of
        /blog/it/)

        NOTICE: this approach is very silly since it does not check against the
        real path of the view - e.g. a legit path like /path/to/it/:lang:/
        would return a wrong result for 'it' language code

        """
        toks = url.split('/')
        if self.conf.lang in toks:
            toks.remove(self.conf.lang)
        url = '/'.join(toks)
        return url

    def context(self, env, request):
        """This method fills up translations variable in the request (like
        Translation class in Acrylamid), creates a languages list based on the
        request contents and fill the context with common data needed by every
        page

        """
        if len(request['translations']):
            return env

        translations = defaultdict(list)
        for key in ('pages', 'entrylist'):
            for entry in request[key][:]:
                if not entry.hasproperty('identifier'):
                    continue

                # check for duplicated identifiers
                for t in translations[entry.identifier]:
                    if entry.identifier == t.identifier and entry.lang == t.lang:
                        raise AcrylamidException("{}: Identifier '{}' already set for entry {}".format(entry, entry.identifier, t))

                translations[entry.identifier].append(entry)
                env.langs.add(entry.lang)
                if entry.lang != self.conf.lang:
                    # remove from original entrylist
                    request[key].remove(entry)
                    request['translations'].append(entry)

        globals = {
            'navmenu':dict(),
            'footer_about':dict(),
            'footer_navmenu':dict(),
        }

        for e in request['entrylist']+request['pages']+request['translations']:
            try:
                globals[e.identifier][e.lang] = e
            except (KeyError, AttributeError):
                continue

        # inject globals into the env
        for k,v in globals.iteritems():
            env[k] = v

        # other global futilities...
        env.current_year = datetime.now().year


        self.env = env

        return env


class PageBase(E9Base):
    """Base class for all the views which generate pages. Expose a common
    algorythm with a template method (_get_page_list) suclasses can override
    to customize which pages have to be generated

    """
    @property
    def type(self):
        return 'pages'

    def _get_page_list(self, request, lang):
        """Get a list containing the pages to generate for the required
        language

        """
        pages = []
        for entry in request['pages']:
            if not entry.context.condition(entry):
                continue
            try:
                pages.append(entry_for_lang(request, lang, entry))
            except TranslationNotFound:
                pages.append(entry)
        return pages

    def generate(self, request):
        for lang in self.env.langs:
            for entry in self._get_page_list(request, lang):
                path = ''
                route = self._strip_default_lang(expand(self.path, entry))

                if entry.hasproperty('permalink'):
                    path = joinurl(self.conf['output_dir'], entry.permalink)
                elif lang == self.conf.lang:
                    path = joinurl(self.conf['output_dir'], route, '/')
                else:
                    path = joinurl(self.conf['output_dir'], expand(self.path, entry))

                if path.endswith('/'):
                    path = joinurl(path, 'index.html')

                request['env']['path'] = '/'
                request['env']['lang'] = lang

                tt = self.env.engine.fromfile(self.template)
                html = tt.render(conf=self.conf, entry=entry, env=union(self.env,
                    type=self.__class__.__name__.lower(), route=route))

                yield html, path


class ActivitiesPage(PageBase):
    def _get_page_list(self, request, lang):
        pages = []
        for entry in request['pages']:
            if not 'activities' in entry.filename.split(os.path.sep):
                continue
            if not entry.context.condition(entry):
                continue
            try:
                pages.append(entry_for_lang(request, lang, entry))
            except TranslationNotFound:
                pages.append(entry)
        return pages


class ExpertisePage(PageBase):
    """Renders the page "Expertise"

    Load contents from expertise folder, we expect all valid contents are of
    page type

    """
    def _get_page_list(self, request, lang):
        pages = []
        for entry in request['pages']:
            if not 'expertise' in entry.filename.split(os.path.sep):
                continue
            if not entry.context.condition(entry):
                continue
            try:
                pages.append(entry_for_lang(request, lang, entry))
            except TranslationNotFound:
                pages.append(entry)

        request['env']['expertiselist'] = pages

        return pages


class E9Home(PageBase):
    """The homepage view. Since in homepage we have a lot of different contents
    coming from different rst files we have to load them and populate the
    context accordingly. Notice: some contents needed to compose the homepage
    do not actually generate pages.

    """
    priority = 100.0

    @property
    def type(self):
        return 'pages'

    def _get_page_list(self, request, lang):
        pages = []
        entry_dict = {
            'hero_list': [],
            'activities': [],
            'expertise': {},
            'banners': [],
        }
        for entry in request['pages'] + request['entrylist']:
            if not entry.context.condition(entry):
                continue

            try:
                e = entry_for_lang(request, lang, entry)
            except TranslationNotFound:
                e = entry

            try:
                if 'banners' in e.filename.split(os.path.sep):
                    entry_dict['banners'].append(e)
                elif 'activities' in e.filename.split(os.path.sep):
                    entry_dict['activities'].append(e)
                elif 'hero-list' in e.filename.split(os.path.sep):
                    entry_dict['hero_list'].append(e)
                elif 'expertise' in e.filename.split(os.path.sep):
                    entry_dict['expertise'][e.frontpage] = e
                else:
                    entry_dict[e.slug] = e
                    if entry.identifier == 'homepage':
                        pages.append(e)

            except KeyError:
                pass

        request['env']['entry_dict'] = entry_dict
        return pages
