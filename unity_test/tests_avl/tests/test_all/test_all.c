#ifdef TEST

/*
 * test_all.c — runner agregado.
 *
 * Inclui os 12 arquivos de teste individuais via #include literal.
 * Define ALL_TESTS antes dos includes para que cada arquivo suprima
 * seu próprio setUp/tearDown/main (via #ifndef ALL_TESTS). O setUp/
 * tearDown e o main globais ficam neste arquivo, deixando as funções
 * test_xxx visíveis para o RUN_TEST.
 *
 * Como usar com o tddl:
 *     tddl test_all.c --src AVLStruct.c
 *     tddl test_all.c --src AVLStruct.c --coverage   # cobertura agregada
 *     tddl test_all.c --src AVLStruct.c --valgrind   # memória zerada
 *
 * Os arquivos individuais continuam podendo ser rodados isoladamente.
 *
 * Estrutura: cada módulo tem sua função run_<modulo>() para manter o
 * main() abaixo dos thresholds do lizard.
 */
#define ALL_TESTS

#include "unity.h"

/* Caminhos relativos a tests/test_all/. */
#include "../test_novoNodo/test_novoNodo.c"
#include "../test_max/test_max.c"
#include "../test_atualizaAltura/test_atualizaAltura.c"
#include "../test_achaAntecessor/test_achaAntecessor.c"
#include "../test_rotDir/test_rotDir.c"
#include "../test_rotEsq/test_rotEsq.c"
#include "../test_rotEsqDir/test_rotEsqDir.c"
#include "../test_rotDirEsq/test_rotDirEsq.c"
#include "../test_balanceamentoAVL/test_balanceamentoAVL.c"
#include "../test_insereAVL/test_insereAVL.c"
#include "../test_removeAVL/test_removeAVL.c"
#include "../test_imprimeArvore/test_imprimeArvore.c"

void setUp(void)    {}
void tearDown(void) {}

static void run_novoNodo(void) {
    RUN_TEST(test_novoNodo_retorna_ponteiro_nao_nulo);
    RUN_TEST(test_novoNodo_grava_chave);
    RUN_TEST(test_novoNodo_filhos_sao_NULL);
    RUN_TEST(test_novoNodo_altura_zero);
    RUN_TEST(test_novoNodo_fator_zero);
    RUN_TEST(test_novoNodo_aceita_chave_negativa);
    RUN_TEST(test_novoNodo_aceita_chave_zero);
}

static void run_max(void) {
    RUN_TEST(test_max_primeiro_maior);
    RUN_TEST(test_max_segundo_maior);
    RUN_TEST(test_max_iguais);
    RUN_TEST(test_max_com_zero);
    RUN_TEST(test_max_com_negativos);
    RUN_TEST(test_max_misto_positivo_negativo);
}

static void run_atualizaAltura(void) {
    RUN_TEST(test_atualizaAltura_folha);
    RUN_TEST(test_atualizaAltura_so_filho_esq);
    RUN_TEST(test_atualizaAltura_so_filho_dir);
    RUN_TEST(test_atualizaAltura_dois_filhos_balanceado);
    RUN_TEST(test_atualizaAltura_subarvore_esq_mais_alta);
    RUN_TEST(test_atualizaAltura_subarvore_dir_mais_alta);
}

static void run_achaAntecessor(void) {
    RUN_TEST(test_achaAntecessor_unico_nodo);
    RUN_TEST(test_achaAntecessor_so_filhos_dir);
    RUN_TEST(test_achaAntecessor_ignora_subarvore_esquerda);
    RUN_TEST(test_achaAntecessor_chamado_em_subarvore);
}

static void run_rotacoes(void) {
    /* rotDir */
    RUN_TEST(test_rotDir_caso_simples_3_nodos);
    RUN_TEST(test_rotDir_preserva_subarvore_T2);
    RUN_TEST(test_rotDir_chaves_mantem_propriedade_BST);
    /* rotEsq */
    RUN_TEST(test_rotEsq_caso_simples_3_nodos);
    RUN_TEST(test_rotEsq_preserva_subarvore_T2);
    RUN_TEST(test_rotEsq_chaves_mantem_BST);
    /* rotEsqDir */
    RUN_TEST(test_rotEsqDir_3_nodos);
    RUN_TEST(test_rotEsqDir_preserva_em_ordem);
    RUN_TEST(test_rotEsqDir_altera_alturas_corretamente);
    /* rotDirEsq */
    RUN_TEST(test_rotDirEsq_3_nodos);
    RUN_TEST(test_rotDirEsq_em_ordem_preservada);
    RUN_TEST(test_rotDirEsq_alturas_corretas);
}

static void run_balanceamentoAVL(void) {
    RUN_TEST(test_balanceamentoAVL_balanceado_retorna_proprio);
    RUN_TEST(test_balanceamentoAVL_caso_EsqEsq_usa_rotDir);
    RUN_TEST(test_balanceamentoAVL_caso_DirDir_usa_rotEsq);
    RUN_TEST(test_balanceamentoAVL_caso_EsqDir_usa_rotEsqDir);
    RUN_TEST(test_balanceamentoAVL_caso_DirEsq_usa_rotDirEsq);
}

static void run_insereAVL(void) {
    RUN_TEST(test_insereAVL_em_arvore_vazia);
    RUN_TEST(test_insereAVL_dois_nodos_propBST);
    RUN_TEST(test_insereAVL_chave_menor_vai_esquerda);
    RUN_TEST(test_insereAVL_duplicata_ignorada);
    RUN_TEST(test_insereAVL_aciona_rotacao_EsqEsq);
    RUN_TEST(test_insereAVL_aciona_rotacao_DirDir);
    RUN_TEST(test_insereAVL_aciona_rotacao_EsqDir);
    RUN_TEST(test_insereAVL_aciona_rotacao_DirEsq);
    RUN_TEST(test_insereAVL_sequencia_do_teste1_do_projeto);
}

static void run_removeAVL(void) {
    RUN_TEST(test_removeAVL_arvore_vazia_retorna_NULL);
    RUN_TEST(test_removeAVL_chave_inexistente_arvore_inalterada);
    RUN_TEST(test_removeAVL_unico_nodo_vira_NULL);
    RUN_TEST(test_removeAVL_folha);
    RUN_TEST(test_removeAVL_nodo_com_um_filho_dir);
    RUN_TEST(test_removeAVL_nodo_com_um_filho_esq);
    RUN_TEST(test_removeAVL_nodo_com_dois_filhos_usa_antecessor);
    RUN_TEST(test_removeAVL_dispara_rebalanceamento);
    RUN_TEST(test_removeAVL_busca_recursiva_pela_esquerda);
}

static void run_imprimeArvore(void) {
    RUN_TEST(test_imprimeArvore_NULL_nao_imprime_nada);
    RUN_TEST(test_imprimeArvore_um_nodo);
    RUN_TEST(test_imprimeArvore_em_ordem);
    RUN_TEST(test_imprimeArvore_reproduz_teste1_out);
}

int main(void) {
    UNITY_BEGIN();
    run_novoNodo();
    run_max();
    run_atualizaAltura();
    run_achaAntecessor();
    run_rotacoes();
    run_balanceamentoAVL();
    run_insereAVL();
    run_removeAVL();
    run_imprimeArvore();
    return UNITY_END();
}

#endif
