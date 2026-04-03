#include "CppUTest/TestHarness.h"

extern "C" {
    #include "../conta_pastilhas.h"
}

TEST_GROUP(ContaPastilhasGroup) {};

TEST(ContaPastilhasGroup, TestRealDir)
{
    argumentos args;
    char* diretorio = "teste_pastilhas";
    args.diretorio = diretorio;
    conta_pastilhas(&args,NULL);
    CHECK_EQUAL(6, args.numero_pastilhas);

}

TEST(ContaPastilhasGroup, TestNotRealDir)
{
    argumentos args;
    char* diretorio = "dir_not_exists";
    args.diretorio = diretorio;
    int result = conta_pastilhas(&args,NULL);
    CHECK_EQUAL(-1,result);
}