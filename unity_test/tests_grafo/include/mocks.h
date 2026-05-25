/*
 * mocks.h
 *
 * Conjunto unificado de mocks __wrap_* para o módulo grafo. Cada mock é
 * "smart pass-through":
 *
 *   - Por padrão, encaminha a chamada para __real_* (comportamento
 *     idêntico ao da função real).
 *
 *   - O teste pode ligar o mock setando o flag g_<func>_mock_on = 1 e
 *     preenchendo as variáveis g_<func>_ret_* / g_<func>_args_* para
 *     controlar retornos e/ou capturar argumentos.
 *
 *   - Independente do modo (passthrough ou controlado), todo mock
 *     registra a chamada via spy_record("nome") para permitir asserts
 *     de "foi chamada N vezes / nesta ordem".
 *
 * Implementação: support/mocks.c. Linker:
 *     -Wl,--wrap=procura_vertice,--wrap=adiciona_vertice,
 *      --wrap=adiciona_aresta,--wrap=cria_fila,--wrap=enfilera,
 *      --wrap=enfilera_ordenado,--wrap=desenfilera,--wrap=fila_vazia,
 *      --wrap=destroi_fila,--wrap=BuscaCaminhosMin,--wrap=BuscaDijkstra,
 *      --wrap=BuscaLowPoint,--wrap=compara,--wrap=compara_nomes,
 *      --wrap=eh_raiz
 *
 * Os testes deste módulo NUNCA mockam:
 *   - funções da libc (malloc, free, strcpy, strtok, strcmp, qsort,
 *     printf, sprintf, fgets, perror...). Mockar libc é caro,
 *     frágil, e a libc já é exaustivamente testada. Faz sentido só se
 *     houvesse um caminho de erro do nosso código que dependesse, por
 *     ex., de malloc retornar NULL — mas o grafo.c não trata esse caso,
 *     então não há comportamento alternativo a validar.
 *
 *   - funções de I/O (fgets, fopen) por motivos análogos. Em
 *     test_le_grafo usamos fmemopen para criar um FILE* a partir de uma
 *     string em memória — mais simples e mais realista que mockar
 *     fgets.
 */

#ifndef GRAFO_MOCKS_H
#define GRAFO_MOCKS_H

#include "grafo_internal.h"

/* ------------------------------------------------------------------ */
/* Estado dos mocks                                                   */
/* ------------------------------------------------------------------ */

/* procura_vertice */
extern int g_pv_mock_on;
extern int g_pv_ret_seq[16];   /* sequência de retornos                 */
extern int g_pv_ret_seq_len;
extern int g_pv_calls;          /* incrementado a cada chamada           */

/* adiciona_vertice / adiciona_aresta — só spy, retorno void */
extern int g_av_mock_on;        /* se 1, intercepta e NÃO chama o real   */
extern int g_aa_mock_on;

/* fila — spies; pass-through preserva semântica                       */
extern int g_fila_mock_on;      /* se 1, ativa contadores específicos    */

/* Buscas (BuscaCaminhosMin, BuscaDijkstra, BuscaLowPoint)             */
extern int g_busca_mock_on;     /* se 1, intercepta e NÃO chama o real   */

/* Reseta TODO o estado de mock (flags e contadores).                  */
void mocks_reset_all(void);

#endif /* GRAFO_MOCKS_H */
