#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: nodo_t *rotDir(nodo_t *nodo)
 *
 * Rotação à direita.
 */

#ifndef ALL_TESTS
void setUp(void)    {}
void tearDown(void) {}
#endif

void test_rotDir_caso_simples_3_nodos(void) {
    nodo_t *t1 = novoNodo(10);
    nodo_t *a  = novoNodo(20);
    nodo_t *b  = novoNodo(30);
    a->esq = t1;
    b->esq = a;
    atualizaAltura(a);
    atualizaAltura(b);

    nodo_t *r = rotDir(b);

    TEST_ASSERT_EQUAL_PTR(a, r);
    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_PTR(t1, r->esq);
    TEST_ASSERT_EQUAL_PTR(b,  r->dir);
    TEST_ASSERT_EQUAL_INT(0, t1->altura);
    TEST_ASSERT_EQUAL_INT(0, b->altura);
    TEST_ASSERT_EQUAL_INT(1, a->altura);
    free(t1); free(a); free(b);
}

void test_rotDir_preserva_subarvore_T2(void) {
    nodo_t *t1 = novoNodo(10);
    nodo_t *t2 = novoNodo(25);
    nodo_t *a  = novoNodo(20);
    nodo_t *b  = novoNodo(30);
    a->esq = t1; a->dir = t2;
    b->esq = a;
    atualizaAltura(a);
    atualizaAltura(b);

    nodo_t *r = rotDir(b);

    TEST_ASSERT_EQUAL_PTR(a, r);
    TEST_ASSERT_EQUAL_PTR(b, a->dir);
    TEST_ASSERT_EQUAL_PTR(t2, b->esq);
    TEST_ASSERT_NULL(b->dir);
    TEST_ASSERT_EQUAL_PTR(t1, a->esq);
    free(t1); free(t2); free(a); free(b);
}

void test_rotDir_chaves_mantem_propriedade_BST(void) {
    nodo_t *t1 = novoNodo(10);
    nodo_t *t2 = novoNodo(25);
    nodo_t *a  = novoNodo(20);
    nodo_t *b  = novoNodo(30);
    a->esq = t1; a->dir = t2;
    b->esq = a;
    atualizaAltura(a);
    atualizaAltura(b);

    nodo_t *r = rotDir(b);

    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    TEST_ASSERT_EQUAL_INT(25, r->dir->esq->chave);
    free(t1); free(t2); free(a); free(b);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_rotDir_caso_simples_3_nodos);
    RUN_TEST(test_rotDir_preserva_subarvore_T2);
    RUN_TEST(test_rotDir_chaves_mantem_propriedade_BST);
    return UNITY_END();
}
#endif

#endif
