#include <iostream>
#include <vector>
#include <fstream>
#include <iomanip>
#include <string>
#include <cuda_runtime.h>

#define CUDA_CHECK(call) \
    do { \
        cudaError_t err = call; \
        if (err != cudaSuccess) { \
            std::cerr << "CUDA Error: " << cudaGetErrorString(err) \
                      << " at line " << __LINE__ << std::endl; \
            exit(1); \
        } \
    } while (0)

__global__ void matrixMulKernel(const double* A, const double* B, double* C, int n) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < n && col < n) {
        double sum = 0.0;
        for (int k = 0; k < n; ++k) {
            sum += A[row * n + k] * B[k * n + col];
        }
        C[row * n + col] = sum;
    }
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Использование: " << argv[0] << " <file_A> <file_B> <file_result> [block_dim]\n";
        return 1;
    }

    std::string path_a = argv[1];
    std::string path_b = argv[2];
    std::string path_out = argv[3];
    int block_dim = (argc >= 5) ? std::stoi(argv[4]) : 16;

    std::ifstream fa(path_a), fb(path_b);
    if (!fa.is_open() || !fb.is_open()) {
        std::cerr << "Ошибка открытия файлов ввода\n";
        return 1;
    }

    size_t n, n_b;
    fa >> n;
    fb >> n_b;

    if (n != n_b) {
        std::cerr << "Размеры матриц не совпадают\n";
        return 1;
    }

    size_t size_bytes = n * n * sizeof(double);
    std::vector<double> h_a(n * n);
    std::vector<double> h_b(n * n);
    std::vector<double> h_c(n * n, 0.0);

    for (size_t i = 0; i < n * n; ++i) fa >> h_a[i];
    for (size_t i = 0; i < n * n; ++i) fb >> h_b[i];

    fa.close();
    fb.close();

    double *d_a = nullptr, *d_b = nullptr, *d_c = nullptr;
    CUDA_CHECK(cudaMalloc(&d_a, size_bytes));
    CUDA_CHECK(cudaMalloc(&d_b, size_bytes));
    CUDA_CHECK(cudaMalloc(&d_c, size_bytes));

    CUDA_CHECK(cudaMemcpy(d_a, h_a.data(), size_bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_b, h_b.data(), size_bytes, cudaMemcpyHostToDevice));

    dim3 block(block_dim, block_dim);
    dim3 grid((static_cast<unsigned int>(n) + block.x - 1) / block.x,
              (static_cast<unsigned int>(n) + block.y - 1) / block.y);

    cudaEvent_t start, stop;
    CUDA_CHECK(cudaEventCreate(&start));
    CUDA_CHECK(cudaEventCreate(&stop));

    CUDA_CHECK(cudaEventRecord(start));
    matrixMulKernel<<<grid, block>>>(d_a, d_b, d_c, static_cast<int>(n));
    CUDA_CHECK(cudaEventRecord(stop));
    CUDA_CHECK(cudaEventSynchronize(stop));

    float ms = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&ms, start, stop));
    double elapsed = ms / 1000.0;

    CUDA_CHECK(cudaMemcpy(h_c.data(), d_c, size_bytes, cudaMemcpyDeviceToHost));

    CUDA_CHECK(cudaFree(d_a));
    CUDA_CHECK(cudaFree(d_b));
    CUDA_CHECK(cudaFree(d_c));
    CUDA_CHECK(cudaEventDestroy(start));
    CUDA_CHECK(cudaEventDestroy(stop));

    std::ofstream fout(path_out);
    if (!fout.is_open()) {
        std::cerr << "Ошибка создания файла вывода\n";
        return 1;
    }

    fout << n << "\n";
    fout << std::fixed << std::setprecision(6);
    fout << "# Время (сек): " << elapsed << "\n";
    fout << "# Блок: " << block_dim << "x" << block_dim << "\n";

    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            fout << h_c[i * n + j] << (j + 1 == n ? "" : " ");
        }
        fout << "\n";
    }
    fout.close();

    std::cout << "Размер: " << n << "x" << n << " | Блок: " << block_dim << "x" << block_dim 
              << " | Время: " << elapsed << " сек.\n";

    return 0;
}