#include "CppUTest/TestHarness.h"

extern "C" {
    #include "../acha_indice.h"
    #include <stdlib.h>
}

/* Helper to create an image_ppm with RGB only */
static image_ppm make_image(int r, int g, int b)
{
    image_ppm img;
    img.red = r;
    img.green = g;
    img.blue = b;
    img.matriz = NULL;
    return img;
}

TEST_GROUP(AchaIndiceTest)
{
    argumentos args;
    image_ppm pastilhas[3];
    image_ppm pedaco;

    void setup()
    {
        args.numero_pastilhas = 3;

        /* Create 3 tiles with different colors */
        pastilhas[0] = make_image(255, 0, 0);   // red
        pastilhas[1] = make_image(0, 255, 0);   // green
        pastilhas[2] = make_image(0, 0, 255);   // blue
    }

    void teardown()
    {
    }
};

TEST(AchaIndiceTest, ReturnsClosestRed)
{
    pedaco = make_image(250, 10, 10);

    int idx = acha_indice(&args, NULL, pastilhas, &pedaco);

    CHECK_EQUAL(0, idx); // closest to red
}

TEST(AchaIndiceTest, ReturnsClosestGreen)
{
    pedaco = make_image(10, 240, 10);

    int idx = acha_indice(&args, NULL, pastilhas, &pedaco);

    CHECK_EQUAL(1, idx); // closest to green
}

TEST(AchaIndiceTest, ReturnsClosestBlue)
{
    pedaco = make_image(10, 10, 240);

    int idx = acha_indice(&args, NULL, pastilhas, &pedaco);

    CHECK_EQUAL(2, idx); // closest to blue
}

TEST(AchaIndiceTest, ReturnsFirstOnTie)
{
    /* Equal distance to red and green */
    pedaco = make_image(128, 128, 0);

    int idx = acha_indice(&args, NULL, pastilhas, &pedaco);

    CHECK_EQUAL(0, idx); // your function keeps first minimum
}

