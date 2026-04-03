#include "mosaico.h"

/*Funcao para criar o mosaico*/
void mosaico(argumentos *args,image_ppm *imagem,image_ppm *pastilhas)
{
  fprintf(stderr, "Building mosaic image\n" );
  int x=0;
  int y=0;
  int xcopia=0;
  int ycopia=0;
  int i=0;
  int j=0;
  int index=0;
  /*Cria pastilha temporaria e a inicializa*/
  image_ppm pedaco;
  pedaco.matriz= malloc(pastilhas[0].altura*pastilhas[0].largura * sizeof(int));
  if(pedaco.matriz==NULL)
  {
    perror("Erro ao alocar memoria");
    exit(1);
  }
  pedaco.tipo=pastilhas[0].tipo;
  pedaco.largura=pastilhas[0].largura;
  pedaco.altura=pastilhas[0].altura;
  pedaco.higherColor=pastilhas[0].higherColor;
  
  /*Zera a matriz*/
  for(i=0;i<pedaco.altura;i++)
    for(j=0;j<pedaco.largura;j++)
    {
      pedaco.matriz[(i*pedaco.largura)+j]=0;
    }

  /*Inicia o processo de criacao do mosaico*/
  while((x<imagem->largura)&&(y<imagem->altura))
  {
  
    /*Guarda o pedaço a ser substitudo na pastilha temporaria*/
    for(i=0;i<pastilhas[0].altura;i++)
    {
      for(j=0;j<pastilhas[0].largura;j++)
      {
        if((xcopia<imagem->largura)&&(ycopia<imagem->altura))/*Evita copia de indice inexistente*/ 
          pedaco.matriz[(i*pastilhas[0].largura)+j]=imagem->matriz[(ycopia*imagem->largura)+xcopia];
        xcopia++;
      }
      ycopia++;/*Pula linha*/
      xcopia-=pastilhas[0].largura;/*Reinicia as colunas*/
    }

    calcula_medias(&pedaco);  
    index=acha_indice(args,imagem,pastilhas,&pedaco);
    /*Guarda a pastilha escolhida na posicao da imagem original*/
    for(i=0;i<pastilhas[index].altura;i++)
    {
      for(j=0;j<pastilhas[index].largura;j++)
      {
        if((x<imagem->largura)&&(y<imagem->altura))
          imagem->matriz[(y*imagem->largura)+x]=pastilhas[index].matriz[(i*pastilhas[index].largura)+j];
        x++;
      }
      y++;/*Pula linha*/
      x-=pastilhas[index].largura;/*Reinicia as colunas*/
    }
    /*Se chegou ao fim da coluna de pastilhas, passa pra proxima*/
    if(y>=imagem->altura)
    {
      x+=pastilhas[index].largura;
      y=0;
    }
    xcopia=x;
    ycopia=y;
  }
  free(pedaco.matriz);
}