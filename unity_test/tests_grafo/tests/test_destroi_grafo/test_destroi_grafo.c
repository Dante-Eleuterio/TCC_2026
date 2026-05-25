#ifdef TEST

#include <stdlib.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: unsigned int destroi_grafo(grafo *g)
 *
 * Não chama outras funções da biblioteca — só libera memória via
 * free(). Mockar free() não traz valor.
 *
 * O comportamento de "memory freed" só é verificável via
 * Valgrind/ASan; testamos o contrato observável: o valor de retorno
 * e que o caminho de execução não crashe em diversos cenários.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_destroi_grafo_retorna_um(void) {
    /* O return é `(g == NULL)` onde g é a variável local pós-`g=NULL`,
     * então sempre será 1.                                            */
    Grafo *g = make_grafo("g");
    TEST_ASSERT_EQUAL_UINT(1, destroi_grafo(g));
}

void test_destroi_grafo_libera_arestas(void) {
    /* Constrói grafo com arestas e destrói. Sucesso = não crashar e
     * Valgrind reportar 0 leaks.                                    */
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    helper_push_vertice(g, "b");
    char o[] = "a"; char d[] = "b";
    adiciona_aresta(g, o, d, 1);

    unsigned int r = destroi_grafo(g);
    TEST_ASSERT_EQUAL_UINT(1, r);
}

void test_destroi_grafo_grafo_sem_vertices(void) {
    Grafo *g = make_grafo("g");
    TEST_ASSERT_EQUAL_UINT(1, destroi_grafo(g));
}

void test_destroi_grafo_vertice_sem_arestas(void) {
    Grafo *g = make_grafo("g");
    helper_push_vertice(g, "a");
    TEST_ASSERT_EQUAL_UINT(1, destroi_grafo(g));
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_destroi_grafo_retorna_um);
    RUN_TEST(test_destroi_grafo_libera_arestas);
    RUN_TEST(test_destroi_grafo_grafo_sem_vertices);
    RUN_TEST(test_destroi_grafo_vertice_sem_arestas);
    return UNITY_END();
}
#endif

#endif
