#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: unsigned int bipartido(grafo *g)
 *
 * Chama BuscaCaminhosMin para distribuir níveis e depois inspeciona
 * arestas para checar paridade.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_bipartido_vazio_retorna_um(void) {
    /* Sem vértices, não há aresta que viole bipartição. */
    Grafo *g = make_grafo("g");
    TEST_ASSERT_EQUAL_UINT(1, bipartido(g));
    free_grafo_raw(g);
}

void test_bipartido_unico_vertice_retorna_um(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    TEST_ASSERT_EQUAL_UINT(1, bipartido(g));
    free_grafo_raw(g);
}

void test_bipartido_caminho_simples_retorna_um(void) {
    /* a -- b -- c : bipartido */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 1));
    TEST_ASSERT_EQUAL_UINT(1, bipartido(g));
    free_grafo_raw(g);
}

void test_bipartido_triangulo_retorna_zero(void) {
    /* Triângulo (ciclo ímpar): NÃO bipartido. */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[2], 1));
    TEST_ASSERT_EQUAL_UINT(0, bipartido(g));
    free_grafo_raw(g);
}

void test_bipartido_quadrilatero_retorna_um(void) {
    /* a-b-c-d-a (ciclo par): bipartido */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_push_vertice(g, "d");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[3], 1));
    helper_append_aresta(&g->vertices[3], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[3], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[3], 1));
    TEST_ASSERT_EQUAL_UINT(1, bipartido(g));
    free_grafo_raw(g);
}

void test_bipartido_chama_BuscaCaminhosMin(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    bipartido(g);
    TEST_ASSERT_GREATER_OR_EQUAL_UINT(1, spy_count_of("BuscaCaminhosMin"));
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_bipartido_vazio_retorna_um);
    RUN_TEST(test_bipartido_unico_vertice_retorna_um);
    RUN_TEST(test_bipartido_caminho_simples_retorna_um);
    RUN_TEST(test_bipartido_triangulo_retorna_zero);
    RUN_TEST(test_bipartido_quadrilatero_retorna_um);
    RUN_TEST(test_bipartido_chama_BuscaCaminhosMin);
    return UNITY_END();
}
#endif

#endif
