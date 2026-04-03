#include "calcula_medias.h"

void calcula_medias(image_ppm *imagem)
{
  int matriz_tam=imagem->largura * imagem->altura;
  imagem->red=0;
  imagem->green=0;
  imagem->blue=0;
  /*Long int por garantia de memoria*/
  long int red=0;
  long int green=0;
  long int blue=0;
  int caso=0;
  /*Guarda os valores de cada pixel de cada cor*/
  for(int i=0;i<imagem->altura;i++){
    for(int j=0;j<imagem->largura;j++){
    switch (caso){
      case 0:
          red += imagem->matriz[(i * imagem->largura) + j];
          caso = 1;
          break;

      case 1:
          green += imagem->matriz[(i * imagem->largura) + j];
          caso = 2;
          break;

      case 2:
          blue += imagem->matriz[(i * imagem->largura) + j];
          caso = 0;
          break;
    }
    }
  }
  
  imagem->red=(red/(matriz_tam/3));
  imagem->green=(green/(matriz_tam/3));
  imagem->blue=(blue/(matriz_tam/3));
}