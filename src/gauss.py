import csv
from fractions import Fraction
from conteo import ContadorOperaciones

def leer_csv(ruta):
    filas = []
    with open(ruta, newline="") as archivo:
        for fila_texto in csv.reader(archivo):
            if fila_texto:
                fila = []
                for valor in fila_texto:
                    fila.append(Fraction(valor.strip()))
                filas.append(fila)
    return filas

def leer_matriz_a(ruta="datos/matriz_a.csv"):
    A = leer_csv(ruta)
    # Comprobamos que llegaron los 144 valores
    assert len(A) == 12 and all(len(fila) == 12 for fila in A), "A no es 12x12"
    return A

def leer_vector_b(ruta="datos/vector_b.csv"):
    # El vector B solo tiene un valor por linea, asi que cada fila trae un solo elemento
    b = []
    for fila in leer_csv(ruta):
        b.append(fila[0])
    assert len(b) == 12, "b no contiene 12 valores"
    return b

def eliminar(A, b, convertir=float, pivotear=False):
    n = len(A)

    # Copias de la matriz A y el vector b segun el tipo de dato elegido
    U = []
    for fila in A:
        fila_convertida = []
        for valor in fila:
            fila_convertida.append(convertir(valor))
        U.append(fila_convertida)
    c = []
    for valor in b:
        c.append(convertir(valor))

    # L guarda los multiplicadores bajo la diagonal de 1's
    L = []
    for i in range(n):
        fila = []
        for j in range(n):
            if i == j:
                fila.append(convertir(1))
            else:
                fila.append(convertir(0))
        L.append(fila)

    mayor_a_inicial = max(abs(valor) for fila in U for valor in fila)
    multiplicador_max = convertir(0)
    mayor_elemento = convertir(0)

    traza = []
    operaciones = []

    # El contador lleva la cuenta real de las operaciones, paso por paso
    contador = ContadorOperaciones(n)

    # Escala de cada fila con su elemento en valor absoluto mas grande
    escalas = []
    for fila in U:
        mayor = convertir(0)
        for valor in fila:
            mayor = max(mayor, abs(valor))
            contador.comparaciones_iniciales_escala += 1 # Cada elemento se compara una vez con el mayor
        escalas.append(mayor)

    permutacion = list(range(n)) # Cada indice es el indice de la fila original que ahora se encuentra en la posicion i
    comparaciones = 0
    intercambios = 0
    divisiones_pivoteo = 0

    # Triangulacion inferior / Eliminacion hacia adelante
    for k in range(n-1):
        mult_div = 0
        suma_resta = 0

        # Abrimos el registro del paso (se numeran desde 1, igual que en el enunciado)
        registro = contador.iniciar_paso(k + 1)

        if pivotear:
            # Elegimos la fila con mejor razon para evitar que numeros grandes ganen
            fila_pivote = k
            mejor_razon = abs(U[k][k] / escalas[k])
            divisiones_pivoteo += 1
            registro.divisiones_escala += 1 # El pivoteo se cuenta aparte, no entra en los flops
            for i in range(k + 1, n):
                razon = abs(U[i][k] / escalas[i])
                divisiones_pivoteo += 1
                registro.divisiones_escala += 1
                comparaciones += 1
                registro.comparaciones_pivoteo += 1
                if razon > mejor_razon:
                    mejor_razon = razon
                    fila_pivote = i

            if fila_pivote != k:
                # Intercambiamos todas las filas correspondientes
                U[k], U[fila_pivote] = U[fila_pivote], U[k]
                c[k], c[fila_pivote] = c[fila_pivote], c[k]
                escalas[k], escalas[fila_pivote] = escalas[fila_pivote], escalas[k]
                permutacion[k], permutacion[fila_pivote] = permutacion[fila_pivote], permutacion[k]

                # Los multiplicadores que ya estan en L viajan con su fila
                for j in range(k):
                    temporal = L[k][j]
                    L[k][j] = L[fila_pivote][j]
                    L[fila_pivote][j] = temporal
                intercambios += 1
                registro.intercambios_de_filas += 1

            # Guardamos que fila quedo como pivote (contada desde 1)
            registro.fila_pivote_elegida = fila_pivote + 1

        for i in range(k + 1, n):
            # Calculamos el multiplicador de la fila
            m = U[i][k] / U[k][k]
            mult_div += 1
            registro.divisiones += 1 # El multiplicador es una division, se calcula una sola vez por fila
            L[i][k] = m
            multiplicador_max = max(multiplicador_max, abs(m))
            registro.multiplicador_max_paso = max(registro.multiplicador_max_paso, float(abs(m)))

            # Restamos (m * fila k) a la fila i solo desde la columna k+1 puesto que todo lo que queda a la izquierda es 0
            for j in range(k + 1, n):
                U[i][j] = U[i][j] - (m * U[k][j])
                mult_div += 1
                suma_resta += 1
                registro.multiplicaciones += 1 # Una multiplicacion y una resta por elemento
                registro.sumasyrestas += 1
                mayor_elemento = max(mayor_elemento, abs(U[i][j]))

            # El elemento (i, k) queda en 0
            U[i][k] = convertir(0)

            # Aplicamos lo mismo al vector b
            c[i] = c[i] - (m * c[k])
            mult_div += 1
            suma_resta += 1
            registro.multiplicaciones += 1
            registro.sumasyrestas += 1

        operaciones.append([mult_div, suma_resta])
        traza.append([fila[:] for fila in U])

    # Sutitucion para atras
    x = [convertir(0)] * n
    mult_div = 0
    suma_resta = 0
    for i in range(n - 1, -1, -1):
        suma = c[i]
        for j in range(i + 1, n):
            suma = suma - U[i][j] * x[j]
            mult_div += 1
            suma_resta += 1
            contador.sust_reg_multiplicaciones += 1 # La sustitucion tambien se cuenta, pero en su propia fase
            contador.sust_reg_restas += 1
        x[i] = suma / U[i][i]
        mult_div += 1
        contador.sust_reg_divisiones += 1
    operaciones.append([mult_div, suma_resta])

    # Factor de crecimiento
    crecimiento = max(mayor_elemento, mayor_a_inicial) / mayor_a_inicial

    return {
        "x": x, "L": L, "U": U, "c": c,
        "multiplicador_max": multiplicador_max,
        "crecimiento": crecimiento,
        "traza": traza,
        "operaciones": operaciones,
        "permutacion": permutacion,
        "comparaciones": comparaciones,
        "intercambios": intercambios,
        "divisiones_pivoteo": divisiones_pivoteo,
        "contador": contador,
    }

