#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "grafo.h"

#ifdef TEST
#  include "grafo_internal.h"   /* expõe tipos e protótipos para os testes */
#endif

#define MAX_CHARS 2048

// Structs e operações em grafos ------------------------------------------------------------------------------------------------------------------------
#ifndef TEST
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
#endif

// Funcoes em grafos--------------------------------------------------------------------------------------------------------------------------
int procura_vertice(grafo *g, char *vertice);
void adiciona_vertice(grafo *g, char *vertice);
void adiciona_aresta(grafo *g, char *origem, char *destino, unsigned int peso);

// Retorna indice de um vértice no array de vértices
int procura_vertice(grafo *g, char *vertice) {
    int achou = -1;
    for (unsigned int i = 0; i < g->num_vertices; i++) {
        if (strcmp(g->vertices[i].nome, vertice) == 0) achou = i;
    }

    return achou;
}

// Adiciona vértice no grafo
void adiciona_vertice(grafo *g, char *vertice) {
    Vértice v;
    g->num_vertices++;
    strcpy(v.nome, vertice);
    v.arestas_head = NULL;
    v.arestas_tail = NULL;
    v.dist = 0;
    v.estado = 0;
    v.pai = NULL;

    g->vertices[g->num_vertices-1] = v;
}

// Adiciona aresta no grafo dado dois vértices que já existem
void adiciona_aresta(grafo *g, char *origem, char *destino, unsigned int peso) {
    int ind_origem = procura_vertice(g, origem);
    int ind_destino = procura_vertice(g, destino);
    
    if ((ind_destino == -1) || (ind_origem == -1)) return;

    g->num_arestas++;

    // Adiciona aresta origem -> destino
    Aresta *nova = malloc(sizeof(Aresta));
    nova->destino = &(g->vertices[ind_destino]);
    nova->peso = peso;
    nova->prox = NULL;

    // Lista de arestas vazia
    if (g->vertices[ind_origem].arestas_head == NULL){
        g->vertices[ind_origem].arestas_head = nova;
        g->vertices[ind_origem].arestas_tail = nova;
    }
    else {
        g->vertices[ind_origem].arestas_tail->prox = nova;
        g->vertices[ind_origem].arestas_tail = nova;
    }

    // Adiciona aresta destino -> origem
    nova = malloc(sizeof(Aresta));
    nova->destino = &(g->vertices[ind_origem]);
    nova->peso = peso;
    nova->prox = NULL;

    // Lista de arestas vazia
    if (g->vertices[ind_destino].arestas_head == NULL){
        g->vertices[ind_destino].arestas_head = nova;
        g->vertices[ind_destino].arestas_tail = nova;
    }
    else {
        g->vertices[ind_destino].arestas_tail->prox = nova;
        g->vertices[ind_destino].arestas_tail = nova;
    }
}

// Structs e funções da fila -----------------------------------------------------------------------------------------------------------------------------
#ifndef TEST
typedef struct nodo {
    Vértice *v;
    struct nodo *prox;
} Nodo;

typedef struct fila {
    Nodo *fila_head;
    Nodo *fila_tail;
} Fila;
#endif

// Funcoes em filas-------------------------------------------------------------------------------------------------------------------
Fila *cria_fila(void);
void enfilera(Vértice *v, Fila *f);
void enfilera_ordenado(Vértice *v, Fila *f);
Vértice *desenfilera(Fila *f);
int fila_vazia(Fila *f);
void destroi_fila(Fila *f);

Fila *cria_fila(void) {
    Fila *f = malloc(sizeof(Fila));
    f->fila_head = NULL;
    f->fila_tail = NULL;

    return f;
}

// Adiciona vértice na fila
void enfilera(Vértice *v, Fila *f) {
    Nodo *n = malloc(sizeof(Nodo));
    n->v = v;
    n->prox = NULL;

    if (f->fila_head == NULL) {
        f->fila_head = n;
        f->fila_tail = n;
    }
    else {
        f->fila_tail->prox = n;
        f->fila_tail = n;
    }
}

// Adiciona vértice na fila ordenado pelo custo
void enfilera_ordenado(Vértice *v, Fila *f) {
    Nodo *n = malloc(sizeof(Nodo));
    n->v = v;
    n->prox = NULL;

    if (f->fila_head == NULL) {
        f->fila_head = n;
        f->fila_tail = n;
    }
    else if (v->dist < f->fila_head->v->dist) {
        n->prox = f->fila_head;
        f->fila_head = n;
    }
    else {
        Nodo *atual = f->fila_head;
        while (atual->prox != NULL && atual->prox->v->dist < v->dist) {
            atual = atual->prox;
        }

        n->prox = atual->prox;
        atual->prox = n;
    }
}

