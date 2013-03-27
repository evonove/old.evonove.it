---
lang: en
title: Django + Jetty + SPDY = blazing fast!!!
date: 28.12.2012, 17:04
identifier: django-jetty-spdy-blazing-fast
slug: django-jetty-spdy-blazing-fast
author: palazzem
tags: [python]
image: /img/2012/chromium.png
intro.maxparagraphs: 3
---

During November, 2009 a new open network protocol named SPDY was defined with a
first draft; the main goal of this new protocol was reducing the latency during
web pages loading. The achievement of the technical specifications must comply
with certain requirements: minimize deployment complexity; avoid the need of any
changes to content by website developers so that the only changes required to
support SPDY are in the client user agent or in the web server application.

Who supports SPDY
------------------

Recently IETF HTTP-bis working group has announced that the first draft of
HTTP 2.0 is based on SPDY protocol drafts. During the evolution of SPDY many of
most famous web servers implement, as experimental feature, this new protocol.
Just to name a few, we are talking about Jetty, Apache (via mod_spdy), node.js
and nginx.

Why Python web framework cannot support SPDY natively?
------------------------------------------------------

PEP-333 defines WSGI specification as a standard interface between the web
server side and the application / framework side for Python web development.
WSGI doesn’t support SPDY natively so the protocol cannot be used with Python
web frameworks like Django.

Django and Jython: prepare for Jetty
------------------------------------

While waiting for an evolution of the current WSGI implementation, it is still
possibile to set up some technologies in order to serve a Django application
with Jetty as web container in order to take advantage of Jetty SPDY and SPDY
push support. To achieve this goal it’s necessary to use Jython, a Java
implementation of Python language. Steps below define how to configure a Django
instance inside Jetty with SPDY push feature enabled.

Download and install the stable version of Jython (currently 2.5.3).
Even if it’s possible to create and develop the Django application using a
traditional Python virtualenv, you need to create a new virtualenv with Jython
interpreter during deployment phase.

The use of Django ORM is a common problem that need to be solved in order to
run Django inside Jython. This is caused by database backends that depend on
libraries written in C language.
To overcome this it’s necessary to install django-jython module so it is
possible to use some useful tool together with all zxJDBC backends.
Unfortunately the currently released version of module (1.3.0) doesn’t have a
working support for Django 1.4. However it’s possibile to use the latest
available version in the official repository
(actually use changeset e2c6ff29cd01) that include some bug fixes and a good
Django support.

To enable django-jython module it’s necessary to edit database backends and
Django INSTALLED_APPS:

.. sourcecode:: python

    DATABASES = {
        'default': {
        'ENGINE': 'doj.backends.zxjdbc.postgresql',
        [...]
        }
    }

    INSTALLED_APPS = (
        [...]
        'doj',
    )

This will enable some extra features like the capability to create a war package
directly from manage.py within Jython, the Django framework, the desired JDBC
driver (an include java lib parameter should be used) and the developed
application.

Deploy Django on Jetty
----------------------

Jetty version 8.1.8.v20121106 stable was used in this setup. Without any
further configuration it is possible to deploy the war package as usual to have
Django up and running.

Django, Jetty and SPDY
----------------------

To serve a web page with SPDY protocol it’s necessary to add ‘spdy’ in OPTIONS
parameter inside start.ini file. Then jetty-spdy.xml configuration file should
be used. As defined by SPDY protocol if SPDY over HTTPS (TLS) is used, the Next
Procol Negotiation (NPN) library is required. The JVM should be started with
non-standard option:

.. sourcecode:: terminal

    java -Xbootclasspath/p:<path_to_npn_boot_jar>

Version of library in use is npn-boot-8.1.2.v20120308.jar. At this point Jetty
can serve your application with SPDY support.

Django, Jetty, SPDY. Time to PUSH!
----------------------------------

Thanks to Jetty and its SPDY implementation it is possible to use server push
to reduce the number of client requests.
To enable transparent push feature a pushStrategy should be activated inside
Jetty configuration file. To improve the behaviour of a push strategy two
variables must be set:

.. sourcecode:: xml

    <Set name="referrerPushPeriod">15000</Set>

define a delay after which Jetty will stop to load in push mode associated
resources of a main request;

.. sourcecode:: xml

    <Set name="maxAssociatedResources">32</Set>

define the maximum associated resources of a main request that can be pushed.
Over this cap the remaining resources are sent using SPDY without push.
After this configuration Django will be served using SPDY-PUSH feature.

To sum up!
----------

Even if this view is optimized to emphasize SPDY potentiality, below we list
the average load time of this Django page served by Jetty:

- HTTP (1.1): **7,63 seconds**
- SPDY/3: **1,71 seconds**
- SPDY/3 (with push): **1,55 seconds**

Collected values refer to a preliminary test run locally with a 200ms round
trip delay and it isn't a benchmark of real use cases.

Source code
-----------

Project code, war package and Jetty configuration: https://bitbucket.org/evonove/django-spdy/

References

- http://webtide.intalio.com/
- http://wiki.eclipse.org/Jetty
- http://chromium.org/spdy
- http://djangoproject.org
- http://packages.python.org/django-jython/
- http://code.google.com/p/mod-spdy/
