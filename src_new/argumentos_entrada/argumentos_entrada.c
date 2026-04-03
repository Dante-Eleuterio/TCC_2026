#include "argumentos_entrada.h"

/*Funcao para receber os argumentos da linha de comando do terminal*/
void argumentos_entrada(argumentos *args,int argc, char const *argv[],image_ppm *imagem)
{
  args->dir=0;
  args->input=0;
  args->output=0;
  int tamanho=0;
  /*Percorre o vetor identificando a posicao dos argumentos*/
  for (int i = 0; i < argc; ++i)
  {
    if(!strncmp(argv[i],"-h",3)){
      my_printf("Este programa recebe uma imagem de entrada no formato .ppm e um diretório de pastilhas .ppm e recria a imagem de entrada em formato de mosaico usando as pastilhas\n");
      return;
    }
    else
      if(!strncmp(argv[i],"-i",3))
        args->input=i+1;
      else
        if(!strncmp(argv[i],"-o",3))
          args->output=i+1;
        else
          if(!strncmp(argv[i],"-p",3))
              args->dir=i+1;
  }
  
  if(args->dir!=0)
  {
    tamanho=strlen(argv[args->dir])+1;
    args->diretorio = (char*)malloc(tamanho*sizeof(char));
    if(args->diretorio==NULL)
    {
      perror ("Erro na alocacao de memoria");
      exit (1) ;
    }
    strncpy(args->diretorio,argv[args->dir],tamanho);
    args->free=1;/*FLag para saber que o malloc foi necessario*/
  }
  else
  {
    args->free=0; /*Não precisa dar free no final*/
    args->diretorio="./tiles";
  }

  
  if(args->output!=0)
    freopen(argv[args->output],"w",stdout);/*Redireciona a entrada para o stdout*/

  if(args->input!=0)  
  {
    freopen(argv[args->input],"r",stdin); /*Redireciona a entrada para o stdin */
    trata_imagem(args,imagem);
  }
  else
    trata_imagem(args,imagem);
  my_fprintf(stderr, "Reading input image\n" );
  my_fprintf(stderr, "input image is PPM P%d, %dx%d pixels\n",imagem->tipo,imagem->largura/3,imagem->altura );
}