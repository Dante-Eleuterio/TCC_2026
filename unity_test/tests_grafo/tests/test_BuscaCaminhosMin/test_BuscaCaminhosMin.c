#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: void BuscaCaminhosMin(Vértice *r)
 *
 * BFS canônica. Usa: cria_fila, enfilera, desenfilera, fila_vazia,
 * destroi_fila. Todos com spy ativo em passthrough.
 *
 * Estratégia: construímos um pequeno grafo manualmente, chamamos a
 * busca e verificamos os efeitos colaterais nos vértices (dist, pai,
 * estado, componente). Em paralelo, asserts sobre o spy garantem que a
 * fila foi de fato usada (cria_fila >=1, destroi_fila >=1).
 *
 * Não mockamos as funções de fila aqui — substituí-las quebraria a BFS
 * inteira e o teste passaria a validar "nada". Spies passthrough já
 * dão a observabilidade de interação.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

/* Helper: monta um grafo a-b-c-d (caminho linear) */
static Grafo *build_path_abcd(void) {
    Grafo *g = make_grafo("g");
    unsigned ia = helper_push_vertice(g, "a");
    unsigned ib = helper_push_vertice(g, "b");
    unsigned ic = helper_push_vertice(g, "c");
    unsigned id = helper_push_vertice(g, "d");
    helper_append_aresta(&g->vertices[ia], helper_make_aresta(&g->vertices[ib], 1));
    helper_append_aresta(&g->vertices[ib], helper_make_aresta(&g->vertices[ia], 1));
    helper_append_aresta(&g->vertices[ib], helper_make_aresta(&g->vertices[ic], 1));
    helper_append_aresta(&g->vertices[ic], helper_make_aresta(&g->vertices[ib], 1));
    helper_append_aresta(&g->vertices[ic], helper_make_aresta(&g->vertices[id], 1));
    helper_append_aresta(&g->vertices[id], helper_make_aresta(&g->vertices[ic], 1));
    return g;
}

void test_BuscaCaminhosMin_marca_raiz_como_visitada(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    BuscaCaminhosMin(&g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(2, g->vertices[0].estado);  /* finalizada  */
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[0].dist);
    free_grafo_raw(g);
}

void test_BuscaCaminhosMin_distancia_correta_em_caminho(void) {
    Grafo *g = build_path_abcd();
    BuscaCaminhosMin(&g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[0].dist);
    TEST_ASSERT_EQUAL_UINT(1, g->vertices[1].dist);
    TEST_ASSERT_EQUAL_UINT(2, g->vertices[2].dist);
    TEST_ASSERT_EQUAL_UINT(3, g->vertices[3].dist);
    free_grafo_raw(g);
}

void test_BuscaCaminhosMin_pai_aponta_para_predecessor(void) {
    Grafo *g = build_path_abcd();
    BuscaCaminhosMin(&g->vertices[0]);
    TEST_ASSERT_NULL(g->vertices[0].pai);
    TEST_ASSERT_EQUAL_PTR(&g->vertices[0], g->vertices[1].pai);
    TEST_ASSERT_EQUAL_PTR(&g->vertices[1], g->vertices[2].pai);
    TEST_ASSERT_EQUAL_PTR(&g->vertices[2], g->vertices[3].pai);
    free_grafo_raw(g);
}

void test_BuscaCaminhosMin_propaga_componente(void) {
    Grafo *g = build_path_abcd();
    g->vertices[0].componente = 42;
    BuscaCaminhosMin(&g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(42, g->vertices[1].componente);
    TEST_ASSERT_EQUAL_UINT(42, g->vertices[2].componente);
    TEST_ASSERT_EQUAL_UINT(42, g->vertices[3].componente);
    free_grafo_raw(g);
}

void test_BuscaCaminhosMin_usa_a_fila(void) {
    /* Verifica interação com colaboradores via spy.            */
    Grafo *g = build_path_abcd();
    BuscaCaminhosMin(&g->vertices[0]);
    TEST_ASSERT_GREATER_OR_EQUAL_UINT(1, spy_count_of("cria_fila"));
    TEST_ASSERT_GREATER_OR_EQUAL_UINT(1, spy_count_of("destroi_fila"));
    TEST_ASSERT_GREATER_OR_EQUAL_UINT(4, spy_count_of("enfilera"));
    free_grafo_raw(g);
}

void test_BuscaCaminhosMin_nao_visita_componente_separada(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    /* Liga só a-b. c fica isolado. */
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));

    BuscaCaminhosMin(&g->vertices[0]);
    TEST_ASSERT_EQUAL_UINT(2, g->vertices[0].estado);
    TEST_ASSERT_EQUAL_UINT(2, g->vertices[1].estado);
    TEST_ASSERT_EQUAL_UINT(0, g->vertices[2].estado);   /* não visitado */
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_BuscaCaminhosMin_marca_raiz_como_visitada);
    RUN_TEST(test_BuscaCaminhosMin_distancia_correta_em_caminho);
    RUN_TEST(test_BuscaCaminhosMin_pai_aponta_para_predecessor);
    RUN_TEST(test_BuscaCaminhosMin_propaga_componente);
    RUN_TEST(test_BuscaCaminhosMin_usa_a_fila);
    RUN_TEST(test_BuscaCaminhosMin_nao_visita_componente_separada);
    return UNITY_END();
}
#endif

#endif
