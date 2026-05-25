#ifdef TEST

#include <stdlib.h>
#include <string.h>
#include "test_helpers.h"

/* ------------------------------------------------------------------ */
/* Builders                                                           */
/* ------------------------------------------------------------------ */

Grafo *make_grafo(const char *nome) {
    Grafo *g = calloc(1, sizeof(Grafo));
    if (nome) strcpy(g->nome, nome);
    return g;
}

void free_grafo_raw(Grafo *g) {
    /* Libera as arestas que o teste eventualmente tenha pendurado
     * manualmente. Não usa destroi_grafo para não acoplar o helper
     * àquela função (que tem seus próprios testes).                */
    if (g == NULL) return;
    for (unsigned int i = 0; i < g->num_vertices; i++) {
        Aresta *a = g->vertices[i].arestas_head;
        while (a != NULL) {
            Aresta *prox = a->prox;
            free(a);
            a = prox;
        }
    }
    free(g);
}

unsigned int helper_push_vertice(Grafo *g, const char *nome) {
    unsigned int idx = g->num_vertices++;
    strcpy(g->vertices[idx].nome, nome);
    g->vertices[idx].arestas_head = NULL;
    g->vertices[idx].arestas_tail = NULL;
    g->vertices[idx].pai          = NULL;
    g->vertices[idx].dist         = 0;
    g->vertices[idx].estado       = 0;
    g->vertices[idx].componente   = 0;
    g->vertices[idx].lowpoint     = 0;
    g->vertices[idx].nivel        = 0;
    g->vertices[idx].corte        = 0;
    return idx;
}

Aresta *helper_make_aresta(Vértice *destino, unsigned int peso) {
    Aresta *a = malloc(sizeof(Aresta));
    a->destino = destino;
    a->peso    = peso;
    a->prox    = NULL;
    return a;
}

void helper_append_aresta(Vértice *v, Aresta *a) {
    if (v->arestas_head == NULL) {
        v->arestas_head = a;
        v->arestas_tail = a;
    } else {
        v->arestas_tail->prox = a;
        v->arestas_tail = a;
    }
}

/* ------------------------------------------------------------------ */
/* Spy                                                                */
/* ------------------------------------------------------------------ */

#define SPY_CAP 1024

static const char *spy_log[SPY_CAP];
static unsigned    spy_len = 0;

void spy_reset(void) {
    spy_len = 0;
}

void spy_record(const char *name) {
    if (spy_len < SPY_CAP) {
        spy_log[spy_len++] = name;
    }
}

unsigned spy_count(void) {
    return spy_len;
}

const char *spy_at(unsigned i) {
    if (i >= spy_len) return NULL;
    return spy_log[i];
}

unsigned spy_count_of(const char *name) {
    unsigned c = 0;
    for (unsigned i = 0; i < spy_len; i++) {
        if (strcmp(spy_log[i], name) == 0) c++;
    }
    return c;
}

#endif /* TEST */
