import sys
import numpy as np

def generate_matrix(filename: str, n: int):
    data = np.random.uniform(-10.0, 10.0, size=(n, n))
    with open(filename, 'w') as f:
        f.write(f"{n}\n")
        np.savetxt(f, data, fmt='%.6f')

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    generate_matrix("matrix_a.txt", n)
    generate_matrix("matrix_b.txt", n)
    print(f"Сгенерированы матрицы A и B размера {n}x{n}")