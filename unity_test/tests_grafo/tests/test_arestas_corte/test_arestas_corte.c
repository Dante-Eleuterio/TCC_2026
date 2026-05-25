#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: char *arestas_corte(grafo *g)
 *
 * Análogo a vertices_corte: roda BuscaLowPoint e procura arestas
 * (u,v) com u->nivel < v->lowpoint na árvore DFS. Cada aresta sai
 * com os dois nomes em ordem alfabética, e o conjunto inteiro fica
 * em ordem alfabética.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_arestas_corte_caminho_simples_3_vertices(void) {
    /* a -- b -- c : ambas arestas são pontes
     * Esperado (cada par alfabético, conjunto alfabético): "a b b c"
     */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 1));
    g->num_arestas = 2;
    char *r = arestas_corte(g);
    TEST_ASSERT_EQUAL_STRING("a b b c", r);
    free(r);
    free_grafo_raw(g);
}

void test_arestas_corte_triangulo_nenhuma_ponte(void) {
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
    g->num_arestas = 3;
    char *r = arestas_corte(g);
    TEST_ASSERT_EQUAL_STRING("", r);
    free(r);
    free_grafo_raw(g);
}

void test_arestas_corte_ordem_alfabetica_por_par(void) {
    /* "z" precede "y"? Não: "y" < "z" → par "y z" não "z y".
     * Configuração: y -- z (única aresta, é ponte).
     */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "z");
    helper_push_vertice(g, "y");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    g->num_arestas = 1;
    char *r = arestas_corte(g);
    TEST_ASSERT_EQUAL_STRING("y z", r);
    free(r);
    free_grafo_raw(g);
}

void test_arestas_corte_chama_BuscaLowPoint(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    g->num_arestas = 1;
    char *r = arestas_corte(g);
    TEST_ASSERT_GREATER_OR_EQUAL_UINT(1, spy_count_of("BuscaLowPoint"));
    free(r);
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_arestas_corte_caminho_simples_3_vertices);
    RUN_TEST(test_arestas_corte_triangulo_nenhuma_ponte);
    RUN_TEST(test_arestas_corte_ordem_alfabetica_por_par);
    RUN_TEST(test_arestas_corte_chama_BuscaLowPoint);
    return UNITY_END();
}
#endif

#endif
