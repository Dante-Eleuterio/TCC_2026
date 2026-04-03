#include "conta_pastilhas.h"

/*Funcao para contar a quantidade de pastilhas no diretorio*/
int conta_pastilhas(argumentos *args,char const *argv[])
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
      return -1;
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
  return 0;
}
