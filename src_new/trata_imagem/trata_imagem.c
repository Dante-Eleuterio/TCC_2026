#include "trata_imagem.h"

/*Funcao para guardar todas as informacoes da imagem ppm*/
void trata_imagem(argumentos *args,image_ppm *imagem)
{  
  char line[LINESIZE+1];
  int lineSize = 0;
  int num;
  int num2;
  unsigned char value;
  
  
  /*Pega o tipo do arquivo*/
  fscanf(stdin,"%s",line);
  lineSize=strlen(line);
  if(strncmp(line,"P3",lineSize)==0)
      imagem->tipo=3;
  else{
    if(strncmp(line,"P6",lineSize)==0)
      imagem->tipo=6;
    else
      imagem->tipo=-1;
  }

  /*Pulando comentarios*/
    fgets(line, LINESIZE,stdin);
    fgets(line, LINESIZE,stdin);
    while(line[0] == '#')
      fgets(line, LINESIZE, stdin);
  
  /*Pegando dimensoes da imagem*/
  sscanf(line, "%d %d", &num,&num2);
  imagem->largura = num*3;
  imagem->altura = num2;
  int matriz_tam=imagem->altura*imagem->largura;
  /*Pegando maximo da cor*/
  fscanf(stdin, "%d", &num);
  imagem->higherColor = num;
  imagem->matriz=malloc (matriz_tam * sizeof(int));
  if(imagem->matriz==NULL)
  {
    perror("Falha ao alocar");
    exit(1);
  }
  /*Zera toda a matriz*/
  for(int i=0;i<imagem->altura;i++)
    for(int j=0;j<imagem->largura;j++)
    {
      imagem->matriz[(i*imagem->largura)+j]=0;
    }
  /*Guarda todos os pixels na matriz*/
  if(imagem->tipo==3)
  {
    for(int i=0;i<imagem->altura;i++)
      for(int j=0;j<imagem->largura;j++)
      {
        fscanf(stdin, "%d", &num);
        imagem->matriz[(i*imagem->largura)+j]=num;
      }
  }
  else
  if(imagem->tipo==6)
  {
      fread (&value, sizeof(char), 1, stdin); /*Pega um \n para começar a pegar os pixels*/
      for(int i=0;i<imagem->altura;i++)
      {
        for(int j=0;j<imagem->largura;j++)
        {
          fread (&value, sizeof(char), 1, stdin);
          imagem->matriz[(i*imagem->largura)+j]=value;
        }
      }
  }
  else{
    for(int i=0;i<imagem->altura;i++)
      {
        for(int j=0;j<imagem->largura;j++)
        {
          imagem->matriz[(i*imagem->largura)+j]=-1;
        }
      }
  }
}
