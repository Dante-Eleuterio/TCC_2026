#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: nodo_t *removeAVL(nodo_t *nodo, int chave)
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

void test_removeAVL_arvore_vazia_retorna_NULL(void) {
    nodo_t *r = removeAVL(NULL, 42);
    TEST_ASSERT_NULL(r);
}

void test_removeAVL_chave_inexistente_arvore_inalterada(void) {
    nodo_t *r = NULL;
    r = insereAVL(r, 10);
    r = insereAVL(r, 20);
    r = removeAVL(r, 99);
    TEST_ASSERT_NOT_NULL(r);
    TEST_ASSERT_EQUAL_INT(10, r->chave);
    TEST_ASSERT_NOT_NULL(r->dir);
    TEST_ASSERT_EQUAL_INT(20, r->dir->chave);
    liberaArvore(r);
}

void test_removeAVL_unico_nodo_vira_NULL(void) {
    nodo_t *r = NULL;
    r = insereAVL(r, 10);
    r = removeAVL(r, 10);
    TEST_ASSERT_NULL(r);
}

void test_removeAVL_folha(void) {
    nodo_t *r = NULL;
    r = insereAVL(r, 20);
    r = insereAVL(r, 10);
    r = insereAVL(r, 30);
    r = removeAVL(r, 30);
    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_NOT_NULL(r->esq);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_NULL(r->dir);
    liberaArvore(r);
}

void test_removeAVL_nodo_com_um_filho_dir(void) {
    nodo_t *r = NULL;
    r = insereAVL(r, 10);
    r = insereAVL(r, 20);
    r = removeAVL(r, 10);
    TEST_ASSERT_NOT_NULL(r);
    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_NULL(r->esq);
    TEST_ASSERT_NULL(r->dir);
    liberaArvore(r);
}

void test_removeAVL_nodo_com_um_filho_esq(void) {
    nodo_t *r = NULL;
    r = insereAVL(r, 20);
    r = insereAVL(r, 10);
    r = removeAVL(r, 20);
    TEST_ASSERT_NOT_NULL(r);
    TEST_ASSERT_EQUAL_INT(10, r->chave);
    TEST_ASSERT_NULL(r->esq);
    TEST_ASSERT_NULL(r->dir);
    liberaArvore(r);
}

void test_removeAVL_nodo_com_dois_filhos_usa_antecessor(void) {
    nodo_t *r = NULL;
    r = insereAVL(r, 20);
    r = insereAVL(r, 10);
    r = insereAVL(r, 30);
    r = removeAVL(r, 20);
    TEST_ASSERT_NOT_NULL(r);
    TEST_ASSERT_EQUAL_INT(10, r->chave);
    TEST_ASSERT_NULL(r->esq);
    TEST_ASSERT_NOT_NULL(r->dir);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    liberaArvore(r);
}

void test_removeAVL_dispara_rebalanceamento(void) {
    nodo_t *r = NULL;
    r = insereAVL(r, 30);
    r = insereAVL(r, 20);
    r = insereAVL(r, 40);
    r = insereAVL(r, 10);
    r = removeAVL(r, 40);
    TEST_ASSERT_EQUAL_INT(20, r->chave);
    TEST_ASSERT_NOT_NULL(r->esq);
    TEST_ASSERT_NOT_NULL(r->dir);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);
    liberaArvore(r);
}

void test_removeAVL_busca_recursiva_pela_esquerda(void) {
    nodo_t *r = NULL;

    r = insereAVL(r, 20);
    r = insereAVL(r, 10);
    r = insereAVL(r, 30);
    r = insereAVL(r, 5);
    
    r = removeAVL(r, 5);

    TEST_ASSERT_NOT_NULL(r);

    TEST_ASSERT_EQUAL_INT(20, r->chave);

    TEST_ASSERT_NOT_NULL(r->esq);
    TEST_ASSERT_EQUAL_INT(10, r->esq->chave);

    TEST_ASSERT_NOT_NULL(r->dir);
    TEST_ASSERT_EQUAL_INT(30, r->dir->chave);

    TEST_ASSERT_NULL(r->esq->esq);
    TEST_ASSERT_NULL(r->esq->dir);

    liberaArvore(r);
}


#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_removeAVL_arvore_vazia_retorna_NULL);
    RUN_TEST(test_removeAVL_chave_inexistente_arvore_inalterada);
    RUN_TEST(test_removeAVL_unico_nodo_vira_NULL);
    RUN_TEST(test_removeAVL_folha);
    RUN_TEST(test_removeAVL_nodo_com_um_filho_dir);
    RUN_TEST(test_removeAVL_nodo_com_um_filho_esq);
    RUN_TEST(test_removeAVL_nodo_com_dois_filhos_usa_antecessor);
    RUN_TEST(test_removeAVL_dispara_rebalanceamento);
    RUN_TEST(test_removeAVL_busca_recursiva_pela_esquerda);
    return UNITY_END();
}
#endif

#endif
