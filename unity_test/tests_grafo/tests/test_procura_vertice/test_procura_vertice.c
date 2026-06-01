#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"

/*
 * Testes para: int procura_vertice(grafo *g, char *vertice)
 *
 * Função puramente local — só lê a lista g->vertices. Não chama nenhuma
 * outra função do módulo, então não há nada a mockar aqui.
 */

#ifndef ALL_TESTS
void setUp(void)    { spy_reset(); }
void tearDown(void) {}
#endif

void test_procura_vertice_grafo_vazio_retorna_menos_um(void) {
    Grafo *g = make_grafo("g");
    char alvo[] = "x";
    TEST_ASSERT_EQUAL_INT(-1, procura_vertice(g, alvo));
    free_grafo_raw(g);
}

void test_procura_vertice_encontra_unico(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    char alvo[] = "a";
    TEST_ASSERT_EQUAL_INT(0, procura_vertice(g, alvo));
    free_grafo_raw(g);
}

void test_procura_vertice_encontra_no_meio(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    helper_push_vertice(g, "c");
    char alvo[] = "b";
    TEST_ASSERT_EQUAL_INT(1, procura_vertice(g, alvo));
    free_grafo_raw(g);
}

void test_procura_vertice_nao_encontra_retorna_menos_um(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    char alvo[] = "z";
    TEST_ASSERT_EQUAL_INT(-1, procura_vertice(g, alvo));
    free_grafo_raw(g);
}

void test_procura_vertice_case_sensitive(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "Abc");
    char alvo[] = "abc";
    TEST_ASSERT_EQUAL_INT(-1, procura_vertice(g, alvo));
    free_grafo_raw(g);
}

void test_procura_vertice_retorna_ultimo_em_caso_de_duplicata(void) {
    /* Sabemos que adiciona_vertice não impede duplicatas. O laço da
     * função sobrescreve `achou` a cada match — então o índice
     * retornado é o último.                                        */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "a");
    char alvo[] = "a";
    TEST_ASSERT_EQUAL_INT(1, procura_vertice(g, alvo));
    free_grafo_raw(g);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_procura_vertice_grafo_vazio_retorna_menos_um);
    RUN_TEST(test_procura_vertice_encontra_unico);
    RUN_TEST(test_procura_vertice_encontra_no_meio);
    RUN_TEST(test_procura_vertice_nao_encontra_retorna_menos_um);
    RUN_TEST(test_procura_vertice_case_sensitive);
    RUN_TEST(test_procura_vertice_retorna_ultimo_em_caso_de_duplicata);
    return UNITY_END();
}
#endif

#endif
