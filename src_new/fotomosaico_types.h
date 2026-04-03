#ifndef FOTOMOSAICO_TYPES_H
#define FOTOMOSAICO_TYPES_H

#include <stdio.h>
#include <sys/types.h>
#include <dirent.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#define LINESIZE 1024

typedef struct
{
  int tipo;
  int largura;
  int altura;
  int higherColor;
  int red;
  int green;
  int blue;
  int *matriz;
} image_ppm;

typedef struct
{
  int dir;
  int input;
  int output;
  char *diretorio;
  int numero_pastilhas;
  int free;
} argumentos;

int my_printf(const char *format, ...);
int my_perror(const char *format, ...);
int my_fprintf(FILE *stream, const char *format, ...);
size_t my_fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream);
void my_exit(int status);

#endif