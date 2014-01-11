# -*- coding: utf-8 -*-
import os
import locale
from datetime import datetime
from collections import defaultdict
from os.path import isfile, exists, getmtime
from hashlib import md5

from acrylamid import AcrylamidException
from acrylamid.views.entry import View
from acrylamid.views.sitemap import Map, Sitemap
from acrylamid.helpers import union, joinurl, event, paginate, expand, link, rchop
from acrylamid.utils import Struct, HashableList, hash as acr_hash
from acrylamid.refs import modified, references
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
    if entry.props.lang == lang:
        return entry

    for t in request['translations']:
        if t.props.identifier == entry.props.identifier and t.props.lang == lang:
            return t
    raise TranslationNotFound()


def date_format(date, lang):
    """Format dates according to the passed language

    """
    locales = {
        'it': ['it_IT', 'it_IT.utf8'],
        'en': ['en_US', 'en_US.utf8']
    }
    for loc in locales.get(lang, ['']):
        try:
            locale.setlocale(locale.LC_TIME, loc)
        except:
            locale.setlocale(locale.LC_TIME, '')
            
    return date.strftime('%d %b %Y')


def strip_default_lang(url, conf):
    """Strip the part of the url containing default language code. In this
    way, default lang will not have postfix in urls (e.g. blog/ instead of
    /blog/it/)

    NOTICE: this approach is very silly since it does not check against the
    real path of the view - e.g. a legit path like /path/to/it/:lang:/
    would return a wrong result for 'it' language code

    """
    toks = url.split('/')
    if conf.lang_code in toks:
        toks.remove(conf.lang_code)

    if len(toks) == 1:
        toks.append('')
    url = '/'.join(toks)
    return url


def strip_langs(url, lang):
    """Strip the part of the url containing any language code

    """
    toks = url.split('/')
    if lang in toks:
        toks.remove(lang)

    url = '/'.join(toks)
    return url


def intro(content, maxparagraphs=1):
    from acrylamid.filters.intro import Introducer
    try:
        return ''.join(Introducer(content, maxparagraphs).result)
    except:
        return content


def get_current_commit():
    import git
    repo = git.Repo(os.path.curdir)
    return repo.commit().hexsha


class E9Base(View):
    """Base class for views in this site.

    The view collects common data needed to *every* site page and push it in
    the global context (e.g. menubar, footer, etc...)

    """
    def init(self, conf, env, template='main.html'):
        if not 'langs' in env:
            env['langs'] = HashableSet()
        env['lang'] = conf.lang_code
        env['commit'] = get_current_commit()
        self.conf = conf
        self.template = template
        env.engine.jinja2.filters['date_format'] = date_format
        env.engine.jinja2.filters['strip_default_lang'] = strip_default_lang
        env.engine.jinja2.filters['strip_langs'] = strip_langs
        env.engine.jinja2.filters['intro'] = intro

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
                if entry.props.lang != self.conf.lang_code:
                    # remove from original entrylist
                    request[key].remove(entry)
                    request['translations'].append(entry)

        global_entries = ('footer_about', 'footer_navmenu', 'license')

        env.banners = Struct({l: HashableList() for l in env.langs})
        env.activities = Struct({l: HashableList() for l in env.langs})
        env.expertise = Struct({l: Struct() for l in env.langs})

        for e in request['entrylist']+request['pages']+request['translations']+request['drafts']:
            if e.props.identifier in global_entries:
                env.setdefault(e.props.identifier, Struct())[e.props.lang] = e
            elif 'banners' in e.filename.split(os.path.sep):
                env['banners'][e.props.lang].append(e)
            elif 'activities' in e.filename.split(os.path.sep):
                env['activities'][e.props.lang].append(e)
            elif 'expertise' in e.filename.split(os.path.sep):
                env['expertise'][e.props.lang][e.frontpage] = e

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
                elif lang == self.conf.lang_code:
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

    def context(self, conf, env, request):
        GRAVATAR_404 = conf['gravatar_404']
        GRAVATAR_SIZE = conf['gravatar_size']
        GRAVATAR_SIZE_BIG = conf['gravatar_size_big']

        env = E9Base.context(self, conf, env, request)

        env['staff'] = Struct()
        for draft in request['pages'] + request['translations']:
            if 'staff' in draft.filename.split(os.path.sep):
                digest = md5(draft.props['email']).hexdigest()
                draft.props['gravatar'] = 'https://www.gravatar.com/avatar/%s?s=%s&d=%s' % (digest, GRAVATAR_SIZE, GRAVATAR_404)
                draft.props['gravatar_big'] = 'https://www.gravatar.com/avatar/%s?s=%s&d=%s' % (digest, GRAVATAR_SIZE_BIG, GRAVATAR_404)
                if not draft.props.identifier in env.staff:
                    env.staff[draft.props.identifier] = Struct()
                env.staff[draft.props.identifier][draft.props.lang] = draft

        return env

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
                    pass#entrylist.append(entry)

            paginator = paginate(entrylist, ipp, self.path, conf.default_orphans)
            route = '/blog/'

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
                elif lang == self.conf.lang_code:
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
        hero_list = HashableList()
        for entry in request['pages'] + request['drafts']:
            if entry.context.condition and not entry.context.condition(entry):
                continue

            try:
                e = entry_for_lang(request, lang, entry)
            except TranslationNotFound:
                e = entry

            ident = e.props.identifier
            if ident == 'homepage':
                pages.append(e)
            elif ident == 'callout':
                request['env']['callout'] = e
            elif 'hero-list' in e.filename.split(os.path.sep):
                hero_list.append(e)

        for entry in request['entrylist']:
            try:
                latest_from_blog.append(entry_for_lang(request, lang, entry))
            except TranslationNotFound:
                pass

        request['env']['hero_list'] = hero_list
        request['env']['latest'] = HashableList(latest_from_blog[:4])
        return pages


class StaffPage(PageBase):
    """Renders the page type "Staff"

    Load contents from staff folder, we expect all valid contents are of
    page type

    """
    def _get_page_list(self, request, lang):
        pages = HashableList()
        for entry in request['pages']:
            if not 'staff' in entry.filename.split(os.path.sep):
                continue
            if entry.context.condition and not entry.context.condition(entry):
                continue
            try:
                pages.append(entry_for_lang(request, lang, entry))
            except TranslationNotFound:
                pages.append(entry)

        request['env']['stafflist'] = pages
        return pages


class StaffIndex(PageBase):
    """

    """
    def _get_page_list(self, request, lang):
        staff_page = HashableList()
        for entry in request['pages']:
            if entry.identifier == 'staff':
                try:
                    e = entry_for_lang(request, lang, entry)
                except TranslationNotFound:
                    e = entry
                staff_page.append(e)
                break

        return staff_page


class E9SiteMap(Sitemap):
    def generate(self, conf, env, data):
        """In this step, we filter drafted entries (they should not be included into the
        Sitemap) and write the pre-defined priorities to the map."""

        path = joinurl(conf['output_dir'], self.path)
        sm = Map()

        if exists(path) and not self.modified:
            event.skip('sitemap', path)
            raise StopIteration

        for ns, fname in self.files:

            if ns == 'draft':
                continue

            url = conf['www_root'] + '/' + fname.replace(conf['output_dir'], '')
            url = strip_default_lang(url, conf)
            priority, changefreq = self.scores.get(ns, (0.5, 'weekly'))
            sm.add(rchop(url, 'index.html'), getmtime(fname), changefreq, priority)

        sm.finish()
        yield sm, path

