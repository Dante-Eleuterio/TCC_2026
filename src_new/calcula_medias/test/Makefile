# compilers
CC = gcc
CXX = g++

# flags
CFLAGS = -std=c99 -g -O0 --coverage -I..
CXXFLAGS = -std=c++11 -g -O0 --coverage -I..
LDFLAGS = --coverage

# libs
CPPUTEST_LIBS = -lCppUTest -lCppUTestExt

# target
TARGET = test_calcula_medias

# sources
TEST_SRC = test_calcula_medias.cpp main.cpp
C_SRC = ../calcula_medias.c

# objects
C_OBJ = calcula_medias.o

# default
all: $(TARGET)

# compile C
$(C_OBJ): $(C_SRC)
	$(CC) $(CFLAGS) -c $< -o $@

# link
$(TARGET): $(TEST_SRC) $(C_OBJ)
	$(CXX) $(CXXFLAGS) $^ $(CPPUTEST_LIBS) $(LDFLAGS) -o $@

# run
run: $(TARGET)
	./$(TARGET)

# coverage
coverage: clean run
	gcovr -r .. --html --html-details -o coverage.html

# clean
clean:
	rm -f *.o $(TARGET) *.gcda *.gcno *.gcov coverage.*