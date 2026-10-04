#include <iostream>
#include <vector>
#include <fstream>
#include <iomanip>
#include <string>
#include <omp.h>

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Использование: " << argv[0] << " <file_A> <file_B> <file_result> [num_threads]\n";
        return 1;
    }

    std::string path_a = argv[1];
    std::string path_b = argv[2];
    std::string path_out = argv[3];
    
    int threads = (argc >= 5) ? std::stoi(argv[4]) : omp_get_max_threads();
    omp_set_num_threads(threads);

    std::ifstream fa(path_a);
    std::ifstream fb(path_b);

    if (!fa.is_open() || !fb.is_open()) {
        std::cerr << "Ошибка: Не удалось открыть входные файлы\n";
        return 1;
    }

    size_t n_a, n_b;
    fa >> n_a;
    fb >> n_b;

    if (n_a != n_b) {
        std::cerr << "Ошибка: Размеры матриц не совпадают\n";
        return 1;
    }

    const size_t n = n_a;
    std::vector<double> a(n * n);
    std::vector<double> b(n * n);
    std::vector<double> c(n * n, 0.0);

    for (size_t i = 0; i < n * n; ++i) fa >> a[i];
    for (size_t i = 0; i < n * n; ++i) fb >> b[i];

    fa.close();
    fb.close();

    double start_time = omp_get_wtime();

    #pragma omp parallel for schedule(static)
    for (int i = 0; i < static_cast<int>(n); ++i) {
        for (size_t k = 0; k < n; ++k) {
            double r = a[i * n + k];
            for (size_t j = 0; j < n; ++j) {
                c[i * n + j] += r * b[k * n + j];
            }
        }
    }

    double end_time = omp_get_wtime();
    double elapsed = end_time - start_time;

    std::ofstream fout(path_out);
    if (!fout.is_open()) {
        std::cerr << "Ошибка: Не удалось создать файл вывода\n";
        return 1;
    }

    fout << n << "\n";
    fout << std::fixed << std::setprecision(6);
    fout << "# Время (сек): " << elapsed << "\n";
    fout << "# Потоков: " << threads << "\n";

    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            fout << c[i * n + j] << (j + 1 == n ? "" : " ");
        }
        fout << "\n";
    }
    fout.close();

    std::cout << "Размер: " << n << "x" << n << " | Потоков: " << threads 
              << " | Время: " << elapsed << " сек.\n";

    return 0;
}