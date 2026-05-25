#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: void destroi_fila(Fila *f)
 *
 * destroi_fila chama fila_vazia internamente. Em modo passthrough o
 * mock só registra a chamada, então conseguimos verificar a interação.
 *
 * A verificação de "memória liberada" em si só é detectável via
 * Valgrind/ASan — os asserts diretos verificam apenas que a função
 * roda até o fim sem crashar em diferentes estados.
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

void test_destroi_fila_em_fila_vazia_nao_crasha(void) {
    mocks_reset_all();
    Fila *f = cria_fila();
    destroi_fila(f);
    /* Sucesso = não crashar. Se chegou aqui, passou.            */
    TEST_PASS();
}

void test_destroi_fila_libera_um_elemento(void) {
    mocks_reset_all();
    Fila *f = cria_fila();
    Vértice v; memset(&v, 0, sizeof(v));
    enfilera(&v, f);
    destroi_fila(f);
    TEST_PASS();
}

void test_destroi_fila_libera_varios_elementos(void) {
    mocks_reset_all();
    Fila *f = cria_fila();
    Vértice a, b, c;
    memset(&a, 0, sizeof(a));
    memset(&b, 0, sizeof(b));
    memset(&c, 0, sizeof(c));
    enfilera(&a, f);
    enfilera(&b, f);
    enfilera(&c, f);
    destroi_fila(f);
    TEST_PASS();
}

void test_destroi_fila_chama_fila_vazia(void) {
    mocks_reset_all();
    Fila *f = cria_fila();
    destroi_fila(f);
    /* O spy registra fila_vazia. Em fila vazia, fila_vazia é
     * chamada uma vez e o laço de free não é executado.        */
    TEST_ASSERT_GREATER_OR_EQUAL_UINT(1, spy_count_of("fila_vazia"));
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_destroi_fila_em_fila_vazia_nao_crasha);
    RUN_TEST(test_destroi_fila_libera_um_elemento);
    RUN_TEST(test_destroi_fila_libera_varios_elementos);
    RUN_TEST(test_destroi_fila_chama_fila_vazia);
    return UNITY_END();
}
#endif

#endif
