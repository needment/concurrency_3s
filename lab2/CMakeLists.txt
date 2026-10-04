cmake_minimum_required(VERSION 3.15...3.30)
project(matrix_mult_openmp CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenMP REQUIRED)

if (MSVC)
    add_compile_options(/O2)
else()
    add_compile_options(-O3)
endif()

add_executable(matrix_omp src/main.cpp)
target_link_libraries(matrix_omp PRIVATE OpenMP::OpenMP_CXX)