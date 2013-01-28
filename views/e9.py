# -*- coding: utf-8 -*-
from collections import defaultdict
from acrylamid import AcrylamidException
from acrylamid.views.entry import Base
from acrylamid.helpers import union, joinurl, expand
from acrylamid.utils import Struct, HashableList, hash as acr_hash
import os
from datetime import datetime


class TranslationNotFound(Exception):
    pass


class HashableSet(set):
    def __hash__(self):
        return acr_hash(*self)


def entry_for_lang(request, lang, entry):
    for t in request['translations']:
        if t.props.identifier == entry.props.identifier and t.props.lang == lang:
            return t
    raise TranslationNotFound()


class E9Base(Base):
    """Base class for views in this site.

    The view collects common data needed to *every* site page and push it in
    the global context (e.g. menubar, footer, etc...)

    """
    def init(self, conf, env, template='main.html'):
        if not 'langs' in env:
            env['langs'] = HashableSet()
        self.conf = conf
        Base.init(self, conf, env, template)

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

    def context(self, conf, env, request):
        """This method fills up translations variable in the request (like
        Translation class in Acrylamid), creates a languages list based on the
        request contents and fill the context with common data needed by every
        page

        """
        if len(request['translations']):
            return env

        translations = defaultdict(list)
        for key in ('pages', 'entrylist', 'drafts'):
            for entry in request[key][:]:
                if not entry.hasproperty('identifier'):
                    continue

                # check for duplicated identifiers
                for t in translations[entry.props.identifier]:
                    if entry.props.identifier == t.props.identifier and entry.props.lang == t.props.lang:
                        raise AcrylamidException("{}: Identifier '{}' already set for entry {}".format(entry, entry.props.identifier, t))

                translations[entry.props.identifier].append(entry)
                env.langs.add(entry.props.lang)
                if entry.props.lang != self.conf.lang:
                    # remove from original entrylist
                    request[key].remove(entry)
                    request['translations'].append(entry)

        globals = {
            'navmenu':Struct(),
            'footer_about':Struct(),
            'footer_navmenu':Struct(),
        }

        for e in request['entrylist']+request['pages']+request['translations']+request['drafts']:
            try:
                globals[e.props.identifier][e.props.lang] = e
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
                p = entry_for_lang(request, lang, entry)
                if not p.hasproperty('permalink'):
                    p.permalink = self._strip_default_lang(expand(self.path, p))
                pages.append(p)
            except TranslationNotFound:
                pages.append(entry)
        return pages

    def generate(self, conf, env, request):
        for lang in env.langs:
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

                tt = env.engine.fromfile(self.template)
                html = tt.render(conf=conf, entry=entry, env=union(env,
                    type=self.__class__.__name__.lower(), route=route))

                yield html, path


class ActivitiesPage(PageBase):
    def _get_page_list(self, request, lang):
        pages = []
        for entry in request['pages']:
            if not 'activities' in entry.filename.split(os.path.sep):
                continue
            if entry.context.condition and not entry.context.condition(entry):
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
        pages = HashableList()
        for entry in request['pages']:
            if not 'expertise' in entry.filename.split(os.path.sep):
                continue
            if entry.context.condition and not entry.context.condition(entry):
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
        entry_dict = Struct({
            'hero_list': HashableList(),
            'activities': HashableList(),
            'expertise': Struct(),
            'banners': HashableList(),
        })
        for entry in request['pages'] + request['entrylist'] + request['drafts']:
            if entry.context.condition and not entry.context.condition(entry):
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
                    if entry.props.identifier == 'homepage':
                        pages.append(e)
            except KeyError:
                pass

        request['env']['entry_dict'] = entry_dict
        return pages
