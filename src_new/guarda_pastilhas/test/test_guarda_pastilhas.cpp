#include "CppUTest/TestHarness.h"

extern "C" {
    #include "../guarda_pastilhas.h"
}

/* ===== MOCKS ===== */

static int trata_called = 0;
static int fprintf_called = 0;
static int calcula_called = 0;
static int freopen_called = 0;
static int exit_called = 0;
static int my_perror_called = 0;

extern "C" int my_fprintf(FILE *stream, const char *format, ...)
{
    fprintf_called++;
    return 0;
}


extern "C" void trata_imagem(argumentos* args, image_ppm* img)
{
    trata_called++;
    img->largura = 6;
    img->altura = 3;
}

extern "C" void calcula_medias(image_ppm* img)
{
    calcula_called++;
}

extern "C" int my_perror(const char* format, ...) {
    my_perror_called++;
    return 0;
}

extern "C" FILE* freopen(const char* filename, const char* mode, FILE* stream)
{
    freopen_called++;
    return stream;
}

extern "C" void constroi_nome(char* dest, char* dir, char* file)
{
    strcpy(dest, dir);
    strcat(dest, "/");
    strcat(dest, file);
}

extern "C" void my_exit(int status)
{
    exit_called++;
}

/* ===== TEST GROUP ===== */

TEST_GROUP(GuardaPastilhasGroup)
{
    void setup()
    {
        trata_called = 0;
        calcula_called = 0;
        freopen_called = 0;
    }
};

/* ===== TEST ===== */

TEST(GuardaPastilhasGroup, ReadsOnlyPPMFilesFromRealFolder)
{
    argumentos args;
    args.diretorio = (char*)"teste_pastilhas";

    image_ppm pastilhas[10] = {};

    guarda_pastilhas(&args, NULL, pastilhas);

    CHECK_EQUAL(6, trata_called);
    CHECK_EQUAL(6, calcula_called);
    CHECK_EQUAL(6, freopen_called);
}

TEST(GuardaPastilhasGroup, DirNotExists)
{
    argumentos args;
    args.diretorio = (char*)"dir_not_real";

    image_ppm pastilhas[10] = {};

    guarda_pastilhas(&args, NULL, pastilhas);

    CHECK_EQUAL(1, exit_called);
    CHECK_EQUAL(1, my_perror_called);
}
