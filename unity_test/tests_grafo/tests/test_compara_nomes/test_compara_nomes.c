#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: int compara_nomes(const void *a, const void *b)
 *
 * Recebe ponteiros para char* (`*(char**)a`). Chama strcmp internamente.
 * Não mockamos strcmp (libc).
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_compara_nomes_iguais_retorna_zero(void) {
    char s[] = "alpha";
    char *pa = s, *pb = s;
    TEST_ASSERT_EQUAL_INT(0, compara_nomes(&pa, &pb));
}

void test_compara_nomes_alfabetico_a_antes_b(void) {
    char s1[] = "abc", s2[] = "xyz";
    char *pa = s1, *pb = s2;
    TEST_ASSERT_TRUE(compara_nomes(&pa, &pb) < 0);
}

void test_compara_nomes_alfabetico_b_antes_a(void) {
    char s1[] = "xyz", s2[] = "abc";
    char *pa = s1, *pb = s2;
    TEST_ASSERT_TRUE(compara_nomes(&pa, &pb) > 0);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_compara_nomes_iguais_retorna_zero);
    RUN_TEST(test_compara_nomes_alfabetico_a_antes_b);
    RUN_TEST(test_compara_nomes_alfabetico_b_antes_a);
    return UNITY_END();
}
#endif

#endif
