#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: nodo_t *rotDirEsq(nodo_t *nodo)
 */

#ifndef ALL_TESTS
void setUp(void)    {}
void tearDown(void) {}
#endif

void test_rotDirEsq_3_nodos(void) {
    nodo_t *a = novoNodo(10);
    nodo_t *b = novoNodo(20);
    nodo_t *c = novoNodo(30);
    c->esq = b;
    a->dir = c;
    atualizaAltura(b);
    atualizaAltura(c);
    atualizaAltura(a);

    nodo_t *r = rotDirEsq(a);

    TEST_ASSERT_EQUAL_PTR(b, r);
    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_PTR(a, r->esq);
    TEST_ASSERT_EQUAL_PTR(c, r->dir);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    free(a); free(b); free(c);
}

void test_rotDirEsq_em_ordem_preservada(void) {
    nodo_t *a = novoNodo(10);
    nodo_t *b = novoNodo(20);
    nodo_t *c = novoNodo(30);
    c->esq = b;
    a->dir = c;
    atualizaAltura(b);
    atualizaAltura(c);
    atualizaAltura(a);

    nodo_t *r = rotDirEsq(a);

    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    TEST_ASSERT_NULL(r->esq->esq);
    TEST_ASSERT_NULL(r->esq->dir);
    TEST_ASSERT_NULL(r->dir->esq);
    TEST_ASSERT_NULL(r->dir->dir);
    free(a); free(b); free(c);
}

void test_rotDirEsq_alturas_corretas(void) {
    nodo_t *a = novoNodo(10);
    nodo_t *b = novoNodo(20);
    nodo_t *c = novoNodo(30);
    c->esq = b;
    a->dir = c;
    atualizaAltura(b);
    atualizaAltura(c);
    atualizaAltura(a);

    nodo_t *r = rotDirEsq(a);

    TEST_ASSERT_EQUAL_INT(1, r->altura);
    TEST_ASSERT_EQUAL_INT(0, r->esq->altura);
    TEST_ASSERT_EQUAL_INT(0, r->dir->altura);
    TEST_ASSERT_EQUAL_INT(0, r->fator);
    free(a); free(b); free(c);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_rotDirEsq_3_nodos);
    RUN_TEST(test_rotDirEsq_em_ordem_preservada);
    RUN_TEST(test_rotDirEsq_alturas_corretas);
    return UNITY_END();
}
#endif

#endif
