# -*- coding: utf-8 -*-
from acrylamid.views.entry import Translation
from acrylamid.helpers import union, joinurl
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

    def _populate_entries(self, request, lang=None):
        entry_dict = {}
        for e in request['entrylist']:
            if lang:
                e = self._entry_for_lang(request, lang, e)
            if 'banners' in e.filename.split(os.path.sep):
                entry_dict.setdefault('banners', []).append(e)
            elif 'hero-list' in e.filename.split(os.path.sep):
                entry_dict.setdefault('hero_list', []).append(e)
            else:
                entry_dict[e.slug] = e

        return entry_dict

    def context(self, env, request):
        for t in request['translations'][:]:
            self.langs.add(t.lang)

        env = Translation.context(self, env, request)
        env.current_year = datetime.now().year
        return env


class E9Home(E9Base):
    def generate(self, request):
        request['env']['entry_dict'] = self._populate_entries(request)
        path = joinurl(self.conf['output_dir'], '/index.html')
        tt = self.env.engine.fromfile(self.template)
        html = tt.render(conf=self.conf, env=union(self.env,
            type=self.__class__.__name__.lower()))

        yield html, path


class E9Homei18n(E9Base):
    def generate(self, request):
        for lang in self.langs:
            request['env']['entry_dict'] = self._populate_entries(request,lang)
            request['env']['path'] = '/'
            path = joinurl(self.conf['output_dir'], lang, 'index.html')
            tt = self.env.engine.fromfile(self.template)
            html = tt.render(conf=self.conf, env=union(self.env,
                type=self.__class__.__name__.lower()))

            yield html, path
