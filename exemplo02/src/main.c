/* BSD 2-Clause License
 *
 * Copyright (c) 2026, Dante Eĺeutério dos Santos
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

