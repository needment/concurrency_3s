#include <iostream>
#include <vector>
#include <fstream>
#include <iomanip>
#include <string>
#include <cstdint>
#include <mpi.h>

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);

    int rank, num_procs;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &num_procs);

    if (argc < 4) {
        if (rank == 0) {
            std::cerr << "Использование: " << argv[0] << " <file_A> <file_B> <file_result>\n";
        }
        MPI_Finalize();
        return 1;
    }

    std::string path_a = argv[1];
    std::string path_b = argv[2];
    std::string path_out = argv[3];

    uint64_t n = 0;
    std::vector<double> a;
    std::vector<double> b;
    std::vector<double> c;

    if (rank == 0) {
        std::ifstream fa(path_a);
        std::ifstream fb(path_b);
        if (!fa.is_open() || !fb.is_open()) {
            std::cerr << "Ошибка: Не удалось открыть входные файлы\n";
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        uint64_t n_b;
        fa >> n;
        fb >> n_b;

        if (n != n_b) {
            std::cerr << "Ошибка: Размеры матриц не совпадают\n";
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        a.resize(n * n);
        b.resize(n * n);
        c.resize(n * n, 0.0);

        for (size_t i = 0; i < n * n; ++i) fa >> a[i];
        for (size_t i = 0; i < n * n; ++i) fb >> b[i];

        fa.close();
        fb.close();
    }

    // Рассылка размера N (C++11 / MPI-2 совместимый тип)
    MPI_Bcast(&n, 1, MPI_UNSIGNED_LONG_LONG, 0, MPI_COMM_WORLD);

    if (rank != 0) {
        b.resize(n * n);
    }
    MPI_Bcast(b.data(), static_cast<int>(n * n), MPI_DOUBLE, 0, MPI_COMM_WORLD);

    std::vector<int> send_counts(num_procs);
    std::vector<int> displs(num_procs);

    int rows_rem = static_cast<int>(n % num_procs);
    int sum = 0;
    for (int p = 0; p < num_procs; ++p) {
        int rows = static_cast<int>(n / num_procs) + (p < rows_rem ? 1 : 0);
        send_counts[p] = rows * static_cast<int>(n);
        displs[p] = sum;
        sum += send_counts[p];
    }

    int local_elements = send_counts[rank];
    int local_rows = local_elements / static_cast<int>(n);

    std::vector<double> a_local(local_elements);
    std::vector<double> c_local(local_elements, 0.0);

    MPI_Scatterv(a.data(), send_counts.data(), displs.data(), MPI_DOUBLE,
                 a_local.data(), local_elements, MPI_DOUBLE,
                 0, MPI_COMM_WORLD);

    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();

    for (int i = 0; i < local_rows; ++i) {
        for (size_t k = 0; k < n; ++k) {
            double r = a_local[i * n + k];
            for (size_t j = 0; j < n; ++j) {
                c_local[i * n + j] += r * b[k * n + j];
            }
        }
    }

    MPI_Barrier(MPI_COMM_WORLD);
    double end_time = MPI_Wtime();
    double elapsed = end_time - start_time;

    MPI_Gatherv(c_local.data(), local_elements, MPI_DOUBLE,
                c.data(), send_counts.data(), displs.data(), MPI_DOUBLE,
                0, MPI_COMM_WORLD);

    if (rank == 0) {
        std::ofstream fout(path_out);
        if (fout.is_open()) {
            fout << n << "\n";
            fout << std::fixed << std::setprecision(6);
            fout << "# Время (сек): " << elapsed << "\n";
            for (size_t i = 0; i < n; ++i) {
                for (size_t j = 0; j < n; ++j) {
                    fout << c[i * n + j] << (j + 1 == n ? "" : " ");
                }
                fout << "\n";
            }
            fout.close();
        }

        double ops = 2.0 * static_cast<double>(n) * static_cast<double>(n) * static_cast<double>(n);
        double gops = (elapsed > 0.0) ? (ops / elapsed / 1e9) : 0.0;

        std::cout << "lab3,"
                  << n << ","
                  << num_procs << ","
                  << std::fixed << std::setprecision(6) << elapsed << ","
                  << std::scientific << std::setprecision(2) << ops << ","
                  << std::fixed << std::setprecision(4) << gops << "\n";
    }

    MPI_Finalize();
    return 0;
}