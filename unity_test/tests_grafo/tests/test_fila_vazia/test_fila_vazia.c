#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: int fila_vazia(Fila *f)
 *
 * Função puramente de leitura. Sem nada a mockar.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_fila_vazia_em_fila_recem_criada(void) {
    Fila *f = cria_fila();
    TEST_ASSERT_EQUAL_INT(1, fila_vazia(f));
    free(f);
}

void test_fila_vazia_apos_enfilera_retorna_zero(void) {
    Fila *f = cria_fila();
    Vértice v; memset(&v, 0, sizeof(v));
    enfilera(&v, f);
    TEST_ASSERT_EQUAL_INT(0, fila_vazia(f));
    free(f->fila_head); free(f);
}

void test_fila_vazia_apos_desenfilera_unico_retorna_um(void) {
    Fila *f = cria_fila();
    Vértice v; memset(&v, 0, sizeof(v));
    enfilera(&v, f);
    desenfilera(f);
    TEST_ASSERT_EQUAL_INT(1, fila_vazia(f));
    free(f);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_fila_vazia_em_fila_recem_criada);
    RUN_TEST(test_fila_vazia_apos_enfilera_retorna_zero);
    RUN_TEST(test_fila_vazia_apos_desenfilera_unico_retorna_um);
    return UNITY_END();
}
#endif

#endif
