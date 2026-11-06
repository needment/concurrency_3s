cmake_minimum_required(VERSION 3.15...3.30)
project(matrix_mult_cuda LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CUDA_STANDARD 17)

add_executable(matrix_cuda src/main.cu)

# Автоопределение или установка целевой архитектуры GPU (Tesla T4 в Colab = sm_75)
if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
    set(CMAKE_CUDA_ARCHITECTURES 75)
endif()

set_target_properties(matrix_cuda PROPERTIES
    CUDA_SEPARABLE_COMPILATION OFF
)