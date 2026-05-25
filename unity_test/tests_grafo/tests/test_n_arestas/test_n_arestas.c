#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/* Testes para: unsigned int n_arestas(grafo *g) — getter trivial. */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_n_arestas_grafo_sem_arestas_retorna_zero(void) {
    Grafo *g = make_grafo("g");
    TEST_ASSERT_EQUAL_UINT(0, n_arestas(g));
    free_grafo_raw(g);
}

void test_n_arestas_apos_adicionar_uma(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    char o[] = "a"; char d[] = "b";
    adiciona_aresta(g, o, d, 1);
    TEST_ASSERT_EQUAL_UINT(1, n_arestas(g));
    free_grafo_raw(g);
}

void test_n_arestas_apos_adicionar_varias(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    char o1[] = "a", d1[] = "b";
    char o2[] = "b", d2[] = "c";
    char o3[] = "a", d3[] = "c";
    adiciona_aresta(g, o1, d1, 1);
    adiciona_aresta(g, o2, d2, 1);
    adiciona_aresta(g, o3, d3, 1);
    TEST_ASSERT_EQUAL_UINT(3, n_arestas(g));
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_n_arestas_grafo_sem_arestas_retorna_zero);
    RUN_TEST(test_n_arestas_apos_adicionar_uma);
    RUN_TEST(test_n_arestas_apos_adicionar_varias);
    return UNITY_END();
}
#endif

#endif
