#ifdef TEST

/*
 * test_all.c — runner agregado para a biblioteca grafo.c.
 *
 * Inclui os 25 arquivos de teste individuais via #include literal.
 * Define ALL_TESTS antes dos includes para que cada arquivo suprima
 * seu próprio setUp/tearDown/main (via #ifndef ALL_TESTS). O setUp/
 * tearDown e o main globais ficam neste arquivo, deixando as funções
 * test_xxx visíveis para o RUN_TEST.
 *
 * Os arquivos individuais continuam podendo ser rodados isoladamente.
 *
 * Estrutura: cada grupo de funções relacionadas tem sua função
 * run_<grupo>() para manter o main() abaixo dos thresholds do lizard.
 *
 * IMPORTANTE: o link precisa dos mesmos --wrap=... que os testes
 * individuais (ver support/mocks.h). Compile grafo.c com -O0
 * -fno-inline -fno-builtin para preservar as chamadas inter-módulo.
 */
#define ALL_TESTS

#include "unity.h"
#include "mocks.h"

/* Caminhos relativos a tests/test_all/. */

/* --- Helpers de construção (operam direto nos structs) --- */
#include "../test_procura_vertice/test_procura_vertice.c"
#include "../test_adiciona_vertice/test_adiciona_vertice.c"
#include "../test_adiciona_aresta/test_adiciona_aresta.c"

/* --- Fila (TAD interno) --- */
#include "../test_cria_fila/test_cria_fila.c"
#include "../test_enfilera/test_enfilera.c"
#include "../test_enfilera_ordenado/test_enfilera_ordenado.c"
#include "../test_desenfilera/test_desenfilera.c"
#include "../test_fila_vazia/test_fila_vazia.c"
#include "../test_destroi_fila/test_destroi_fila.c"

/* --- Funções utilitárias --- */
#include "../test_compara/test_compara.c"
#include "../test_compara_nomes/test_compara_nomes.c"
#include "../test_eh_raiz/test_eh_raiz.c"

/* --- Getters / acesso a campos --- */
#include "../test_n_vertices/test_n_vertices.c"
#include "../test_n_arestas/test_n_arestas.c"
#include "../test_nome/test_nome.c"

/* --- Leitura e destruição --- */
#include "../test_le_grafo/test_le_grafo.c"
#include "../test_destroi_grafo/test_destroi_grafo.c"

/* --- Algoritmos de busca (BFS, Dijkstra, LowPoint) --- */
#include "../test_BuscaCaminhosMin/test_BuscaCaminhosMin.c"
#include "../test_BuscaDijkstra/test_BuscaDijkstra.c"
#include "../test_BuscaLowPoint/test_BuscaLowPoint.c"

/* --- API de alto nível (consultas sobre o grafo) --- */
#include "../test_n_componentes/test_n_componentes.c"
#include "../test_bipartido/test_bipartido.c"
#include "../test_diametros/test_diametros.c"
#include "../test_vertices_corte/test_vertices_corte.c"
#include "../test_arestas_corte/test_arestas_corte.c"

void setUp(void)    { mocks_reset_all(); }
void tearDown(void) {}

/* ===================================================================
 * Grupo 1: helpers internos sobre a estrutura do grafo
 * =================================================================== */
static void run_helpers_grafo(void) {
    /* procura_vertice */
    RUN_TEST(test_procura_vertice_grafo_vazio_retorna_menos_um);
    RUN_TEST(test_procura_vertice_encontra_unico);
    RUN_TEST(test_procura_vertice_encontra_no_meio);
    RUN_TEST(test_procura_vertice_nao_encontra_retorna_menos_um);
    RUN_TEST(test_procura_vertice_case_sensitive);
    RUN_TEST(test_procura_vertice_retorna_ultimo_em_caso_de_duplicata);
    /* adiciona_vertice */
    RUN_TEST(test_adiciona_vertice_incrementa_num_vertices);
    RUN_TEST(test_adiciona_vertice_grava_nome);
    RUN_TEST(test_adiciona_vertice_inicializa_listas_em_NULL);
    RUN_TEST(test_adiciona_vertice_inicializa_pai_dist_estado);
    RUN_TEST(test_adiciona_vertice_dois_em_sequencia);
    /* adiciona_aresta */
    RUN_TEST(test_adiciona_aresta_cria_aresta_origem_destino);
    RUN_TEST(test_adiciona_aresta_eh_bidirecional);
    RUN_TEST(test_adiciona_aresta_incrementa_num_arestas_apenas_uma_vez);
    RUN_TEST(test_adiciona_aresta_anexa_no_tail_quando_ja_existe);
    RUN_TEST(test_adiciona_aresta_origem_inexistente_nao_altera_grafo);
    RUN_TEST(test_adiciona_aresta_destino_inexistente_nao_altera_grafo);
    RUN_TEST(test_adiciona_aresta_chama_procura_vertice_duas_vezes);
}

