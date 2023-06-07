TEXFILE = main.tex
BIBFILE = name.bib

all:
    pdflatex $(TEXFILE)
    bibtex $(basename $(TEXFILE))
    pdflatex $(TEXFILE)
    pdflatex $(TEXFILE)

clean:
    rm -f *.aux *.bbl *.blg *.log *.out *.pdf
