LaTeX Handouts Builder
======================

This script is currenly still a work in progress. The features are based on a similar bash script that I have been using for several years.

Program flow:
-------------
Run one command 'build.py'

Several sets of LaTeX-beamer slides are build:
 * pdf documents are created
 * Different versions: 6 slides per page, handout version with printer friendly colors

These slide handouts are merged in one 'ExampleHandoutsBook.pdf' file, with a title page, introduction, table of contents,...

All these documents are compressed in a single .zip archive. (and uploaded to the course website)

Dependencies:
-------------
 * pdflatex
 * pdfjam
 * zip

typical output:
---------------
PDF output: https://github.com/jeroendoggen/latex-handouts-builder/blob/master/Handouts/ExampleHandoutsBook.pdf?raw=true

    user@computer~/latex-handouts-builder$ python build.py 
    The following files will be processed:
    1. chap1.tex
    2. chap2.tex
    3. chap3.tex
    4. ExampleHandoutsBook.tex

    1/17 pdflatex chap1
    2/17 pdflatex chap1
    3/17 pdfjam-slides6up chap1.pdf --nup 2x3 --suffix 6pp -q
    4/17 mv chap1.pdf ../Handouts
    5/17 mv chap1-6pp.pdf ../Handouts
    6/17 pdflatex chap2
    7/17 pdflatex chap2
    8/17 pdfjam-slides6up chap2.pdf --nup 2x3 --suffix 6pp -q
    9/17 mv chap2.pdf ../Handouts
    10/17 mv chap2-6pp.pdf ../Handouts
    11/17 pdflatex chap3
    12/17 pdflatex chap3
    13/17 pdfjam-slides6up chap3.pdf --nup 2x3 --suffix 6pp -q
    14/17 mv chap3.pdf ../Handouts
    15/17 mv chap3-6pp.pdf ../Handouts
    16/17 pdflatex ExampleHandoutsBook
    17/17 pdflatex ExampleHandoutsBook
    Build finished
    Output written to: ExampleHandoutsBook.pdf


