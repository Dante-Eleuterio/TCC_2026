#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: nodo_t *rotEsqDir(nodo_t *nodo)
 */

#ifndef ALL_TESTS
void setUp(void)    {}
void tearDown(void) {}
#endif

void test_rotEsqDir_3_nodos(void) {
    nodo_t *a = novoNodo(10);
    nodo_t *b = novoNodo(20);
    nodo_t *c = novoNodo(30);
    a->dir = b;
    c->esq = a;
    atualizaAltura(b);
    atualizaAltura(a);
    atualizaAltura(c);

    nodo_t *r = rotEsqDir(c);

    TEST_ASSERT_EQUAL_PTR(b, r);
    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_PTR(a, r->esq);
    TEST_ASSERT_EQUAL_PTR(c, r->dir);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    free(a); free(b); free(c);
}

void test_rotEsqDir_preserva_em_ordem(void) {
    nodo_t *a = novoNodo(10);
    nodo_t *b = novoNodo(20);
    nodo_t *c = novoNodo(30);
    a->dir = b;
    c->esq = a;
    atualizaAltura(b);
    atualizaAltura(a);
    atualizaAltura(c);

    nodo_t *r = rotEsqDir(c);

    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    TEST_ASSERT_NULL(r->esq->esq);
    TEST_ASSERT_NULL(r->esq->dir);
    TEST_ASSERT_NULL(r->dir->esq);
    TEST_ASSERT_NULL(r->dir->dir);
    free(a); free(b); free(c);
}

void test_rotEsqDir_altera_alturas_corretamente(void) {
    nodo_t *a = novoNodo(10);
    nodo_t *b = novoNodo(20);
    nodo_t *c = novoNodo(30);
    a->dir = b;
    c->esq = a;
    atualizaAltura(b);
    atualizaAltura(a);
    atualizaAltura(c);

    nodo_t *r = rotEsqDir(c);

    TEST_ASSERT_EQUAL_INT(1, r->altura);
    TEST_ASSERT_EQUAL_INT(0, r->esq->altura);
    TEST_ASSERT_EQUAL_INT(0, r->dir->altura);
    TEST_ASSERT_EQUAL_INT(0, r->fator);
    free(a); free(b); free(c);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_rotEsqDir_3_nodos);
    RUN_TEST(test_rotEsqDir_preserva_em_ordem);
    RUN_TEST(test_rotEsqDir_altera_alturas_corretamente);
    return UNITY_END();
}
#endif

#endif