// Retira primeiro vértice da fila
Vértice *desenfilera(Fila *f) {
    Nodo *n = f->fila_head;
    f->fila_head = f->fila_head->prox;

    n->prox = NULL;
    Vértice *v = n->v;
    free(n);
    return v;
}

// Retorna se fila esta vazia ou nao
int fila_vazia(Fila *f) {
    if (f->fila_head == NULL) return 1;
    return 0;
}

// Destroi uma fila f
void destroi_fila(Fila *f) {
    if (!fila_vazia(f)) {
        Nodo *n = f->fila_head;
        while (n != NULL) {
            Nodo *prox = n->prox;
            free(n);
            n = prox;
        }
    }
    free(f);
    f = NULL;
    return;
}

// Funções do trabalho em si ----------------------------------------------------------------------------------------------------------------------------
void BuscaCaminhosMin(Vértice *r);
void BuscaDijkstra(Vértice *r);
int compara(const void *a, const void *b);
void BuscaLowPoint(grafo *g, Vértice *r);
int compara_nomes(const void* a, const void* b);
int eh_raiz(Vértice *v);

grafo *le_grafo(FILE *f) {
    Grafo *g = malloc(sizeof(Grafo));
    if (g == NULL) {
        perror("Erro ao alocar memória para o grafo");
        return NULL;
    }

    char linha[MAX_CHARS];

    // Lê da entrada f
    int primeira_linha = 1;

    while (fgets(linha, sizeof(linha), f)) {
        // Remove \n da linha
        linha[strcspn(linha, "\n")] = '\0';

        // Apenas processa se não for comentario
        if ((strncmp(linha, "//", 2) != 0) && (linha[0] != '\0')){
            // Primeira linha é o nome do grafo
            if (primeira_linha){
                primeira_linha = 0;
                strcpy(g->nome, linha);
            }
            // Outras linhas de vértices e arestas
            else{
                // Linha com arestas
                if (strstr(linha, "--") != NULL) {
                    const char delim[] = " ";
                    char *prim, *seg, *peso;

                    // Primeira ponta da aresta
                    prim = strtok(linha, delim);
                    if (procura_vertice(g, prim) == -1) {
                        adiciona_vertice(g, prim);
                    }

                    strtok(NULL, delim); // --
                    
                    // Segunda ponta da aresta
                    seg = strtok(NULL, delim);
                    if (procura_vertice(g, seg) == -1) {
                        adiciona_vertice(g, seg);
                    }

                    // Peso da aresta
                    peso = strtok(NULL, delim);
                    if (peso != NULL) {
                        unsigned int peso_int = atoi(peso);
                        adiciona_aresta(g, prim, seg, peso_int);
                    }
                    else{
                        adiciona_aresta(g, prim, seg, 1);
                    }
                }

                // Linha com vértice sem arestas
                else adiciona_vertice(g, linha);
            }
        }

    }

    /* Printa todos os vertices e arestas lidos*/
    // for (int i = 0; i < g->num_vertices; i++) {
    //     printf("Vértice %s: ", g->vertices[i].nome);
    //     Aresta *a = g->vertices[i].arestas_head;
    //     while (a != NULL) {
    //         printf("-> %s(peso %d) ", a->destino->nome, a->peso);
    //         a = a->prox;
    //     }
    //     printf("\n");
    // }

    return g;
}

//------------------------------------------------------------------------------
// desaloca toda a estrutura de dados alocada em g
//
// devolve 1 em caso de sucesso e 0 em caso de erro

unsigned int destroi_grafo(grafo *g){
    // Libera memória de todas as arestas
    for (unsigned int i = 0; i < g->num_vertices; i++) {
        Aresta *a = g->vertices[i].arestas_head;
        Aresta *prox;
        while (a != NULL) {
            prox = a->prox;
            free(a);
            a = prox;
        }
        g->vertices[i].arestas_head = NULL;
        g->vertices[i].arestas_tail = NULL;
    }

    // Libera memória do grafo
    free(g);
    g = NULL;
    return (g == NULL);
}

//------------------------------------------------------------------------------
// devolve o nome de g

char *nome(grafo *g){
    return (*g).nome;
}

// Busca em largura para determinar se grafo é bipartido
void BuscaCaminhosMin(Vértice *r) {
    Fila *V = cria_fila();
    r->dist = 0;
    enfilera(r, V);
    r->estado = 1;

    while (!fila_vazia(V)){
        Vértice *v = desenfilera(V);

        // Itera para todas as arestas de v
        Aresta *a = v->arestas_head;
        while (a != NULL) {
            Vértice *w = a->destino;
            if(w->estado == 0){
                w->pai = v;
                w->dist = w->pai->dist+1;
                w->componente = w->pai->componente;
                enfilera(w, V);
                w->estado = 1;
            }

            a = a->prox;
        }
        v->estado = 2;
    }

    destroi_fila(V);
    return;
}

