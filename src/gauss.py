import csv
from fractions import Fraction

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

def eliminar_sin_pivoteo(A, b, convertir=float):
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

    # Triangulacion inferior / Eliminacion hacia adelante
    for k in range(n-1):
        mult_div = 0
        suma_resta = 0
        for i in range(k + 1, n):
            # Calculamos el multiplicador de la fila
            m = U[i][k] / U[k][k]
            mult_div += 1
            L[i][k] = m
            multiplicador_max = max(multiplicador_max, abs(m))

            # Restamos (m * fila k) a la fila i solo desde la columna k+1 puesto que todo lo que queda a la izquierda es 0
            for j in range(k + 1, n):
                U[i][j] = U[i][j] - (m * U[k][j])
                mult_div += 1
                suma_resta += 1
                mayor_elemento = max(mayor_elemento, abs(U[i][j]))

            # El elemento (i, k) queda en 0
            U[i][k] = convertir(0)

            # Aplicamos lo mismo al vector b
            c[i] = c[i] - (m * c[k])
            mult_div += 1
            suma_resta += 1

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
        x[i] = suma / U[i][i]
        mult_div += 1
    operaciones.append([mult_div, suma_resta])

    # Factor de crecimiento
    crecimiento = max(mayor_elemento, mayor_a_inicial) / mayor_a_inicial

    return {
        "x": x, "L": L, "U": U, "c": c,
        "multiplicador_max": multiplicador_max,
        "crecimiento": crecimiento,
        "traza": traza,
        "operaciones": operaciones,
    }

if __name__ == "__main__":
    A = leer_matriz_a()
    b = leer_vector_b()

    exacto = eliminar_sin_pivoteo(A, b, Fraction) # Sin error de redondeo
    doble = eliminar_sin_pivoteo(A, b, float) # Eliminacion real

    # Comprobamos si L * U resultan en A
    n = 12
    for i in range(n):
        for j in range(n):
            producto = 0
            for k in range(n):
                producto += (exacto["L"][i][k] * exacto["U"][k][j])
            assert producto == A[i][j], f"L * U no es lo mismo que A en ({i}, {j})"

    # Comprobamos los 66 0's bajo la diagonal
    ceros = 0
    for i in range(n):
        for j in range(i):
            if exacto["U"][i][j] == 0:
                ceros += 1
    assert ceros == 66, f"No hay 66 0's bajo la diagonal, hay {ceros}"

    print("multiplicador_max: %.3e" % doble["multiplicador_max"])
    print("crecimiento:       %.3e" % doble["crecimiento"])
    print()
    print(" i |          x_i (float)          | error relativo")
    print("---+-------------------------------+---------------")
    for i in range(n):
        xe = exacto["x"][i]
        xd = doble["x"][i]
        error = abs((xd - xe) / xe)
        # i + 1 para que se vea x1..x12, como en el enunciado
        print("%2d | %29.17e | %.2e" % (i + 1, xd, error))