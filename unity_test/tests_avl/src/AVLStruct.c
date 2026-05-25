#include <stdlib.h>
#include <stdio.h>
#include "AVLStruct.h"

/* Esta funcao recebe a raiz de uma arvore e realiza a impressao 
   EM ORDEM da arvore (as chaves acompanham sua altura na arvore) */
void imprimeArvore(nodo_t *nodo, int altura) {
    if (nodo == NULL)
        return;
    imprimeArvore(nodo->esq, altura+1);
    printf("%d,%d\n", nodo->chave, altura);
    imprimeArvore(nodo->dir, altura+1);
}

/* Faz a insercao AVL! Primeiro executa-se uma insercao BST
   Atualiza a altura/fator de balanceamento e executa o 
   balanceamento se necessario */
nodo_t *insereAVL(nodo_t *nodo, int chave) {
    // Insere mantendo prop. BST
    if (nodo == NULL) 
        return novoNodo(chave);

    if (chave > nodo->chave)
        nodo->dir = insereAVL(nodo->dir, chave);
    else if (chave < nodo->chave)
        nodo->esq = insereAVL(nodo->esq, chave);
    else
        return nodo;
    // Atualiza altura e fatorBalanceamento do nodo
    atualizaAltura(nodo);
    //Balanceamento AVL
    return balanceamentoAVL(nodo);
}

/* Faz a remocao AVL! Primeira executa-se uma remocao BST
   Atualiza a altura/fator de balanceamento e executa o 
   balanceamento se necessario */
nodo_t *removeAVL(nodo_t *nodo, int chave) {
    // Nodo nao encontrado
    if (nodo == NULL)
        return nodo;

    // Remocao BST
    if (chave > nodo->chave)
        nodo->dir = removeAVL(nodo->dir, chave);
    else if (chave < nodo->chave) 
        nodo->esq = removeAVL(nodo->esq, chave);
    else {
       if ((nodo->dir != NULL) && (nodo->esq != NULL)) {
           //nodo com dois filhos 
           nodo_t *antecessor = achaAntecessor(nodo->esq);
           nodo->chave = antecessor->chave;
           //remove antecessor na subarvore esquerda
           nodo->esq = removeAVL(nodo->esq, antecessor->chave);
       } else if (nodo->dir != NULL) {
           //nodo com um filho na direita
           nodo_t *aux = nodo;
           nodo = nodo->dir;
           free(aux);   
       } else if (nodo-> esq != NULL) {
           //nodo com um filho na esquerda
           nodo_t *aux = nodo;
           nodo = nodo->esq;
           free(aux);
       } else {
           // nodo sem filho
           free(nodo);
           nodo = NULL;
       }
    }

    // Retorna se o nodo nao existir mais
    if (nodo == NULL) return nodo;
    // Atualiza altura e fatorBalanceamento do nodo
    atualizaAltura(nodo);
    // Balanceamento AVL
    return balanceamentoAVL(nodo);
}

/* Acha o nodo com maior chave em uma arvore */
nodo_t *achaAntecessor(nodo_t *nodo) {
    nodo_t *aux = nodo; 
    while (aux->dir != NULL)
        aux = aux->dir;
    return aux;
}

nodo_t *balanceamentoAVL(nodo_t *nodo) {
    // Desbalanceamento na esquerda
    if (nodo->fator > 1) {
        if (nodo->esq->fator >= 0) {
            return rotDir(nodo); // Caso Esquerda-Esquerda
        } else {
            return rotEsqDir(nodo); // Caso Esquerda-Direita
        }
    }

    // Desbalanceamento na direita
    if (nodo->fator < -1) {
        if (nodo->dir->fator <= 0) {
            return rotEsq(nodo); // Caso Direita-Direita
        } else {
            return rotDirEsq(nodo); // Caso Direita-esquerda
        }
    }

    // Nodo balanceado.
    return nodo;
}

/* Dada uma chave, cria-se um novo nodo com altura e balanceamento zero
   Os ponteiros para filhos sao nulos */
nodo_t *novoNodo(int chave) {
    nodo_t *novo = (nodo_t*) malloc(sizeof(nodo_t));
    novo->esq = NULL;
    novo->dir = NULL;
    novo->chave = chave;
    novo->altura = 0;
    novo->fator = 0;
    return novo;
}


/* Esta funcao atualiza a altura E fator de balanceamento do nodo!
   Utiliza informacao dos filhos do nodo para calcular a atualizacao
   Importante utilizar de baixo para cima */
void atualizaAltura(nodo_t *nodo) {
    int altEsq = -1;
    int altDir = -1;
    // Se filhos nao forem nulos, entao atualize as variaveis 
    if (nodo->esq != NULL)
        altEsq = nodo->esq->altura;
    if (nodo->dir != NULL)
        altDir = nodo->dir->altura;
    nodo->altura = max(altEsq, altDir) + 1;
    nodo->fator = altEsq - altDir;
}

/* Funcao BST de rotacao para direita */
nodo_t *rotDir(nodo_t *nodo) {
    nodo_t *aux = nodo->esq;
    nodo->esq = aux->dir;
    aux->dir = nodo;
    atualizaAltura(nodo);
    atualizaAltura(aux);
    return aux;
}
/* Funcao BST de rotacao para esquerda */
nodo_t *rotEsq(nodo_t *nodo) {
    nodo_t *aux = nodo->dir;
    nodo->dir = aux->esq;
    aux->esq = nodo;
    atualizaAltura(nodo);
    atualizaAltura(aux);
    return aux;
}

nodo_t *rotEsqDir(nodo_t *nodo) {
    nodo->esq = rotEsq(nodo->esq);
    return rotDir(nodo);
}

nodo_t *rotDirEsq(nodo_t *nodo) {
    nodo->dir = rotDir(nodo->dir);
    return rotEsq(nodo);
}

/* Funcao auxiliar que recebe dois inteiros e retorna o maior deles */
int max(int a, int b) {
    if (a >= b)
        return a;
    return b;
}
