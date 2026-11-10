import subprocess
import os
import sys
import re
import matplotlib.pyplot as plt

THREADS = [1, 2, 3, 4, 8, 16]
VIEW = 1  # Базовый ракурс для анализа по условию задания

# Поиск исполняемого файла
CANDIDATES = [
    os.path.join("build", "Release", "mandelbrot.exe"),
    os.path.join("build", "mandelbrot.exe"),
    os.path.join("build", "mandelbrot"),
    os.path.join(".", "mandelbrot.exe"),
    os.path.join(".", "mandelbrot")
]

EXEC_PATH = None
for path in CANDIDATES:
    if os.path.exists(path):
        EXEC_PATH = path
        break

if not EXEC_PATH:
    print("ОШИБКА: Исполняемый файл 'mandelbrot' не найден в папке build/ или текущей директории.")
    sys.exit(1)

results_thread_ms = []
serial_time_ms = None

print(f"Используется бинарник: {EXEC_PATH}")
print(f"Тестирование на View {VIEW} для потоков: {THREADS}\n")

# Регулярные выражения для парсинга вывода
re_serial = re.compile(r"\[mandelbrot serial\]:\s+\[([\d\.]+)\]\s+ms")
re_thread = re.compile(r"\[mandelbrot thread\]:\s+\[([\d\.]+)\]\s+ms")

for t in THREADS:
    cmd = [EXEC_PATH, "-t", str(t), "-v", str(VIEW)]
    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode != 0:
        print(f"Ошибка при запуске на {t} потоках: {res.stderr}")
        sys.exit(1)

    out = res.stdout

    # Замер последовательного времени фиксируется при первом запуске
    if serial_time_ms is None:
        match_s = re_serial.search(out)
        if match_s:
            serial_time_ms = float(match_s.group(1))

    match_t = re_thread.search(out)
    if not match_t:
        print(f"Не удалось распарсить время потоков для {t} потоков:\n{out}")
        sys.exit(1)

    t_ms = float(match_t.group(1))
    results_thread_ms.append(t_ms)
    print(f"Потоков: {t:<2} | Время: {t_ms:<8.3f} мс")

# Расчет метрик ускорения
speedups = [serial_time_ms / t_ms for t_ms in results_thread_ms]
efficiencies = [(s / t) * 100 for s, t in zip(speedups, THREADS)]

# Вывод сводной Markdown-таблицы
print("\n### Таблица результатов для README.md\n")
print(f"Последовательная версия (Serial): {serial_time_ms:.3f} мс\n")
print("| Потоки (p) | Время (мс) | Ускорение S(p) | Эффективность E(p) |")
print("|:----------:|:----------:|:--------------:|:------------------:|")
for t, t_ms, s, e in zip(THREADS, results_thread_ms, speedups, efficiencies):
    print(f"| {t:<10} | {t_ms:<10.3f} | {s:<14.2f}x | {e:<17.1f}% |")

# 1. Построение графика времени выполнения
plt.figure(figsize=(8, 5))
plt.plot(THREADS, results_thread_ms, marker='o', color='#1f77b4', linewidth=2, label='Многопоточная версия')
plt.axhline(y=serial_time_ms, color='r', linestyle='--', label=f'Serial ({serial_time_ms:.1f} мс)')
plt.title(f'Время рендеринга фрактала Мандельброта (View {VIEW})')
plt.xlabel('Количество потоков (p)')
plt.ylabel('Время выполнения (мс)')
plt.xticks(THREADS)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig('time_plot.png', dpi=300)
plt.close()

# 2. Построение графика ускорения
plt.figure(figsize=(8, 5))
plt.plot(THREADS, speedups, marker='s', color='#2ca02c', linewidth=2, label='Экспериментальное ускорение')
plt.plot(THREADS, THREADS, linestyle='--', color='gray', label='Идеальное ускорение (S = p)')
plt.title(f'Ускорение S(p) генерации фрактала (View {VIEW})')
plt.xlabel('Количество потоков (p)')
plt.ylabel('Ускорение S = T_serial / T_thread')
plt.xticks(THREADS)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig('speedup_plot.png', dpi=300)
plt.close()

print("\nГрафики успешно сохранены: lab5/time_plot.png и lab5/speedup_plot.png")