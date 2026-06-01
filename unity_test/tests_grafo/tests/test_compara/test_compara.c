#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: int compara(const void *a, const void *b)
 *
 * Comparador para qsort de inteiros. Função pura — nada a mockar.
 *
 * Atenção: o código faz `*(int*)a - *(int*)b`, mas é usado em
 * qsort sobre `unsigned int`. O sinal vem de uma subtração entre
 * dois ints reinterpretados, então testamos com valores que cabem
 * em int normal.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_compara_a_maior_retorna_positivo(void) {
    int a = 10, b = 3;
    TEST_ASSERT_TRUE(compara(&a, &b) > 0);
}

void test_compara_b_maior_retorna_negativo(void) {
    int a = 3, b = 10;
    TEST_ASSERT_TRUE(compara(&a, &b) < 0);
}

void test_compara_iguais_retorna_zero(void) {
    int a = 7, b = 7;
    TEST_ASSERT_EQUAL_INT(0, compara(&a, &b));
}

void test_compara_com_zero(void) {
    int a = 0, b = 5;
    TEST_ASSERT_TRUE(compara(&a, &b) < 0);
    TEST_ASSERT_TRUE(compara(&b, &a) > 0);
}

void test_compara_funciona_para_qsort(void) {
    int v[] = {5, 2, 9, 1, 7, 3};
    qsort(v, 6, sizeof(int), compara);
    int esp[] = {1, 2, 3, 5, 7, 9};
    for (int i = 0; i < 6; i++) {
        TEST_ASSERT_EQUAL_INT(esp[i], v[i]);
    }
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_compara_a_maior_retorna_positivo);
    RUN_TEST(test_compara_b_maior_retorna_negativo);
    RUN_TEST(test_compara_iguais_retorna_zero);
    RUN_TEST(test_compara_com_zero);
    RUN_TEST(test_compara_funciona_para_qsort);
    return UNITY_END();
}
#endif

#endif