/* ===================================================================
 * Grupo 2: TAD fila
 * =================================================================== */
static void run_fila(void) {
    /* cria_fila */
    RUN_TEST(test_cria_fila_retorna_ponteiro_nao_nulo);
    RUN_TEST(test_cria_fila_head_e_tail_iniciam_NULL);
    RUN_TEST(test_cria_fila_aloca_inst_independentes);
    /* enfilera */
    RUN_TEST(test_enfilera_em_fila_vazia_head_e_tail_iguais);
    RUN_TEST(test_enfilera_dois_elementos_ordem_FIFO);
    RUN_TEST(test_enfilera_atualiza_tail_corretamente);
    /* enfilera_ordenado */
    RUN_TEST(test_enfilera_ordenado_em_fila_vazia);
    RUN_TEST(test_enfilera_ordenado_insere_no_inicio_se_menor);
    RUN_TEST(test_enfilera_ordenado_insere_no_final_se_maior);
    RUN_TEST(test_enfilera_ordenado_insere_no_meio);
    RUN_TEST(test_enfilera_ordenado_estavel_para_dist_iguais);
    /* desenfilera */
    RUN_TEST(test_desenfilera_retira_unico_elemento);
    RUN_TEST(test_desenfilera_FIFO_dois_elementos);
    RUN_TEST(test_desenfilera_atualiza_head);
    /* fila_vazia */
    RUN_TEST(test_fila_vazia_em_fila_recem_criada);
    RUN_TEST(test_fila_vazia_apos_enfilera_retorna_zero);
    RUN_TEST(test_fila_vazia_apos_desenfilera_unico_retorna_um);
    /* destroi_fila */
    RUN_TEST(test_destroi_fila_em_fila_vazia_nao_crasha);
    RUN_TEST(test_destroi_fila_libera_um_elemento);
    RUN_TEST(test_destroi_fila_libera_varios_elementos);
    RUN_TEST(test_destroi_fila_chama_fila_vazia);
}

/* ===================================================================
 * Grupo 3: funções utilitárias (comparações e predicados)
 * =================================================================== */
static void run_utilitarios(void) {
    /* compara */
    RUN_TEST(test_compara_a_maior_retorna_positivo);
    RUN_TEST(test_compara_b_maior_retorna_negativo);
    RUN_TEST(test_compara_iguais_retorna_zero);
    RUN_TEST(test_compara_com_zero);
    RUN_TEST(test_compara_funciona_para_qsort);
    /* compara_nomes */
    RUN_TEST(test_compara_nomes_alfabetico_a_antes_b);
    RUN_TEST(test_compara_nomes_alfabetico_b_antes_a);
    RUN_TEST(test_compara_nomes_iguais_retorna_zero);
    /* eh_raiz */
    RUN_TEST(test_eh_raiz_pai_NULL_retorna_um);
    RUN_TEST(test_eh_raiz_com_pai_retorna_zero);
}

/* ===================================================================
 * Grupo 4: getters da API pública
 * =================================================================== */
static void run_getters(void) {
    /* n_vertices */
    RUN_TEST(test_n_vertices_grafo_vazio_retorna_zero);
    RUN_TEST(test_n_vertices_apos_adicionar_um);
    RUN_TEST(test_n_vertices_apos_adicionar_varios);
    /* n_arestas */
    RUN_TEST(test_n_arestas_grafo_sem_arestas_retorna_zero);
    RUN_TEST(test_n_arestas_apos_adicionar_uma);
    RUN_TEST(test_n_arestas_apos_adicionar_varias);
    /* nome */
    RUN_TEST(test_nome_retorna_string_correta);
    RUN_TEST(test_nome_retorna_string_vazia_para_grafo_sem_nome);
    RUN_TEST(test_nome_retorna_ponteiro_interno);
}

/* ===================================================================
 * Grupo 5: leitura e destruição do grafo
 * =================================================================== */
static void run_le_destroi(void) {
    /* le_grafo */
    RUN_TEST(test_le_grafo_retorna_ponteiro_nao_nulo);
    RUN_TEST(test_le_grafo_grava_nome_do_grafo);
    RUN_TEST(test_le_grafo_adiciona_vertices_isolados);
    RUN_TEST(test_le_grafo_processa_aresta_com_peso);
    RUN_TEST(test_le_grafo_aresta_sem_peso_assume_um);
    RUN_TEST(test_le_grafo_nao_duplica_vertices);
    RUN_TEST(test_le_grafo_pula_comentarios);
    RUN_TEST(test_le_grafo_pula_linhas_em_branco);
    RUN_TEST(test_le_grafo_chama_adiciona_vertice_no_caso_vertice_solto);
    RUN_TEST(test_le_grafo_chama_adiciona_aresta_no_caso_aresta);
    /* destroi_grafo */
    RUN_TEST(test_destroi_grafo_grafo_sem_vertices);
    RUN_TEST(test_destroi_grafo_vertice_sem_arestas);
    RUN_TEST(test_destroi_grafo_libera_arestas);
    RUN_TEST(test_destroi_grafo_retorna_um);
}

