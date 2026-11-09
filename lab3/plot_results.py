import pandas as pd
import matplotlib.pyplot as plt

# Загрузка скачанного CSV
df = pd.read_csv("results.csv")

# Усреднение по повторам
avg_df = df.groupby(['n', 'workers'], as_index=False)['time_s'].mean()

# Сводная таблица времени
pivot_time = avg_df.pivot(index='n', columns='workers', values='time_s')
print("### Таблица времени выполнения (сек):\n")
print(pivot_time.to_markdown())

# Расчет ускорения S = T(1) / T(p)
speedup = pivot_time.div(pivot_time[1], axis=0).pow(-1)
print("\n### Таблица ускорения:\n")
print(speedup.to_markdown())

sizes = pivot_time.index.values
procs = pivot_time.columns.values

# 1. График времени выполнения
plt.figure(figsize=(9, 5))
for p in procs:
    plt.plot(sizes, pivot_time[p], marker='o', label=f'{p} процесс(ов)')
plt.title('Время умножения матриц (MPI, кластер)')
plt.xlabel('Размер матрицы N')
plt.ylabel('Время выполнения (сек)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig('time_plot.png', dpi=300)
plt.close()

# 2. График ускорения для максимального размера N
max_n = sizes[-1]
speedups_max_n = speedup.loc[max_n].values

plt.figure(figsize=(8, 5))
plt.plot(procs, speedups_max_n, marker='s', color='r', label='Экспериментальное ускорение')
plt.plot(procs, procs, linestyle='--', color='gray', label='Идеальное (линейное)')
plt.title(f'Ускорение S(p) для матрицы {max_n}x{max_n} (MPI)')
plt.xlabel('Количество процессов (p)')
plt.ylabel('Ускорение S = T1 / Tp')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig('speedup_plot.png', dpi=300)
plt.close()

print("\nГрафики time_plot.png и speedup_plot.png сформированы.")