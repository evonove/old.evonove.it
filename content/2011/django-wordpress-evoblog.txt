---
title: Django + Wordpress = EvoBlog
date: 14.10.2011, 20:25
lang: it
identifier: django-wordpress-evoblog
slug: django-wordpress-evoblog
author: masci
tags: [django,python,wordpress,software]
intro.maxparagraphs: 1
image: /img/2011/wordpress_logo.png
---
Ho appena terminato lo switch dell'engine che sta dietro al nostro blog:
da django-blog-zinnia siamo passati a Wordpress, prodotto che nell'ultimo anno
abbiamo avuto modo di vedere in dettaglio durante lo sviluppo di integrazioni
per alcuni clienti.

Zinnia è un ottimo prodotto e sicuramente la migliore app Django che sono
riuscito a trovare che implementi un blog, prendete ad esempio il codice che
serve ad utilizzare `Shorty <http://evo9.it>`_ come shortener per gli articoli
(a meno del caching che vi risparmio):

.. sourcecode:: python

    def backend(entry):
        url = '%s%s' % (Site.objects.get_current().domain,
                            urllib2.quote(entry.get_absolute_url()))
        try:
            f = urllib2.urlopen("http://www.evo9.it/api/short/%s" % url,
                data='')
        except Exception as e:
            return ''
        return json.loads(f.read())

E' stato altrettanto semplice integrare i contenuti del blog nella homepage del
sito, realizzata con un'applicazione Django custom.  Tutto questo però non
riesce a bilanciare le difficoltà di gestione (ad esempio) delle immagini, degli
aggiornamenti, dei contenuti evoluti che a volte vorremmo mettere negli articoli
(codice sorgente formattato). Le motivazioni dello switch sono quindi da
ricercarsi esclusivamente nella facilità con cui Wordpress ci permette di
inserire e modificare gli articoli ed il suo altissimo livello di
SEO-friendlyness.

L'integrazione con Django è stata realizzata utilizzando i feed RSS messi a
disposizione da Wordpress, che in questo contesto eccelle. Si tratta di
aggiungere qualcosa del genere alle viste esistenti:

.. sourcecode:: python

    rss_url = 'http://www.evonove.it/blog/%s/category/front-page/feed/'
        % context['lang']
    feed = feedparser.parse(rss_url)

I feed vengono recuperati e parsati dalla libreria feedparser: ho barattato
una serie di query al database di backend con una HTTP/GET fatta in localhost,
non ho ancora fatto i benchmark ma ad occhio non mi pare di aver perso nulla in
termini di velocità di elaborazione della pagina.
