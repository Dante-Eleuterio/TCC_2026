#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: nodo_t *novoNodo(int chave)
 *
 * Contrato (relatorio.pdf):
 *  - Aloca dinamicamente um nodo_t.
 *  - Inicializa chave com o valor recebido.
 *  - esq e dir devem ser NULL.
 *  - altura e fator devem ser zero.
 */

#ifndef ALL_TESTS
void setUp(void)    {}
void tearDown(void) {}
#endif

void test_novoNodo_retorna_ponteiro_nao_nulo(void) {
    nodo_t *n = novoNodo(42);
    TEST_ASSERT_NOT_NULL(n);
    free(n);
}

void test_novoNodo_grava_chave(void) {
    nodo_t *n = novoNodo(123);
    TEST_ASSERT_EQUAL_INT(123, n->chave);
    free(n);
}

void test_novoNodo_filhos_sao_NULL(void) {
    nodo_t *n = novoNodo(1);
    TEST_ASSERT_NULL(n->esq);
    TEST_ASSERT_NULL(n->dir);
    free(n);
}

void test_novoNodo_altura_zero(void) {
    nodo_t *n = novoNodo(1);
    TEST_ASSERT_EQUAL_INT(0, n->altura);
    free(n);
}

void test_novoNodo_fator_zero(void) {
    nodo_t *n = novoNodo(1);
    TEST_ASSERT_EQUAL_INT(0, n->fator);
    free(n);
}

void test_novoNodo_aceita_chave_negativa(void) {
    nodo_t *n = novoNodo(-50);
    TEST_ASSERT_EQUAL_INT(-50, n->chave);
    free(n);
}

void test_novoNodo_aceita_chave_zero(void) {
    nodo_t *n = novoNodo(0);
    TEST_ASSERT_EQUAL_INT(0, n->chave);
    free(n);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_novoNodo_retorna_ponteiro_nao_nulo);
    RUN_TEST(test_novoNodo_grava_chave);
    RUN_TEST(test_novoNodo_filhos_sao_NULL);
    RUN_TEST(test_novoNodo_altura_zero);
    RUN_TEST(test_novoNodo_fator_zero);
    RUN_TEST(test_novoNodo_aceita_chave_negativa);
    RUN_TEST(test_novoNodo_aceita_chave_zero);
    return UNITY_END();
}
#endif

#endif
