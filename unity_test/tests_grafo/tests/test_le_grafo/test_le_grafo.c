#ifdef TEST

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: grafo *le_grafo(FILE *f)
 *
 * le_grafo chama: procura_vertice, adiciona_vertice, adiciona_aresta.
 * Estratégia:
 *
 *   - Para entrada usamos `fmemopen` (cria um FILE* a partir de um
 *     buffer em memória). É preferível a mockar `fgets`: muito mais
 *     simples, mais realista, e a libc já é confiável.
 *
 *   - Não mockamos malloc — não há caminho alternativo a validar quando
 *     a alocação falha (o código apenas faz `perror` e retorna NULL, e
 *     reproduzir esse caminho exigiria mockar malloc só para um teste).
 *
 *   - Verificamos via spy_count_of() que as funções internas foram
 *     chamadas o número correto de vezes, confirmando a interação
 *     com os colaboradores.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

static FILE *open_mem(const char *s) {
    return fmemopen((void*)s, strlen(s), "r");
}

void test_le_grafo_retorna_ponteiro_nao_nulo(void) {
    mocks_reset_all();
    const char *txt = "g1\na\nb\n";
    FILE *f = open_mem(txt);
    grafo *g = le_grafo(f);
    fclose(f);
    TEST_ASSERT_NOT_NULL(g);
    destroi_grafo(g);
}

void test_le_grafo_grava_nome_do_grafo(void) {
    mocks_reset_all();
    const char *txt = "meu_grafo\na\n";
    FILE *f = open_mem(txt);
    grafo *g = le_grafo(f);
    fclose(f);
    TEST_ASSERT_EQUAL_STRING("meu_grafo", nome(g));
    destroi_grafo(g);
}

void test_le_grafo_pula_comentarios(void) {
    mocks_reset_all();
    const char *txt = "// header comment\ng1\n// outro\na\nb\n";
    FILE *f = open_mem(txt);
    grafo *g = le_grafo(f);
    fclose(f);
    TEST_ASSERT_EQUAL_STRING("g1", nome(g));
    TEST_ASSERT_EQUAL_UINT(2, n_vertices(g));
    destroi_grafo(g);
}

void test_le_grafo_pula_linhas_em_branco(void) {
    mocks_reset_all();
    const char *txt = "g1\n\na\n\nb\n";
    FILE *f = open_mem(txt);
    grafo *g = le_grafo(f);
    fclose(f);
    TEST_ASSERT_EQUAL_UINT(2, n_vertices(g));
    destroi_grafo(g);
}

void test_le_grafo_adiciona_vertices_isolados(void) {
    mocks_reset_all();
    const char *txt = "g\na\nb\nc\n";
    FILE *f = open_mem(txt);
    grafo *g = le_grafo(f);
    fclose(f);
    TEST_ASSERT_EQUAL_UINT(3, n_vertices(g));
    TEST_ASSERT_EQUAL_UINT(0, n_arestas(g));
    destroi_grafo(g);
}

void test_le_grafo_processa_aresta_com_peso(void) {
    mocks_reset_all();
    const char *txt = "g\na -- b 7\n";
    FILE *f = open_mem(txt);
    grafo *g = le_grafo(f);
    fclose(f);
    TEST_ASSERT_EQUAL_UINT(2, n_vertices(g));
    TEST_ASSERT_EQUAL_UINT(1, n_arestas(g));
    destroi_grafo(g);
}

void test_le_grafo_aresta_sem_peso_assume_um(void) {
    mocks_reset_all();
    const char *txt = "g\na -- b\n";
    FILE *f = open_mem(txt);
    grafo *g = le_grafo(f);
    fclose(f);
    TEST_ASSERT_EQUAL_UINT(1, n_arestas(g));
    /* O peso default deveria ser 1 — checamos pela estrutura interna. */
    Grafo *gg = (Grafo*)g;
    TEST_ASSERT_EQUAL_UINT(1, gg->vertices[0].arestas_head->peso);
    destroi_grafo(g);
}

void test_le_grafo_nao_duplica_vertices(void) {
    /* "a -- b" e "b -- c" devem produzir 3 vértices, não 4. */
    mocks_reset_all();
    const char *txt = "g\na -- b\nb -- c\n";
    FILE *f = open_mem(txt);
    grafo *g = le_grafo(f);
    fclose(f);
    TEST_ASSERT_EQUAL_UINT(3, n_vertices(g));
    destroi_grafo(g);
}

void test_le_grafo_chama_adiciona_vertice_no_caso_vertice_solto(void) {
    mocks_reset_all();
    const char *txt = "g\na\nb\n";
    FILE *f = open_mem(txt);
    grafo *g = le_grafo(f);
    fclose(f);
    /* Cada linha com vértice solto dispara uma chamada a
     * adiciona_vertice. (Inclui as chamadas via spy passthrough.) */
    TEST_ASSERT_EQUAL_UINT(2, spy_count_of("adiciona_vertice"));
    destroi_grafo(g);
}

void test_le_grafo_chama_adiciona_aresta_no_caso_aresta(void) {
    mocks_reset_all();
    const char *txt = "g\nx -- y 5\n";
    FILE *f = open_mem(txt);
    grafo *g = le_grafo(f);
    fclose(f);
    TEST_ASSERT_EQUAL_UINT(1, spy_count_of("adiciona_aresta"));
    destroi_grafo(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_le_grafo_retorna_ponteiro_nao_nulo);
    RUN_TEST(test_le_grafo_grava_nome_do_grafo);
    RUN_TEST(test_le_grafo_pula_comentarios);
    RUN_TEST(test_le_grafo_pula_linhas_em_branco);
    RUN_TEST(test_le_grafo_adiciona_vertices_isolados);
    RUN_TEST(test_le_grafo_processa_aresta_com_peso);
    RUN_TEST(test_le_grafo_aresta_sem_peso_assume_um);
    RUN_TEST(test_le_grafo_nao_duplica_vertices);
    RUN_TEST(test_le_grafo_chama_adiciona_vertice_no_caso_vertice_solto);
    RUN_TEST(test_le_grafo_chama_adiciona_aresta_no_caso_aresta);
    return UNITY_END();
}
#endif

#endif
