#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/* Testes para: unsigned int n_vertices(grafo *g) — getter trivial. */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_n_vertices_grafo_vazio_retorna_zero(void) {
    Grafo *g = make_grafo("g");
    TEST_ASSERT_EQUAL_UINT(0, n_vertices(g));
    free_grafo_raw(g);
}

void test_n_vertices_apos_adicionar_um(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    TEST_ASSERT_EQUAL_UINT(1, n_vertices(g));
    free_grafo_raw(g);
}

void test_n_vertices_apos_adicionar_varios(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    TEST_ASSERT_EQUAL_UINT(3, n_vertices(g));
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_n_vertices_grafo_vazio_retorna_zero);
    RUN_TEST(test_n_vertices_apos_adicionar_um);
    RUN_TEST(test_n_vertices_apos_adicionar_varios);
    return UNITY_END();
}
#endif

#endif
