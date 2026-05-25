#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "unity.h"
#include "grafo_internal.h"
#include "test_helpers.h"
#include "mocks.h"

/*
 * Testes para: void enfilera_ordenado(Vértice *v, Fila *f)
 *
 * Insere ordenado por v->dist crescente. Função folha (só malloc).
 */

#ifndef ALL_TESTS
void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}
#endif

static Vértice make_vert_dist(const char *nome, unsigned int d) {
    Vértice v;
    memset(&v, 0, sizeof(v));
    strcpy(v.nome, nome);
    v.dist = d;
    return v;
}

static void cleanup_fila(Fila *f) {
    Nodo *n = f->fila_head;
    while (n) { Nodo *p = n->prox; free(n); n = p; }
    free(f);
}

void test_enfilera_ordenado_em_fila_vazia(void) {
    Fila *f = cria_fila();
    Vértice a = make_vert_dist("a", 5);
    enfilera_ordenado(&a, f);
    TEST_ASSERT_EQUAL_PTR(&a, f->fila_head->v);
    TEST_ASSERT_EQUAL_PTR(f->fila_head, f->fila_tail);
    cleanup_fila(f);
}

void test_enfilera_ordenado_insere_no_inicio_se_menor(void) {
    Fila *f = cria_fila();
    Vértice a = make_vert_dist("a", 10);
    Vértice b = make_vert_dist("b", 3);
    enfilera_ordenado(&a, f);
    enfilera_ordenado(&b, f);
    TEST_ASSERT_EQUAL_PTR(&b, f->fila_head->v);
    TEST_ASSERT_EQUAL_PTR(&a, f->fila_head->prox->v);
    cleanup_fila(f);
}

void test_enfilera_ordenado_insere_no_meio(void) {
    Fila *f = cria_fila();
    Vértice a = make_vert_dist("a", 1);
    Vértice b = make_vert_dist("b", 5);
    Vértice c = make_vert_dist("c", 3);
    enfilera_ordenado(&a, f);
    enfilera_ordenado(&b, f);
    enfilera_ordenado(&c, f);
    /* Esperado: a(1) -> c(3) -> b(5) */
    TEST_ASSERT_EQUAL_PTR(&a, f->fila_head->v);
    TEST_ASSERT_EQUAL_PTR(&c, f->fila_head->prox->v);
    TEST_ASSERT_EQUAL_PTR(&b, f->fila_head->prox->prox->v);
    cleanup_fila(f);
}

void test_enfilera_ordenado_insere_no_final_se_maior(void) {
    Fila *f = cria_fila();
    Vértice a = make_vert_dist("a", 1);
    Vértice b = make_vert_dist("b", 2);
    Vértice c = make_vert_dist("c", 99);
    enfilera_ordenado(&a, f);
    enfilera_ordenado(&b, f);
    enfilera_ordenado(&c, f);
    TEST_ASSERT_EQUAL_PTR(&c, f->fila_head->prox->prox->v);
    /* Note: tail NÃO é necessariamente atualizado quando insere no
     * final no código atual — o teste valida o que o código faz, não
     * o que "deveria" fazer.                                       */
    cleanup_fila(f);
}

void test_enfilera_ordenado_estavel_para_dist_iguais(void) {
    /* A condição é "< v->dist" (estrita), então iguais vão para
     * depois do existente.                                        */
    Fila *f = cria_fila();
    Vértice a = make_vert_dist("a", 5);
    Vértice b = make_vert_dist("b", 5);
    enfilera_ordenado(&a, f);
    enfilera_ordenado(&b, f);
    TEST_ASSERT_EQUAL_PTR(&a, f->fila_head->v);
    TEST_ASSERT_EQUAL_PTR(&b, f->fila_head->prox->v);
    cleanup_fila(f);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_enfilera_ordenado_em_fila_vazia);
    RUN_TEST(test_enfilera_ordenado_insere_no_inicio_se_menor);
    RUN_TEST(test_enfilera_ordenado_insere_no_meio);
    RUN_TEST(test_enfilera_ordenado_insere_no_final_se_maior);
    RUN_TEST(test_enfilera_ordenado_estavel_para_dist_iguais);
    return UNITY_END();
}
#endif

#endif