def ceros_bajo_diagonal(matriz):
    ceros = 0
    for i in range(len(matriz)):
        for j in range(i):
            if matriz[i][j] == 0:
                ceros += 1
    return ceros

def escribir_traza(corrida, ruta, titulo):
    # Escribimos la matriz tras cada paso de la eliminacion en notacion cientifica para asegurarnos de la precision
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(f"Traza de la eliminacion gaussiana - {titulo}\n")
        archivo.write(f"Permutacion de filas (orden final): {corrida['permutacion']}\n\n")

        for k in range(len(corrida["traza"])):
            matriz = corrida["traza"][k]
            archivo.write(f"Paso {k + 1} de {len(corrida['traza'])}\n")

            for fila in matriz:
                linea = ""
                for valor in fila:
                    linea += f"{float(valor):>14.6e} "
                archivo.write(linea + "\n")

            ceros = ceros_bajo_diagonal(matriz)
            archivo.write(f"0's bajo la diagonal tras este paso: {ceros}\n\n")

        # El ultimo paso debe dejar los 66 ceros
        total = ceros_bajo_diagonal(corrida["traza"][-1])
        archivo.write(f"Total de 0's bajo la diagonal: {total} (esperado: 66)\n")


if __name__ == "__main__":
    A = leer_matriz_a()
    b = leer_vector_b()

    n = 12
    # La solucion exacta (Fraction) no depende del pivoteo: es la referencia para ambas corridas
    exacto = eliminar(A, b, Fraction)
    exacto_piv = eliminar(A, b, Fraction, pivotear=True)

    for nombre, corrida in [("sin pivoteo", exacto), ("con pivoteo", exacto_piv)]:
        # Comprobamos que L * U reconstruye A (con pivoteo, A con las filas permutadas)
        for i in range(n):
            for j in range(n):
                producto = 0
                for k in range(n):
                    producto += (corrida["L"][i][k] * corrida["U"][k][j])
                assert producto == A[corrida["permutacion"][i]][j], f"{nombre}: L * U no coincide con A en ({i}, {j})"

        # Comprobamos los 66 0's bajo la diagonal
        ceros = ceros_bajo_diagonal(corrida["U"])
        assert ceros == 66, f"{nombre}: no hay 66 0's bajo la diagonal, hay {ceros}"

    # Ambas soluciones exactas deben ser identicas
    for i in range(n):
        assert exacto["x"][i] == exacto_piv["x"][i], f"x[{i}] difiere entre corridas exactas"

    doble = eliminar(A, b, float)
    doble_piv = eliminar(A, b, float, pivotear=True)

    print("                    sin pivoteo   con pivoteo")
    print("multiplicador_max:  %.3e    %.3e" % (doble["multiplicador_max"], doble_piv["multiplicador_max"]))
    print("crecimiento:        %.3e    %.3e" % (doble["crecimiento"], doble_piv["crecimiento"]))
    print("comparaciones: %d, intercambios: %d, divisiones de pivoteo: %d" % (
        doble_piv["comparaciones"], doble_piv["intercambios"], doble_piv["divisiones_pivoteo"]))
    print()
    print(" i |   error relativo sin pivoteo | error relativo con pivoteo")
    print("---+------------------------------+---------------------------")
    for i in range(n):
        xe = exacto["x"][i]
        error_sin = abs((doble["x"][i] - xe) / xe)
        error_con = abs((doble_piv["x"][i] - xe) / xe)
        # i + 1 para que se vea x1..x12, como en el enunciado
        print("%2d | %28.2e | %.2e" % (i + 1, error_sin, error_con))