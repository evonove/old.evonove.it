# -*- coding: utf-8 -*-
from collections import defaultdict
from acrylamid import AcrylamidException
from acrylamid.views.entry import View
from acrylamid.helpers import union, joinurl, event, paginate, expand, link
from acrylamid.utils import Struct, HashableList, hash as acr_hash
from acrylamid.refs import modified, references
import os
import locale
from os.path import isfile
from datetime import datetime
from acrylamid import refs


class TranslationNotFound(Exception):
    pass


class HashableSet(set):
    """Useful to remove duplicates"""
    def __hash__(self):
        return acr_hash(*self)


def entry_for_lang(request, lang, entry):
    """Returns an entry translated in the language passed, otherwise raises an
    exception

    """
    for t in request['translations']:
        if t.props.identifier == entry.props.identifier and t.props.lang == lang:
            return t
    raise TranslationNotFound()


def date_format(date, lang):
    """Format dates according to the passed language

    """
    locales = {'it':'it_IT', 'en':'en_US'}
    locale.setlocale(locale.LC_TIME, locales.get(lang, 'en_US'))
    return date.strftime('%d %b %Y')


def strip_default_lang(url,conf):
    """Strip the part of the url containing default language code. In this
    way, default lang will not have postfix in urls (e.g. blog/ instead of
    /blog/it/)

    NOTICE: this approach is very silly since it does not check against the
    real path of the view - e.g. a legit path like /path/to/it/:lang:/
    would return a wrong result for 'it' language code

    """
    toks = url.split('/')
    if conf.lang in toks:
        toks.remove(conf.lang)
    url = '/'.join(toks)
    return url


class E9Base(View):
    """Base class for views in this site.

    The view collects common data needed to *every* site page and push it in
    the global context (e.g. menubar, footer, etc...)

    """
    def init(self, conf, env, template='main.html'):
        if not 'langs' in env:
            env['langs'] = HashableSet()
        self.conf = conf
        self.template = template
        env.engine.jinja2.filters['date_format'] = date_format
        env.engine.jinja2.filters['strip_default_lang'] = strip_default_lang

    def context(self, conf, env, request):
        """This method fills up translations variable in the request (like
        Translation class in Acrylamid), creates a languages list based on the
        request contents and fill the context with common data needed by every
        page

        """
        if len(request['translations']):
            return env

        tags = HashableSet()
        translations = defaultdict(list)
        for key in ('pages', 'entrylist', 'drafts'):
            for entry in request[key][:]:
                if entry.hasproperty('tags'):
                    for t in entry.props.tags:
                        tags.add(t)

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

        _globals = {
            'footer_about': Struct(),
            'footer_navmenu': Struct(),
            'license': Struct(),
        }

        for e in request['entrylist']+request['pages']+request['translations']+request['drafts']:
            try:
                _globals[e.props.identifier][e.props.lang] = e
            except (KeyError, AttributeError):
                continue

        # inject globals into the env
        for k,v in _globals.iteritems():
            env[k] = v

        # other global futilities...
        env.current_year = datetime.now().year
        env.tags = tags

        self.env = env

        return env

    def generate(self, conf, env, data):
        for lang in env.langs:
            entrylist = []
            for entry in data[self.type]:
                try:
                    e = entry_for_lang(data, lang, entry)
                    entrylist.append(e)
                except TranslationNotFound:
                    entrylist.append(entry)

            unmodified = not env.modified and not conf.modified

            for i, entry in enumerate(entrylist):
                route = strip_default_lang(expand(self.path, entry), self.conf)
                if entry.hasproperty('permalink'):
                    path = joinurl(conf['output_dir'], entry.permalink)
                elif lang == self.conf.lang:
                    path = joinurl(self.conf['output_dir'], route, '/')
                    entry.permalink = route
                else:
                    path = joinurl(self.conf['output_dir'],
                                   expand(self.path, entry))
                    entry.permalink = route

                if path.endswith('/'):
                    path = joinurl(path, 'index.html')

                next, prev = self.next(entrylist, i), self.prev(entrylist, i)
                env['lang'] = lang
                env['active_route'] = route

                # per-entry template
                tt = env.engine.fromfile(entry.props.get('layout', self.template))

                if all([isfile(path), unmodified, not tt.modified, not entry.modified,
                        not modified(*references(entry))]):
                    event.skip(self.name, path)
                    continue

                html = tt.render(conf=conf, entry=entry, env=union(env,
                                                                   entrylist=[entry],
                                                                   type=self.__class__.__name__.lower(),
                                                                   prev=prev, next=next,
                                                                   route=expand(
                                                                       self.path,
                                                                       entry)))

                yield html, path


