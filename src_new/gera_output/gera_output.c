#include "gera_output.h"

/*Imprime a imagem de saida no output*/
void gera_output(image_ppm *imagem)
{
  my_fprintf(stderr, "Writing output file\n" );
  unsigned char output;
  my_printf("P%d\n", imagem->tipo);
  my_printf("%d %d\n", imagem->largura/3, imagem->altura);
  my_printf("%d\n", imagem->higherColor);
  
  if(imagem->tipo==3)
    for(int i=0;i<imagem->altura;i++)
    {
      for(int j=0;j<imagem->largura;j++)
      {
        my_printf("%d ",imagem->matriz[(i*imagem->largura)+j]);
      }
      my_printf("\n");
    }
  else
    for(int i=0;i<imagem->altura;i++)
    {
      for(int j=0;j<imagem->largura;j++)
      {
        output=imagem->matriz[(i*imagem->largura)+j];
        my_fwrite(&output,sizeof(char),1,stdout);
      }
    }
}