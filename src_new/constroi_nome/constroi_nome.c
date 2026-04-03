#include "constroi_nome.h"

/*Funcao para criar uma string com a posicao do arquivo*/
void constroi_nome(char *nome,char *diretorio,char *arquivo)
{
  strncpy(nome,diretorio,strlen(diretorio)+1);
  strcat(nome,"/");
  strcat(nome,arquivo);
}