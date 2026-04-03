/*Dante Eĺeutério dos Santos GRR20206686*/
#ifndef __FOTOMOSAICO__
#define __FOTOMOSAICO__

#include <stdio.h>
#include <sys/types.h>
#include <dirent.h>
#include <stdlib.h>
#include <string.h>
#define LINESIZE 1024

/*Struct com informações da imagem ppm*/
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
}image_ppm;

/*Struct com os argumentos de entrada e extras*/
typedef struct
{
  int dir;
  int input;
  int output;
  char *diretorio;
  int numero_pastilhas;
  int free;
}argumentos;

void calcula_medias(image_ppm *);

void trata_imagem(argumentos *,image_ppm *);

void argumentos_entrada(argumentos *,int ,char const **,image_ppm *);

int conta_pastilhas(argumentos *,char const **);

void constroi_nome(char *, char *,char *);

void guarda_pastilhas(argumentos *,char const **,image_ppm *);

void gera_output(image_ppm *);

int acha_indice(argumentos *,image_ppm *,image_ppm *,image_ppm *);

void mosaico(argumentos *, image_ppm *, image_ppm *);

#endif // __FOTOMOSAICO__