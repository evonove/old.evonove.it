# -*- coding: utf-8 -*-
from acrylamid.views.entry import Translation
import os
from pprint import pprint

def entry_filename(entry):
    return entry.filename.split(os.path.sep)[-1]


def entry_for_lang(request, entry):
    try:
        lang = request['env']['route'][1:-1]
        for t in request.get('translations'):
            if t.identifier == entry.identifier and t.lang == lang:
                return t
        return entry
    except (AttributeError, KeyError):
        return  entry


class E9Home(Translation):
    def __init__(self, *args, **kw):
        Translation.__init__(self, *args, **kw)

    def generate(self, request):
        content_dir = os.path.abspath(self.conf['content_dir'])

        entry_dict = {}
        #pprint(request)

        for e in request['entrylist']:
            #print e, [x for x in request['env']['translationsfor'](e)]
            e = entry_for_lang(request, e)
            if 'banners' in e.filename.split(os.path.sep):
                entry_dict.setdefault('banners', []).append(e)
            elif 'hero-list' in e.filename.split(os.path.sep):
                entry_dict.setdefault('hero_list', []).append(e)
            else:
                entry_dict[e.slug] = e

        request['env']['entry_dict'] = entry_dict
        request['env']['path'] = '/'

        return Translation.generate(self, request)
