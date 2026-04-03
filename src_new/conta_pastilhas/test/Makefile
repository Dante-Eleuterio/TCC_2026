# compilers
CC = gcc
CXX = g++

# flags
CFLAGS = -std=c99 -g -O0 --coverage -I..
CXXFLAGS = -std=c++11 -g -O0 --coverage -I..
LDFLAGS = --coverage

# CppUTest
CPPUTEST_LIBS = -lCppUTest -lCppUTestExt

# files
TARGET = test_acha_indice

TEST_SRC = test_conta_pastilhas.cpp main.cpp
C_SRC = ../conta_pastilhas.c

C_OBJ = acha_indice.o

# default
all: $(TARGET)

# compile C source
$(C_OBJ): $(C_SRC)
	$(CC) $(CFLAGS) -c $< -o $@

# build test
$(TARGET): $(TEST_SRC) $(C_OBJ)
	$(CXX) $(CXXFLAGS) $^ $(CPPUTEST_LIBS) $(LDFLAGS) -o $@

# run tests
run: $(TARGET)
	./$(TARGET)

# coverage report
coverage: run
	gcovr -r .. --html --html-details -o coverage.html

# clean
clean:
	rm -f *.o $(TARGET) *.gcda *.gcno *.gcov coverage.*