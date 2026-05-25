#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: nodo_t *insereAVL(nodo_t *nodo, int chave)
 */

#ifndef ALL_TESTS
void setUp(void)    {}
void tearDown(void) {}
#endif

#ifndef AVL_TESTS_HELPER_LIBERAARVORE
#define AVL_TESTS_HELPER_LIBERAARVORE
static void liberaArvore(nodo_t *n) {
    if (n == NULL) return;
    liberaArvore(n->esq);
    liberaArvore(n->dir);
    free(n);
}
#endif

void test_insereAVL_em_arvore_vazia(void) {
    nodo_t *raiz = insereAVL(NULL, 10);
    TEST_ASSERT_NOT_NULL(raiz);
    TEST_ASSERT_EQUAL_INT(10, raiz->chave);
    TEST_ASSERT_NULL(raiz->esq);
    TEST_ASSERT_NULL(raiz->dir);
    TEST_ASSERT_EQUAL_INT(0, raiz->altura);
    TEST_ASSERT_EQUAL_INT(0, raiz->fator);
    liberaArvore(raiz);
}

void test_insereAVL_dois_nodos_propBST(void) {
    nodo_t *raiz = NULL;
    raiz = insereAVL(raiz, 10);
    raiz = insereAVL(raiz, 20);
    TEST_ASSERT_EQUAL_INT(10, raiz->chave);
    TEST_ASSERT_NOT_NULL(raiz->dir);
    TEST_ASSERT_EQUAL_INT(20, raiz->dir->chave);
    TEST_ASSERT_NULL(raiz->esq);
    liberaArvore(raiz);
}

void test_insereAVL_chave_menor_vai_esquerda(void) {
    nodo_t *raiz = NULL;
    raiz = insereAVL(raiz, 10);
    raiz = insereAVL(raiz, 5);
    TEST_ASSERT_EQUAL_INT(10, raiz->chave);
    TEST_ASSERT_NOT_NULL(raiz->esq);
    TEST_ASSERT_EQUAL_INT(5, raiz->esq->chave);
    TEST_ASSERT_NULL(raiz->dir);
    liberaArvore(raiz);
}

void test_insereAVL_duplicata_ignorada(void) {
    nodo_t *raiz = NULL;
    raiz = insereAVL(raiz, 10);
    raiz = insereAVL(raiz, 10);
    TEST_ASSERT_EQUAL_INT(10, raiz->chave);
    TEST_ASSERT_NULL(raiz->esq);
    TEST_ASSERT_NULL(raiz->dir);
    TEST_ASSERT_EQUAL_INT(0, raiz->altura);
    liberaArvore(raiz);
}

void test_insereAVL_aciona_rotacao_EsqEsq(void) {
    nodo_t *raiz = NULL;
    raiz = insereAVL(raiz, 30);
    raiz = insereAVL(raiz, 20);
    raiz = insereAVL(raiz, 10);
    TEST_ASSERT_EQUAL_INT(20, raiz->chave);
    TEST_ASSERT_EQUAL_INT(10, raiz->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, raiz->dir->chave);
    TEST_ASSERT_EQUAL_INT(1, raiz->altura);
    liberaArvore(raiz);
}

void test_insereAVL_aciona_rotacao_DirDir(void) {
    nodo_t *raiz = NULL;
    raiz = insereAVL(raiz, 10);
    raiz = insereAVL(raiz, 20);
    raiz = insereAVL(raiz, 30);
    TEST_ASSERT_EQUAL_INT(20, raiz->chave);
    TEST_ASSERT_EQUAL_INT(10, raiz->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, raiz->dir->chave);
    liberaArvore(raiz);
}

void test_insereAVL_aciona_rotacao_EsqDir(void) {
    nodo_t *raiz = NULL;
    raiz = insereAVL(raiz, 30);
    raiz = insereAVL(raiz, 10);
    raiz = insereAVL(raiz, 20);
    TEST_ASSERT_EQUAL_INT(20, raiz->chave);
    TEST_ASSERT_EQUAL_INT(10, raiz->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, raiz->dir->chave);
    liberaArvore(raiz);
}

void test_insereAVL_aciona_rotacao_DirEsq(void) {
    nodo_t *raiz = NULL;
    raiz = insereAVL(raiz, 10);
    raiz = insereAVL(raiz, 30);
    raiz = insereAVL(raiz, 20);
    TEST_ASSERT_EQUAL_INT(20, raiz->chave);
    TEST_ASSERT_EQUAL_INT(10, raiz->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, raiz->dir->chave);
    liberaArvore(raiz);
}

void test_insereAVL_sequencia_do_teste1_do_projeto(void) {
    nodo_t *r = NULL;
    int seq[] = {10, 20, 30, 40, 50, 45, 48};
    for (int i = 0; i < 7; i++)
        r = insereAVL(r, seq[i]);
    TEST_ASSERT_EQUAL_INT(40, r->chave);
    TEST_ASSERT_NOT_NULL(r->esq);
    TEST_ASSERT_NOT_NULL(r->dir);
    TEST_ASSERT_EQUAL_INT(20, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(48, r->dir->chave);
    liberaArvore(r);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_insereAVL_em_arvore_vazia);
    RUN_TEST(test_insereAVL_dois_nodos_propBST);
    RUN_TEST(test_insereAVL_chave_menor_vai_esquerda);
    RUN_TEST(test_insereAVL_duplicata_ignorada);
    RUN_TEST(test_insereAVL_aciona_rotacao_EsqEsq);
    RUN_TEST(test_insereAVL_aciona_rotacao_DirDir);
    RUN_TEST(test_insereAVL_aciona_rotacao_EsqDir);
    RUN_TEST(test_insereAVL_aciona_rotacao_DirEsq);
    RUN_TEST(test_insereAVL_sequencia_do_teste1_do_projeto);
    return UNITY_END();
}
#endif

#endif
