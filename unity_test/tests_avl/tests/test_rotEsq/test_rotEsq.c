#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: nodo_t *rotEsq(nodo_t *nodo)
 */

#ifndef ALL_TESTS
void setUp(void)    {}
void tearDown(void) {}
#endif

void test_rotEsq_caso_simples_3_nodos(void) {
    nodo_t *t3 = novoNodo(30);
    nodo_t *b  = novoNodo(20);
    nodo_t *a  = novoNodo(10);
    b->dir = t3;
    a->dir = b;
    atualizaAltura(b);
    atualizaAltura(a);

    nodo_t *r = rotEsq(a);

    TEST_ASSERT_EQUAL_PTR(b, r);
    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_PTR(a,  r->esq);
    TEST_ASSERT_EQUAL_PTR(t3, r->dir);
    TEST_ASSERT_EQUAL_INT(0, t3->altura);
    TEST_ASSERT_EQUAL_INT(0, a->altura);
    TEST_ASSERT_EQUAL_INT(1, b->altura);
    free(t3); free(b); free(a);
}

void test_rotEsq_preserva_subarvore_T2(void) {
    nodo_t *t2 = novoNodo(15);
    nodo_t *t3 = novoNodo(30);
    nodo_t *b  = novoNodo(20);
    nodo_t *a  = novoNodo(10);
    b->esq = t2; b->dir = t3;
    a->dir = b;
    atualizaAltura(b);
    atualizaAltura(a);

    nodo_t *r = rotEsq(a);

    TEST_ASSERT_EQUAL_PTR(b, r);
    TEST_ASSERT_EQUAL_PTR(a,  b->esq);
    TEST_ASSERT_EQUAL_PTR(t3, b->dir);
    TEST_ASSERT_EQUAL_PTR(t2, a->dir);
    TEST_ASSERT_NULL(a->esq);
    free(t2); free(t3); free(b); free(a);
}

void test_rotEsq_chaves_mantem_BST(void) {
    nodo_t *t2 = novoNodo(15);
    nodo_t *t3 = novoNodo(30);
    nodo_t *b  = novoNodo(20);
    nodo_t *a  = novoNodo(10);
    b->esq = t2; b->dir = t3;
    a->dir = b;
    atualizaAltura(b);
    atualizaAltura(a);

    nodo_t *r = rotEsq(a);

    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    TEST_ASSERT_EQUAL_INT(15, r->esq->dir->chave);
    free(t2); free(t3); free(b); free(a);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_rotEsq_caso_simples_3_nodos);
    RUN_TEST(test_rotEsq_preserva_subarvore_T2);
    RUN_TEST(test_rotEsq_chaves_mantem_BST);
    return UNITY_END();
}
#endif

#endif
