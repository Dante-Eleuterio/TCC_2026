#include "acha_indice.h"

/*Calcula a pastilha mais proxima ao pedaço da imagem e devolve o indice do vetor*/
int acha_indice(argumentos *args,image_ppm *imagem,image_ppm *pastilhas,image_ppm *pedaco)
{
  int menor=1000;
  int indice=0;
  int x=0;
  for (int i = 0; i < args->numero_pastilhas; ++i)
  {
    /*Soma o modulo da diferença de cada componente RGB e guarda a pastilha com a menor diferença*/
    x=(abs(pedaco->red-pastilhas[i].red)+abs(pedaco->green-pastilhas[i].green)+abs(pedaco->blue-pastilhas[i].blue));
    if (x<menor)
    {
      menor=x;
      indice=i;
    }
  }
  return indice;
}