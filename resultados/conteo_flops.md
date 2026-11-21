# Conteo de operaciones

Convención: 1 flop = 1 operación elemental (suma, resta, multiplicación o división).
Incluye la actualización de b y la sustitución regresiva. El pivoteo se reporta aparte.

## Costo por paso (corrida con pivoteo)

| Paso k | Filas por eliminar | Divisiones | Multiplicaciones | Total mul/div | Total sumas/restas | Total flops del paso | Comparaciones de pivote | Divisiones de escala | Intercambios de fila |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 11 | 11 | 132 | 143 | 132 | 275 | 11 | 12 | 1 |
| 2 | 10 | 10 | 110 | 120 | 110 | 230 | 10 | 11 | 0 |
| 3 | 9 | 9 | 90 | 99 | 90 | 189 | 9 | 10 | 1 |
| 4 | 8 | 8 | 72 | 80 | 72 | 152 | 8 | 9 | 1 |
| 5 | 7 | 7 | 56 | 63 | 56 | 119 | 7 | 8 | 1 |
| 6 | 6 | 6 | 42 | 48 | 42 | 90 | 6 | 7 | 1 |
| 7 | 5 | 5 | 30 | 35 | 30 | 65 | 5 | 6 | 1 |
| 8 | 4 | 4 | 20 | 24 | 20 | 44 | 4 | 5 | 1 |
| 9 | 3 | 3 | 12 | 15 | 12 | 27 | 3 | 4 | 1 |
| 10 | 2 | 2 | 6 | 8 | 6 | 14 | 2 | 3 | 0 |
| 11 | 1 | 1 | 2 | 3 | 2 | 5 | 1 | 2 | 0 |

## Totales

| Fase / corrida | Mul/div | Sumas/restas | Total |
| --- | ---: | ---: | ---: |
| Eliminación (11 pasos) | 638 | 572 | 1210 |
| Sustitución regresiva | 78 | 66 | 144 |
| Total sin pivoteo | 716 | 638 | 1354 |
| Total con pivoteo | 716 | 638 | 1354 |

## Sobrecosto del pivoteo (aparte)

- Comparaciones: 144 (escalas) + 66 (pasos) = 210
- Divisiones de escala: 77
- Intercambios de fila: 8

Cota de referencia: 1486 flops. Medido: 1354 (-8.88 %).
Flops reutilizados de L y U: 4140 (1980 progresiva + 2160 regresiva)
Se calculan despues de la eliminacion, por eso no entran en el total de flops de arriba.
