/*
 * grafo_internal.h
 *
 * Header exclusivo dos testes. Replica os tipos internos do grafo.c
 * (Aresta, Vértice, Grafo, Nodo, Fila) e declara os protótipos de todas as
 * funções privadas do módulo (procura_vertice, adiciona_vertice, fila etc.).
 *
 * Para que isso funcione, grafo.c precisa expor seus símbolos internos
 * quando TEST estiver definido. Veja support/grafo_testable_patch.md para
 * o patch sugerido — basicamente: nenhum desses helpers deve ser declarado
 * static, e em modo TEST os typedefs internos podem ser incluídos a partir
 * deste mesmo arquivo.
 *
 * Este header NÃO deve ser incluído em código de produção.
 */

#ifndef GRAFO_INTERNAL_H
#define GRAFO_INTERNAL_H

#include <stdio.h>
#include "grafo.h"

#define MAX_CHARS 2048

/* ------------------------------------------------------------------ */
/* Tipos internos                                                     */
/* ------------------------------------------------------------------ */

typedef struct aresta {
    struct vértice *destino;
    unsigned int peso;
    struct aresta *prox;
} Aresta;

typedef struct vértice {
    char nome[MAX_CHARS];
    Aresta *arestas_head;
    Aresta *arestas_tail;
    struct vértice *pai;
    unsigned int dist;
    unsigned int estado;
    unsigned int componente;
    unsigned int lowpoint;
    unsigned int nivel;
    unsigned int corte;
} Vértice;

typedef struct grafo {
    char nome[MAX_CHARS];
    Vértice vertices[1024];
    unsigned int num_vertices;
    unsigned int num_arestas;
} Grafo;

typedef struct nodo {
    Vértice *v;
    struct nodo *prox;
} Nodo;

typedef struct fila {
    Nodo *fila_head;
    Nodo *fila_tail;
} Fila;

/* ------------------------------------------------------------------ */
/* Protótipos internos                                                */
/* ------------------------------------------------------------------ */

/* Grafo */
int  procura_vertice(grafo *g, char *vertice);
void adiciona_vertice(grafo *g, char *vertice);
void adiciona_aresta(grafo *g, char *origem, char *destino, unsigned int peso);

/* Fila */
Fila    *cria_fila(void);
void     enfilera(Vértice *v, Fila *f);
void     enfilera_ordenado(Vértice *v, Fila *f);
Vértice *desenfilera(Fila *f);
int      fila_vazia(Fila *f);
void     destroi_fila(Fila *f);

/* Buscas */
void BuscaCaminhosMin(Vértice *r);
void BuscaDijkstra(Vértice *r);
void BuscaLowPoint(grafo *g, Vértice *r);

/* Utilitários */
int compara(const void *a, const void *b);
int compara_nomes(const void *a, const void *b);
int eh_raiz(Vértice *v);

#endif /* GRAFO_INTERNAL_H */
