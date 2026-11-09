#!/bin/bash
#SBATCH --job-name=lab3_mpi
#SBATCH --partition=batch
#SBATCH --ntasks-per-node=8
#SBATCH --time=02:00:00
#SBATCH --output=slurm-%j.out

set -u

SIZES="200 400 800 1200 1600 2000"
NPROCS="1 2 4 8"
REPEATS=3

module load intel/mpi5

mkdir -p data

echo "=== 1. Проверка и генерация входных данных ==="
for n in $SIZES; do
    if [ ! -f "data/A_$n.txt" ]; then
        echo "Генерация N=$n..."
        python3 generate_cluster.py "$n" "data/A_$n.txt" "data/B_$n.txt"
    fi
done

echo "=== 2. Запуск экспериментов ==="
echo "lab,n,workers,time_s,ops,gops" > results.csv

for n in $SIZES; do
    for np in $NPROCS; do
        for r in $(seq $REPEATS); do
            echo "N=$n, ядер=$np, прогон=$r"
            mpirun -np "$np" ./matrix_mpi "data/A_$n.txt" "data/B_$n.txt" "matrix_c.txt" >> results.csv
        done
    done
done

echo "Эксперимент завершен. Файл: results.csv"