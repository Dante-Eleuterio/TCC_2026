#include "unity.h"
#include "sum.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_sum_should_add_numbers(void)
{
    TEST_ASSERT_EQUAL(5, sum(2, 3));
}

void test_read_value_should_segfault(void)
{
    int *ptr = NULL;

    /* Isto causará um segfault */
    read_value(ptr);

    TEST_FAIL_MESSAGE("This line should never be reached");
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_sum_should_add_numbers);
    RUN_TEST(test_read_value_should_segfault);

    return UNITY_END();
}
