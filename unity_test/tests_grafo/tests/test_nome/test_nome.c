#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/* Testes para: char *nome(grafo *g) — getter trivial. */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_nome_retorna_string_correta(void) {
    Grafo *g = make_grafo("meu_grafo");
    TEST_ASSERT_EQUAL_STRING("meu_grafo", nome(g));
    free_grafo_raw(g);
}

void test_nome_retorna_string_vazia_para_grafo_sem_nome(void) {
    Grafo *g = make_grafo("");
    TEST_ASSERT_EQUAL_STRING("", nome(g));
    free_grafo_raw(g);
}

void test_nome_retorna_ponteiro_interno(void) {
    /* O contrato é "devolve o nome de g" — verificamos que aponta
     * para dentro do struct, não para uma cópia.                 */
    Grafo *g = make_grafo("xyz");
    char *p = nome(g);
    TEST_ASSERT_EQUAL_PTR((char*)g->nome, p);
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_nome_retorna_string_correta);
    RUN_TEST(test_nome_retorna_string_vazia_para_grafo_sem_nome);
    RUN_TEST(test_nome_retorna_ponteiro_interno);
    return UNITY_END();
}
#endif

#endif
