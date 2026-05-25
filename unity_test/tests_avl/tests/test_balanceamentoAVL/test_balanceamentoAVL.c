#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: nodo_t *balanceamentoAVL(nodo_t *nodo)
 */

#ifndef ALL_TESTS
void setUp(void)    {}
void tearDown(void) {}
#endif

/* Helper compartilhado por múltiplos arquivos de teste; guard evita
 * redefinição quando test_all.c inclui vários ao mesmo tempo. */
#ifndef AVL_TESTS_HELPER_LIBERAARVORE
#define AVL_TESTS_HELPER_LIBERAARVORE
static void liberaArvore(nodo_t *n) {
    if (n == NULL) return;
    liberaArvore(n->esq);
    liberaArvore(n->dir);
    free(n);
}
#endif

void test_balanceamentoAVL_balanceado_retorna_proprio(void) {
    nodo_t *n = novoNodo(10);
    atualizaAltura(n);
    nodo_t *r = balanceamentoAVL(n);
    TEST_ASSERT_EQUAL_PTR(n, r);
    liberaArvore(r);
}

void test_balanceamentoAVL_caso_EsqEsq_usa_rotDir(void) {
    nodo_t *t1 = novoNodo(10);
    nodo_t *a  = novoNodo(20);
    nodo_t *b  = novoNodo(30);
    a->esq = t1;
    b->esq = a;
    atualizaAltura(a);
    atualizaAltura(b);
    TEST_ASSERT_EQUAL_INT(2, b->fator);
    TEST_ASSERT_EQUAL_INT(1, a->fator);

    nodo_t *r = balanceamentoAVL(b);

    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    liberaArvore(r);
}

void test_balanceamentoAVL_caso_DirDir_usa_rotEsq(void) {
    nodo_t *a  = novoNodo(10);
    nodo_t *b  = novoNodo(20);
    nodo_t *t3 = novoNodo(30);
    b->dir = t3;
    a->dir = b;
    atualizaAltura(b);
    atualizaAltura(a);
    TEST_ASSERT_EQUAL_INT(-2, a->fator);
    TEST_ASSERT_EQUAL_INT(-1, b->fator);

    nodo_t *r = balanceamentoAVL(a);

    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    liberaArvore(r);
}

void test_balanceamentoAVL_caso_EsqDir_usa_rotEsqDir(void) {
    nodo_t *a = novoNodo(10);
    nodo_t *b = novoNodo(20);
    nodo_t *c = novoNodo(30);
    a->dir = b;
    c->esq = a;
    atualizaAltura(b);
    atualizaAltura(a);
    atualizaAltura(c);
    TEST_ASSERT_EQUAL_INT(2,  c->fator);
    TEST_ASSERT_EQUAL_INT(-1, a->fator);

    nodo_t *r = balanceamentoAVL(c);

    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    liberaArvore(r);
}

void test_balanceamentoAVL_caso_DirEsq_usa_rotDirEsq(void) {
    nodo_t *a = novoNodo(10);
    nodo_t *b = novoNodo(20);
    nodo_t *c = novoNodo(30);
    c->esq = b;
    a->dir = c;
    atualizaAltura(b);
    atualizaAltura(c);
    atualizaAltura(a);
    TEST_ASSERT_EQUAL_INT(-2, a->fator);
    TEST_ASSERT_EQUAL_INT(1,  c->fator);

    nodo_t *r = balanceamentoAVL(a);

    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    liberaArvore(r);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_balanceamentoAVL_balanceado_retorna_proprio);
    RUN_TEST(test_balanceamentoAVL_caso_EsqEsq_usa_rotDir);
    RUN_TEST(test_balanceamentoAVL_caso_DirDir_usa_rotEsq);
    RUN_TEST(test_balanceamentoAVL_caso_EsqDir_usa_rotEsqDir);
    RUN_TEST(test_balanceamentoAVL_caso_DirEsq_usa_rotDirEsq);
    return UNITY_END();
}
#endif

#endif
