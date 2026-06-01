#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: void BuscaLowPoint(grafo *g, Vértice *r)
 *
 * DFS recursivo que computa lowpoints e marca vértices de corte.
 * É chamado por vertices_corte/arestas_corte. Não chama nenhuma outra
 * função do módulo a não ser ela mesma (recursão).
 *
 * Não mockamos a recursão — substituir BuscaLowPoint por uma versão
 * que não recurse esvaziaria o teste. Em vez disso, validamos os
 * estados finais dos vértices em grafos pequenos com cortes
 * conhecidos.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

static void prep(Grafo *g) {
    for (unsigned i = 0; i < g->num_vertices; i++) {
        g->vertices[i].estado   = 0;
        g->vertices[i].pai      = NULL;
        g->vertices[i].lowpoint = 0;
        g->vertices[i].nivel    = 0;
        g->vertices[i].corte    = 0;
    }
}

void test_BuscaLowPoint_unico_vertice_nao_eh_corte(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    prep(g);
    BuscaLowPoint(g, &g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[0].corte);
    TEST_ASSERT_EQUAL_UINT(2, g->vertices[0].estado);
    free_grafo_raw(g);
}

void test_BuscaLowPoint_caminho_3_vertices_meio_eh_corte(void) {
    /* a -- b -- c : b é vértice de corte */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 1));
    prep(g);
    BuscaLowPoint(g, &g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[0].corte);  /* extremidade */
    TEST_ASSERT_EQUAL_UINT(1, g->vertices[1].corte);  /* meio        */
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[2].corte);  /* extremidade */
    free_grafo_raw(g);
}

void test_BuscaLowPoint_ciclo_nao_tem_corte(void) {
    /* a -- b -- c -- a (triângulo) */
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
    prep(g);
    BuscaLowPoint(g, &g->vertices[0]);
    for (unsigned i = 0; i < 3; i++) {
        TEST_ASSERT_EQUAL_UINT(0, g->vertices[i].corte);
    }
    free_grafo_raw(g);
}

void test_BuscaLowPoint_marca_niveis_em_dfs(void) {
    /* a -- b -- c (a é raiz; b nível 1; c nível 2) */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 1));
    prep(g);
    BuscaLowPoint(g, &g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[0].nivel);
    TEST_ASSERT_EQUAL_UINT(1, g->vertices[1].nivel);
    TEST_ASSERT_EQUAL_UINT(2, g->vertices[2].nivel);
    free_grafo_raw(g);
}

void test_BuscaLowPoint_raiz_com_dois_filhos_eh_corte(void) {
    /* b -- a -- c (a é raiz com 2 filhos: corte) */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[0], 1));
    prep(g);
    BuscaLowPoint(g, &g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(1, g->vertices[0].corte);
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_BuscaLowPoint_unico_vertice_nao_eh_corte);
    RUN_TEST(test_BuscaLowPoint_caminho_3_vertices_meio_eh_corte);
    RUN_TEST(test_BuscaLowPoint_ciclo_nao_tem_corte);
    RUN_TEST(test_BuscaLowPoint_marca_niveis_em_dfs);
    RUN_TEST(test_BuscaLowPoint_raiz_com_dois_filhos_eh_corte);
    return UNITY_END();
}
#endif

#endif
