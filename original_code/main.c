/*Dante Eĺeutério dos Santos GRR20206686*/

#include "fotomosaico.h"
int main(int argc, char const *argv[])
{
  
  image_ppm imagem_principal;
  image_ppm *pastilhas;
  argumentos args;
  argumentos_entrada(&args,argc,argv,&imagem_principal);
  conta_pastilhas(&args,argv);
  pastilhas=malloc(args.numero_pastilhas * sizeof(image_ppm));/*Aloca um vetor para todas as pastilhas*/
  if(pastilhas==NULL)
  {
    perror("Falha ao alocar a memoria");
    exit(1);
  }
  guarda_pastilhas(&args,argv,pastilhas);
  mosaico(&args,&imagem_principal,pastilhas);
  gera_output(&imagem_principal);

  /*Libera toda a memória*/
  free(imagem_principal.matriz);
  if(args.free)
    free(args.diretorio);
  for (int i = 0; i < args.numero_pastilhas; ++i)
    free(pastilhas[i].matriz);
  free(pastilhas);
  return 0;
}

