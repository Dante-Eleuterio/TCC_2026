#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: char *vertices_corte(grafo *g)
 *
 * Chama BuscaLowPoint e qsort. Note que o código original passa
 * `strcmp` direto para qsort sobre `char[N]` — funciona porque
 * `char[N]` decai para `char*`, mas é não-portável. Os testes
 * verificam apenas o *contrato* (string com nomes em ordem
 * alfabética).
 *
 * Edge case: vertices_corte aloca `nomes[g->num_arestas][MAX_CHARS]`.
 * Em grafos com num_arestas==0 isso é um VLA de tamanho 0 (UB em C
 * estrito, mas aceito por GCC/clang). Os testes evitam esse cenário —
 * ou seja, sempre há ao menos uma aresta nos grafos de teste.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_vertices_corte_caminho_3_vertices_meio_eh_corte(void) {
    /* a -- b -- c : b é vértice de corte */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 1));
    g->num_arestas = 2;
    char *c = vertices_corte(g);
    TEST_ASSERT_EQUAL_STRING("b", c);
    free(c);
    free_grafo_raw(g);
}

void test_vertices_corte_sem_cortes_retorna_vazio(void) {
    /* Triângulo: nenhum vértice de corte */
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
    char *c = vertices_corte(g);
    TEST_ASSERT_EQUAL_STRING("", c);
    free(c);
    free_grafo_raw(g);
}

void test_vertices_corte_multiplos_em_ordem_alfabetica(void) {
    /* x -- b -- a -- c -- y
     * b, a e c são cortes; nomes orden. alfabética: "a b c"
     */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "x");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "c");
    helper_push_vertice(g, "y");
    /* x--b */
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    /* b--a */
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[2], 1));
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[1], 1));
    /* a--c */
    helper_append_aresta(&g->vertices[2], helper_make_aresta(&g->vertices[3], 1));
    helper_append_aresta(&g->vertices[3], helper_make_aresta(&g->vertices[2], 1));
    /* c--y */
    helper_append_aresta(&g->vertices[3], helper_make_aresta(&g->vertices[4], 1));
    helper_append_aresta(&g->vertices[4], helper_make_aresta(&g->vertices[3], 1));
    g->num_arestas = 4;
    char *c = vertices_corte(g);
    TEST_ASSERT_EQUAL_STRING("a b c", c);
    free(c);
    free_grafo_raw(g);
}

void test_vertices_corte_chama_BuscaLowPoint(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_append_aresta(&g->vertices[0], helper_make_aresta(&g->vertices[1], 1));
    helper_append_aresta(&g->vertices[1], helper_make_aresta(&g->vertices[0], 1));
    g->num_arestas = 1;
    char *c = vertices_corte(g);
    TEST_ASSERT_GREATER_OR_EQUAL_UINT(1, spy_count_of("BuscaLowPoint"));
    free(c);
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_vertices_corte_caminho_3_vertices_meio_eh_corte);
    RUN_TEST(test_vertices_corte_sem_cortes_retorna_vazio);
    RUN_TEST(test_vertices_corte_multiplos_em_ordem_alfabetica);
    RUN_TEST(test_vertices_corte_chama_BuscaLowPoint);
    return UNITY_END();
}
#endif

#endif
