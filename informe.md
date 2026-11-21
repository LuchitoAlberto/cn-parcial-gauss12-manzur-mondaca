# Informe: Laboratorio "El pivote"

## 1. Identificación

- Asignatura: INF-321 Computación Numérica, Ingeniería Civil Informática, Universidad Católica del Maule
- Integrantes: Luis Manzur y Antonella Mondaca
- Docentes: Juan Manuel Cabezas Contardo y Pedro Pesante
- Fecha: noviembre de 2026
- Repositorio: https://github.com/LuchitoAlberto/cn-parcial-gauss12-manzur-mondaca (la rama que se evalúa es main)
- Problema: resolver Ax = b con A densa de 12×12 usando eliminación gaussiana hecha por nosotros
- Datos: la matriz A y el vector b vienen del enunciado (Rubrica.docx) y los copiamos como texto, sin redondear nada

**Uso de IA.** Usamos Claude (Anthropic) como ayudante. Nos sirvió para discutir cómo armar las funciones, para revisar el código que escribimos nosotros y para comprobar que las cifras medidas tuvieran sentido. También nos ayudó con la primera redacción de este informe y del README, que después revisamos y ajustamos. El código de src/ lo escribimos nosotros con su ayuda y todas las cifras salen de correr python src/main.py.

## 2. Planteamiento

Queremos que el vector x cumpla Ax = b, con n = 12 y una A completamente densa (144 elementos distintos de cero). Hay que lograr dos cosas en este caso: gastar pocas operaciones (alrededor de 2n³/3, sin repetir trabajo) y perder la menor cantidad posible de cifras por el redondeo de la mantisa (doble precisión, 53 bits).

Al mirar los datos vimos tres cosas que condicionan lo que hicimos:

1. Las filas tienen escalas muy distintas: hay filas del orden de 1e-5 (F1, F5, F9) y otras de 1e4 a 1e5 (F2, F6, F8, F12). Si le restamos un múltiplo de una fila grande a una chica sin escalar, los bits bajos de la chica se salen de los 53 bits de la mantisa. Por eso no basta con pivoteo parcial normal, hay que escalar por filas.
2. a(1,1) = 1.3407e-08 es unas doce potencias de diez más chico que a(2,1) = 1.19229739e4. Sin pivoteo ningún pivote se hace cero, así que el método igual termina, pero el error crece mucho (sección 5). Eso nos permite medir cuánto se degrada la mantisa.
3. La fila 7 es casi una combinación de las filas 3 y 5, lo que sube κ₂(A) a 3,085e13 y deja a A muy cerca de ser singular, sin llegar a serlo (sección 6).

Los datos se leen como texto y se convierten a Fraction (para tener una referencia exacta) o a float (para las corridas en double). Nunca pasan por un float escrito a mano, porque b trae 20 dígitos y si lo truncamos la respuesta cambia. La misma rutina de eliminación se corre también con Fraction para tener la solución de referencia.

## 3. Estrategia de eliminación

Todo está en la función eliminar de src/gauss.py, que se puede usar con o sin pivoteo. Hacemos la factorización PA = LU en 11 pasos:

- En 11 pasos dejamos en cero lo que está bajo la diagonal. En total son 66 ceros. La traza (resultados/traza_eliminacion.txt) muestra la matriz después de cada paso y cuenta esos ceros: 66 de 66.
- Para el pivoteo escalado calculamos una vez las escalas s(i) = max |a(i,j)| de cada fila. En el paso k elegimos como pivote la fila con mayor |a(i,k)| / s(i) y la cambiamos de lugar con la fila k. Al intercambiar también movemos lo que ya está guardado en L, el vector b y las escalas.
- Para cada fila calculamos una sola vez el multiplicador m(i,k) = a(i,k) / a(k,k) y lo reusamos en toda la fila y en b. Lo guardamos en L.
- La resta de filas parte desde la columna k+1. La columna k no se calcula, simplemente se pone el cero, porque a(i,k) - m*a(k,k) da cero por lógica. Así nos ahorramos 66 × 2 = 132 operaciones. En el mismo recorrido actualizamos b.
- Después viene la sustitución regresiva sobre U.
- Nunca invertimos A ni factorizamos dos veces. Guardamos L, U y la permutación de filas, y todo lo que se resuelve después (sustitución regresiva, refinamiento y estimación de κ∞ con la función resolver_con_lu) reusa esos factores.

