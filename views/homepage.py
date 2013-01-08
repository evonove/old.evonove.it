# -*- coding: utf-8 -*-
import acrylamid
from acrylamid.views.index import Index

import os


def entry_filename(entry):
    return entry.filename.split(os.path.sep)[-1]


class Homepage(Index):
    def __init__(self, *args, **kw):
        Index.__init__(self, *args, **kw)

    def generate(self, request):

        content_dir = os.path.abspath(self.conf['content_dir'])

        self.env['banners'] = []
        self.env['homepage_entry'] = None
        self.env['callout'] = None
        self.env['hero_list'] = []

        for e in request['entrylist']:
            fname = entry_filename(e)
            if 'banners' in e.filename.split(os.path.sep):
                self.env['banners'].append(e)
            elif fname == 'homepage.rst':
                self.env['homepage_entry'] = e
            elif fname == 'callout.rst':
                self.env['callout'] = e
            elif 'hero-list' in e.filename.split(os.path.sep):
                self.env['hero_list'].append(e)

        return Index.generate(self, request)
