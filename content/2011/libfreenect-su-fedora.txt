---
title: libFreenect su Fedora
date: 29.12.2011, 20:58
lang: it
identifier: libfreenect-su-fedora
slug: libfreenect-su-fedora
author: masci
tags: [python,fedora,linux,kinect]
intro.maxparagraphs: 1
image: /img/2011/openkinect_shaded.png
---

OpenKinect è una community di appassionati dediti in particolare all'utilizzo di
Microsoft Kinect in ambiente desktop attraverso strumenti open source.
In particolare OpenKinect è responsabile dello sviluppo della libreria Freenect
grazie alla quale è possibile accedere a molti dei dati che arrivano dal Kinect
quando connesso ad un PC attraverso una porta USB. Freenect è una libreria
multipiattaforma (Mac, Linux, Win) dotata di bindings Python; sebbene OpenKinect
non ne fornisca pacchetti o distribuzioni binarie, compilare ed installare la
libreria è abbastanza semplice, soprattutto in una distribuzione Fedora 15 con
l'aiuto di Yum.

Prerequisiti
------------

Prima di procedere con la build della libreria abbiamo bisogno di installare
alcuni strumenti e dipendenze, cosa che facciamo con yum:

.. sourcecode:: terminal

    yum install git cmake gcc gcc-c++ libXi libXi-devel libXmu libXmu-devel freeglut freeglut-devel libusb1-devel Cython

Fatto.

libFreenect
-----------

Possiamo recuperare facilmente una versione aggiornata dei sorgenti della
libreria da GitHub:

.. sourcecode:: terminal

    git clone git://github.com/OpenKinect/libfreenect.git

Creiamo poi una directory che conterrà i files della build senza "sporcare" la
directory dei sorgenti, ci spostiamo al suo interno e da lì invochiamo cmake:

.. sourcecode:: terminal

    mkdir libfreenect_build && cd libfreenect_build/
    ccmake ../libfreenect

Dall'interfaccia di CMake è importante abilitare il flag per la build dei
bindings Python:

.. sourcecode:: terminal

    BUILD_PYTHON: ON

A questo punto non resta che procedere con l'invocazione di make per la build e
l'installazione (quest'ultima dovrà essere effettuata con i privilegi di root
nel caso non abbiate impostato la variabile INSTALL_PREFIX con un path su cui
avete i permessi di scrittura).

.. sourcecode:: terminal

    make && make install

Finito. Se la build è stata completata con successo potete verificare la
corretta installazione direttamente con l'interprete Python. Se dalla shell il
comando:

.. sourcecode:: terminal

    python -c "import freenect"

finisce senza produrre errori, libFreenect è correttamente installata nel
vostro sistema.