## 4. Conteo de operaciones

Contamos 1 flop por cada operación elemental (suma, resta, multiplicación o división). Entra la actualización de b y la sustitución regresiva. Lo que cuesta el pivoteo (comparaciones, divisiones de escala e intercambios) lo dejamos aparte, como sobrecosto por estabilidad.

El conteo lo hace el propio código, la clase ContadorOperaciones (src/conteo.py) suma cada operación mientras eliminar (src/gauss.py) trabaja y separa mul/div de sumas/restas, paso por paso.

| Paso k | Filas a anular | Divisiones | Mult. | Mul/div | Sumas/restas | Flops del paso | Comp. pivote | Div. escala | Intercambios |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
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

| Fase | Mul/div | Sumas/restas | Total |
|---|---:|---:|---:|
| Eliminación (11 pasos) | 638 | 572 | 1210 |
| Sustitución regresiva | 78 | 66 | 144 |
| Total | 716 | 638 | 1354 |

Quedamos en 1354 flops contra la cota de referencia de unos 1486, es decir 8,88 % por debajo, dentro del ±10 % pedido. Nos da menos porque la cota cuenta el barrido de la columna k y nosotros no la operamos.

El pivoteo no agrega flops, da 1354 con y sin él. Lo que sí agrega son 210 comparaciones (144 para las escalas y 66 para elegir pivote), 77 divisiones de escala y 8 intercambios de fila.

Las 15 resoluciones que hicimos después con L y U (3 pasadas de refinamiento y 12 para estimar κ∞) costaron 4140 flops en total (1980 de la parte progresiva y 2160 de la regresiva), o sea 276 cada una. Volver a factorizar costaría 1210 cada vez, así que reusar L y U ahorra bastante.

## 5. Análisis de mantisa y pivoteo

Usamos las mismas rutinas en dos corridas en double, una sin pivoteo y otra con pivoteo parcial escalado, y comparamos con la solución exacta calculada en Fraction (datos de resultados/residuo.txt).

| | Sin pivoteo | Con pivoteo escalado |
|---|---:|---:|
| Multiplicador máximo | 2,753e13 | 2,466e9 |
| Factor de crecimiento | 2,641e3 | 1,783 |
| Error relativo (norma 2) | 2,380e-10 | 2,702e-13 |
| Error relativo (norma ∞) | 2,080e-10 | 2,357e-13 |
| Bits correctos / perdidos (de 53) | 32,0 / 21,0 | 41,8 / 11,2 |
| ‖b − Ax‖∞ | 1,772e-07 | 2,291e-10 |

Los bits correctos son −log₂ del error relativo en norma 2, y los perdidos son 53 menos esos.

Por qué no se puede usar a(1,1) como pivote?

R: Sin pivoteo, el primer paso divide por a(1,1) = 1.3407e-08 y da un multiplicador m(2,1) ≈ 1.1923e4 / 1.3407e-8 ≈ 8,89e11. En total el multiplicador máximo llega a 2,75e13, que es más o menos 2^44,6, y el crecimiento a 2,6e3. A cada fila le restamos la fila 1 multiplicada por ese número gigante, así que el error de redondeo de la fila 1 (del orden de 2^-53) se puede amplificar unas 2^44 veces. En el peor caso quedarían solo unos 9 bits buenos de 53. Además, los datos propios de cada fila quedan tapados por la fila 1, que pesa muchísimo más, y eso es pérdida de información y no solo de precisión. Con pivoteo el multiplicador baja a 2,47e9 y el crecimiento casi no existe (1,78 contra 2,64e3). El error final queda unas 880 veces menor y el residuo unas 770 veces menor.

