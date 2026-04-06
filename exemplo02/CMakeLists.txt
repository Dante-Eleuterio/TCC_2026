cmake_minimum_required(VERSION 3.10)
project(exemplo02)

include_directories(./include)
add_executable(exemplo02 src/main.c src/fotomosaico.c)

enable_testing()
add_test(NAME tddl_start             COMMAND tddl start)
add_test(NAME funcao_constroi_nome   COMMAND tddl ./tests/test_constroi_nome.c)

