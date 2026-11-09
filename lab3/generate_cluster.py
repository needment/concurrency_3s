import sys
import random

def generate_matrix(filename: str, n: int):
    with open(filename, 'w') as f:
        f.write(f"{n}\n")
        for _ in range(n):
            row = [f"{random.uniform(-10.0, 10.0):.6f}" for _ in range(n)]
            f.write(" ".join(row) + "\n")

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    file_a = sys.argv[2] if len(sys.argv) > 2 else "matrix_a.txt"
    file_b = sys.argv[3] if len(sys.argv) > 3 else "matrix_b.txt"
    generate_matrix(file_a, n)
    generate_matrix(file_b, n)