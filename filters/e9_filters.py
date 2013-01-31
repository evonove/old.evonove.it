# -*- encoding: utf-8 -*-
from acrylamid import log
from acrylamid.filters import Filter
from acrylamid.helpers import system as defaultsystem
from acrylamid.errors import AcrylamidException

from jinja2 import Environment, TemplateError


class E9Jinja2(Filter):
    """Jinja2 filter that pre-processes in Markdown/reStructuredText
    written posts. XXX: and offers some jinja2 extensions."""

    match = ['e9jinja2', 'E9Jinja2']
    version = '1.0.0'

    priority = 91.0

    def init(self, conf, env, *args):

        def system(cmd, stdin=None):
            try:
                return defaultsystem(cmd, stdin, shell=True).strip()
            except (OSError, AcrylamidException) as e:
                log.warn('%s: %s' % (e.__class__.__name__, e.args[0]))
                return e.args[0]

        def strip_default_lang(url):
            """Strip the part of the url containing language code.

            NOTICE: this approach is very silly since it does not check against the
            real path of the view - e.g. a legit path like /path/to/it/:lang:/
            would return a wrong result for 'it' language code

            """
            toks = url.split('/')
            if conf.lang in toks:
                toks.remove(conf.lang)
            url = '/'.join(toks)
            return url

        self.conf = conf
        self.env = env

        # jinja2 is stupid and can't import any module
        import time, datetime, urllib

        self.jinja2_env = Environment(cache_size=0)
        self.jinja2_env.filters['system'] = system
        self.jinja2_env.filters['split'] = unicode.split
        self.jinja2_env.filters.update({
            'time': time, 'datetime': datetime, 'urllib': urllib,
            })
        self.jinja2_env.filters['strip_default_lang'] = strip_default_lang

        for module in (time, datetime, urllib):
            for name in dir(module):
                if name.startswith('_'):
                    continue

                self.jinja2_env.filters[module.__name__ + '.' + name] = getattr(module, name)

    def transform(self, content, entry):
        try:
            tt = self.jinja2_env.from_string(content)
            return tt.render(conf=self.conf, env=self.env, entry=entry)
        except (TemplateError, AcrylamidException) as e:
            log.warn('%s: %s in %r' % (e.__class__.__name__, e.args[0], entry.filename))
            return content