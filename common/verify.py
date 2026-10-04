import sys
import numpy as np

def verify(file_a: str, file_b: str, file_res: str):
    a = np.loadtxt(file_a, skiprows=1)
    b = np.loadtxt(file_b, skiprows=1)

    c_actual = np.loadtxt(file_res, skiprows=2)

    c_expected = a @ b

    if np.allclose(c_actual, c_expected, rtol=1e-5, atol=1e-5):
        max_diff = np.max(np.abs(c_actual - c_expected))
        print("ВЕРИФИКАЦИЯ: УСПЕШНО (OK)")
        print(f"Максимальная абсолютная погрешность: {max_diff:.2e}")
    else:
        print("ВЕРИФИКАЦИЯ: ОШИБКА (FAIL)")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        verify("matrix_a.txt", "matrix_b.txt", "matrix_c.txt")
    else:
        verify(sys.argv[1], sys.argv[2], sys.argv[3])