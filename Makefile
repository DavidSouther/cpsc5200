all: pdf 

pdf:
	asciidoctor-pdf -r asciidoctor-diagram **/*.adoc
	pandoc 07_20200316_final.md -o 07_20200316_final.pdf

