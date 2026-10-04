#include <iostream>
#include <vector>
#include <fstream>
#include <chrono>
#include <iomanip>

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Использование: " << argv[0] << " <file_A> <file_B> <file_result>\n";
        return 1;
    }

    std::string path_a = argv[1];
    std::string path_b = argv[2];
    std::string path_out = argv[3];

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
        std::cerr << "Ошибка: Матрицы должны быть одинакового размера\n";
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

    // Замер чистого времени вычислений
    auto start_time = std::chrono::high_resolution_clock::now();

    // Оптимальный порядок обхода i-k-j (Spatial Locality)
    for (size_t i = 0; i < n; ++i) {
        for (size_t k = 0; k < n; ++k) {
            double r = a[i * n + k];
            for (size_t j = 0; j < n; ++j) {
                c[i * n + j] += r * b[k * n + j];
            }
        }
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;

    // Запись результатов
    std::ofstream fout(path_out);
    if (!fout.is_open()) {
        std::cerr << "Ошибка: Не удалось создать файл вывода\n";
        return 1;
    }

    fout << n << "\n";
    fout << std::fixed << std::setprecision(6);
    fout << "# Время (сек): " << elapsed.count() << "\n";

    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            fout << c[i * n + j] << (j + 1 == n ? "" : " ");
        }
        fout << "\n";
    }
    fout.close();

    std::cout << "Размер: " << n << "x" << n << "\n";
    std::cout << "Время выполнения: " << elapsed.count() << " сек.\n";

    return 0;
}