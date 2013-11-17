# LaTeX Handouts Builder
Build Script for Latex-beamer based course handouts.
This tool can be used to build "course handout books" using multiple LaTeX beamer slides sets.

### What is it does:
 * Build multiple LaTeX beamer slide sets with one command: ``python build.py``
 * Convert the slides to a printer-friendly format (no slide transitions, 6 slides per page, less colors)
 * Build a main "course handouts book" with all the slides (one chapter per beamer slide set, title page, introduction, table of contents,...)
 * Create a .zip archive with all the documents

### Book structure:
Title page, introduction, table of contents

One chapter per slide set (three printer-friendly versions: no slides transitions &  less colors)
 * three slides per page with room for notes (example)
 * six slides per page (example)
 * two slides per page (example)

### Dependencies:
 * pdflatex - PDF output from TeX
 * pdfjam - A shell script for manipulating PDF files

### Typical output:

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
