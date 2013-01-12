# -*- coding: utf-8 -*-
from collections import defaultdict
from acrylamid.views.entry import Translation
from acrylamid.helpers import union, joinurl, expand
import os
from datetime import datetime


def entry_filename(entry):
    return entry.filename.split(os.path.sep)[-1]


class E9Base(Translation):
    def __init__(self, *args, **kw):
        Translation.__init__(self, *args, **kw)
        self.langs = set()

    def _entry_for_lang(self, request, lang, entry):
        try:
            for t in request['translations']:
                if t.identifier == entry.identifier and t.lang == lang:
                    return t
            return entry
        except (AttributeError, KeyError):
            return  entry

    def context(self, env, request):
        for t in request['translations'][:]:
            self.langs.add(t.lang)
        self.langs.add(self.conf.lang)

        globals = {
            'navmenu': dict(),
            'footer_about': dict(),
            'footer_navmenu': dict()
        }

        for e in request['entrylist']+request['translations']+request['pages']:
            try:
                if e.identifier == 'navmenu':
                    globals['navmenu'][e.lang] = e
                elif e.identifier == 'footer_about':
                    globals['footer_about'][e.lang] = e
                elif e.identifier == 'footer_navmenu':
                    globals['footer_navmenu'][e.lang] = e
            except AttributeError:
                pass

        def get_globals(elem, lang):
            if elem in globals and lang in globals[elem]:
                return globals[elem][lang]
            return None
        env.get_globals = get_globals

        env = Translation.context(self, env, request)
        env.current_year = datetime.now().year
        return env


class E9Home(E9Base):
    def _clean_permalink(self, entry):
        toks = entry.permalink.split('/')
        if self.conf.lang in toks:
            toks.remove(self.conf.lang)
        entry.permalink = '/'.join(toks)
        return entry

    def _populate_entries(self, request, lang=None):
        entry_dict = {
            'hero_list': [],
            'banners': [],
            'expertise': {},
        }
        if lang is None:
            lang = self.conf.lang

        for e in request['entrylist'] + request['pages']:
            e = self._entry_for_lang(request, lang, e)
            e = self._clean_permalink(e)
            if 'banners' in e.filename.split(os.path.sep):
                entry_dict['banners'].append(e)
                print e.permalink
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
        request['env']['entry_dict'] = self._populate_entries(request)
        request['env']['lang'] = self.conf['lang']
        path = joinurl(self.conf['output_dir'], '/index.html')
        tt = self.env.engine.fromfile(self.template)
        html = tt.render(conf=self.conf, env=union(self.env,
            type=self.__class__.__name__.lower()))

        yield html, path


class E9Homei18n(E9Home):
    def generate(self, request):
        for lang in self.langs:
            request['env']['entry_dict'] = self._populate_entries(request,lang)
            request['env']['path'] = '/'
            request['env']['lang'] = lang
            path = joinurl(self.conf['output_dir'], lang, 'index.html')
            tt = self.env.engine.fromfile(self.template)
            html = tt.render(conf=self.conf, env=union(self.env,
                type=self.__class__.__name__.lower()))

            yield html, path


class E9Page(E9Base):
    @property
    def type(self):
        return 'pages'

    def context(self, env, request):

        translations = defaultdict(list)
        for entry in request['pages'][:]:

            if entry.hasproperty('identifier'):
                translations[entry.identifier].append(entry)

                if entry.lang != self.conf.lang:
                    entry.props['entry_permalink'] = self.path

                    # remove from original entrylist
                    request['pages'].remove(entry)
                    request['translations'].append(entry)

        env = E9Base.context(self, env, request)
        return env

    def generate(self, request):
        for lang in self.langs:
            for entry in request['pages']:
                entry = self._entry_for_lang(request, lang, entry)
                path = ''
                route = expand(self.path, entry)
                if entry.hasproperty('permalink'):
                    path = joinurl(self.conf['output_dir'], entry.permalink)
                elif lang == self.conf.lang:
                    path = joinurl(self.conf['output_dir'], entry.slug, '/')
                    entry.permalink = entry.permalink[:-3]
                else:
                    path = joinurl(self.conf['output_dir'], expand(self.path, entry))

                if path.endswith('/'):
                    path = joinurl(path, 'index.html')

                #request['env']['entry_dict'] = self._populate_entries(request,lang)
                request['env']['path'] = '/'
                request['env']['lang'] = lang
                #path = joinurl(self.conf['output_dir'], lang, 'index.html')

                print self.path,lang,route
                tt = self.env.engine.fromfile(self.template)
                html = tt.render(conf=self.conf, entry=entry, env=union(self.env,
                    type=self.__class__.__name__.lower(), route=route))

                yield html, path
