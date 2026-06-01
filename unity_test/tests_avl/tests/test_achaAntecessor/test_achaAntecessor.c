#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: nodo_t *achaAntecessor(nodo_t *nodo)
 *
 * Caminha sempre para a direita até dir == NULL.
 */

#ifndef ALL_TESTS
void setUp(void)    {}
void tearDown(void) {}
#endif

void test_achaAntecessor_unico_nodo(void) {
    nodo_t *n = novoNodo(42);
    nodo_t *ant = achaAntecessor(n);
    TEST_ASSERT_EQUAL_PTR(n, ant);
    TEST_ASSERT_EQUAL_INT(42, ant->chave);
    free(n);
}

void test_achaAntecessor_so_filhos_dir(void) {
    nodo_t *a = novoNodo(10);
    nodo_t *b = novoNodo(20);
    nodo_t *c = novoNodo(30);
    a->dir = b;
    b->dir = c;
    nodo_t *ant = achaAntecessor(a);
    TEST_ASSERT_EQUAL_PTR(c, ant);
    TEST_ASSERT_EQUAL_INT(30, ant->chave);
    free(c); free(b); free(a);
}

void test_achaAntecessor_ignora_subarvore_esquerda(void) {
    nodo_t *raiz = novoNodo(20);
    nodo_t *e    = novoNodo(5);
    nodo_t *d    = novoNodo(50);
    nodo_t *e1   = novoNodo(1);
    nodo_t *e2   = novoNodo(8);
    raiz->esq = e;  raiz->dir = d;
    e->esq    = e1; e->dir    = e2;
    nodo_t *ant = achaAntecessor(raiz);
    TEST_ASSERT_EQUAL_PTR(d, ant);
    TEST_ASSERT_EQUAL_INT(50, ant->chave);
    free(e1); free(e2); free(e); free(d); free(raiz);
}

void test_achaAntecessor_chamado_em_subarvore(void) {
    nodo_t *e  = novoNodo(5);
    nodo_t *e8 = novoNodo(8);
    e->dir = e8;
    nodo_t *ant = achaAntecessor(e);
    TEST_ASSERT_EQUAL_PTR(e8, ant);
    TEST_ASSERT_EQUAL_INT(8, ant->chave);
    free(e8); free(e);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_achaAntecessor_unico_nodo);
    RUN_TEST(test_achaAntecessor_so_filhos_dir);
    RUN_TEST(test_achaAntecessor_ignora_subarvore_esquerda);
    RUN_TEST(test_achaAntecessor_chamado_em_subarvore);
    return UNITY_END();
}
#endif

#endif