/* ===================================================================
 * Grupo 6: algoritmos de busca (BFS, Dijkstra, LowPoint)
 * =================================================================== */
static void run_buscas(void) {
    /* BuscaCaminhosMin (BFS) */
    RUN_TEST(test_BuscaCaminhosMin_marca_raiz_como_visitada);
    RUN_TEST(test_BuscaCaminhosMin_distancia_correta_em_caminho);
    RUN_TEST(test_BuscaCaminhosMin_pai_aponta_para_predecessor);
    RUN_TEST(test_BuscaCaminhosMin_nao_visita_componente_separada);
    RUN_TEST(test_BuscaCaminhosMin_propaga_componente);
    RUN_TEST(test_BuscaCaminhosMin_usa_a_fila);
    /* BuscaDijkstra */
    RUN_TEST(test_BuscaDijkstra_raiz_com_dist_zero);
    RUN_TEST(test_BuscaDijkstra_caminho_simples_3_vertices);
    RUN_TEST(test_BuscaDijkstra_escolhe_caminho_mais_curto);
    RUN_TEST(test_BuscaDijkstra_marca_estado_final_dois);
    RUN_TEST(test_BuscaDijkstra_usa_enfilera_ordenado);
    /* BuscaLowPoint (DFS) */
    RUN_TEST(test_BuscaLowPoint_unico_vertice_nao_eh_corte);
    RUN_TEST(test_BuscaLowPoint_caminho_3_vertices_meio_eh_corte);
    RUN_TEST(test_BuscaLowPoint_ciclo_nao_tem_corte);
    RUN_TEST(test_BuscaLowPoint_raiz_com_dois_filhos_eh_corte);
    RUN_TEST(test_BuscaLowPoint_marca_niveis_em_dfs);
}

/* ===================================================================
 * Grupo 7: API de alto nível (consultas sobre o grafo)
 * =================================================================== */
static void run_api_alto_nivel(void) {
    /* n_componentes */
    RUN_TEST(test_n_componentes_grafo_vazio);
    RUN_TEST(test_n_componentes_um_vertice_isolado);
    RUN_TEST(test_n_componentes_dois_vertices_isolados);
    RUN_TEST(test_n_componentes_dois_conectados);
    RUN_TEST(test_n_componentes_dois_componentes_separados);
    RUN_TEST(test_n_componentes_chama_BuscaCaminhosMin_uma_vez_por_componente);
    /* bipartido */
    RUN_TEST(test_bipartido_vazio_retorna_um);
    RUN_TEST(test_bipartido_unico_vertice_retorna_um);
    RUN_TEST(test_bipartido_caminho_simples_retorna_um);
    RUN_TEST(test_bipartido_quadrilatero_retorna_um);
    RUN_TEST(test_bipartido_triangulo_retorna_zero);
    RUN_TEST(test_bipartido_chama_BuscaCaminhosMin);
    /* diametros */
    RUN_TEST(test_diametros_um_vertice_isolado_retorna_zero);
    RUN_TEST(test_diametros_caminho_3_vertices_retorna_2);
    RUN_TEST(test_diametros_com_pesos);
    RUN_TEST(test_diametros_dois_componentes_ordem_crescente);
    RUN_TEST(test_diametros_chama_BuscaDijkstra);
    /* vertices_corte */
    RUN_TEST(test_vertices_corte_sem_cortes_retorna_vazio);
    RUN_TEST(test_vertices_corte_caminho_3_vertices_meio_eh_corte);
    RUN_TEST(test_vertices_corte_multiplos_em_ordem_alfabetica);
    RUN_TEST(test_vertices_corte_chama_BuscaLowPoint);
    /* arestas_corte */
    RUN_TEST(test_arestas_corte_caminho_simples_3_vertices);
    RUN_TEST(test_arestas_corte_triangulo_nenhuma_ponte);
    RUN_TEST(test_arestas_corte_ordem_alfabetica_por_par);
    RUN_TEST(test_arestas_corte_chama_BuscaLowPoint);
}

int main(void) {
    UNITY_BEGIN();
    run_helpers_grafo();
    run_fila();
    run_utilitarios();
    run_getters();
    run_le_destroi();
    run_buscas();
    run_api_alto_nivel();
    return UNITY_END();
}

#endif