//------------------------------------------------------------------------------
// devolve 1 se g é bipartido e 0 caso contrário

unsigned int bipartido(grafo *g){
    for (unsigned int i = 0; i < g->num_vertices; i++) {
        g->vertices[i].estado = 0;
    }

    for (unsigned int i = 0; i < g->num_vertices; i++) {
        if (g->vertices[i].estado == 0) BuscaCaminhosMin(&(g->vertices[i]));
    }

    unsigned int bipart = 1;
    for (unsigned int i = 0; i < g->num_vertices; i++) {
        Vértice *v = &(g->vertices[i]);
        Aresta *a = v->arestas_head;
        while (a != NULL){
            Vértice *w = a->destino;
            // Procura arestas fora da arvore, ou seja, sem relacao de descendencia
            if ((v != w->pai) && (w != v->pai)) {
                // Se tem paridades diferentes, n eh bipartido
                if ((v->dist % 2) == (w->dist % 2)) bipart = 0;
            }
            a = a->prox;
        }
    }

    return bipart;
}

//------------------------------------------------------------------------------
// devolve o número de vértices em g

unsigned int n_vertices(grafo *g){
    return g->num_vertices;
}

//------------------------------------------------------------------------------
// devolve o número de arestas em g

unsigned int n_arestas(grafo *g){
    return g->num_arestas;
}

//------------------------------------------------------------------------------
// devolve o número de componentes em g

unsigned int n_componentes(grafo *g){
    for (unsigned int i = 0; i < g->num_vertices; i++) {
        g->vertices[i].estado = 0;
    }

    unsigned int c = 0;
    for (unsigned int i = 0; i < g->num_vertices; i++) {
        if (g->vertices[i].estado == 0) {
            g->vertices[i].componente = c++;
            BuscaCaminhosMin(&(g->vertices[i]));
        }
    }

    return c;
}

// Busca usando Dijkstra para determinar se grafo é bipartido
void BuscaDijkstra(Vértice *r) {
    Fila *V = cria_fila();
    r->dist = 0;
    r->estado = 1;
    enfilera_ordenado(r, V);

    while (!fila_vazia(V)){
        Vértice *v = desenfilera(V);

        // Itera para todas as arestas de v
        Aresta *a = v->arestas_head;
        while (a != NULL) {
            Vértice *u = a->destino;
            if (u->estado == 1) {
                if (v->dist + a->peso < u->dist){
                    u->pai = v;
                    u->dist = v->dist + a->peso;
                }
            }
            else if(u->estado == 0){
                u->pai = v;
                u->dist = v->dist + a->peso;
                u->componente = u->pai->componente;
                enfilera_ordenado(u, V);
                u->estado = 1;
            }

            a = a->prox;
        }
        v->estado = 2;
    }

    destroi_fila(V);
}

// Compara dois numeros (Usado para o qsort)
int compara(const void *a, const void *b) {
    return (*(int*)a - *(int*)b);
}

//------------------------------------------------------------------------------
// devolve uma "string" com os diâmetros dos componentes de g separados por brancos
// em ordem não decrescente

char *diametros(grafo *g){
    unsigned int num_comp = n_componentes(g);
    unsigned int diametros[num_comp];

    char *diam = malloc(MAX_CHARS);
   
    // Itera um componente de cada vez
    for (unsigned int i = 0; i < num_comp; i++) {
        unsigned int maxdist = 0;

        // Para todos os vertices do componente, realiza a busca
        for (unsigned int j = 0; j < g->num_vertices; j++) {
            for (unsigned int k = 0; k < g->num_vertices; k++) {
                g->vertices[k].estado = 0;
                g->vertices[k].dist = 0;
            }
            if (g->vertices[j].componente == i) BuscaDijkstra(&(g->vertices[j]));

            // Pega a distancia maxima de cada busca e as compara, deixando sempre a maior
            for (unsigned int k = 0; k < g->num_vertices; k++){
                if (g->vertices[k].dist > maxdist) maxdist = g->vertices[k].dist;
            }
        }

        diametros[i] = maxdist;
    }

    // Ordena vetor
    qsort(diametros, num_comp, sizeof(unsigned int), compara);
    
    // Escreve os números em uma string
    int index = 0;
    for (unsigned int i=0; i<num_comp; i++)
        if (i == num_comp-1){
            index += sprintf(&diam[index], "%d", diametros[i]);
        } 
        else {
            index += sprintf(&diam[index], "%d ", diametros[i]);
        }

    return diam;
}

