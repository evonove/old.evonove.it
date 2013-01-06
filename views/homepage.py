# -*- coding: utf-8 -*-
from acrylamid.views.index import Index
import os

class Homepage(Index):
    def __init__(self, *args, **kw):
        Index.__init__(self, *args, **kw)

    def generate(self, request):

        content_dir = os.path.abspath(self.conf['content_dir'])
        banners=[]
        for e in request['entrylist']:
            if 'banners/' in e.filename:
                banners.append(e)
        self.env['banners'] = banners

        return Index.generate(self, request)
