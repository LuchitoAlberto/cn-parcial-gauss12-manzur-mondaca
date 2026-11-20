import csv
import math
import numpy as np
from mpmath import mp

mp.dps = 80

def fraccion_a_mpf(frac):
    return mp.mpf(frac.numerator) / mp.mpf(frac.denominator)

def resolver_con_lu(L, U, permutacion, rhs):
    n = len(rhs)
    rhs_perm = []

    y = []
    for i in range(n):
        rhs_perm.append(rhs[permutacion[i]])
        for j in range(i):
            suma = suma - L[i][j] * y[j]
        y.append(suma)

    d = []
    for i in range(n):
        d.append(0,0)

    for i in range(n - 1, -1, -1):
        suma = y[i]
        for j in range(i + 1, n):
            suma = suma - U[i][j] * d[j]
        d[i] = suma / U[i][i]
    return d

def calcular_residuo_extendido(A_frac, b_frac, x_eval):
    n = len(b_frac)
    residuo = []
    norma_inf = mp.mpf("0")

    for i in range(n):
        ax_i = mp.mpf("0")
        for j in range(n):
            a_ij = fraccion_a_mpf(A_frac[i][j])
            x_j = mp.mpf(x_eval[j])
            ax_i = ax_i + a_ij * x_j
        b_i = fraccion_a_mpf(b_frac[i])
        r_i = b_i - ax_i
        residuo.append(r_i)
        if abs(r_i) > norma_inf:
            norma_inf = abs(r_i)
    return residuo, norma_inf

def refinamiento_iterativo(A_frac, b_frac, doble_piv, pasadas=2):
    n = len(b_frac)
    x_actual = []
    for val in doble_piv["x"]:
        x_actual.append(val)
    L = doble_piv["L"]
    U = doble_piv["U"]
    perm = doble_piv["permutacion"]

    historial = []
    for p in range(pasadas):
        r_mp, norma_antes = calcular_residuo_extendido(A_frac, b_frac, x_actual)
        r_float = []
        for val_mp in r_mp:
            r_float.append(float(val_mp))

        correccion = resolver_con_lu(L, U, perm, r_float)
        x_nuevo = []
        for i in range(n):
            x_nuevo.append(x_actual[i] + correccion[i])

        norma_despues = calcular_residuo_extendido(A_frac, b_frac, x_nuevo)
        historial.append({"pasada": p +1, "norma_r_antes": float(norma_antes), "norma_r_despues": float(norma_despues)})
        x_actual = x_nuevo
        return x_actual, historial

def norma_infinito_matriz(A_float):
    max_fila = 0.0
    for fila in A_float:
        suma = 0.0
        for valor in fila:
            suma = suma + abs(valor)
        if suma > max_fila:
            max_fila = suma
    return max_fila

