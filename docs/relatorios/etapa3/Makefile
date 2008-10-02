MAINNAME=relatorio

all:
	mkdir -p build
	cp *.tex build
	cp -fR imagens build/
	cp -fR capitulos build/
	cp Makefile build/
	make -C build build 

build:
	pdflatex ${MAINNAME}.tex
	pdflatex ${MAINNAME}.tex
	cp ${MAINNAME}.pdf ../

clean:
	rm -fR build
	rm -fR ${MAINNAME}.pdf
