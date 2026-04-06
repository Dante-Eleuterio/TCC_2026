#include "CppUTest/TestHarness.h"

extern "C" {
#include "fotomosaico.h"
}


TEST_GROUP(ConstroiNomeGroup) {};

TEST(ConstroiNomeGroup,ConstroiNome )
{
    const char* expected_nome = "folder_name/file_name";
    char nome[256];
    char* diretorio = "folder_name";
    char* arquivo = "file_name";

    constroi_nome(nome,diretorio,arquivo);
    
    STRCMP_EQUAL(expected_nome, nome);

}