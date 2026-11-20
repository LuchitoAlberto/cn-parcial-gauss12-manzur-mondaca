import csv
import math
import numpy as np
from mpmath import mp

mp.dps = 80

def fraccion_a_mpf(frac):
    return mp.mpf(frac.numerator) / mp.mpf(frac.denominator)

def resolver_con_lu(L, U, permutacion, rhs, contador=None):
    n = len(rhs)

    # Sustitucion hacia adelante: L y = P b (L tiene 1's en la diagonal)
    y = []
    for i in range(n):
        suma = rhs[permutacion[i]]
        for j in range(i):
            suma = suma - L[i][j] * y[j]
            if contador is not None:
                contador.sust_prog_reutilizacion_flops += 2 # Una multiplicacion y una resta, sin volver a eliminar
        y.append(suma)

    d = []
    for i in range(n):
        d.append(0.0)

    # Sustitucion para atras: U d = y
    for i in range(n - 1, -1, -1):
        suma = y[i]
        for j in range(i + 1, n):
            suma = suma - U[i][j] * d[j]
            if contador is not None:
                contador.sust_reg_reutilizacion_flops += 2 # Una multiplicacion y una resta
        d[i] = suma / U[i][i]
        if contador is not None:
            contador.sust_reg_reutilizacion_flops += 1 # La division por el pivote
    return d

def calcular_residuo_extendido(A_frac, b_frac, x_eval):
    n = len(b_frac)
    residuo = []
    norma_inf = mp.mpf("0")

    # Todo el producto A * x se hace en mpf para que el residuo no se pierda en el redondeo
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

def refinamiento_iterativo(A_frac, b_frac, doble_piv, pasadas=3):
    n = len(b_frac)

    # x se guarda en mpf, si fuera float la correccion se perderia al redondear
    x_actual = []
    for valor in doble_piv["x"]:
        x_actual.append(mp.mpf(valor))
    L = doble_piv["L"]
    U = doble_piv["U"]
    perm = doble_piv["permutacion"]
    contador = doble_piv["contador"] # Aqui se acumulan los flops de reusar L y U

    historial = []
    for p in range(pasadas):
        r_mp, norma_antes = calcular_residuo_extendido(A_frac, b_frac, x_actual)
        r_float = []
        for valor_mp in r_mp:
            r_float.append(float(valor_mp))

        # Reusamos la misma L y U, no se factoriza otra vez
        correccion = resolver_con_lu(L, U, perm, r_float, contador)
        x_nuevo = []
        for i in range(n):
            x_nuevo.append(x_actual[i] + mp.mpf(correccion[i]))

        _, norma_despues = calcular_residuo_extendido(A_frac, b_frac, x_nuevo)
        historial.append({"pasada": p + 1, "norma_r_antes": float(norma_antes), "norma_r_despues": float(norma_despues)})
        x_actual = x_nuevo

    # El return va afuera del for para que se hagan todas las pasadas
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

def estimar_kappa_infinito(A_float, L, U, permutacion, contador=None):
    n = len(A_float)
    norma_A = norma_infinito_matriz(A_float)

    # La columna j de A^-1 es la solucion de A x = e_j (reusamos L y U)
    columnas_inv = []
    for j in range(n):
        e_j = []
        for i in range(n):
            if i == j:
                e_j.append(1.0)
            else:
                e_j.append(0.0)
        columnas_inv.append(resolver_con_lu(L, U, permutacion, e_j, contador))

    norma_inv = 0.0
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

    # Cada intercambio de filas cambia el signo del determinante
    if cantidad_intercambios % 2 == 1:
        determinante = -determinante
    return determinante

def detectar_dependencia_fila7(A_frac):
    f3 = A_frac[2]
    f5 = A_frac[4]
    f7 = A_frac[6]

    # Buscamos c3 y c5 tales que fila7 ~ c3 * fila3 + c5 * fila5, usando las dos primeras columnas (Cramer)
    det2 = f3[0] * f5[1] - f3[1] * f5[0]
    c3 = (f7[0] * f5[1] - f7[1] * f5[0]) / det2
    c5 = (f3[0] * f7[1] - f3[1] * f7[0]) / det2

    max_diff = mp.mpf("0")
    max_f7 = mp.mpf("0")
    for j in range(len(f7)):
        diff = abs(fraccion_a_mpf(f7[j] - (c3 * f3[j] + c5 * f5[j])))
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
    suma_exact2 = mp.mpf("0")

    for i in range(len(x_exact_frac)):
        xc = mp.mpf(x_comp[i])
        xe = fraccion_a_mpf(x_exact_frac[i])
        diff = abs(xc - xe)
        if diff > max_diff:
            max_diff = diff
        if abs(xe) > max_exact:
            max_exact = abs(xe)
        suma_diff2 = suma_diff2 + diff * diff
        suma_exact2 = suma_exact2 + xe * xe

    err_inf = float(max_diff / max_exact)
    err_2 = float(mp.sqrt(suma_diff2) / mp.sqrt(suma_exact2))

    # Si el error es 0 no existe log2(0), asi que tomamos los 53 bits completos de la mantisa
    if err_2 == 0.0:
        return err_inf, err_2, 53.0, 0.0

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

    # Primero sacamos una cota de digitos desde el error, el maximo de un double es 15
    d_cota = int(math.floor(-math.log10(2 * float(err_rel))))
    if d_cota < 0:
        d_cota = 0
    if d_cota > 15:
        d_cota = 15

    # Luego bajamos hasta que el valor redondeado coincida con el exacto redondeado
    d_final = d_cota
    while d_final > 0:
        val_comp_red = mp.mpf(f"{float(valor_float):.{d_final}g}")
        val_exac_red = mp.mpf(mp.nstr(xe_mp, d_final))
        if val_comp_red == val_exac_red:
            break
        d_final = d_final - 1
    return d_final