class E9Entry(E9Base):
    """A view to generate single blog posts

    """
    @property
    def type(self):
        return 'entrylist'

    def next(self, entrylist, i):

        if i == 0:
            return None

        refs.append(entrylist[i], entrylist[i - 1])
        return link(entrylist[i-1].title, entrylist[i-1].permalink)

    def prev(self, entrylist, i):

        if i == len(entrylist) - 1:
            return None

        refs.append(entrylist[i], entrylist[i + 1])
        return link(entrylist[i+1].title, entrylist[i+1].permalink)


class E9Index(E9Base):
    """This view generated the blog index page, with pagination

    """
    @property
    def type(self):
        return None

    def init(self, conf, env, template='main.html', items_per_page=5, pagination='/page/:num/'):
        self.items_per_page = items_per_page
        self.pagination = pagination
        self.filters.append('relative')
        E9Base.init(self, conf, env, template)

    def generate(self, conf, env, data):
        for lang in env.langs:
            ipp = self.items_per_page
            tt = env.engine.fromfile(self.template)

            entrylist = []
            for entry in data['entrylist']:
                try:
                    e = entry_for_lang(data, lang, entry)
                    entrylist.append(e)
                except TranslationNotFound:
                    entrylist.append(entry)

            paginator = paginate(entrylist, ipp, self.path, conf.default_orphans)
            route = self.path

            for (next, curr, prev), entries, modified in paginator:
                # curr = current page, next = newer pages, prev = older pages

                if next is None:
                    pass
                elif next == 1:
                    next = link(u'« Next', expand(self.path.rstrip('/'), {'lang':lang}))
                else:
                    next = link(u'« Next', expand(self.pagination, {'num': next,'lang': lang}))

                if next:
                    next.href = strip_default_lang(next.href, self.conf)

                curr = link(curr, self.path) if curr == 1 \
                    else link(expand(self.pagination, {'num': curr,'lang': lang}))
                curr.href = strip_default_lang(curr.href, self.conf)

                prev = None if prev is None \
                   else link(u'Previous »', expand(self.pagination, {'num': prev,'lang': lang}))
                if prev:
                    prev.href = strip_default_lang(prev.href, self.conf)

                path = joinurl(conf['output_dir'], expand(curr.href, {'lang': lang}), 'index.html')
                path = strip_default_lang(path, self.conf)
                env['lang'] = lang
                env['active_route'] = route

                if isfile(path) and not (modified or tt.modified or env.modified or conf.modified):
                    event.skip(path)
                    continue

                html = tt.render(conf=conf, env=union(env, entrylist=entries,
                                      type='index', prev=prev, curr=curr, next=next,
                                      items_per_page=ipp, num_entries=len(entrylist), route=route))
                yield html, path


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
        pages = HashableList()
        for entry in request['pages']:
            if entry.context.condition and not entry.context.condition(entry):
                continue
            try:
                p = entry_for_lang(request, lang, entry)
                if not p.hasproperty('permalink'):
                    p.permalink = strip_default_lang(expand(self.path, p), self.conf)
                pages.append(p)
            except TranslationNotFound:
                pages.append(entry)
        return pages

    def generate(self, conf, env, request):
        for lang in env.langs:
            for entry in self._get_page_list(request, lang):
                path = ''
                route = strip_default_lang(expand(self.path, entry), self.conf)

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
                request['env']['active_route'] = route

                tt = env.engine.fromfile(self.template)
                html = tt.render(conf=conf, entry=entry, env=union(env,
                    type=self.__class__.__name__.lower(), route=route))

                yield html, path


class ActivitiesPage(PageBase):
    """Renders the page type "Activity"

    Load contents from activities folder, we expect all valid contents are of
    page type

    """
    def _get_page_list(self, request, lang):
        pages = HashableList()
        for entry in request['pages']:
            if not 'activities' in entry.filename.split(os.path.sep):
                continue
            if entry.context.condition and not entry.context.condition(entry):
                continue
            try:
                pages.append(entry_for_lang(request, lang, entry))
            except TranslationNotFound:
                pages.append(entry)

        request['env']['activitylist'] = pages

        return pages


class ExpertisePage(PageBase):
    """Renders the page type "Expertise"

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

    def _get_page_list(self, request, lang):
        pages = []
        latest_from_blog = []
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

        for entry in request['entrylist']:
            try:
                latest_from_blog.append(entry_for_lang(request, lang, entry))
            except TranslationNotFound:
                latest_from_blog.append(entry)

        request['env']['entry_dict'] = entry_dict
        request['env']['latest'] = HashableList(latest_from_blog[:4])
        return pages
