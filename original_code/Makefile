#Dante Eĺeutério dos Santos GRR20206686

CFLAGS = -Wall -std=c99

objects = main.o fotomosaico.o
all: mosaico


mosaico: main.o fotomosaico.o
		cc -std=c99 -Wall main.o fotomosaico.o -o mosaico

main.o: main.c fotomosaico.h
		cc -c main.c $(CFLAGS)

fotomosaico.o: fotomosaico.c fotomosaico.h
		cc -c fotomosaico.c $(CFLAGS)

clean: 
		-rm -f $(objects)
purge:	clean
		-rm -f mosaico
