#include "CppUTest/TestHarness.h"

extern "C" {
    #include "../calcula_medias.h"
}

/* Helper to create image */
static image_ppm make_image(int largura, int altura, int *data)
{
    image_ppm img;
    img.largura = largura;
    img.altura = altura;
    img.matriz = data;
    img.red = 0;
    img.green = 0;
    img.blue = 0;
    return img;
}

TEST_GROUP(CalculaMediasGroup)
{
};

TEST(CalculaMediasGroup, SimpleRGB)
{
    /* 1 pixel (R,G,B) */
    int data[] = {100, 150, 200};

    image_ppm img = make_image(3, 1, data);

    calcula_medias(&img);

    CHECK_EQUAL(100, img.red);
    CHECK_EQUAL(150, img.green);
    CHECK_EQUAL(200, img.blue);
}

TEST(CalculaMediasGroup, TwoPixelsAverage)
{
    /* 2 pixels: (R,G,B)(R,G,B) */
    int data[] = {
        100, 150, 200,
        50,  50,  50
    };

    image_ppm img = make_image(6, 1, data);

    calcula_medias(&img);

    CHECK_EQUAL((100+50)/2, img.red);
    CHECK_EQUAL((150+50)/2, img.green);
    CHECK_EQUAL((200+50)/2, img.blue);
}

TEST(CalculaMediasGroup, AllSameColor)
{
    int data[] = {
        10, 20, 30,
        10, 20, 30,
        10, 20, 30
    };

    image_ppm img = make_image(9, 1, data);

    calcula_medias(&img);

    CHECK_EQUAL(10, img.red);
    CHECK_EQUAL(20, img.green);
    CHECK_EQUAL(30, img.blue);
}

TEST(CalculaMediasGroup, LargerMatrix)
{
    int data[] = {
        10,20,30,
        40,50,60,
        70,80,90
    };

    image_ppm img = make_image(9, 1, data);

    calcula_medias(&img);

    CHECK_EQUAL((10+40+70)/3, img.red);
    CHECK_EQUAL((20+50+80)/3, img.green);
    CHECK_EQUAL((30+60+90)/3, img.blue);
}