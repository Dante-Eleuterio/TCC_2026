#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: void adiciona_aresta(grafo *g, char *origem,
 *                                   char *destino, unsigned int peso)
 *
 * adiciona_aresta chama procura_vertice() duas vezes. Usamos o mock
 * centralizado de procura_vertice (g_pv_*) para testar o ramo de
 * "vértice inexistente" sem depender da implementação real.
 *
 * Não mockamos malloc: o grafo.c não trata malloc==NULL, logo não há
 * comportamento alternativo a validar. Mockar libc só agrega ruído.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_adiciona_aresta_origem_inexistente_nao_altera_grafo(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");

    g_pv_mock_on = 1;
    g_pv_ret_seq[0] = -1;  /* origem inexistente */
    g_pv_ret_seq[1] =  1;
    g_pv_ret_seq_len = 2;

    char o[] = "a"; char d[] = "b";
    adiciona_aresta(g, o, d, 5);

    TEST_ASSERT_EQUAL_UINT(0, g->num_arestas);
    TEST_ASSERT_NULL(g->vertices[0].arestas_head);
    TEST_ASSERT_NULL(g->vertices[1].arestas_head);
    free_grafo_raw(g);
}

void test_adiciona_aresta_destino_inexistente_nao_altera_grafo(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");

    g_pv_mock_on = 1;
    g_pv_ret_seq[0] =  0;
    g_pv_ret_seq[1] = -1;  /* destino inexistente */
    g_pv_ret_seq_len = 2;

    char o[] = "a"; char d[] = "z";
    adiciona_aresta(g, o, d, 5);

    TEST_ASSERT_EQUAL_UINT(0, g->num_arestas);
    free_grafo_raw(g);
}

void test_adiciona_aresta_chama_procura_vertice_duas_vezes(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");

    char o[] = "a"; char d[] = "b";
    adiciona_aresta(g, o, d, 7);

    /* Em modo passthrough, procura_vertice real roda mas o spy
     * mesmo assim registra cada chamada.                          */
    TEST_ASSERT_EQUAL_UINT(2, spy_count_of("procura_vertice"));
    free_grafo_raw(g);
}

void test_adiciona_aresta_cria_aresta_origem_destino(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");

    char o[] = "a"; char d[] = "b";
    adiciona_aresta(g, o, d, 7);

    Aresta *h = g->vertices[0].arestas_head;
    TEST_ASSERT_NOT_NULL(h);
    TEST_ASSERT_EQUAL_PTR(&g->vertices[1], h->destino);
    TEST_ASSERT_EQUAL_UINT(7, h->peso);
    TEST_ASSERT_NULL(h->prox);
    free_grafo_raw(g);
}

void test_adiciona_aresta_eh_bidirecional(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");

    char o[] = "a"; char d[] = "b";
    adiciona_aresta(g, o, d, 3);

    Aresta *h0 = g->vertices[0].arestas_head;
    TEST_ASSERT_NOT_NULL(h0);
    TEST_ASSERT_EQUAL_PTR(&g->vertices[1], h0->destino);

    Aresta *h1 = g->vertices[1].arestas_head;
    TEST_ASSERT_NOT_NULL(h1);
    TEST_ASSERT_EQUAL_PTR(&g->vertices[0], h1->destino);
    TEST_ASSERT_EQUAL_UINT(3, h1->peso);
    free_grafo_raw(g);
}

void test_adiciona_aresta_incrementa_num_arestas_apenas_uma_vez(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");

    char o[] = "a"; char d[] = "b";
    adiciona_aresta(g, o, d, 1);

    TEST_ASSERT_EQUAL_UINT(1, g->num_arestas);
    free_grafo_raw(g);
}

void test_adiciona_aresta_anexa_no_tail_quando_ja_existe(void) {
    mocks_reset_all();
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");

    char o1[] = "a"; char d1[] = "b";
    adiciona_aresta(g, o1, d1, 1);

    char o2[] = "a"; char d2[] = "c";
    adiciona_aresta(g, o2, d2, 9);

    Aresta *h = g->vertices[0].arestas_head;
    TEST_ASSERT_NOT_NULL(h);
    TEST_ASSERT_EQUAL_PTR(&g->vertices[1], h->destino);
    TEST_ASSERT_NOT_NULL(h->prox);
    TEST_ASSERT_EQUAL_PTR(&g->vertices[2], h->prox->destino);
    TEST_ASSERT_EQUAL_UINT(9, h->prox->peso);
    TEST_ASSERT_EQUAL_PTR(h->prox, g->vertices[0].arestas_tail);
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_adiciona_aresta_origem_inexistente_nao_altera_grafo);
    RUN_TEST(test_adiciona_aresta_destino_inexistente_nao_altera_grafo);
    RUN_TEST(test_adiciona_aresta_chama_procura_vertice_duas_vezes);
    RUN_TEST(test_adiciona_aresta_cria_aresta_origem_destino);
    RUN_TEST(test_adiciona_aresta_eh_bidirecional);
    RUN_TEST(test_adiciona_aresta_incrementa_num_arestas_apenas_uma_vez);
    RUN_TEST(test_adiciona_aresta_anexa_no_tail_quando_ja_existe);
    return UNITY_END();
}
#endif

#endif
