#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: char *diametros(grafo *g)
 *
 * Chama n_componentes (que chama BuscaCaminhosMin) e BuscaDijkstra
 * (uma vez por par origem-componente), depois qsort+sprintf.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_diametros_um_vertice_isolado_retorna_zero(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    char *d = diametros(g);
    TEST_ASSERT_EQUAL_STRING("0", d);
    free(d);
    free_grafo_raw(g);
}

void test_diametros_caminho_3_vertices_retorna_2(void) {
    /* a -- b -- c : diâmetro = 2 */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 1));
    char *d = diametros(g);
    TEST_ASSERT_EQUAL_STRING("2", d);
    free(d);
    free_grafo_raw(g);
}

void test_diametros_dois_componentes_ordem_crescente(void) {
    /* {a-b} (diam 1) e {c-d-e} (diam 2)  =>  "1 2" */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_push_vertice(g, "d");
    helper_push_vertice(g, "e");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[3], 1));
    helper_append_aresta(&g->vertices[3], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[3], helper_make_aresta(&g->vertices[4], 1));
    helper_append_aresta(&g->vertices[4], helper_make_aresta(&g->vertices[3], 1));
    char *d = diametros(g);
    TEST_ASSERT_EQUAL_STRING("1 2", d);
    free(d);
    free_grafo_raw(g);
}

void test_diametros_com_pesos(void) {
    /* a --5-- b --3-- c : diâmetro 8 */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 5));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 5));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 3));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 3));
    char *d = diametros(g);
    TEST_ASSERT_EQUAL_STRING("8", d);
    free(d);
    free_grafo_raw(g);
}

void test_diametros_chama_BuscaDijkstra(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    char *d = diametros(g);
    TEST_ASSERT_GREATER_OR_EQUAL_UINT(2, spy_count_of("BuscaDijkstra"));
    free(d);
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_diametros_um_vertice_isolado_retorna_zero);
    RUN_TEST(test_diametros_caminho_3_vertices_retorna_2);
    RUN_TEST(test_diametros_dois_componentes_ordem_crescente);
    RUN_TEST(test_diametros_com_pesos);
    RUN_TEST(test_diametros_chama_BuscaDijkstra);
    return UNITY_END();
}
#endif

#endif
