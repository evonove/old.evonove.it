---
title: Navigation Menu
lang: it
date: 01-01-2013
slug: navmenu
draft: yes
identifier: navmenu
filters: E9Jinja2
---

.. raw:: html

    <ul class="nav nav-pills">

        <li class="active single">
            <a href="/">
                HOME<i>pagina principale</i>
            </a>
        </li>

        {% if env.entry_dict.activities %}
        <li class="dropdown">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#menu1">
                ATTIVITA'<i>cosa facciamo</i>
            </a>
            <ul class="dropdown-menu">
                {% for a in env.entry_dict.activities %}
                <li><a href="{{a.permalink|strip_default_lang}}">{{a.title}}</a></li>
                {% endfor %}
            </ul>
        </li>
        {% endif %}

        {% if env.entry_dict.expertise %}
        <li class="dropdown">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#menu1">
                SPECIALIZZAZIONI<i>cosa sappiamo fare</i>
            </a>
            <ul class="dropdown-menu">
                {% for e in env.entry_dict.expertise.values() %}
                <li><a href="{{e.permalink}}">{{e.title}}</a></li>
                {% endfor %}
            </ul>
        </li>
        {% endif %}

        <li class="single">
            <a class="single" href="#menu4">
                BLOG<i>evonove techies</i>
            </a>
        </li>

        <li class="single">
            <a href="contacts/">
                CONTATTI<i>get in touch</i>
            </a>
        </li>
    </ul>

