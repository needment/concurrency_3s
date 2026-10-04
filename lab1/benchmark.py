import subprocess
import os
import sys
import matplotlib.pyplot as plt

SIZES = [200, 400, 800, 1200, 1600, 2000]

if os.path.exists(os.path.join("build", "Release", "matrix_serial.exe")):
    EXEC_PATH = os.path.join("build", "Release", "matrix_serial.exe")
elif os.path.exists(os.path.join("build", "matrix_serial.exe")):
    EXEC_PATH = os.path.join("build", "matrix_serial.exe")
else:
    print("ОШИБКА: Исполняемый файл matrix_serial.exe не найден в папке build/")
    sys.exit(1)

RESULTS = []

print(f"Используется бинарник: {EXEC_PATH}\n", flush=True)
print("| Размер матрицы (N) | Количество операций (FLOP) | Время выполнения (сек) |", flush=True)
print("|--------------------|----------------------------|------------------------|", flush=True)

for n in SIZES:
    print(f"[{n}x{n}] 1/2 Генерация данных...", end="", flush=True)
    gen_res = subprocess.run(["python", os.path.join("..", "common", "generate.py"), str(n)])
    if gen_res.returncode != 0:
        print(f"\nОшибка генерации данных на N={n}")
        sys.exit(1)

    print(f"\r[{n}x{n}] 2/2 Вычисление C++...   ", end="", flush=True)
    cmd = [EXEC_PATH, "matrix_a.txt", "matrix_b.txt", "matrix_c.txt"]
    run_res = subprocess.run(cmd, capture_output=True, text=True)
    if run_res.returncode != 0:
        print(f"\nОшибка выполнения C++: {run_res.stderr}")
        sys.exit(1)

    elapsed = 0.0
    with open("matrix_c.txt", "r") as f:
        for line in f:
            if "Время (сек):" in line:
                elapsed = float(line.split(":")[1].strip())
                break

    flops = 2 * (n ** 3)
    RESULTS.append((n, flops, elapsed))
    print(f"\r| {n:<18} | {flops:<26.2e} | {elapsed:<22.4f} |", flush=True)

for tmp_file in ["matrix_a.txt", "matrix_b.txt", "matrix_c.txt"]:
    if os.path.exists(tmp_file):
        os.remove(tmp_file)

ns = [r[0] for r in RESULTS]
times = [r[2] for r in RESULTS]

plt.figure(figsize=(9, 5))
plt.plot(ns, times, marker='o', color='b', linewidth=2, label='Последовательная версия (MSVC /O2)')
plt.title('Зависимость времени последовательного умножения от размера матрицы')
plt.xlabel('Размер матрицы N (N x N)')
plt.ylabel('Время выполнения (сек)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig('plot.png', dpi=300)
print("\nУспешно. График сохранен в lab1/plot.png", flush=True)