#ifdef TEST

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "unity.h"
#include "AVLStruct.h"

/*
 * Testes para: void imprimeArvore(nodo_t *nodo, int altura)
 *
 * Percurso em-ordem, imprime "%d,%d\n" com chave e nível recursivo.
 */

#ifndef ALL_TESTS
void setUp(void)    {}
void tearDown(void) {}
#endif

#ifndef AVL_TESTS_HELPER_LIBERAARVORE
#define AVL_TESTS_HELPER_LIBERAARVORE
static void liberaArvore(nodo_t *n) {
    if (n == NULL) return;
    liberaArvore(n->esq);
    liberaArvore(n->dir);
    free(n);
}
#endif

/* Helpers para captura de stdout: guarded para evitar redefinição. */
#ifndef AVL_TESTS_HELPER_CAPTURA
#define AVL_TESTS_HELPER_CAPTURA

static char *le_tudo_do_fd(int fd) {
    size_t cap = 256;
    size_t len = 0;
    char *buf = malloc(cap);
    if (!buf) return NULL;

    char tmp[128];
    ssize_t n;
    while ((n = read(fd, tmp, sizeof(tmp))) > 0) {
        if (len + (size_t)n + 1 > cap) {
            cap = (len + (size_t)n + 1) * 2;
            char *novo = realloc(buf, cap);
            if (!novo) { free(buf); return NULL; }
            buf = novo;
        }
        memcpy(buf + len, tmp, (size_t)n);
        len += (size_t)n;
    }
    buf[len] = '\0';
    return buf;
}

static char *captura_imprimeArvore(nodo_t *raiz) {
    int pipefd[2];
    if (pipe(pipefd) != 0) {
        TEST_FAIL_MESSAGE("pipe() falhou");
        return NULL;
    }

    fflush(stdout);
    int stdout_backup = dup(STDOUT_FILENO);
    dup2(pipefd[1], STDOUT_FILENO);
    close(pipefd[1]);

    imprimeArvore(raiz, 0);

    fflush(stdout);
    dup2(stdout_backup, STDOUT_FILENO);
    close(stdout_backup);

    char *out = le_tudo_do_fd(pipefd[0]);
    close(pipefd[0]);
    if (!out) TEST_FAIL_MESSAGE("malloc/realloc falhou");
    return out;
}

#endif  /* AVL_TESTS_HELPER_CAPTURA */

void test_imprimeArvore_NULL_nao_imprime_nada(void) {
    char *out = captura_imprimeArvore(NULL);
    TEST_ASSERT_NOT_NULL(out);
    TEST_ASSERT_EQUAL_STRING("", out);
    free(out);
}

void test_imprimeArvore_um_nodo(void) {
    nodo_t *r = novoNodo(42);
    char *out = captura_imprimeArvore(r);
    TEST_ASSERT_EQUAL_STRING("42,0\n", out);
    free(out);
    liberaArvore(r);
}

void test_imprimeArvore_em_ordem(void) {
    nodo_t *r = NULL;
    r = insereAVL(r, 20);
    r = insereAVL(r, 10);
    r = insereAVL(r, 30);

    char *out = captura_imprimeArvore(r);
    TEST_ASSERT_EQUAL_STRING(
        "10,1\n"
        "20,0\n"
        "30,1\n",
        out
    );
    free(out);
    liberaArvore(r);
}

void test_imprimeArvore_reproduz_teste1_out(void) {
    nodo_t *r = NULL;
    int seq[] = {10, 20, 30, 40, 50, 45, 48};
    for (int i = 0; i < 7; i++)
        r = insereAVL(r, seq[i]);

    const char *esperado =
        "10,2\n"
        "20,1\n"
        "30,2\n"
        "40,0\n"
        "45,2\n"
        "48,1\n"
        "50,2\n";

    char *out = captura_imprimeArvore(r);
    TEST_ASSERT_EQUAL_STRING(esperado, out);
    free(out);
    liberaArvore(r);
}

#ifndef ALL_TESTS
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_imprimeArvore_NULL_nao_imprime_nada);
    RUN_TEST(test_imprimeArvore_um_nodo);
    RUN_TEST(test_imprimeArvore_em_ordem);
    RUN_TEST(test_imprimeArvore_reproduz_teste1_out);
    return UNITY_END();
}
#endif

#endif
