# -*- coding: utf-8 -*-
from acrylamid.views.entry import Translation, Base
from acrylamid.helpers import expand, union, joinurl, event
import os
from os.path import isfile
from pprint import pprint

def entry_filename(entry):
    return entry.filename.split(os.path.sep)[-1]


def entry_for_lang(request, lang, entry):
    try:
        for t in request.get('translations'):
            if t.identifier == entry.identifier and t.lang == lang:
                return t
        return entry
    except (AttributeError, KeyError):
        return  entry


class E9Base(Translation):
    pass


class E9Home(Translation):
    def __init__(self, *args, **kw):
        Translation.__init__(self, *args, **kw)

    def generate(self, request):
        content_dir = os.path.abspath(self.conf['content_dir'])

        entry_dict = {}
        #request['entrylist'] = []
        #pprint(request)

        for e in request['entrylist']:
            e = entry_for_lang(request, 'en', e)
            if 'banners' in e.filename.split(os.path.sep):
                entry_dict.setdefault('banners', []).append(e)
            elif 'hero-list' in e.filename.split(os.path.sep):
                entry_dict.setdefault('hero_list', []).append(e)
            else:
                entry_dict[e.slug] = e

        request['env']['entry_dict'] = entry_dict
        request['env']['path'] = '/'
        path = joinurl(self.conf['output_dir'], 'en', 'index.html')
        tt = self.env.engine.fromfile(self.template)
        html = tt.render(conf=self.conf, env=union(self.env,
            type=self.__class__.__name__.lower()))

        yield html, path


class E9HomeIt(Translation):
    def __init__(self, *args, **kw):
        Translation.__init__(self, *args, **kw)

    def generate(self, request):
        entry_dict = {}

        for e in request['entrylist']:
            if 'banners' in e.filename.split(os.path.sep):
                entry_dict.setdefault('banners', []).append(e)
            elif 'hero-list' in e.filename.split(os.path.sep):
                entry_dict.setdefault('hero_list', []).append(e)
            else:
                entry_dict[e.slug] = e

        request['env']['entry_dict'] = entry_dict
        path = joinurl(self.conf['output_dir'], '/index.html')
        tt = self.env.engine.fromfile(self.template)
        html = tt.render(conf=self.conf, env=union(self.env,
            type=self.__class__.__name__.lower()))

        yield html, path
