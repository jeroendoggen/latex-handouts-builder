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
 * pdflatex
 * pdfjam

Typical output:
---------------
Example .zip output: https://github.com/jeroendoggen/latex-handouts-builder/blob/master/Handouts/ExampleHandoutsBook.zip?raw=true

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
    
    Output written to: ExampleHandoutsBook.zip
    Build took 10 seconds