// Busca em profundidade com objetivo de achar lowpoints
void BuscaLowPoint(grafo *g, Vértice *r) {
    unsigned int filhos = 0;
    r->estado = 1;
    
    // Itera para todas as arestas de v
    Aresta *a = r->arestas_head;
    while (a != NULL) {
        Vértice *w = a->destino;
        if ((w->estado == 1) && (w->nivel < r->lowpoint) && (r->pai != w)) r->lowpoint = w->nivel;
        else if(w->estado == 0){
            filhos += 1;
            w->pai = r;
            w->lowpoint = r->nivel + 1;
            w->nivel = r->nivel + 1;
            BuscaLowPoint(g, w);
            if (w->lowpoint < r->lowpoint) r->lowpoint = w->lowpoint;
            if ((r->pai != NULL) && (r->nivel <= w->lowpoint)) r->corte = 1;
        }
        a = a->prox;
    }
    if (r->pai == NULL && (filhos > 1)) r->corte = 1;
    r->estado = 2;
}

// Comparador para qsort
int compara_nomes(const void* a, const void* b) {
    char* nome1 = *(char**)a;
    char* nome2 = *(char**)b;
    return strcmp(nome1, nome2);
}

int eh_raiz(Vértice *v) {
    if (v->pai == NULL) return 1;
    return 0;
}

//------------------------------------------------------------------------------
// devolve uma "string" com os nomes dos vértices de corte de g em
// ordem alfabética, separados por brancos

char *vertices_corte(grafo *g){
    char *cortes = malloc(MAX_CHARS);
    strcpy(cortes, "");

    for (unsigned int i = 0; i < g->num_vertices; i++) {
        g->vertices[i].pai = NULL;
        g->vertices[i].estado = 0;
        g->vertices[i].corte = 0;
    }

    // Roda busca em todo o grafo
    for (unsigned int i = 0; i < g->num_vertices; i++) {
        Vértice *v = &(g->vertices[i]);
        if (v->estado == 0) {
            v->lowpoint = 0;
            v->nivel = 0;
            BuscaLowPoint(g, v);
        }
    }

    // Cria vetor de ponteiros para os nomes
    char nomes[g->num_arestas][MAX_CHARS];
    int ind_nome = 0;

    // Procura vértices de corte
    for (unsigned int i = 0; i < g->num_vertices; i++) {
        Vértice *v = &(g->vertices[i]);
        
        if (v->corte) {
            sprintf(nomes[ind_nome], "%s", v->nome);
            ind_nome++;
        }
    }

    // Ordena vetor
    qsort(nomes, ind_nome, MAX_CHARS, strcmp);

    for (int i = 0; i < ind_nome; i++) {
        strcat(cortes, nomes[i]);
        if (i < ind_nome - 1) {
            strcat(cortes, " ");
        }
    }

    return cortes;
}

//------------------------------------------------------------------------------
// devolve uma "string" com as arestas de corte de g em ordem alfabética, separadas por brancos
// cada aresta é o par de nomes de seus vértices em ordem alfabética, separadas por brancos
//
// por exemplo, se as arestas de corte são {z, a}, {x, b} e {y, c}, a resposta será a string
// "a z b x c y"

char *arestas_corte(grafo *g){
    char *cortes = malloc(MAX_CHARS);
    strcpy(cortes, "");

    for (unsigned int i = 0; i < g->num_vertices; i++) {
        g->vertices[i].pai = NULL;
        g->vertices[i].estado = 0;
        g->vertices[i].corte = 0;
    }

    for (unsigned int i = 0; i < g->num_vertices; i++) {
        Vértice *v = &(g->vertices[i]);
        if (v->estado == 0) {
            v->lowpoint = 0;
            v->nivel = 0;
            BuscaLowPoint(g, v);
        }
    }

    // Cria vetor de ponteiros para os nomes
    char nomes[g->num_arestas][MAX_CHARS];
    int ind_nome = 0;

    // Procura arestas de corte
    for (unsigned int i = 0; i < g->num_vertices; i++) {
        Vértice *u = &(g->vertices[i]);

        Aresta *a = u->arestas_head;
        while (a != NULL) {
            Vértice *v = a->destino;
            // u é pai de v e L(u) < l(v)
            if ((v->pai == u) && (u->nivel < v->lowpoint)) {
                if (strcmp(u->nome, v->nome) < 0) {
                    sprintf(nomes[ind_nome], "%s %s", u->nome, v->nome);
                }
                else {
                    sprintf(nomes[ind_nome], "%s %s", v->nome, u->nome);
                }
                ind_nome++;
            }
            a = a->prox;
        }
    }

    // Ordena vetor
    qsort(nomes, ind_nome, MAX_CHARS, strcmp);

    for (int i = 0; i < ind_nome; i++) {
        strcat(cortes, nomes[i]);
        if (i < ind_nome - 1) {
            strcat(cortes, " ");
        }
    }

    return cortes;
}