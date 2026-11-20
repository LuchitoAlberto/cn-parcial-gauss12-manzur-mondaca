from fractions import Fraction
from pathlib import Path
from gauss import leer_matriz_a, leer_vector_b, eliminar, escribir_traza
from verificacion import ejecutar_verificacion_completa
from conteo import generar_reporte_flops

# Partimos de la carpeta del repo para que funcione se ejecute desde donde se ejecute
RAIZ = Path(__file__).resolve().parent.parent

def main():
    carpeta_resultados = RAIZ / "resultados"
    carpeta_resultados.mkdir(exist_ok=True)

    # Leemos los datos exactos, sin truncar
    A = leer_matriz_a(str(RAIZ / "datos" / "matriz_a.csv"))
    b = leer_vector_b(str(RAIZ / "datos" / "vector_b.csv"))

    # Corrida exacta (referencia) y las dos corridas en double
    exacto_piv = eliminar(A, b, convertir=Fraction, pivotear=True)
    doble_sin = eliminar(A, b, convertir=float, pivotear=False)
    doble_con = eliminar(A, b, convertir=float, pivotear=True)

    # Traza de la corrida con pivoteo
    escribir_traza(doble_con, str(carpeta_resultados / "traza_eliminacion.txt"),
                   "double con pivoteo parcial escalado")

    # Primero la verificacion: ahi se acumula el reuso de L y U en el contador
    ejecutar_verificacion_completa(A, b, exacto_piv, doble_sin, doble_con,
                                   str(carpeta_resultados / "residuo.txt"),
                                   str(carpeta_resultados / "solucion.csv"))

    # Despues el reporte de flops
    generar_reporte_flops(doble_sin["contador"], doble_con["contador"],
                          carpeta_resultados / "conteo_flops.md")

if __name__ == "__main__":
    main()