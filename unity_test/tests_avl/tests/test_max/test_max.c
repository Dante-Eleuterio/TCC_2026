#ifdef TEST

#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: int max(int a, int b)
 *
 * Contrato:
 *  - Retorna o maior dos dois inteiros.
 *  - Empate: retorna esse mesmo valor.
 */

#ifndef ALL_TESTS
void setUp(void)    {}
void tearDown(void) {}
#endif

void test_max_primeiro_maior(void) {
    TEST_ASSERT_EQUAL_INT(5, max(5, 3));
}

void test_max_segundo_maior(void) {
    TEST_ASSERT_EQUAL_INT(7, max(2, 7));
}

void test_max_iguais(void) {
    TEST_ASSERT_EQUAL_INT(4, max(4, 4));
}

void test_max_com_zero(void) {
    TEST_ASSERT_EQUAL_INT(0, max(0, -1));
    TEST_ASSERT_EQUAL_INT(1, max(0, 1));
}

void test_max_com_negativos(void) {
    TEST_ASSERT_EQUAL_INT(-1, max(-1, -5));
    TEST_ASSERT_EQUAL_INT(-3, max(-10, -3));
}

void test_max_misto_positivo_negativo(void) {
    TEST_ASSERT_EQUAL_INT(10, max(-100, 10));
    TEST_ASSERT_EQUAL_INT(10, max(10, -100));
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_max_primeiro_maior);
    RUN_TEST(test_max_segundo_maior);
    RUN_TEST(test_max_iguais);
    RUN_TEST(test_max_com_zero);
    RUN_TEST(test_max_com_negativos);
    RUN_TEST(test_max_misto_positivo_negativo);
    return UNITY_END();
}
#endif

#endif
