all: proposal.pdf progress.pdf report.pdf

%.pdf: %.tex
	pdflatex --shell-escape $<
	pdflatex --shell-escape $<
	pdflatex --shell-escape $<
