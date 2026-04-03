#include "CppUTest/TestHarness.h"

extern "C" {
    #include "../argumentos_entrada.h"
}

static int trata_called = 0;
static int my_printf_called = 0;
static int exit_called = 0;
static char expected_input_file[256];
static char expected_output_file[256];
static FILE* last_input_stream = NULL;
static FILE* last_output_stream = NULL;

extern "C" int my_printf(const char* format, ...) {
    my_printf_called++;
    return 0;
}

extern "C" int my_fprintf(FILE *stream,const char* format, ...) {
    my_printf_called++;
    return 0;
}

// extern "C" void exit(int status)
// {
//     exit_called++;
// }

extern "C" void trata_imagem(argumentos *args, image_ppm *imagem)
{
    trata_called +=1;
    imagem->tipo = 3;
    imagem->largura = 6;
    imagem->altura = 2;
}

extern "C" FILE* freopen(const char* filename, const char* mode, FILE* stream)
{
    if (mode[0] == 'r'){
        snprintf(expected_input_file, sizeof(expected_input_file), "%s", filename);
        last_input_stream = stream;
    }

    if (mode[0] == 'w'){
        snprintf(expected_output_file, sizeof(expected_output_file), "%s", filename);
        last_output_stream = stream;
    }

    return stream;
}

TEST_GROUP(ArgumentosGroup) {};

TEST(ArgumentosGroup, CustomDirectoryAndIO)
{
    argumentos args;
    const char* input_file  = "input.jpeg";
    const char* output_file = "output.jpeg";
    const char* tiles_folder = "tiles_test";
    const char* argv[] = {"prog","-i",input_file,"-o", output_file,"-p",tiles_folder};
    int argc = 6;
    image_ppm img;
    argumentos_entrada(&args, argc, argv, &img);

    STRCMP_EQUAL(input_file,  expected_input_file);
    STRCMP_EQUAL(output_file, expected_output_file);
    STRCMP_EQUAL(tiles_folder, args.diretorio);
    CHECK_EQUAL(1, trata_called);

}

TEST(ArgumentosGroup, TestHelp)
{
    argumentos args;
    const char* argv[] = {"prog","-h"};
    int argc = 2;
    image_ppm img;
    argumentos_entrada(&args, argc, argv, &img);
    CHECK_EQUAL(1, my_printf_called);

}

// TEST(ArgumentosGroup, NoArgs)
// {
//     argumentos args;
//     const char* argv[] = {};
//     int argc = 0;
//     image_ppm img;
//     argumentos_entrada(&args, argc, argv, &img);
//     const char* tiles_folder = "./tiles";
//     STRCMP_EQUAL(tiles_folder, args.diretorio);
//     POINTERS_EQUAL(stdin,  last_input_stream);
//     POINTERS_EQUAL(stdout, last_output_stream);
// }