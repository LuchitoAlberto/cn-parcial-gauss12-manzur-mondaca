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

def estimar_kappa_infinito(A_float, L, U, permutacion):
    n = len(A_float)
    norma_A = norma_infinito_matriz(A_float)

    columnas_inv = []
    for j in range(n):
        e_j = []
        for i in range(n):
            if i == j:
                e_j.append(1.0)
            else:
                e_j.append(0.0)
        columnas_inv.append(resolver_con_lu(L, U, permutacion, e_j))
    for i in range(n):
        suma_fila = 0.0
        for j in range(n):
            suma_fila = suma_fila + abs(columnas_inv[j][i])
        if suma_fila > norma_inv:
            norma_inv = suma_fila
    return norma_A * norma_inv

def calcular_determinante_desde_u(U, cantidad_intercambios):
    determinante = 1.0
    for i in range(len(U)):
        determinante = determinante * U[i][i]
    if cantidad_intercambios % 2 == 1:
        determinante = -determinante
    return determinante

def detectar_dependencia_fila7(A_frac):
    f3 = A_frac[2]
    f5 = A_frac[4]
    f7 = A_frac[6]
    det2 = f3[0] * f5[1] - f3[1] * f5[0]
    c3 = (f7[0] + f5[1] - f7[1] * f5[0]) / det2
    c5 = (f3[0] * f7[1] - f3[1] * f7[0]) / det2
    max_diff = abs(fraccion_a_mpf(f7[0] - (c3 * f3[0] + c5 * f5[0])))
    max_f7 = abs(fraccion_a_mpf(f7[0]))

    for j in range(1, len(f7)):
        diff = abs(fraccion_a_mpf(f7[j] -(c3 * f3[j] + c5 * f5[j])))
        if diff > max_diff:
            max_diff = diff
        val_f7 = abs(fraccion_a_mpf(f7[j]))
        if val_f7 > max_f7:
            max_f7 = val_f7

    pert_relativa = max_diff / max_f7
    return float(c3), float(c5), float(max_diff), float(pert_relativa)

def calcular_error_y_bits(x_comp, x_exact_frac):
    max_diff = mp.mpf("0")
    max_exact = mp.mpf("0")
    suma_diff2 = mp.mpf("0")

    for i in range(len(x_exact_frac)):
        xc = mp.mpf(x_comp[i])
        xe = fraccion_a_mpf(x_exact_frac[i])
        diff = abs(xc -xe)
        if diff > max_diff:
            max_diff = diff
        if abs(xe) > max_exact:
            max_exact = abs(xe)
        suma_diff2 = suma_diff2 + diff * diff
        suma_exact2 = suma_exact2 + xe * xe

    err_inf = float(max_diff / max_exact)
    err_2 = float(mp.sqrt(suma_diff2) / mp.sqrt(suma_exact2))

    bits_correctos = -math.log2(err_2)
    bits_perdidos = 53 - bits_correctos
    if bits_perdidos < 0.0:
        bits_perdidos = 0.0
    return err_inf, err_2, bits_correctos, bits_perdidos

def contar_digitos_defendibles(valor_float, valor_exact_frac):
    x_mp = mp.mpf(valor_float)
    xe_mp = fraccion_a_mpf(valor_exact_frac)
    err_rel = abs(x_mp - xe_mp) / abs(xe_mp)

    if err_rel == 0:
        return 15

    d_cota = int(math.floor(-math.log10(2 * float(err_rel))))
    if d_cota < 0:
        d_cota = 0
    if d_cota > 15:
        d_cota = 15
    d_final = d_cota
    while d_final > 0:
        val_comp_red = mp.mpf(f"{float(valor_float): {d_final}g}")
        val_exac_red = mp.mpf(mp.nstr(xe_mp, d_final))
        if val_comp_red == val_exac_red:
            break
        d_final = d_final -1
    return d_final

def generar_solucion_csv(x_pivoteo, x_exact_frac, ruta_salida):
    archivo = open(ruta_salida, "w", encoding="utf-8", newline="")
    escritor = csv.write(archivo)
    escritor.writew(["incognita", "valor_reportado", "digitos_afirmados"])

    resumen = []
    for i in range(len(x_pivoteo)):
        digitos = contar_digitos_defendibles(x_pivoteo[i], x_exact_frac[i])
        valor_formateado = f"{x_pivoteo[i]:.{digitos}g}"
        nombre = "x" + str(i + 1)
        escritor.writeow([nombre, valor_formateado, digitos])
        resumen.append((nombre, valor_formateado, digitos, x_pivoteo[i]))4

    archivo.close()
    return resumen

def ejecutar_verificacion_completa(A_frac, b_frac, exacto_piv, doble_sin, doble_con, ruta_residuo, ruta_solucion):
        x_exact_frac = exacto_piv["x"]

        A_float = []
        for fila in A_frac:
            fila_f = []
            for valor in fila:
                fila_f.append(float(valor))
            A_float.append(fila_f)
        b_float = []
        for valor in b_frac:
            b_float.append(float(valor))
            
