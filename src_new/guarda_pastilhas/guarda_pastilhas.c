#include "guarda_pastilhas.h"

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
      my_perror ("Couldn't open the directory");
      my_exit (1);
      return;
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
        my_perror("Falha ao alocar");
        my_exit(1);
        return;
      }
      constroi_nome(nome,args->diretorio,direntry->d_name);
      freopen(nome,"r",stdin); /*Redireciona a entrada para o stdin */
      trata_imagem(args,&pastilhas[i]);
      calcula_medias(&pastilhas[i]);
      i++;
      free(nome);
    }
  }
  my_fprintf(stderr, "Tiles size is %dx%d\n",pastilhas[0].largura/3,pastilhas[0].altura );
  my_fprintf(stderr, "Calculating tiles' average colors\n");
  closedir(dirstream);
}