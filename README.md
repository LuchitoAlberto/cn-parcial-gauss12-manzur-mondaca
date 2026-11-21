# El pivote

### Eliminación gaussiana en un sistema denso 12×12

Resolución de un sistema lineal denso mal condicionado ($n = 12$) mediante eliminación gaussiana propia con pivoteo parcial escalado, control del costo operacional y verificación en precisión extendida.

---

## Autoría y asignatura

| | |
| :--- | :--- |
| **Estudiantes** | Luis Manzur · Antonella Mondaca |
| **Asignatura** | Computación Numérica (INF-321) |
| **Carrera** | Ingeniería Civil Informática, Universidad Católica del Maule |

---

## Requisitos

- Python 3.10 o superior.
- Instalar las dependencias:

```bash
pip install -r requirements.txt
```

---

## Ejecución

Un solo comando, sin pasos manuales:

```bash
python src/main.py
```

Al terminar, la carpeta `resultados/` queda regenerada con:

| Archivo | Contenido |
| :--- | :--- |
| `solucion.csv` | Las 12 incógnitas con los dígitos reportados |
| `traza_eliminacion.txt` | La matriz tras cada uno de los 11 pasos |
| `conteo_flops.md` | Tabla de operaciones por paso |
| `residuo.txt` | Residuo $r = b - Ax$ y su norma infinito |

---

## Estructura de carpetas

```text
cn-parcial-gauss12-manzur-mondaca/
├─ readme.md          # este archivo
├─ informe.md         # informe técnico y análisis de error
├─ requirements.txt   # dependencias con versión fija
├─ datos/             # matriz A y vector b, sin truncar
├─ src/               # código fuente (eliminación, conteo, verificación, main)
└─ resultados/        # salidas generadas por main.py
```

---

## Resultado resumido

| Incógnita | Valor (10 dígitos) |
| :--- | :--- |
| $x_1$ | [PEGAR] |
| $x_2$ | [PEGAR] |
| $x_3$ | [PEGAR] |
| $x_4$ | [PEGAR] |
| $x_5$ | [PEGAR] |
| $x_6$ | [PEGAR] |
| $x_7$ | [PEGAR] |
| $x_8$ | [PEGAR] |
| $x_9$ | [PEGAR] |
| $x_{10}$ | [PEGAR] |
| $x_{11}$ | [PEGAR] |
| $x_{12}$ | [PEGAR] |

| Indicador | Valor |
| :--- | ---: |
| Total de flops | [PEGAR] |
| $\lVert r\rVert_\infty$ del residuo | [PEGAR] |

---

## Informe

El análisis completo está en [`informe.md`](informe.md).

---

## Licencia

Trabajo de uso académico para la asignatura Computación Numérica (INF-321), Universidad Católica del Maule.