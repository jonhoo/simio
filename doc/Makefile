all: proposal.pdf progress.pdf report.pdf

report.pdf: figures/start.svg
report.pdf: figures/one-hop.svg
report.pdf: figures/far.svg
report.pdf: figures/end.svg

%.pdf: %.tex
	pdflatex --shell-escape $<
	pdflatex --shell-escape $<
	pdflatex --shell-escape $<
