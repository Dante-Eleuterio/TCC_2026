#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: void BuscaDijkstra(Vértice *r)
 *
 * Dijkstra clássico via fila ordenada. Verificamos distâncias finais
 * em pequenos grafos com pesos não-uniformes e usamos o spy para
 * checar que enfilera_ordenado foi usada.
 *
 * IMPORTANTE — antes de chamar a busca, todos os vértices devem ter
 * dist = UINT_MAX para que a comparação `v->dist + peso < u->dist`
 * funcione no ramo "u já estava na fila com estado 1". Como o código
 * faz inicialização das distâncias por fora (em quem chama Dijkstra),
 * fazemos o mesmo aqui nos testes.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

#include <limits.h>

static void reset_dists(Grafo *g) {
    for (unsigned i = 0; i < g->num_vertices; i++) {
        g->vertices[i].dist   = UINT_MAX;
        g->vertices[i].estado = 0;
        g->vertices[i].pai    = NULL;
    }
}

void test_BuscaDijkstra_raiz_com_dist_zero(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    reset_dists(g);
    BuscaDijkstra(&g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[0].dist);
    free_grafo_raw(g);
}

void test_BuscaDijkstra_caminho_simples_3_vertices(void) {
    /* a --1-- b --2-- c */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 2));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 2));
    reset_dists(g);
    BuscaDijkstra(&g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[0].dist);
    TEST_ASSERT_EQUAL_UINT(1, g->vertices[1].dist);
    TEST_ASSERT_EQUAL_UINT(3, g->vertices[2].dist);
    free_grafo_raw(g);
}

void test_BuscaDijkstra_escolhe_caminho_mais_curto(void) {
    /*  a --10-- b
     *   \--1--/c--1--b   melhor: a->c->b = 2
     */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 10));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 10));
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 1));
    reset_dists(g);
    BuscaDijkstra(&g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[0].dist);
    TEST_ASSERT_EQUAL_UINT(2, g->vertices[1].dist);
    TEST_ASSERT_EQUAL_UINT(1, g->vertices[2].dist);
    free_grafo_raw(g);
}

void test_BuscaDijkstra_usa_enfilera_ordenado(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    reset_dists(g);
    BuscaDijkstra(&g->vertices[0]);
    TEST_ASSERT_GREATER_OR_EQUAL_UINT(1, spy_count_of("enfilera_ordenado"));
    TEST_ASSERT_GREATER_OR_EQUAL_UINT(1, spy_count_of("cria_fila"));
    TEST_ASSERT_GREATER_OR_EQUAL_UINT(1, spy_count_of("destroi_fila"));
    free_grafo_raw(g);
}

void test_BuscaDijkstra_marca_estado_final_dois(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    reset_dists(g);
    BuscaDijkstra(&g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(2, g->vertices[0].estado);
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_BuscaDijkstra_raiz_com_dist_zero);
    RUN_TEST(test_BuscaDijkstra_caminho_simples_3_vertices);
    RUN_TEST(test_BuscaDijkstra_escolhe_caminho_mais_curto);
    RUN_TEST(test_BuscaDijkstra_usa_enfilera_ordenado);
    RUN_TEST(test_BuscaDijkstra_marca_estado_final_dois);
    return UNITY_END();
}
#endif

#endif
