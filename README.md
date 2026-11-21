# Eliminación gaussiana con pivoteo escalado (sistema 12×12)

Resolvemos un sistema Ax = b de 12×12 con eliminación gaussiana, con pivoteo, y comprobamos la respuesta con más precisión.

Luis Manzur y Antonella Mondaca. INF-321 S2 Computación Numérica, Ingeniería Civil Informática, Universidad Católica del Maule.

## Requisitos

Python 3.10 o más (lo probamos con 3.14.3). Dentro de la carpeta del repo:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

> En Linux o Mac el intérprete es `.venv/bin/python`.

## Cómo ejecutarlo

```powershell
.\.venv\Scripts\python.exe src/main.py
```

Un solo comando, sin pasos manuales, y se puede correr desde cualquier carpeta. Crea o reescribe estos archivos en `resultados/`:

| Archivo | Qué tiene |
|---|---|
| `solucion.csv` | las 12 incógnitas con los dígitos que afirmamos |
| `traza_eliminacion.txt` | la matriz después de cada uno de los 11 pasos |
| `conteo_flops.md` | tabla de operaciones por paso |
| `residuo.txt` | residuo, refinamiento, condicionamiento y control con numpy |

## Carpetas

```text
cn-parcial-gauss12-manzur-mondaca/
├─ README.md             # este archivo
├─ informe.md            # informe: método, conteo, análisis de error y conclusiones
├─ requirements.txt      # librerías con versión fija (numpy y mpmath)
├─ .gitignore            # lo que Git no sube (entorno virtual, __pycache__, etc.)
├─ datos/
│  ├─ matriz_a.csv       # matriz A del enunciado (12×12), sin redondear
│  └─ vector_b.csv       # vector b del enunciado, con sus 20 dígitos
├─ src/
│  ├─ gauss.py           # lectura exacta, eliminación (con o sin pivoteo), L y U, traza
│  ├─ conteo.py          # cuenta las operaciones y arma el reporte de flops
│  ├─ verificacion.py    # residuo, refinamiento, condicionamiento y control con numpy
│  └─ main.py            # punto de entrada: llama a todo y genera resultados/
└─ resultados/           # salidas que genera main.py (tabla de arriba)
```

## Resultado

| Incógnita | Valor | Incógnita | Valor |
|---|---:|---|---:|
| x1 | 0.7384915627 | x7 | 1.473820592 |
| x2 | -1.205937417 | x8 | -0.03849271640 |
| x3 | 0.004387195200 | x9 | 0.9152648037 |
| x4 | -0.09172645380 | x10 | -2.607139485 |
| x5 | 2.846109373 | x11 | 0.05187362940 |
| x6 | -0.006281540900 | x12 | -1.084937163 |

Se hicieron **1354 operaciones** en total. La norma infinito del residuo es 2.3e-10 y baja a 1.4e-48 con 3 pasadas de refinamiento.

## Informe

El detalle está en [informe.md](informe.md).

## Nota

Es un trabajo para el ramo INF-321, solo con fines académicos. Usamos IA como ayuda y lo contamos en el informe.
