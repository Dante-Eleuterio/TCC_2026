#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: Fila *cria_fila(void)
 *
 * Função folha — só chama malloc. Não mockamos malloc porque o código
 * de produção não checa retorno (qualquer cenário de NULL geraria
 * SEGV, não um caminho a validar).
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_cria_fila_retorna_ponteiro_nao_nulo(void) {
    Fila *f = cria_fila();
    TEST_ASSERT_NOT_NULL(f);
    free(f);
}

void test_cria_fila_head_e_tail_iniciam_NULL(void) {
    Fila *f = cria_fila();
    TEST_ASSERT_NULL(f->fila_head);
    TEST_ASSERT_NULL(f->fila_tail);
    free(f);
}

void test_cria_fila_aloca_inst_independentes(void) {
    Fila *a = cria_fila();
    Fila *b = cria_fila();
    TEST_ASSERT_NOT_EQUAL(a, b);
    free(a); free(b);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_cria_fila_retorna_ponteiro_nao_nulo);
    RUN_TEST(test_cria_fila_head_e_tail_iniciam_NULL);
    RUN_TEST(test_cria_fila_aloca_inst_independentes);
    return UNITY_END();
}
#endif

#endif
