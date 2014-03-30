---
title: Build Python desktop application with Jenkins
date: 24.07.2013, 14:38
lang: en
identifier: build-python-desktop-application-with-jenkins
slug: build-python-desktop-application-with-jenkins
author: masci
tags: [python,Qt,Jenkins]
intro.maxparagraphs: 2
---

We recently started using `Jenkins <http://jenkins-ci.org/>`_, a well known system for Continuous Integration,
and make it perform tasks like build and package multiplatform desktop
applications.

We're currently in charge of developing a desktop application written in **Python** using the **Qt framework**.
Though small, the application is quite complex and has a lot of dependencies which is quite easy to satisfy on a local
environment (provided that you're not on Windows, but that's another story).

There are several proprietary **C/C++** libraries involved, and some of them are under active development, so we have to
stay up to date with them and with the relative Python bindings. At an early stage of the development the environment
was entirely hand crafted, so building and packaging the software with the right configuration was up to the single
developer who wrote the first draft of the project.

The prototype was ok, so we started a refactoring of the codebase and assigned other resources to the project. Problems
with the building environment arose almost instantly: not every developer works on the same configuration (and this is
a choice) and maintaining different build scripts was not acceptable.

We needed a build system and we needed it fast, so we started reviewing all of these:

 * Gnu Make
 * `Fabric <http://docs.fabfile.org/en/latest/>`_
 * `Paver <http://paver.github.io/paver/>`_
 * `buildout <http://www.buildout.org/en/latest/>`_
 * `CMake <http://www.cmake.org/>`_

CMake seems the most flexible of the above (at least for a newcomer) and it was the only one which let us collect the code
from several sources **(CVS repos, git repos, source tarballs)** build it with different build systems **(Make, QMake, distutils,
custom scripts)**, make the executable with PyInstaller and create the archive to distribute. First issue solved:
developers can now build the software with minimum effort and in a well defined and versioned environment

Now the real issue, beta tester started asking for packages for their own distributions/OSs - we needed a build
system capable to run our CMake script on several machines, produce the software package and make it available for download
somewhere on the internet.

Our requirements:

 * a turnkey solution
 * should be able to start and stop virtual machines inside our LAN
 * should be able to start and stop EC2 machines
 * can speak with cloud storaging systems (e.g. S3)

We briefly reviewed two products, Jenkins and `CDash <http://www.cdash.org/>`_, and we ended up with **Jenkins**
basically for two reasons:

 * documentation
 * huge amount of very useful plugins
 * easy installation and maintaining

At the moment we have a master/slave installation on Jenkins running on a physical machine and several slave nodes with
different Linux distributions (both physical and virtual) where the git repository containing the CMake builder is cloned,
run, and the final product is actually produced. Jenkins can remotely control **KVM** virtual machines, starting and stopping
them depending on its needs. Artifacts produced by the builders (i.e. the tarballs containing the software package ready
to be shipped) are collected and uploaded to a **S3 bucket**, where authorized beta testers can download them.

**Feel free to drop here a comment** and share your experience, it's never easy finding a best practice when the requirements
are complex and not always well defined as they are in this case.