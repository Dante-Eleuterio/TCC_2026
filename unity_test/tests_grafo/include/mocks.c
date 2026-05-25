#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "mocks.h"
#include "test_helpers.h"

/* ------------------------------------------------------------------ */
/* Declarações dos __real_*                                           */
/* ------------------------------------------------------------------ */

int  __real_procura_vertice(grafo *g, char *vertice);
void __real_adiciona_vertice(grafo *g, char *vertice);
void __real_adiciona_aresta(grafo *g, char *origem, char *destino, unsigned int peso);

Fila    *__real_cria_fila(void);
void     __real_enfilera(Vértice *v, Fila *f);
void     __real_enfilera_ordenado(Vértice *v, Fila *f);
Vértice *__real_desenfilera(Fila *f);
int      __real_fila_vazia(Fila *f);
void     __real_destroi_fila(Fila *f);

void __real_BuscaCaminhosMin(Vértice *r);
void __real_BuscaDijkstra(Vértice *r);
void __real_BuscaLowPoint(grafo *g, Vértice *r);

int __real_compara(const void *a, const void *b);
int __real_compara_nomes(const void *a, const void *b);
int __real_eh_raiz(Vértice *v);

/* ------------------------------------------------------------------ */
/* Estado dos mocks                                                   */
/* ------------------------------------------------------------------ */

int g_pv_mock_on      = 0;
int g_pv_ret_seq[16]  = {0};
int g_pv_ret_seq_len  = 0;
int g_pv_calls        = 0;

int g_av_mock_on      = 0;
int g_aa_mock_on      = 0;
int g_fila_mock_on    = 0;
int g_busca_mock_on   = 0;

void mocks_reset_all(void) {
    g_pv_mock_on = 0;
    g_pv_calls   = 0;
    g_pv_ret_seq_len = 0;
    memset(g_pv_ret_seq, 0, sizeof(g_pv_ret_seq));

    g_av_mock_on    = 0;
    g_aa_mock_on    = 0;
    g_fila_mock_on  = 0;
    g_busca_mock_on = 0;

    spy_reset();
}

/* ------------------------------------------------------------------ */
/* __wrap_*                                                           */
/* ------------------------------------------------------------------ */

int __wrap_procura_vertice(grafo *g, char *vertice) {
    spy_record("procura_vertice");
    if (g_pv_mock_on) {
        int n = g_pv_calls++;
        if (n < g_pv_ret_seq_len) return g_pv_ret_seq[n];
        return -1;
    }
    g_pv_calls++;
    return __real_procura_vertice(g, vertice);
}

void __wrap_adiciona_vertice(grafo *g, char *vertice) {
    spy_record("adiciona_vertice");
    if (g_av_mock_on) return;
    __real_adiciona_vertice(g, vertice);
}

void __wrap_adiciona_aresta(grafo *g, char *origem, char *destino, unsigned int peso) {
    spy_record("adiciona_aresta");
    if (g_aa_mock_on) return;
    __real_adiciona_aresta(g, origem, destino, peso);
}

Fila *__wrap_cria_fila(void) {
    spy_record("cria_fila");
    return __real_cria_fila();
}
void __wrap_enfilera(Vértice *v, Fila *f) {
    spy_record("enfilera");
    __real_enfilera(v, f);
}
void __wrap_enfilera_ordenado(Vértice *v, Fila *f) {
    spy_record("enfilera_ordenado");
    __real_enfilera_ordenado(v, f);
}
Vértice *__wrap_desenfilera(Fila *f) {
    spy_record("desenfilera");
    return __real_desenfilera(f);
}
int __wrap_fila_vazia(Fila *f) {
    spy_record("fila_vazia");
    return __real_fila_vazia(f);
}
void __wrap_destroi_fila(Fila *f) {
    spy_record("destroi_fila");
    __real_destroi_fila(f);
}

void __wrap_BuscaCaminhosMin(Vértice *r) {
    spy_record("BuscaCaminhosMin");
    if (g_busca_mock_on) return;
    __real_BuscaCaminhosMin(r);
}
void __wrap_BuscaDijkstra(Vértice *r) {
    spy_record("BuscaDijkstra");
    if (g_busca_mock_on) return;
    __real_BuscaDijkstra(r);
}
void __wrap_BuscaLowPoint(grafo *g, Vértice *r) {
    spy_record("BuscaLowPoint");
    if (g_busca_mock_on) return;
    __real_BuscaLowPoint(g, r);
}

int __wrap_compara(const void *a, const void *b) {
    spy_record("compara");
    return __real_compara(a, b);
}
int __wrap_compara_nomes(const void *a, const void *b) {
    spy_record("compara_nomes");
    return __real_compara_nomes(a, b);
}
int __wrap_eh_raiz(Vértice *v) {
    spy_record("eh_raiz");
    return __real_eh_raiz(v);
}

#endif /* TEST */
