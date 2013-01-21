# -*- coding: utf-8 -*-
from collections import defaultdict
from acrylamid import AcrylamidException
from acrylamid.views.entry import Base
from acrylamid.helpers import union, joinurl, expand
import os
from datetime import datetime


class TranslationNotFound(Exception):
    pass


def entry_filename(entry):
    return entry.filename.split(os.path.sep)[-1]


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

    def _strip_current_lang(self, url):
        """Strip the part of the url containing language code.

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
                print entry.filename,entry.lang
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
                print 'appending',e.filename
            except (KeyError, AttributeError):
                continue

        # inject globals into the env
        for k,v in globals.iteritems():
            env[k] = v

        from pprint import pprint
        pprint (env)

        # other global futilities...
        env.current_year = datetime.now().year
        self.env = env

        return env


class BasePage(E9Base):
    @property
    def type(self):
        return 'pages'

    def generate(self, request):
        for lang in self.env.langs:
            for entry in request['pages']:
                path = ''
                route = self._strip_current_lang(expand(self.path, entry))

                if entry.hasproperty('permalink'):
                    path = joinurl(self.conf['output_dir'], entry.permalink)
                elif lang == self.conf.lang:
                    path = joinurl(self.conf['output_dir'], route, '/')
                    entry.permalink = route
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


class ExpertisePage(E9Base):
    """Renders the page "Expertise"

    Load contents from expertise folder

    """
    @property
    def type(self):
        return 'pages'

    def generate(self, request):
        for lang in self.env.langs:
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

            for entry in pages:
                path = ''
                route = self._strip_current_lang(expand(self.path, entry))

                if entry.hasproperty('permalink'):
                    path = joinurl(self.conf['output_dir'], entry.permalink)
                elif lang == self.conf.lang:
                    path = joinurl(self.conf['output_dir'], route, '/')
                    entry.permalink = route
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


class E9Home(E9Base):
    priority = 100.0

    @property
    def type(self):
        return 'pages'

    def _populate_entries(self, request, lang=None):
        entry_dict = {
            'hero_list': [],
            'banners': [],
            'expertise': {},
        }
        if lang is None:
            lang = self.conf.lang

        for e in request['entrylist'] + request['pages']:
            try:
                e = entry_for_lang(request, lang, e)
            except TranslationNotFound:
                pass

            e.permalink = self._strip_current_lang(e.permalink)

            if 'banners' in e.filename.split(os.path.sep):
                entry_dict['banners'].append(e)
            elif 'hero-list' in e.filename.split(os.path.sep):
                entry_dict['hero_list'].append(e)
            elif 'expertise' in e.filename.split(os.path.sep):
                try:
                    entry_dict['expertise'][e.frontpage] = e
                except KeyError:
                    pass
            else:
                entry_dict[e.slug] = e

        return entry_dict

    def generate(self, request):
        for lang in self.env.langs:
            request['env']['entry_dict'] = self._populate_entries(request,lang)
            request['env']['lang'] = lang

            if lang != self.conf.lang:
                request['env']['path'] = '/'
                path = joinurl(self.conf['output_dir'], lang, 'index.html')
            else:
                path = joinurl(self.conf['output_dir'], 'index.html')

            tt = self.env.engine.fromfile(self.template)
            html = tt.render(conf=self.conf, env=union(self.env,
                type=self.__class__.__name__.lower()))

            yield html, path
