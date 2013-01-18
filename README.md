LaTeX Handouts Builder
======================
Build Script for Latex-beamer based course handouts

What is it does:
 * Build LaTeX several beamer slide sets
 * Convert the slides to a printer-friendly format (no slide transitions, 6 slides per page, less colors)
 * Build a main "course handouts book" with all the slides (title page, introduction, table of contents,...)
 * Create a .zip archive with all the documents

Dependencies:
-------------
 * pdflatex
 * pdfjam

Typical output:
---------------
Zip output: https://github.com/jeroendoggen/latex-handouts-builder/blob/master/Handouts/ExampleHandoutsBook.zip?raw=true

    user@computer~/latex-handouts-builder$ python build.py 
    The following files will be processed:
    1. chap1.tex
    2. chap2.tex
    3. chap3.tex
    4. ExampleHandoutsBook.tex

    1/18 pdflatex chap1
    2/18 pdflatex chap1
    3/18 pdfjam-slides6up chap1.pdf --nup 2x3 --suffix 6pp -q
    4/18 mv chap1.pdf ../Handouts
    5/18 mv chap1-6pp.pdf ../Handouts
    6/18 pdflatex chap2
    7/18 pdflatex chap2
    8/18 pdfjam-slides6up chap2.pdf --nup 2x3 --suffix 6pp -q
    9/18 mv chap2.pdf ../Handouts
    10/18 mv chap2-6pp.pdf ../Handouts
    11/18 pdflatex chap3
    12/18 pdflatex chap3
    13/18 pdfjam-slides6up chap3.pdf --nup 2x3 --suffix 6pp -q
    14/18 mv chap3.pdf ../Handouts
    15/18 mv chap3-6pp.pdf ../Handouts
    16/18 pdflatex ExampleHandoutsBook
    17/18 pdflatex ExampleHandoutsBook
    Output written to: ExampleHandoutsBook.zip
    Build took 17 seconds


