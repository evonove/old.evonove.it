---
title: Django admin e permessi
date: 08.02.2011, 10:29
lang: it
identifier: django-admin-e-permessi
slug: django-admin-e-permessi
author: masci
tags: [python,django]
intro.maxparagraphs: 1
---

.. raw:: html

    <p>Capita che a volte framework come <strong>Django</strong> e tool come il suo '<em>admin site'</em>, ci vengano in mente come scelte per sviluppare velocemente dei CRUD. Tuttavia ci accorgiamo altrettanto velocemente che questo potente strumento propone delle soluzioni che non sempre si sposano con la nostra logica di business. E' questo il caso dei permessi. L'amministrazione di Django non ha il permesso '<em>view</em>', o meglio: se un oggetto di buisiness &egrave; visibile da un utente dell'admin site, questo ha anche la possbilit&agrave; di modificarlo.&nbsp;Nelle seguenti verr&agrave; introdotta una possibile soluzione per creare e utilizzare il permesso <em>view</em> all'interno dell'amministrazione di Django, semplificando cos&igrave; la gestione di tutti quegli oggetti su cui la sicurezza del nostro CRUD identifica un gruppo di utenze con il solo diritto di lettura.</p>
    <p>La soluzione suggerita ruota intorno alla classe Django che ha nome di <strong>Backend.</strong> Questa, nelle ultime versioni di Django (v. 1.2), ha subito delle modifiche, dando allo sviluppatore la possibilit&agrave; di subentrare, meno intrusivamente ma pi&ugrave; efficacemente, nel flusso della sicurezza del framework: tanto da poter manipolare i permessi e renderli applicabili esclusivamente a determinati oggetti. Per dettagliare al meglio quali classi create e quali template personalizzare, si rimanda al wiki aziendale <strong><a title="wiki.evonove.it" href="http://wiki.evonove.it">wiki.evonove.it</a></strong> nella sessione Django sotto la voce&nbsp;<a title="CustomizeAdminSite" href="http://wiki.evonove.it/Django/CustomizeAdminSite">CustomizeAdminSite</a>&nbsp;.</p>
    <p>Buona lettura, e se voleste perfezionare o sconvolgere o commentare l'algoritmo proposto siete i ben venuti; sicuro non vi mancano gli strumenti&nbsp;per farlo&nbsp;(wiki, blog, email, ...) .</p>
