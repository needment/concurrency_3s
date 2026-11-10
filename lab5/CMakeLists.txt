cmake_minimum_required(VERSION 3.15...3.30)
project(cs149_mandelbrot CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (MSVC)
    add_compile_options(/O2)
else()
    add_compile_options(-O3 -pthread)
endif()

include_directories(common src)

add_executable(mandelbrot
    src/main.cpp
    src/mandelbrotSerial.cpp
    src/mandelbrotThread.cpp
    common/ppm.cpp
)