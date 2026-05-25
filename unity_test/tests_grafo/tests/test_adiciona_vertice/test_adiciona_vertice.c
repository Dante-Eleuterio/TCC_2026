#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"

/*
 * Testes para: void adiciona_vertice(grafo *g, char *vertice)
 *
 * Função interna que só manipula campos do struct Grafo. Nenhuma chamada
 * a outras funções da biblioteca a ser mockada.
 */

#ifndef ALL_TESTS
void setUp(void)    { spy_reset(); }
void tearDown(void) {}
#endif

void test_adiciona_vertice_incrementa_num_vertices(void) {
    Grafo *g = make_grafo("g");
    char nome[] = "a";
    adiciona_vertice(g, nome);
    TEST_ASSERT_EQUAL_UINT(1, g->num_vertices);
    free_grafo_raw(g);
}

void test_adiciona_vertice_grava_nome(void) {
    Grafo *g = make_grafo("g");
    char nome[] = "alpha";
    adiciona_vertice(g, nome);
    TEST_ASSERT_EQUAL_STRING("alpha", g->vertices[0].nome);
    free_grafo_raw(g);
}

void test_adiciona_vertice_inicializa_listas_em_NULL(void) {
    Grafo *g = make_grafo("g");
    char nome[] = "v";
    adiciona_vertice(g, nome);
    TEST_ASSERT_NULL(g->vertices[0].arestas_head);
    TEST_ASSERT_NULL(g->vertices[0].arestas_tail);
    free_grafo_raw(g);
}

void test_adiciona_vertice_inicializa_pai_dist_estado(void) {
    Grafo *g = make_grafo("g");
    char nome[] = "v";
    adiciona_vertice(g, nome);
    TEST_ASSERT_NULL(g->vertices[0].pai);
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[0].dist);
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[0].estado);
    free_grafo_raw(g);
}

void test_adiciona_vertice_dois_em_sequencia(void) {
    Grafo *g = make_grafo("g");
    char a[] = "a"; char b[] = "b";
    adiciona_vertice(g, a);
    adiciona_vertice(g, b);
    TEST_ASSERT_EQUAL_UINT(2, g->num_vertices);
    TEST_ASSERT_EQUAL_STRING("a", g->vertices[0].nome);
    TEST_ASSERT_EQUAL_STRING("b", g->vertices[1].nome);
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_adiciona_vertice_incrementa_num_vertices);
    RUN_TEST(test_adiciona_vertice_grava_nome);
    RUN_TEST(test_adiciona_vertice_inicializa_listas_em_NULL);
    RUN_TEST(test_adiciona_vertice_inicializa_pai_dist_estado);
    RUN_TEST(test_adiciona_vertice_dois_em_sequencia);
    return UNITY_END();
}
#endif

#endif
