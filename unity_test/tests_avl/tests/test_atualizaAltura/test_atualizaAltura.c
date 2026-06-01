#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: void atualizaAltura(nodo_t *nodo)
 *
 * Regras (relatorio.pdf):
 *   altura = max(alt(esq), alt(dir)) + 1
 *   fator  = alt(esq) - alt(dir)
 * Filho NULL conta como altura -1.
 */

#ifndef ALL_TESTS
void setUp(void)    {}
void tearDown(void) {}
#endif

void test_atualizaAltura_folha(void) {
    nodo_t *n = novoNodo(10);
    atualizaAltura(n);
    TEST_ASSERT_EQUAL_INT(0, n->altura);
    TEST_ASSERT_EQUAL_INT(0, n->fator);
    free(n);
}

void test_atualizaAltura_so_filho_esq(void) {
    nodo_t *pai = novoNodo(10);
    nodo_t *esq = novoNodo(5);
    pai->esq = esq;
    atualizaAltura(pai);
    TEST_ASSERT_EQUAL_INT(1, pai->altura);
    TEST_ASSERT_EQUAL_INT(1, pai->fator);
    free(esq);
    free(pai);
}

void test_atualizaAltura_so_filho_dir(void) {
    nodo_t *pai = novoNodo(10);
    nodo_t *dir = novoNodo(15);
    pai->dir = dir;
    atualizaAltura(pai);
    TEST_ASSERT_EQUAL_INT(1, pai->altura);
    TEST_ASSERT_EQUAL_INT(-1, pai->fator);
    free(dir);
    free(pai);
}

void test_atualizaAltura_dois_filhos_balanceado(void) {
    nodo_t *pai = novoNodo(10);
    nodo_t *e   = novoNodo(5);
    nodo_t *d   = novoNodo(15);
    pai->esq = e;
    pai->dir = d;
    atualizaAltura(pai);
    TEST_ASSERT_EQUAL_INT(1, pai->altura);
    TEST_ASSERT_EQUAL_INT(0, pai->fator);
    free(e); free(d); free(pai);
}

void test_atualizaAltura_subarvore_esq_mais_alta(void) {
    nodo_t *pai = novoNodo(10);
    nodo_t *e   = novoNodo(5);
    e->altura   = 3;
    nodo_t *d   = novoNodo(15);
    pai->esq = e;
    pai->dir = d;
    atualizaAltura(pai);
    TEST_ASSERT_EQUAL_INT(4, pai->altura);
    TEST_ASSERT_EQUAL_INT(3, pai->fator);
    free(e); free(d); free(pai);
}

void test_atualizaAltura_subarvore_dir_mais_alta(void) {
    nodo_t *pai = novoNodo(10);
    nodo_t *e   = novoNodo(5);
    nodo_t *d   = novoNodo(15);
    d->altura   = 2;
    pai->esq = e;
    pai->dir = d;
    atualizaAltura(pai);
    TEST_ASSERT_EQUAL_INT(3, pai->altura);
    TEST_ASSERT_EQUAL_INT(-2, pai->fator);
    free(e); free(d); free(pai);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_atualizaAltura_folha);
    RUN_TEST(test_atualizaAltura_so_filho_esq);
    RUN_TEST(test_atualizaAltura_so_filho_dir);
    RUN_TEST(test_atualizaAltura_dois_filhos_balanceado);
    RUN_TEST(test_atualizaAltura_subarvore_esq_mais_alta);
    RUN_TEST(test_atualizaAltura_subarvore_dir_mais_alta);
    return UNITY_END();
}
#endif

#endif
