"""Dependency-free statistics helpers."""

from __future__ import annotations

import math
from typing import Iterable


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def mean(values: Iterable[float]) -> float:
    vals = list(values)
    if not vals:
        raise ValueError("mean requires at least one value")
    return sum(vals) / len(vals)


def percentile_rank(values: list[float], value: float) -> float | None:
    if not values:
        return None
    below = sum(1 for item in values if item < value)
    equal = sum(1 for item in values if item == value)
    return 100.0 * (below + 0.5 * equal) / len(values)


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*matrix)]


def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    if not a or not b:
        raise ValueError("matmul requires non-empty matrices")
    rows = len(a)
    inner = len(b)
    cols = len(b[0])
    out = [[0.0 for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for k in range(inner):
            aik = a[i][k]
            for j in range(cols):
                out[i][j] += aik * b[k][j]
    return out


def invert(matrix: list[list[float]]) -> list[list[float]]:
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("invert requires a non-empty square matrix")

    augmented = [
        [float(matrix[i][j]) for j in range(n)]
        + [1.0 if i == j else 0.0 for j in range(n)]
        for i in range(n)
    ]

    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(augmented[r][col]))
        pivot = augmented[pivot_row][col]
        if abs(pivot) < 1e-12:
            raise ValueError("matrix is singular")
        if pivot_row != col:
            augmented[col], augmented[pivot_row] = augmented[pivot_row], augmented[col]

        pivot = augmented[col][col]
        for j in range(2 * n):
            augmented[col][j] /= pivot

        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            if factor == 0:
                continue
            for j in range(2 * n):
                augmented[row][j] -= factor * augmented[col][j]

    return [row[n:] for row in augmented]


def ols(
    y: list[float],
    x: list[list[float]],
    names: list[str],
) -> dict[str, object]:
    if len(y) != len(x):
        raise ValueError("y and x must have the same number of observations")
    if not y:
        raise ValueError("ols requires observations")
    if len(x[0]) != len(names):
        raise ValueError("x column count must match names")
    n = len(y)
    k = len(names)
    if n <= k:
        raise ValueError(f"ols requires more observations than variables: n={n}, k={k}")

    xt = transpose(x)
    xtx = matmul(xt, x)
    xtx_inv = invert(xtx)
    xty = matmul(xt, [[val] for val in y])
    beta_matrix = matmul(xtx_inv, xty)
    betas = [row[0] for row in beta_matrix]

    fitted = [sum(row[j] * betas[j] for j in range(k)) for row in x]
    residuals = [actual - pred for actual, pred in zip(y, fitted)]
    sse = sum(resid * resid for resid in residuals)
    y_mean = mean(y)
    tss = sum((val - y_mean) ** 2 for val in y)
    dof = n - k
    sigma2 = sse / dof
    se = [math.sqrt(max(0.0, sigma2 * xtx_inv[i][i])) for i in range(k)]
    t_stats = [
        betas[i] / se[i] if se[i] > 0 else float("nan")
        for i in range(k)
    ]

    coefficients = {
        name: {
            "beta": betas[i],
            "std_error": se[i],
            "t_stat": t_stats[i],
        }
        for i, name in enumerate(names)
    }
    return {
        "coefficients": coefficients,
        "observations": n,
        "r_squared": 1.0 - sse / tss if tss > 0 else 0.0,
        "residual_std_error": math.sqrt(sigma2),
    }

