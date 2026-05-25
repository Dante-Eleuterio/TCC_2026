/*
 * test_helpers.h
 *
 * Conjunto de utilidades compartilhadas pelos arquivos test_*.c:
 *
 *   - Builders de grafo "manual" (sem precisar passar por le_grafo)
 *   - Builders de fila/vértice para testes das funções de fila
 *   - Estado global dos spies/mocks (uso opcional)
 *
 * Implementação está em test_helpers.c.
 */

#ifndef TEST_HELPERS_H
#define TEST_HELPERS_H

#include "grafo_internal.h"

/* ------------------------------------------------------------------ */
/* Builders manuais                                                   */
/* ------------------------------------------------------------------ */

/* Aloca um Grafo zerado (calloc), sem passar por le_grafo.
 * O chamador é responsável por liberar via free_grafo_raw.        */
Grafo *make_grafo(const char *nome);
void   free_grafo_raw(Grafo *g);

/* Adiciona um vértice "à mão" no grafo. Diferente de adiciona_vertice
 * do módulo, esta versão é o que o teste considera correto e serve de
 * referência quando adiciona_vertice é mockada.                    */
unsigned int helper_push_vertice(Grafo *g, const char *nome);

/* Cria uma Aresta isolada (não liga a nenhuma lista). Útil para testes
 * de funções que operam sobre arestas individuais.                  */
Aresta *helper_make_aresta(Vértice *destino, unsigned int peso);

/* Anexa uma aresta na lista de arestas_head/tail de v. Libera o
 * trabalho braçal dos testes.                                      */
void helper_append_aresta(Vértice *v, Aresta *a);

/* ------------------------------------------------------------------ */
/* Spies — registro genérico de chamadas                              */
/* ------------------------------------------------------------------ */
/*
 * Cada mock __wrap_* deve, antes de qualquer outra coisa, chamar
 * spy_record("nome_da_funcao"). O teste verifica a sequência de
 * chamadas via spy_count / spy_at.
 */

void        spy_reset(void);
void        spy_record(const char *name);
unsigned    spy_count(void);
const char *spy_at(unsigned i);
unsigned    spy_count_of(const char *name);

#endif /* TEST_HELPERS_H */