Antes de medir esperábamos 6 o 7 dígitos correctos sin pivoteo, y medimos 9 o 10 (32 bits correctos, 21 perdidos). La diferencia se explica porque 2^44 es el máximo posible, que solo pasaría si todos los redondeos se amplificaran al máximo y con el mismo signo. En la práctica los errores se compensan en parte y no todas las filas tienen multiplicadores enormes. En el informe damos lo medido, y los 6 o 7 dígitos quedan como una estimación pesimista más que nada. Con pivoteo medimos 12 o 13 dígitos antes de refinar.

## 6. Condicionamiento

| Magnitud | Valor |
|---|---:|
| κ₂(A) | 3,085e13 |
| κ∞(A) | 5,368e13 |
| det(A) | 1,3646e9 |
| κ₂·u (con u = 2^-53, unos 1,11e-16) | 3,4e-3 |
| κ₂·ε (con ε = 2^-52, unos 2,22e-16) | 6,8e-3 |
| κ∞·u | 6,0e-3 |

El determinante sale de la diagonal de U, con el signo según la paridad de los intercambios. κ∞ la estimamos reusando L y U, y κ₂ la sacamos como control con el espectro de A.

La fila 7 es casi 4,19496·fila3 + 586,116·fila5 (la función detectar_dependencia_fila7 la ajusta): la diferencia máxima respecto de esa combinación es 3,47e-4 (5,5e-3 en términos relativos). Esa casi dependencia hace chico el menor valor singular de A y es lo que hace que κ sea tan grande. Hay que notar que el det(A) no es chico, pero eso no dice nada porque depende de la escala de las filas. Lo que mide qué tan cerca está A de ser singular es κ.

La cota error relativo ≲ κ·u da 3,4e-3 (6,8e-3 con ε), o sea que solo garantizaría unos 2 o 3 dígitos. En la práctica, con pivoteo, medimos un error de 2,7e-13, es decir 12 o 13 dígitos. Esa cota es de peor caso, el error tendría que caer justo en la dirección peor condicionada, y además el pivoteo escalado mantiene el crecimiento cerca de 1, así que el error de redondeo no se amplifica por el algoritmo. Sí hay un límite que se respeta, puesto que si κ llegara a 1e16 ya no se podría afirmar ningún dígito, y estamos tres órdenes por debajo.

## 7. Resultados

Los valores vienen de resultados/solucion.csv. Para cada incógnita, la función contar_digitos_defendibles revisa la cota relativa y que las cifras coincidan con la solución exacta en Fraction. La solución exacta tiene 10 cifras significativas y después puros ceros. Después de refinar, el error contra ella es de unos 5e-51.

Afirmamos 15 dígitos porque es lo que un double puede guardar de forma defendible (15 a 17 cifras decimales). Afirmar más sería sobre-reportar, porque el double no almacena más. Afirmar menos (los 12 o 13 de la corrida sin refinar) sería sub-reportar, porque el refinamiento con residuo en precisión extendida demuestra que las 15 cifras son correctas.

| Incógnita | Valor (15 cifras) | Dígitos afirmados |
|---|---:|---:|
| x1 | 0,738491562700000 | 15 |
| x2 | −1,20593741680000 | 15 |
| x3 | 0,00438719520000000 | 15 |
| x4 | −0,0917264538000000 | 15 |
| x5 | 2,84610937250000 | 15 |
| x6 | −0,00628154090000000 | 15 |
| x7 | 1,47382059160000 | 15 |
| x8 | −0,0384927164000000 | 15 |
| x9 | 0,915264803700000 | 15 |
| x10 | −2,60713948520000 | 15 |
| x11 | 0,0518736294000000 | 15 |
| x12 | −1,08493716250000 | 15 |

