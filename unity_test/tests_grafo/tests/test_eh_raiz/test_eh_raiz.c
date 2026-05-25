#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: int eh_raiz(Vértice *v)
 *
 * Função pura: 1 se v->pai == NULL, 0 caso contrário.
 *
 * Nota: a função está declarada no código mas, da forma como
 * implementada, nunca é chamada por outras funções do módulo
 * (vertices_corte usa a checagem inline `r->pai == NULL`). Os testes
 * abaixo cobrem o contrato declarado.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_eh_raiz_pai_NULL_retorna_um(void) {
    Vértice v; memset(&v, 0, sizeof(v));
    v.pai = NULL;
    TEST_ASSERT_EQUAL_INT(1, eh_raiz(&v));
}

void test_eh_raiz_com_pai_retorna_zero(void) {
    Vértice v, p;
    memset(&v, 0, sizeof(v));
    memset(&p, 0, sizeof(p));
    v.pai = &p;
    TEST_ASSERT_EQUAL_INT(0, eh_raiz(&v));
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_eh_raiz_pai_NULL_retorna_um);
    RUN_TEST(test_eh_raiz_com_pai_retorna_zero);
    return UNITY_END();
}
#endif

#endif
