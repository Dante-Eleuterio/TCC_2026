/* BSD 2-Clause License
 *
 * Copyright (c) 2026, Dante Eleutério dos Santos
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 * 
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

// ============================================================================
//  Header
// ============================================================================

#include "fotomosaico.h"


// ============================================================================
//  Functions
// ============================================================================

/*Funcao para calcular as medias das pastilhas*/
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
  for(int i=0;i<imagem->altura;i++)
    for(int j=0;j<imagem->largura;j++)
    {
      if(caso==0)
      {
        red+=imagem->matriz[(i*imagem->largura)+j];
        caso++;
      }
      else
        if(caso==1)
        {
          green+=imagem->matriz[(i*imagem->largura)+j];
          caso++;
        }
        else
          if(caso==2)
          {
            blue+=imagem->matriz[(i*imagem->largura)+j];
            caso=0;
          }
    }
  
  imagem->red=(red/(matriz_tam/3));
  imagem->green=(green/(matriz_tam/3));
  imagem->blue=(blue/(matriz_tam/3));
}

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
  if(strncmp(line,"P6",lineSize)==0)
      imagem->tipo=6;

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
}

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
    if(!strncmp(argv[i],"-p",3))
      args->dir=i+1;
    else
      if(!strncmp(argv[i],"-i",3))
        args->input=i+1;
      else
        if(!strncmp(argv[i],"-o",3))
          args->output=i+1;
        else
          if(!strncmp(argv[i],"-h",3))
              printf("Este programa recebe uma imagem de entrada no formato .ppm e um diretório de pastilhas .ppm e recria a imagem de entrada em formato de mosaico usando as pastilhas\n");
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
  fprintf(stderr, "Reading input image\n" );
  fprintf(stderr, "input image is PPM P%d, %dx%d pixels\n",imagem->tipo,imagem->largura/3,imagem->altura );
}

/*Funcao para contar a quantidade de pastilhas no diretorio*/
void conta_pastilhas(argumentos *args,char const *argv[])
{
  fprintf(stderr, "Readin tiles from %s\n",args->diretorio );
  args->numero_pastilhas=0;
  DIR *dirstream;
  struct dirent *direntry;
  char *teste;
    dirstream = opendir (args->diretorio);
    if(!dirstream)
    {
      perror ("Couldn't open the directory");
      exit (1) ;
    }

  for (;;)
  {
    // pega a próxima entrada
    direntry = readdir (dirstream) ;
    // se for nula, encerra a varredura
    if (! direntry)
      break;
    teste= strstr(direntry->d_name,".ppm");
    if(teste!=NULL)
      args->numero_pastilhas++;
  }
  fprintf(stderr,"%d tiles read\n",args->numero_pastilhas);
  closedir(dirstream);
}


//APAGAR
int testa_nome(char *nome)   // same signature as the real one in the header
{
  if (nome) 
    return 1;
  return 0;
}
//APAGAR

/*Funcao para criar uma string com a posicao do arquivo*/
void constroi_nome(char *nome,char *diretorio,char *arquivo)
{
  strncpy(nome,diretorio,strlen(diretorio)+1);
  strcat(nome,"/");
  strcat(nome,arquivo);
}

/*Funcao para encontrar as pastilhas e guarda-las no vetor*/
void guarda_pastilhas(argumentos *args,char const *argv[],image_ppm *pastilhas)
{
  int i=0;
  DIR *dirstream;
  char *nome;
  struct dirent *direntry;
  char *teste;

    /*Abre o diretorio*/
    dirstream = opendir (args->diretorio);
    if(!dirstream)
    {
      perror ("Couldn't open the directory");
      exit (1) ;
    }
  
  for (;;)
  {
    // pega a próxima entrada
    direntry = readdir (dirstream) ;
    // se for nula, encerra a varredura
    if (! direntry)
      break;
    teste= strstr(direntry->d_name,".ppm");/*Confere se o arquivo é ppm*/
    if(teste!=NULL)
    {
      nome=malloc((strlen(args->diretorio)+ strlen(direntry->d_name)+3)*sizeof(char));
      if(nome==NULL)
      {
        perror("Falha ao alocar");
        exit(1);
      }
      constroi_nome(nome,args->diretorio,direntry->d_name);
      freopen(nome,"r",stdin); /*Redireciona a entrada para o stdin */
      trata_imagem(args,&pastilhas[i]);
      calcula_medias(&pastilhas[i]);
      i++;
      free(nome);
    }
  }
  fprintf(stderr, "Tiles size is %dx%d\n",pastilhas[0].largura/3,pastilhas[0].altura );
  fprintf(stderr, "Calculating tiles' average colors\n");
  closedir(dirstream);
}
/*Imprime a imagem de saida no output*/
void gera_output(image_ppm *imagem)
{
  fprintf(stderr, "Writing output file\n" );
  unsigned char output;
  printf("P%d\n", imagem->tipo);
  printf("%d %d\n", imagem->largura/3, imagem->altura);
  printf("%d\n", imagem->higherColor);
  
  if(imagem->tipo==3)
    for(int i=0;i<imagem->altura;i++)
    {
      for(int j=0;j<imagem->largura;j++)
      {
        printf("%d ",imagem->matriz[(i*imagem->largura)+j]);
      }
      printf("\n");
    }
  else
    for(int i=0;i<imagem->altura;i++)
    {
      for(int j=0;j<imagem->largura;j++)
      {
        output=imagem->matriz[(i*imagem->largura)+j];
        fwrite(&output,sizeof(char),1,stdout);
      }
    }
}

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