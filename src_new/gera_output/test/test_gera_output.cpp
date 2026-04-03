#include "CppUTest/TestHarness.h"

extern "C" {
    #include "../gera_output.h"
}

/* ===== MOCKS ===== */

static int printf_called = 0;
static int fprintf_called = 0;
static int fwrite_called = 0;

static char printf_buffer[2048];

extern "C" int my_printf(const char *format, ...)
{
    printf_called++;

    va_list args;
    va_start(args, format);
    vsnprintf(printf_buffer, sizeof(printf_buffer), format, args);
    va_end(args);

    return 0;
}

extern "C" int my_fprintf(FILE *stream, const char *format, ...)
{
    fprintf_called++;
    return 0;
}

extern "C" size_t my_fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream)
{
    fwrite_called++;
    return nmemb;
}

/* ===== HELPER ===== */

static image_ppm make_image(int tipo, int largura, int altura, int higherColor, int *data)
{
    image_ppm img;
    img.tipo = tipo;
    img.largura = largura;
    img.altura = altura;
    img.higherColor = higherColor;
    img.matriz = data;
    return img;
}

/* ===== TEST GROUP ===== */

TEST_GROUP(GeraOutputGroup)
{
    void setup()
    {
        printf_called = 0;
        fprintf_called = 0;
        fwrite_called = 0;
    }
};

/* ===== TESTS ===== */

TEST(GeraOutputGroup, HeaderIsPrinted)
{
    int data[] = {1,2,3};
    image_ppm img = make_image(3, 3, 1, 255, data);

    gera_output(&img);

    CHECK(printf_called > 0);
    CHECK_EQUAL(1, fprintf_called); // "Writing output file"
}

TEST(GeraOutputGroup, Tipo3UsesPrintf)
{
    int data[] = {10,20,30};
    image_ppm img = make_image(3, 3, 1, 255, data);

    gera_output(&img);

    CHECK(printf_called > 0);
    CHECK_EQUAL(0, fwrite_called); // should NOT use fwrite
}

TEST(GeraOutputGroup, TipoNao3UsesFwrite)
{
    int data[] = {10,20,30};
    image_ppm img = make_image(6, 3, 1, 255, data);

    gera_output(&img);

    CHECK(fwrite_called > 0);
}

TEST(GeraOutputGroup, CorrectNumberOfFwriteCalls)
{
    int data[] = {1,2,3,4,5,6};
    image_ppm img = make_image(6, 3, 2, 255, data);

    gera_output(&img);

    // altura * largura calls
    CHECK_EQUAL(6, fwrite_called);
}