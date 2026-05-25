#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: Vértice *desenfilera(Fila *f)
 *
 * Função folha — só free. Sem mocks de módulo.
 *
 * Observação: desenfilera de fila vazia derreferencia NULL no código
 * atual (não há proteção). Não testamos esse caminho porque o
 * comportamento é "segfault", não algo a validar via TEST_ASSERT.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_desenfilera_retira_unico_elemento(void) {
    Fila *f = cria_fila();
    Vértice v; memset(&v, 0, sizeof(v));
    enfilera(&v, f);
    Vértice *out = desenfilera(f);
    TEST_ASSERT_EQUAL_PTR(&v, out);
    TEST_ASSERT_NULL(f->fila_head);
    free(f);
}

void test_desenfilera_FIFO_dois_elementos(void) {
    Fila *f = cria_fila();
    Vértice a, b;
    memset(&a, 0, sizeof(a)); memset(&b, 0, sizeof(b));
    enfilera(&a, f);
    enfilera(&b, f);
    Vértice *o1 = desenfilera(f);
    Vértice *o2 = desenfilera(f);
    TEST_ASSERT_EQUAL_PTR(&a, o1);
    TEST_ASSERT_EQUAL_PTR(&b, o2);
    free(f);
}

void test_desenfilera_atualiza_head(void) {
    Fila *f = cria_fila();
    Vértice a, b;
    memset(&a, 0, sizeof(a)); memset(&b, 0, sizeof(b));
    enfilera(&a, f);
    enfilera(&b, f);
    desenfilera(f);
    TEST_ASSERT_NOT_NULL(f->fila_head);
    TEST_ASSERT_EQUAL_PTR(&b, f->fila_head->v);
    /* cleanup */
    free(f->fila_head); free(f);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_desenfilera_retira_unico_elemento);
    RUN_TEST(test_desenfilera_FIFO_dois_elementos);
    RUN_TEST(test_desenfilera_atualiza_head);
    return UNITY_END();
}
#endif

#endif
