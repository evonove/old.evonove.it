---
title: Progetto Kimol - Diario di Bordo - 1
date: 09.10.2011, 10:29
lang: it
identifier: progetto-kimol-diario-di-bordo-1
slug: progetto-kimol-diario-di-bordo-1
author: masci
tags: [asus,fedora,freenect,kinect,microsoft,opencv,python,xtion]
intro.maxparagraphs: 1
---

Si è conclusa la prima settimana di lavoro su KiMol, il progetto sviluppato da
uno studente dell'Università degli Studi di Perugia nell'ambito di un
<a href="/it/workshop/">tirocinio esterno</a> presso Evonove.

Riassumo brevemente per chi non abbia letto la
`pagina del progetto nel wiki <http://wiki.evonove.it/Concepts/KiMol>`_: si
tratta dello sviluppo di un'interfaccia utente gesture based per
`PyMol <http://www.pymol.org/>`_, un noto visualizzatore open source di
strutture molecolari.

.. image:: /img/2011/foto-1.jpg
    :alt: Kinect e Xtion sulla scrivania
    :align: center
    :class: bordered-img

Abbiamo approfittato del recente ingresso in commercio della periferica
`Xtion <http://www.asus.com/Multimedia/Motion_Sensor/Xtion_PRO/>`_ da parte di
Asus per affiancarla al Kinect di Microsoft come dispositivo di acquisizione
(nella foto); l'idea è poter utilizzare indifferentemente l'una o l'altra
periferica anche se al momento lo sviluppo è guidato dal Kinect.

Chi ha avuto esperienza con l'hacking del Kinect saprà che sono diverse le
soluzioni a disposizione degli sviluppatori per interfacciarsi al dispositivo,
recuperarne i dati ed elaborarli in modo da realizzare funzionalità di gesture
tracking. Per il momento noi ci siamo affidati al progetto
`OpenKinect <http://openkinect.org/wiki/Main_Page>`_ per la parte acquisizione
e ad `OpenCV <http://opencv.willowgarage.com/wiki/Welcome>`_ per quella di
elaborazione; i risultati sono incoraggianti e gran parte del merito va ai
bindings Python per la libreria freenect che ci permettono una prototipazione
rapida molto utile soprattutto in questa fase esplorativa delle potenzialità
della periferica.

Mettere in piedi tutta la toolchain è stato abbastanza semplice e facilmente
replicabile grazie alla configurazione di freenect, molto ben organizzata
attraverso `CMake <http://www.cmake.org/>`_ ed alla semplicità con cui reperire
le dipendenze sulla distribuzione Fedora 15 con la quale è equipaggiata la
macchina di riferimento per lo sviluppo del progetto.

Il prossimo step consiste nel comprendere al meglio i dati che vengono forniti
dal Kinect attraverso freenect e sondare le potenzialità di OpenCV rispetto al
progetto finale.
