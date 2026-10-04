import subprocess
import os
import sys
import matplotlib.pyplot as plt

# ==============================================================================

TARGET_NAME = "matrix_omp"
PARAM_LABEL = "Потоки"
SIZES       = [200, 400, 800, 1200, 1600, 2000]
PARAMS      = [1, 2, 4, 8, 16]

def build_command(binary: str, file_a: str, file_b: str, file_c: str, param: int) -> list:
    """Формирование команды запуска в зависимости от технологии."""
    return [binary, file_a, file_b, file_c, str(param)]

# ==============================================================================

def find_executable(name: str) -> str:
    candidates = [
        os.path.join("build", "Release", f"{name}.exe"),
        os.path.join("build", f"{name}.exe"),
        os.path.join("build", name),
        os.path.join(".", name)
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    print(f"ОШИБКА: Исполняемый файл для '{name}' не найден.")
    sys.exit(1)

EXEC_PATH = find_executable(TARGET_NAME)
GEN_SCRIPT = os.path.join("..", "common", "generate.py")
FILE_A, FILE_B, FILE_C = "matrix_a.txt", "matrix_b.txt", "matrix_c.txt"

results = {n: {} for n in SIZES}
print(f"Запуск бенчмарка: {EXEC_PATH}\nПараметр '{PARAM_LABEL}': {PARAMS}\n", flush=True)

for n in SIZES:
    print(f"[{n}x{n}] Генерация данных...", end="", flush=True)
    subprocess.run(["python", GEN_SCRIPT, str(n)], check=True, stdout=subprocess.DEVNULL)
    print("\r", end="", flush=True)

    for p in PARAMS:
        print(f"[{n}x{n}] {PARAM_LABEL}: {p} ... ", end="", flush=True)
        cmd = build_command(EXEC_PATH, FILE_A, FILE_B, FILE_C, p)
        run_res = subprocess.run(cmd, capture_output=True, text=True)

        if run_res.returncode != 0:
            print(f"\nОшибка выполнения: {run_res.stderr}")
            sys.exit(1)

        elapsed = 0.0
        with open(FILE_C, "r") as f:
            for line in f:
                if "Время (сек):" in line:
                    elapsed = float(line.split(":")[1].strip())
                    break

        results[n][p] = elapsed
        print(f"{elapsed:.4f} сек.", flush=True)

for tmp in [FILE_A, FILE_B, FILE_C]:
    if os.path.exists(tmp):
        os.remove(tmp)

# ==============================================================================

print("\n" + "="*50)
print("РЕЗУЛЬТАТЫ ДЛЯ ТАБЛИЦ В README.md")
print("="*50 + "\n")

if len(PARAMS) == 1:
    p = PARAMS[0]
    print("| Размер матрицы (N) | Количество операций (FLOP) | Время выполнения (сек) |")
    print("|:------------------:|:--------------------------:|:----------------------:|")
    for n in SIZES:
        flops = 2 * (n ** 3)
        print(f"| {n:<18} | {flops:<26.2e} | {results[n][p]:<22.4f} |")

    plt.figure(figsize=(9, 5))
    plt.plot(SIZES, [results[n][p] for n in SIZES], marker='o', color='b', linewidth=2)
    plt.title('Время последовательного умножения матриц')
    plt.xlabel('Размер матрицы N')
    plt.ylabel('Время (сек)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('plot.png', dpi=300)
    print("\nГрафик сохранен: plot.png")

else:
    header = "| Размер (N) | " + " | ".join([f"{p} {PARAM_LABEL}" for p in PARAMS]) + " |"
    print(header)
    print("|:---:|" + ":---:|" * len(PARAMS))
    for n in SIZES:
        row = f"| {n} | " + " | ".join([f"{results[n][p]:.4f}" for p in PARAMS]) + " |"
        print(row)

    plt.figure(figsize=(9, 5))
    for p in PARAMS:
        plt.plot(SIZES, [results[n][p] for n in SIZES], marker='o', label=f'{p} {PARAM_LABEL}')
    plt.title(f'Сравнение времени работы ({TARGET_NAME})')
    plt.xlabel('Размер матрицы N')
    plt.ylabel('Время (сек)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig('time_plot.png', dpi=300)
    plt.close()

    max_n = SIZES[-1]
    base_t = results[max_n][PARAMS[0]]
    speedups = [base_t / results[max_n][p] for p in PARAMS]

    plt.figure(figsize=(8, 5))
    plt.plot(PARAMS, speedups, marker='s', color='r', label='Экспериментальное ускорение')
    plt.plot(PARAMS, PARAMS, linestyle='--', color='gray', label='Идеальное ускорение')
    plt.title(f'Ускорение S({PARAM_LABEL}) для матрицы {max_n}x{max_n}')
    plt.xlabel(PARAM_LABEL)
    plt.ylabel('S = T1 / Tp')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig('speedup_plot.png', dpi=300)
    plt.close()

    print("\nГрафики сохранены: time_plot.png и speedup_plot.png")