cmake_minimum_required(VERSION 3.10)
project(exemplo01_tests C)

set(CMAKE_C_STANDARD 11)

# Mode: gcc (coverage enabled via gcovr)

# ============================================================================
#  Directories
# ============================================================================

set(INC_DIR   /home/des20/TCC_2026/unity_test/exemplo01/include)
set(UNITY_INC /home/des20/tcc/Unity/src)

# ============================================================================
#  Test target : tddl_constroi_nome
#  Test file   : constroi_nome.c
#  Src file    : fotomosaico.c (linked separately)
#  Wrapped     : testa_nome, constroi_nome
# ============================================================================

add_executable(tddl_constroi_nome
    /home/des20/TCC_2026/unity_test/exemplo01/tests/constroi_nome/constroi_nome.c
    /home/des20/tcc/Unity/src/unity.c
    /home/des20/TCC_2026/unity_test/exemplo01/src/fotomosaico.c
)

target_include_directories(tddl_constroi_nome PRIVATE
    ${INC_DIR}
    ${UNITY_INC}
)

target_compile_definitions(tddl_constroi_nome PRIVATE
    TEST
    UNITY_USE_COMMAND_LINE_ARGS
    UNITY_OUTPUT_COLOR
)

target_compile_options(tddl_constroi_nome PRIVATE
    --coverage
    -O0
    -g
)

target_link_options(tddl_constroi_nome PRIVATE
    --coverage
    -Wl,--wrap=testa_nome
    -Wl,--wrap=constroi_nome
)
