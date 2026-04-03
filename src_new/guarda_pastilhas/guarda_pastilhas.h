#ifndef GUARDA_PASTILHAS_H
#define GUARDA_PASTILHAS_H

#include "../fotomosaico_types.h"

void guarda_pastilhas(argumentos *, char const **, image_ppm *);
void constroi_nome(char*, char*, char*);
void trata_imagem(argumentos*, image_ppm*);
void calcula_medias(image_ppm*);
#endif