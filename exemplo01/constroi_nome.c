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

#include <string.h>

#include "constroi_nome.h"

// ============================================================================
//  Functions
// ============================================================================

/**
 * @brief Funcao para criar uma string com a posicao do arquivo
 * 
 * @param[out] nome
 * @param[in]  diretorio
 * @param[in]  arquivo
 */

void constroi_nome(char *nome, char *diretorio, char *arquivo)
{
  strncpy(nome,diretorio,strlen(diretorio)+1);
  strcat(nome,"/");
  strcat(nome,arquivo);
}


// ============================================================================
//  Tests
// ============================================================================

#define TEST
#ifdef TEST

#include <assert.h>

static
void teste1() {
  const char* expected_nome = "folder_name/file_name";
  char nome[256];
  char* diretorio = "folder_name";
  char* arquivo = "file_name";
  constroi_nome(nome,diretorio,arquivo);
  assert( strcmp(expected_nome, nome) == 0 );
}

int main() {
  teste1();
  return 0;
}

#endif