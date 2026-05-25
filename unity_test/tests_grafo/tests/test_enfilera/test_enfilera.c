#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: void enfilera(Vértice *v, Fila *f)
 *
 * Função folha (só malloc). Sem mocks de módulo.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

static Vértice make_vert(const char *nome) {
    Vértice v;
    memset(&v, 0, sizeof(v));
    strcpy(v.nome, nome);
    return v;
}

void test_enfilera_em_fila_vazia_head_e_tail_iguais(void) {
    Fila *f = cria_fila();
    Vértice v = make_vert("a");
    enfilera(&v, f);
    TEST_ASSERT_NOT_NULL(f->fila_head);
    TEST_ASSERT_EQUAL_PTR(f->fila_head, f->fila_tail);
    TEST_ASSERT_EQUAL_PTR(&v, f->fila_head->v);
    TEST_ASSERT_NULL(f->fila_head->prox);
    free(f->fila_head); free(f);
}

void test_enfilera_dois_elementos_ordem_FIFO(void) {
    Fila *f = cria_fila();
    Vértice a = make_vert("a"), b = make_vert("b");
    enfilera(&a, f);
    enfilera(&b, f);
    TEST_ASSERT_EQUAL_PTR(&a, f->fila_head->v);
    TEST_ASSERT_EQUAL_PTR(&b, f->fila_head->prox->v);
    TEST_ASSERT_EQUAL_PTR(&b, f->fila_tail->v);
    free(f->fila_head->prox); free(f->fila_head); free(f);
}

void test_enfilera_atualiza_tail_corretamente(void) {
    Fila *f = cria_fila();
    Vértice a = make_vert("a"), b = make_vert("b"), c = make_vert("c");
    enfilera(&a, f);
    enfilera(&b, f);
    enfilera(&c, f);
    TEST_ASSERT_EQUAL_PTR(&c, f->fila_tail->v);
    TEST_ASSERT_NULL(f->fila_tail->prox);
    /* cleanup */
    Nodo *n = f->fila_head;
    while (n) { Nodo *p = n->prox; free(n); n = p; }
    free(f);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_enfilera_em_fila_vazia_head_e_tail_iguais);
    RUN_TEST(test_enfilera_dois_elementos_ordem_FIFO);
    RUN_TEST(test_enfilera_atualiza_tail_corretamente);
    return UNITY_END();
}
#endif

#endif
