#ifndef __AVLSTRUCT__
#define __AVLSTRUCT__

typedef struct nodo_t {
    int chave;
    int altura;
    int fator; // Fator de balanceamento
    struct nodo_t *esq;
    struct nodo_t *dir;
} nodo_t;

void imprimeArvore(nodo_t *nodo, int altura);
nodo_t *insereAVL(nodo_t *nodo, int chave);
nodo_t *removeAVL(nodo_t *nodo, int chave);
nodo_t *balanceamentoAVL(nodo_t *nodo);
nodo_t *novoNodo(int chave);
nodo_t *achaAntecessor(nodo_t *nodo);
void atualizaAltura(nodo_t *nodo);
nodo_t *rotDir(nodo_t *nodo);
nodo_t *rotEsq(nodo_t *nodo);
nodo_t *rotEsqDir(nodo_t *nodo);
nodo_t *rotDirEsq(nodo_t *nodo);
int max(int a, int b);

#endif
