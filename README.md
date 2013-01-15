LaTeX Handouts Builder
======================

This script is currenly still a work in progress. The features are based on a similar bash script that I have been using for several years.

Program flow:
-------------
Run one command 'build.py'

Several sets of LaTeX-beamer slides are build:
 * pdf documents are created
 * Different versions: 4/6 slides per page, handout version with printer friendly colors

These slide handouts are merged in one 'handouts-LaTeX-book' with a title page, introduction, table of contents,...

All these documents are compressed in a single .zip archive. (and uploaded to the course website)

typical output:
---------------
    user@computer~/latex-handouts-builder$ python build.py 
    The following chapters will be processed:
      1. chap0
      2. chap1
      3. chap2
      4. chap3

    pdflatex chap0
    mv chap0.pdf ../Handouts
    pdflatex chap1
    mv chap1.pdf ../Handouts
    pdflatex chap2
    mv chap2.pdf ../Handouts
    pdflatex chap3
    mv chap3.pdf ../Handouts

