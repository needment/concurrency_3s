cmake_minimum_required(VERSION 3.15...3.30)
project(matrix_mult_mpi CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(MPI QUIET)

add_executable(matrix_mpi src/main.cpp)

if (MPI_FOUND)
    target_link_libraries(matrix_mpi PRIVATE MPI::MPI_CXX)
else()
    target_include_directories(matrix_mpi PRIVATE "$ENV{MSMPI_INC}")
    target_link_libraries(matrix_mpi PRIVATE "$ENV{MSMPI_LIB64}/msmpi.lib")
endif()

if (MSVC)
    add_compile_options(/O2)
else()
    add_compile_options(-O3)
endif()