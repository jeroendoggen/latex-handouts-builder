LaTeX Handouts Builder
======================
Build Script for Latex-beamer based course handouts

What is it does:
 * Build multiple LaTeX beamer slide sets with one command: ``python build.py``
 * Convert the slides to a printer-friendly format (no slide transitions, 6 slides per page, less colors)
 * Build a main "course handouts book" with all the slides (one chapter per beamer slide set, title page, introduction, table of contents,...)
 * Create a .zip archive with all the documents
 
The scripts starts multiple processes in parallel to build all slide sets at the same time. This results in a big speedup on multi-core systems.

Dependencies:
-------------
 * pdflatex - PDF output from TeX
 * pdfjam - A shell script for manipulating PDF files

Typical output:
---------------
#### Parallel build: (using multiple processes, fastests)

    user@computer~/latex-handouts-builder$ python build.py 
    The following files will be processed:
     1. chap1.tex
     2. chap2.tex
     3. chap3.tex
     4. chap4.tex
     5. chap5.tex
     6. chap6.tex
     7. chap7.tex
     8. chap8.tex
     9. ExampleHandoutsBook.tex

    Building chapter: chap1
    Building chapter: chap2
    Building chapter: chap3
    Building chapter: chap4
    Building chapter: chap5
    Building chapter: chap6
    Building chapter: chap7
    Building chapter: chap8

    Remaining processes:
    8/8
    7/8
    6/8
    5/8
    4/8
    3/8
    2/8
    1/8
    Building the final book: ExampleHandoutsBook
    Output written to: ExampleHandoutsBook.zip
    Build took 17 seconds
    
#### Sequential build: (easier for debugging LaTeX errors, but slower)

    The following files will be processed:
     1. chap1.tex
     2. chap2.tex
     3. chap3.tex
     4. chap4.tex
     5. chap5.tex
     6. chap6.tex
     7. chap7.tex
     8. chap8.tex
     9. ExampleHandoutsBook.tex

    1/43 pdflatex chap1
    2/43 pdflatex chap1
    3/43 pdfjam-slides6up chap1.pdf --nup 2x3 --suffix 6pp -q
    4/43 mv chap1.pdf ../Handouts
    5/43 mv chap1-6pp.pdf ../Handouts
    6/43 pdflatex chap2
    7/43 pdflatex chap2
    8/43 pdfjam-slides6up chap2.pdf --nup 2x3 --suffix 6pp -q
    9/43 mv chap2.pdf ../Handouts
    10/43 mv chap2-6pp.pdf ../Handouts
    ...
    36/43 pdflatex chap8
    37/43 pdflatex chap8
    38/43 pdfjam-slides6up chap8.pdf --nup 2x3 --suffix 6pp -q
    39/43 mv chap8.pdf ../Handouts
    40/43 mv chap8-6pp.pdf ../Handouts
    41/43 pdflatex ExampleHandoutsBook
    42/43 pdflatex ExampleHandoutsBook
    Output written to: ExampleHandoutsBook.zip
    Build took 42 seconds

