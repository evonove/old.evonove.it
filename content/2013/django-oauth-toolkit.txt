---
lang: en
title: Django OAuth Toolkit is out!
date: 13.06.2013, 08:19
identifier: django-oauth-toolkit-is-out
slug: django-oauth-toolkit-is-out
author: masci
tags: [python,django]
image: /img/2013/oauthLogo.png
intro.maxparagraphs: 2
---

We just released the `latest version <https://pypi.python.org/pypi/django-oauth-toolkit/0.3.0>`_ of Django OAuth Toolkit,
a library to add OAuth goodies to Django projects. The project is under active development, at the moment it offers
fully-featured and RFC6749 compliant OAuth2 providers implementation and it runs on Django 1.4, 1.5 and 1.6a1 with
Python 2.7 and 3.3.

A brief history
===============

Everything started when we found ourselves in the need to implement an OAuth2 provider for a Django web service.
We happily use Django REST framework wherever we have to expose an API, and that was right the case. Django REST framework
has built-in support for a third party Django app implementing OAuth providers but we shortly faced some issues and
started to search for an alternative.

Digging around we stumbled upon this blog post from Daniel Greenfeld:
`The sorry state of Python OAuth providers <http://pydanny.com/the-sorry-state-of-python-oauth-providers.html>`_. Enough
is enough but we were still not sure whether starting another project from scratch or not, when we met Daniel at the Django
Circus in Warsaw. We talked shortly about the topic but he was very convincing and we started coding as soon as we came
back at work.

Why?
====

We're trying to involve other people in the project and usually this is the first question we're asked: why another
project? Instead of complaining about other projects, we usually list what we got so far and possibly other don't have:
features and goodies we strongly needed and now actually have.

DRY
---

We think `oauthlib <https://github.com/idan/oauthlib>`_ is currently the state of the art OAuth library in the Python
world. We choose to rely on a well documented, well supported and active project instead of write one on our own, with
all the FUD of the case.

Documentation
-------------

OAuth protocol can be quite mind boggling every here and there. We think writing good docs is mandatory when the code
may be quite simple but the workflow heavily complicated. We are also putting a lot of efforts on writing tutorials, as
one line of code worths thousand words (expecially with OAuth workflows :-).

Testing
-------

I'm not referring to Unit testing here (still we do our best to keep coverage over 95% ;-) but to some stuff users
can actually use to test their applications on a real OAuth2 workflow. In some circumstances, OAuth2 applications need
a companion to exchange tokens, provide authorizations and so on. We deployed an OAuth2 playground on Heroku to let
users perform a roundtrip between their local apps and a real server (or client, depending on the case).

Timezone aware
--------------

We strongly believe that if your dates and times are not timezone aware, they're broken. That said.

Python 3
--------

On the neverending effort of porting our codebase to Python 3, we cannot rely anymore on libraries and tools which do
not have at least any roadmap for the porting. Django OAuth Toolkit is alredy working with both Python 2.7 and 3.3.

Support
-------

We're working hard on the project also because we're using it internally in our company, so we can guarantee our full
support on the middle term and hopefully longer, depending on the success it could be have in the Django world.

We want you!
============

As any other Open Source project, we're nothing without a community: any help is appreciated, code of course but also
docs, testing and any kind of feedback. `Fork the project <https://github.com/evonove/django-oauth-toolkit>`_,
take a ride, fill some PRs!