def generar_solucion_csv(x_final, x_exact_frac, ruta_salida):
    resumen = []
    with open(ruta_salida, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["incognita", "valor_reportado", "digitos_afirmados"])

        for i in range(len(x_final)):
            digitos = contar_digitos_defendibles(x_final[i], x_exact_frac[i])

            # Si no hay ningun digito defendible igual mostramos 1 cifra para que el formato funcione
            cifras = max(digitos, 1)
            # El # conserva los ceros finales, para que se vean las cifras que afirmamos
            valor_formateado = f"{x_final[i]:#.{cifras}g}"

            # i + 1 para que se vea x1..x12, como en el enunciado
            nombre = "x" + str(i + 1)
            escritor.writerow([nombre, valor_formateado, digitos])
            resumen.append((nombre, valor_formateado, digitos, x_final[i]))
    return resumen

def ejecutar_verificacion_completa(A_frac, b_frac, exacto_piv, doble_sin, doble_con, ruta_residuo, ruta_solucion):
    # La solucion exacta (Fraction) es la referencia para comparar ambas corridas
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

    lineas = []

    # Residuo y error de cada corrida, calculados en precision extendida
    lineas.append("== Residuo r = b - Ax (precision extendida, norma infinito) ==")
    for nombre, corrida in [("sin pivoteo", doble_sin), ("con pivoteo", doble_con)]:
        r, norma_r = calcular_residuo_extendido(A_frac, b_frac, corrida["x"])
        err_inf, err_2, bits_ok, bits_perdidos = calcular_error_y_bits(corrida["x"], x_exact_frac)
        lineas.append(f"{nombre}: ||r||inf = {float(norma_r):.3e}")
        lineas.append(f"  multiplicador max = {corrida['multiplicador_max']:.3e}, crecimiento = {corrida['crecimiento']:.3e}")
        lineas.append(f"  error relativo (inf) = {err_inf:.3e}, (2) = {err_2:.3e}")
        lineas.append(f"  bits correctos = {bits_ok:.1f}, bits de mantisa perdidos = {bits_perdidos:.1f}")

    # Vector residuo completo de la corrida con pivoteo (el ultimo del for), a 20 digitos
    lineas.append("")
    lineas.append("== Vector residuo r = b - Ax (con pivoteo) ==")
    for i in range(len(r)):
        lineas.append("r[" + str(i + 1) + "] = " + mp.nstr(r[i], 20))

    # Refinamiento iterativo sobre la corrida con pivoteo
    x_refinado, historial = refinamiento_iterativo(A_frac, b_frac, doble_con)
    lineas.append("")
    lineas.append("== Refinamiento iterativo (con pivoteo, reusando L y U) ==")
    for h in historial:
        lineas.append(f"pasada {h['pasada']}: ||r||inf {h['norma_r_antes']:.3e} -> {h['norma_r_despues']:.3e}")
    _, err_2_ref, bits_ref, _ = calcular_error_y_bits(x_refinado, x_exact_frac)
    lineas.append(f"error relativo tras refinar (2) = {err_2_ref:.3e}, bits correctos = {bits_ref:.1f}")

    # Condicionamiento y determinante, para acotar los digitos que se pueden afirmar
    kappa_inf = estimar_kappa_infinito(A_float, doble_con["L"], doble_con["U"], doble_con["permutacion"], doble_con["contador"])
    kappa_2 = np.linalg.cond(np.array(A_float), 2) # numpy solo como estimacion, no resuelve el sistema
    det = calcular_determinante_desde_u(doble_con["U"], doble_con["intercambios"])
    c3, c5, max_diff, pert_rel = detectar_dependencia_fila7(A_frac)
    lineas.append("")
    lineas.append("== Condicionamiento ==")
    lineas.append(f"kappa_inf(A) ~ {kappa_inf:.3e}")
    lineas.append(f"kappa_2(A)   ~ {kappa_2:.3e}")
    lineas.append(f"cota kappa_2*eps ~ {kappa_2 * 2.0 ** -53:.3e}")
    lineas.append(f"cota kappa_inf*eps ~ {kappa_inf * 2.0 ** -53:.3e}")
    lineas.append(f"det(A) ~ {det:.4e}")
    lineas.append(f"fila 7 ~ {c3:.6g}*fila3 + {c5:.6g}*fila5, diferencia max = {max_diff:.3e}, perturbacion relativa = {pert_rel:.3e}")

    # numpy.linalg.solve solo como control, la solucion sale de nuestra eliminacion
    x_numpy = np.linalg.solve(np.array(A_float), np.array(b_float))
    err_inf_np, err_2_np, bits_np, _ = calcular_error_y_bits(list(x_numpy), x_exact_frac)
    lineas.append("")
    lineas.append("== Control: numpy.linalg.solve ==")
    lineas.append(f"error relativo (inf) = {err_inf_np:.3e}, (2) = {err_2_np:.3e}, bits correctos = {bits_np:.1f}")

    # Solucion final con los digitos defendibles de cada incognita
    x_final = []
    for valor in x_refinado:
        x_final.append(float(valor))
    resumen = generar_solucion_csv(x_final, x_exact_frac, ruta_solucion)
    lineas.append("")
    lineas.append("== Solucion reportada ==")
    for nombre, valor_formateado, digitos, _ in resumen:
        lineas.append(f"{nombre} = {valor_formateado}  ({digitos} digitos afirmados)")

    with open(ruta_residuo, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas) + "\n")
    return resumen
