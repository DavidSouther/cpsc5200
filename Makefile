all: pdf 

pdf:
	asciidoctor-pdf -r asciidoctor-diagram **/*.adoc