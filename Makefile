TEXFILE = main.tex
BIBFILE = name.bib

all: $(TEXFILE)
	pdflatex $(TEXFILE) 2>/dev/null
	bibtex $(basename $(TEXFILE))
	pdflatex $(TEXFILE) 2>/dev/null
	pdflatex $(TEXFILE) 2>/dev/null

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.pdf

.PHONY: all clean
