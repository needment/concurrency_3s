#!/bin/bash
set -euo pipefail

module load intel/mpi5

if command -v icpc >/dev/null 2>&1; then
    MPICXX=mpiicpc
else
    MPICXX=mpicxx
fi

echo "Используется компилятор: $MPICXX"
$MPICXX -std=c++11 -O3 src/main.cpp -o matrix_mpi
echo "Готово. Создан исполняемый файл ./matrix_mpi"