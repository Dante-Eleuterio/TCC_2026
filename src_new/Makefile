# compilers
CC = gcc
CXX = g++

# flags
CFLAGS = -std=c99 -g -O0 --coverage -I.
CXXFLAGS = -std=c++11 -g -O0 --coverage -I.
LDFLAGS = --coverage

# libs
CPPUTEST_LIBS = -lCppUTest -lCppUTestExt

# target
TARGET = all_tests

# find all test files
TEST_SRC := $(shell find . -name "test_*.cpp")

# find all C sources (excluding test folders)
C_SRC := $(shell find . -name "*.c")

# objects
C_OBJ := $(C_SRC:.c=.o)

# default
all: $(TARGET)

# compile C files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# build all tests
$(TARGET): $(TEST_SRC) all_tests.cpp $(C_OBJ)
	$(CXX) $(CXXFLAGS) $^ $(CPPUTEST_LIBS) $(LDFLAGS) -o $@

# run everything
run: $(TARGET)
	./$(TARGET)

# coverage
coverage: clean run
	gcovr -r . --html --html-details -o coverage.html

# clean (keeps coverage.html)
clean:
	rm -f $(C_OBJ) $(TARGET) *.gcda *.gcno *.gcov