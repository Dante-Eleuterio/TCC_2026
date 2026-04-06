# TCC 2026

## 1. Introdução


Focar na linguagem C
Linguagem C++ é bem mais complexa e está ficando ruim para desenvolvimento de sistemas embarcados
Linguagens novas como Rust, Zig e outras podem ter outras abordagens para testes



## 2. Objetivos

- O Framework deve facilitar a criação de testes unitarios para os códigos em C.
- Pode-se pensar primeiramente no público alvo sendo os alunos do BCC. Posteriormente podemos pensar para sistemas embarcados.

## 3. Requisitos

- O arquivo de teste deve seu autocontido e ser executado com um comando sobre ele
  - Vai precisar um local para apontar onde estão os includes
- Quanto mais fácil e compativel com o Linux melhor
- Menos dependencias de outras bibliotecas é melhor, mas não é um impedimento
- O projeto em C de base inicialmente vai seguir uma estrutura padrão do CMake. 
  - CMakeLists.txt
  - ./src/ : diretorio onde estará o código fonte (.c)
  - ./include/ : diretorio onde estará os headers
  - ./tests/ : diretorio onde estará os testes






## 4. Ferramentas similares

- cmake test
- cpputest
- googletest
- [tdd do Milan Neubert](https://github.com/neubertm/TDD_framework)
- https://github.com/djboni/unit_test_c_with_python

## 5. Ferramentas que podem ser uteis

- doxygen
- lizard
- cppcheck
- gcovr

## 6. Problemas para fazer os Testes Unitarios

- Dificuldade para realizar o mock, principalmente de funções do sistema como malloc
- Seria interessante fazer o mock das funções dentro dos testes?