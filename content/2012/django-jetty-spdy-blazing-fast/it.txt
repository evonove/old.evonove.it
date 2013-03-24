---
lang: it
title: Django + Jetty + SPDY = blazing fast!
date: 28.12.2012, 17:04
identifier: django-jetty-spdy-blazing-fast
slug: django-jetty-spdy-blazing-fast
author: palazzem
tags: [python]
image: /img/2012/chromium.png
intro.maxparagraphs: 3
---

Nel novembre del 2009 fu redatto il primo draft di un nuovo protocollo di
networking aperto chiamato SPDY il cui obiettivo primario era quello di ridurre
la latenza di caricamento delle pagine web. Il raggiungimento delle specifiche
tecniche stabilite doveva rispettare alcuni requisiti fondamentali: minimizzare
la complessità di distribuzione del protocollo; evitare cambiamenti da parte
degli sviluppatori delle pagine web affinché le modifiche dovessero essere fatte
solo al client web ed al web server.

Chi supporta SPDY?
------------------

Durante l’evoluzione del protocollo, che attualmente è stato preso come base
per la redazione del primo draft dell’HTTP 2.0 ad opera del gruppo di lavoro
IETF HTTP-bis, molti dei più noti web server si sono adattati in via
sperimentale a questa nuova implementazione. Per citarne alcuni parliamo di
Jetty, Apache (tramite mod_spdy), node.js e nginx.

Perché Python non può sfruttare SPDY?
-------------------------------------

Per quanto riguarda il linguaggio Python ed il suo uso per sviluppare
applicazioni web, la specifica PEP-333 stabilì l’utilizzo di WSGI come
interfaccia standard tra il lato web server ed il lato applicazione / framework.
WSGI non supporta attualmente SPDY pertanto il protocollo non può essere
utilizzato nativamente con framework web quali Django.

Django e Jython: prepararsi per Jetty
--------------------------------------

In attesa di un’evoluzione dell’attuale implementazione di WSGI è possibile
integrare alcune tecnologie in modo da distribuire un’applicazione Django
all’interno del web container Jetty. L’utilità di questo approccio è quello di
sfruttare il supporto di Jetty a SPDY ed alla sua funzione push. Per raggiungere
l’obiettivo è necessario utilizzare Jython ovvero un’implementazione del
linguaggio Python scritto in Java. Di seguito si elencano i passaggi da seguire
per configurare un’istanza Django all’interno di Jetty con abilitata la funzione
SPDY push.

Scaricare ed installare la versione stable di Jython (attualmente 2.5.3).
Nonostante sia possibile creare e sviluppare l’applicazione Django direttamente
in un virtualenv Python, durante la fase di deploy sarà necessario creare un
nuovo virtualenv con Jython come interprete.

Uno dei problemi da risolvere per eseguire Django su Jython è il suo ORM in
quanto i backends che si collegano al database dipendono da librerie scritte
in C. Per ovviare a questo è necessario installare l’estensione django-jython in
modo da poter usufruire di una serie di tool e di tutti i backends zxJDBC per i
database principali. Purtroppo l’attuale versione rilasciata (1.3.0) non ha un
corretto supporto per Django 1.4. Tuttavia è possibile utilizzare l’ultima
versione disponibile nel repository ufficiale
(attualmente è il changeset e2c6ff29cd01) che include una serie di fix per il
corretto funzionamento.

Dopo aver installato l’estensione è necessario abilitarla tra i database
backends e le INSTALLED_APPS di Django:

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

Questo abiliterà la possibilità di poter generare direttamente il package war
con al suo interno Jython, Django, il driver JDBC scelto (bisogna specificare
l’inclusione) e l’applicazione sviluppata.

Deploy di Django su Jetty
-------------------------

La versione di Jetty utilizzata è la versione 8.1.8.v20121106 stable.
Senza nessuna configurazione aggiuntiva è possibile fare il deploy del package
war per poi richiedere a Jetty di servire l’applicazione.

Django, Jetty e SPDY
--------------------

Per servire una pagina con il protocollo SPDY è necessario aggiungere spdy tra
le OPTIONS nel file start.ini. A quel punto aggiungere jetty-spdy.xml tra i file
di configurazione da utilizzare. Come da specifica, qualora venga utilizzato
SPDY su HTTPS (TLS), è richiesta l’attivazione dell’estensione TLS Next
Protocol Negotiation (NPN). La JVM che eseguirà Jetty dovrà essere avviata
utilizzando l’opzione non standard:

.. sourcecode:: terminal

    java -Xbootclasspath/p:<path_to_npn_boot_jar>

La versione utilizzata della libreria è la npn-boot-8.1.2.v20120308.jar.
A questo punto sarà possibile farsi servire la pagina con il protocollo SPDY.

Django, Jetty, SPDY e poi PUSH!
-------------------------------

Sfruttando l’implementazione SPDY di Jetty è possibile usufruire della
modalità server push così da ridurre notevolmente il numero di richieste fatte
dal client per il recupero delle risorse. Per attivare in modo trasparente
questa funzionalità è opportuno abilitare una pushStrategy nel file di
configurazione di Jetty. Per migliorare il comportamento della push strategy,
è possibile configurare due variabili nel file di configurazione:

.. sourcecode:: xml

    <Set name="referrerPushPeriod">15000</Set>

definisce il tempo scaduto il quale Jetty smetterà di caricare in modalità push
risorse associate alla risorsa principale richiesta;

.. sourcecode:: xml

    <Set name="maxAssociatedResources">32</Set>

definisce il numero massimo di risorse da associare alla risorsa principale.
Oltre questo numero le risorse saranno inviate secondo il protocollo SPDY senza push.
Abilitata questa configurazione Django sarà servito in modalità SPDY-PUSH.

Tirando le somme
----------------

Nonostante la vista sia stata costruita proprio per mettere in risalto le
potenzialità di SPDY, di seguito elenchiamo i tempi di caricamento medi della
pagina Django servita da Jetty:

- HTTP (1.1): **7,63 secondi**
- SPDY/3: **1,71 secondi**
- SPDY/3 (with push): **1,55 secondi**

I valori raccolti interessano dei test preliminari eseguiti in locale con un
roundtrip delay di 200ms e non sono dei benchmark su dei casi d'uso
reale.

Codice sorgente
---------------

Progetto, package war e configurazione Jetty: https://bitbucket.org/evonove/django-spdy/

Riferimenti

- http://webtide.intalio.com/
- http://wiki.eclipse.org/Jetty
- http://chromium.org/spdy
- http://djangoproject.org
- http://packages.python.org/django-jython/
- http://code.google.com/p/mod-spdy/