Los ceros del final cuentan como cifras afirmadas, porque la solución exacta no tiene más dígitos distintos de cero.

## 8. Verificación

Lo hicimos aparte de la eliminación, en src/verificacion.py.

**Residuo.** Calculamos r = b − Ax con mpmath a 80 dígitos, no en double, y con los datos exactos en Fraction. Con pivoteo da ‖r‖∞ = 2,291e-10 y sin pivoteo 1,772e-07. El vector completo está en resultados/residuo.txt.

**Refinamiento iterativo.** Calculamos el residuo en mpmath y resolvemos la corrección en double reusando L, U y la permutación. Con tres pasadas:

| Pasada | ‖r‖∞ antes | ‖r‖∞ después |
|---:|---:|---:|
| 1 | 2,291e-10 | 1,366e-22 |
| 2 | 1,366e-22 | 3,928e-35 |
| 3 | 3,928e-35 | 1,383e-48 |

Cada pasada baja el residuo unos 12 órdenes de magnitud, y el error relativo en norma 2 termina en 4,8e-51 (la solución refinada se guarda en precisión extendida, por eso baja de lo que cabe en 53 bits).

**Control con numpy.** numpy.linalg.solve da un error relativo de 2,9e-13 (norma 2) y 41,6 bits correctos, casi igual a nuestra eliminación con pivoteo antes de refinar (2,7e-13). Eso nos da confianza en que nuestro código está bien. Lo usamos solo como control y la solución no sale de ahí.

**Uso de κ(A).** Un residuo chico no asegura un error chico, porque ‖δx‖/‖x‖ ≤ κ·‖r‖/‖b‖ y con κ ≈ 3e13 esa cota deja pasar errores mucho mayores que el residuo. Lo que confirma los dígitos es el refinamiento con residuo extendido, que converge a una solución con error de 5e-51.

## 9. Conclusiones

- Con pivoteo parcial escalado nuestra eliminación da 12 o 13 dígitos correctos con 1354 flops (8,9 % menos que la referencia), y el refinamiento lleva la solución hasta el límite del double sin refactorizar.
- El pivoteo no suma flops a la eliminación, solo 210 comparaciones, 77 divisiones y 8 intercambios, y a cambio el error baja unas 880 veces. Evita perder decenas de bits por culpa de a(1,1) y de las escalas distintas. En este problema conviene.
- κ ≈ 3e13 viene de que la fila 7 casi depende de las filas 3 y 5. La cota κ·u es muy pesimista frente a lo medido, y en el informe damos lo medido.
- Con n = 1000 cambiaría lo siguiente:
  1. Costos: la eliminación serían unos 2n³/3 ≈ 6,7e8 flops, mucho más que los 1354 de ahora, mientras que las comparaciones del pivoteo crecen como n²/2 ≈ 5e5, así que el pivoteo pesaría menos de 0,1 %.
  2. Implementación y memoria: los bucles de Python puro con listas anidadas serían demasiado lentos, así que usaríamos arreglos contiguos y una LU por bloques con BLAS (o la rutina de una librería), y aprovecharíamos que la matriz sea rala o en banda si lo fuera.
  3. Estabilidad: con mil pasos el crecimiento acumulado importa más, así que vigilaríamos el residuo en precisión extendida y haríamos refinamiento si κ(A) supera 1e10. El pivoteo seguiría siendo obligatorio.

## 10. Reproducibilidad

Python 3.14.3 (con 3.10 o más debería bastar), numpy==2.5.5 y mpmath==1.4.1 (están en requirements.txt).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/main.py
```

src/main.py regenera sin tocar nada a mano los cuatro archivos de resultados/: solucion.csv, traza_eliminacion.txt, conteo_flops.md y residuo.txt.
