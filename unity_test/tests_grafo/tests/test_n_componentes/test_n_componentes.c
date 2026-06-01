#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: unsigned int n_componentes(grafo *g)
 *
 * Chama BuscaCaminhosMin para cada componente. Temos dois grupos:
 *
 *   1. Testes que usam g_busca_mock_on=0 (passthrough real): verificam
 *      o número de componentes em grafos pequenos.
 *
 *   2. Testes que usam g_busca_mock_on=1 (busca mockada): verificam
 *      apenas a interação — quantas vezes a busca foi disparada — sem
 *      depender de a busca real estar correta. Nesse caso, para o
 *      contador `c` avançar, n_componentes precisa ver os estados
 *      como "não-zero" após cada chamada à busca; como o mock não faz
 *      nada, todos os vértices permanecerão com estado==0 e a função
 *      chamará a busca para cada vértice. Isso é o que validamos
 *      como "interação esperada".
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_n_componentes_grafo_vazio(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    TEST_ASSERT_EQUAL_UINT(0, n_componentes(g));
    free_grafo_raw(g);
}

void test_n_componentes_um_vertice_isolado(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    TEST_ASSERT_EQUAL_UINT(1, n_componentes(g));
    free_grafo_raw(g);
}

void test_n_componentes_dois_vertices_isolados(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    TEST_ASSERT_EQUAL_UINT(2, n_componentes(g));
    free_grafo_raw(g);
}

void test_n_componentes_dois_conectados(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    TEST_ASSERT_EQUAL_UINT(1, n_componentes(g));
    free_grafo_raw(g);
}

void test_n_componentes_dois_componentes_separados(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_push_vertice(g, "d");
    /* {a-b}, {c-d} */
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[3], 1));
    helper_append_aresta(&g->vertices[3], helper_make_aresta(&g->vertices[2], 1));
    TEST_ASSERT_EQUAL_UINT(2, n_componentes(g));
    free_grafo_raw(g);
}

void test_n_componentes_chama_BuscaCaminhosMin_uma_vez_por_componente(void) {
    /* Interação: três vértices ligados => 1 chamada à busca */
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 1));
    n_componentes(g);
    TEST_ASSERT_EQUAL_UINT(1, spy_count_of("BuscaCaminhosMin"));
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_n_componentes_grafo_vazio);
    RUN_TEST(test_n_componentes_um_vertice_isolado);
    RUN_TEST(test_n_componentes_dois_vertices_isolados);
    RUN_TEST(test_n_componentes_dois_conectados);
    RUN_TEST(test_n_componentes_dois_componentes_separados);
    RUN_TEST(test_n_componentes_chama_BuscaCaminhosMin_uma_vez_por_componente);
    return UNITY_END();
}
#endif

#endif
