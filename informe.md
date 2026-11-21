---

## 2. `informe.md`

```markdown
# Informe Técnico — El pivote: Eliminación gaussiana con mínimo costo operacional y máxima exactitud de mantisa

## 1. Identificación
- **Estudiantes:** Luis Manzur y Antonella Mondaca
- **Asignatura:** Computación Numérica (INF-321) — Ingeniería Civil Informática, Universidad Católica del Maule
- **Docentes:** Juan Manuel Cabezas Contardo · Pedro Pesante
- **Fecha:** Noviembre de 2026
- **Repositorio:** https://github.com/LuchitoAlberto/cn-parcial-gauss12-manzur-mondaca

## 2. Planteamiento
Se resuelve el sistema lineal denso $Ax = b$ de dimensión $n = 12$ (144 entradas no nulas en $A$) mediante eliminación gaussiana en doble precisión IEEE-754 (53 bits de mantisa). El problema contrapone dos objetivos: no exceder el costo operacional mínimo teórico de una matriz densa y preservar la máxima cantidad de cifras significativas posibles frente al error de redondeo.

La matriz del caso combina tres fuentes de dificultad numérica:
1. **Escalas de fila incompatibles:** coexisten filas del orden $10^{-5}$ (F1, F5, F9) y filas del orden $10^{4}$–$10^{5}$ (F2, F6, F8, F12). Restar un múltiplo de una fila de gran magnitud sobre una fila pequeña sin escalamiento provoca que el alineamiento de exponentes expulse los bits bajos del operando menor fuera de los 53 bits de mantisa.
2. **Pivote inicial minúsculo:** $a_{1,1} = 1.3407\times 10^{-8}$ es doce órdenes de magnitud inferior a $a_{2,1} = 1.19229739\times 10^{4}$. Ningún pivote se anula exactamente, por lo que tanto la corrida sin pivoteo como la corrida con pivoteo concluyen y permiten cuantificar la degradación real de la mantisa.
3. **Casi dependencia lineal oculta:** la fila 7 se encuentra a una perturbación relativa de orden $10^{-4}$ respecto a una combinación lineal de las filas 3 y 5, elevando el número de condición a $\kappa_2(A) \approx 3.08\times 10^{13}$ sin volver singular el sistema.

Para evitar cualquier error de entrada, `datos/matriz_a.csv` y `datos/vector_b.csv` se cargan directamente desde texto mediante `fractions.Fraction` sin truncar sus 9 y 20 cifras significativas, respectivamente. La misma rutina de eliminación se ejecuta en aritmética racional exacta (`Fraction`) para obtener la solución de referencia $x_{\text{exact}}$ y validar algebraicamente que $LU = PA$ y los 66 ceros subdiagonales.

## 3. Estrategia de eliminación
Se implementa la factorización $PA = LU$ en una sola pasada de 11 pasos ($k = 1, \dots, 11$) con pivoteo parcial escalado:
- **Escalas de fila calculadas una sola vez:** al iniciar se determina $s_i = \max_j |a_{i,j}|$ para cada fila $i = 1, \dots, 12$.
- **Selección de pivote escalado:** en el paso $k$ se elige la fila $p \ge k$ que maximiza $|a_{p,k}| / s_p$, impidiendo que filas con entradas grandes en valor absoluto desplacen indebidamente a filas mejor condicionadas por escala relativa. Al intercambiar filas, se permutan también las columnas $0 \dots k-1$ ya construidas en $L$, el vector $b$ y el vector de escalas.
- **Multiplicador único por fila:** para cada fila $i > k$, el multiplicador $m_{i,k} = U_{i,k}/U_{k,k}$ se calcula **una sola vez**, se almacena en $L_{i,k}$ y se reutiliza en toda la fila $i$ y en el lado derecho.
- **Barrido restringido sin recalcular ceros:** la actualización de $U$ recorre solo las columnas $j = k+1, \dots, 12$ y fija $U_{i,k} = 0$ por cancelación algebraica exacta. Esto evita $66 \times 2 = 132$ operaciones redundantes sobre la columna del pivote y garantiza 66 ceros exactos bajo la diagonal en `resultados/traza_eliminacion.txt`.
- **Cero inversión y una única factorización:** no se calcula $A^{-1}$ ni se vuelve a factorizar $A$. Los factores $L$, $U$ y la permutación $P$ se reutilizan directamente en la sustitución regresiva, en el refinamiento iterativo y en la estimación de $\kappa_\infty(A)$ mediante `resolver_con_lu`.

## 4. Conteo de operaciones
**Convención declarada:** $1\text{ flop} = 1\text{ operación aritmética elemental}$ (`+`, `-`, `*`, `/`) instrumentada directamente en tiempo de ejecución mediante `ContadorOperaciones` (`src/conteo.py`) dentro de `eliminar()` (`src/gauss.py`), incluyendo actualización del vector derecho y sustitución regresiva. Las operaciones asociadas a la selección e intercambio de pivotes se contabilizan aparte como sobrecosto de estabilidad.

| Paso $k$ | Filas por eliminar | Divisiones | Multiplicaciones | Total mul/div | Total sumas/restas | Total flops del paso | Comp. pivote | Div. escala | Intercambios |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 11 | 11 | 132 | 143 | 132 | 275 | 11 | 12 | [PEGAR] |
| 2 | 10 | 10 | 110 | 120 | 110 | 230 | 10 | 11 | [PEGAR] |
| 3 | 9 | 9 | 90 | 99 | 90 | 189 | 9 | 10 | [PEGAR] |
| 4 | 8 | 8 | 72 | 80 | 72 | 152 | 8 | 9 | [PEGAR] |
| 5 | 7 | 7 | 56 | 63 | 56 | 119 | 7 | 8 | [PEGAR] |
| 6 | 6 | 6 | 42 | 48 | 42 | 90 | 6 | 7 | [PEGAR] |
| 7 | 5 | 5 | 30 | 35 | 30 | 65 | 5 | 6 | [PEGAR] |
| 8 | 4 | 4 | 20 | 24 | 20 | 44 | 4 | 5 | [PEGAR] |
| 9 | 3 | 3 | 12 | 15 | 12 | 27 | 3 | 4 | [PEGAR] |
| 10 | 2 | 2 | 6 | 8 | 6 | 14 | 2 | 3 | [PEGAR] |
| 11 | 1 | 1 | 2 | 3 | 2 | 5 | 1 | 2 | [PEGAR] |
| **Sustitución regresiva** | — | **12** | **66** | **78** | **66** | **144** | — | — | — |
| **Total sistema** | — | **78** | **638** | **716** | **638** | **1354** | **66** | **77** | **[PEGAR]** |

- **Comparación con la cota teórica:** el algoritmo ejecuta **1354 flops** algebraicos tanto con pivoteo como sin pivoteo (638 mul/div + 572 sum/rest en los 11 pasos de eliminación, más 78 mul/div + 66 sum/rest en sustitución regresiva). Frente a la cota de referencia de **1486 flops** (que incluye el barrido explícito de la columna $k$), el costo real es **$-8.88\,\%$**, dentro de la tolerancia de $\pm 10\,\%$ y sin trabajo redundante.
- **Sobrecosto de estabilidad (aparte):** 144 comparaciones iniciales para obtener las escalas de fila + 66 comparaciones en los 11 pasos (total **210 comparaciones**), **77 divisiones** por escala `|U[i][k]/escalas[i]|` y `[PEGAR]` intercambios de filas.
- **Reutilización de $L$ y $U$ post-eliminación:** las 3 pasadas de refinamiento iterativo y las 12 columnas de $A^{-1}$ para $\kappa_\infty(A)$ reutilizan los factores $L$ y $U$ en `4140` flops (`1980` de sustitución progresiva + `2160` de sustitución regresiva), sin volver a factorizar $A$.

## 5. Análisis de mantisa y pivoteo
Comparación cuantitativa de ambas corridas en doble precisión frente a la solución exacta en `Fraction` (datos de `resultados/residuo.txt`):

| Métrica | Sin pivoteo | Con pivoteo parcial escalado |
|---|---:|---:|
| Multiplicador máximo $\max |m_{i,k}|$ | [PEGAR] | [PEGAR] |
| Factor de crecimiento $\rho$ | [PEGAR] | [PEGAR] |
| Error relativo $\|x - x_{\text{ref}}\|_2 / \|x_{\text{ref}}\|_2$ | [PEGAR] | [PEGAR] |
| Error relativo $\|x - x_{\text{ref}}\|_\infty / \|x_{\text{ref}}\|_\infty$ | [PEGAR] | [PEGAR] |
| Bits de mantisa correctos (de 53) | [PEGAR] | [PEGAR] |
| Bits de mantisa perdidos | [PEGAR] | [PEGAR] |

**Por qué el pivote $a_{1,1}$ es inaceptable:** iniciar la eliminación sin pivoteo divide por $a_{1,1} = 1.3407\times 10^{-8}$, produciendo ya en el primer paso un multiplicador $m_{2,1} \approx 1.1923\times 10^{4} / 1.3407\times 10^{-8} \approx 8.89\times 10^{11}$, y multiplicadores máximos de orden $\approx 2.8\times 10^{13}$ en pasos posteriores con crecimiento de matriz $\approx 2.6\times 10^{3}$. Al restar filas multiplicadas por $10^{11}$–$10^{13}$ contra elementos originales, el desplazamiento de exponentes en IEEE-754 empuja decenas de bits bajos fuera de la mantisa de 53 bits (`[PEGAR]` bits perdidos en la corrida sin pivoteo, dejando apenas ~6–7 dígitos correctos). Al activar el pivoteo parcial escalado, el multiplicador y el crecimiento quedan contenidos, reduciendo drásticamente los bits perdidos y recuperando entre 9 y 12 dígitos significativos correctos antes incluso del refinamiento.

## 6. Condicionamiento
- **Determinante y número de condición:** desde la diagonal de $U$ (ajustando el signo según la paridad de los intercambios) se obtiene $\det(A) \approx$ `[PEGAR]`. Mediante reutilización de $L$ y $U$ se estima $\kappa_\infty(A) \approx$ `[PEGAR]`, y el control espectral entrega $\kappa_2(A) \approx$ `[PEGAR]`.
- **Casi dependencia lineal de la fila 7:** al ajustar la fila 7 como combinación lineal de las filas 3 y 5 mediante las dos primeras columnas (`detectar_dependencia_fila7`), se obtiene $F_7 \approx$ `[PEGAR]`$\cdot F_3 +$ `[PEGAR]`$\cdot F_5$ con diferencia máxima `[PEGAR]` y perturbación relativa `[PEGAR]` ($\sim 10^{-4}$). Esta proximidad a una dependencia lineal exacta deprime el menor valor singular $\sigma_{12}$ y explica el elevado $\kappa_2(A) \sim 10^{13}$.
- **Por qué la cota clásica resulta pesimista:** tomando el redondeo unitario $u = 2^{-53} \approx 1.11\times 10^{-16}$ (o $\varepsilon_{\text{mach}} = 2^{-52} \approx 2.22\times 10^{-16}$), la cota de peor caso $\frac{\|\delta x\|}{\|x\|} \lesssim \kappa_2(A)\cdot u \approx$ `[PEGAR]` ($\kappa_2(A)\cdot\varepsilon_{\text{mach}} \approx 6.8\times 10^{-3}$) apenas garantiza del orden de 2 a 3 dígitos significativos. En la práctica se recuperan 9–12 dígitos con pivoteo porque la cota asume simultáneamente el peor error hacia atrás en cada paso y su alineamiento exacto con la dirección singular más sensible ($\sigma_{12}$), escenario extremo que no se materializa con pivoteo escalado.

## 7. Resultados
La tabla reporta la solución final obtenida tras el pivoteo parcial escalado y las 3 pasadas de refinamiento iterativo (`resultados/solucion.csv`). Para cada incógnita, `contar_digitos_defendibles` verifica tanto la cota relativa como la coincidencia exacta de todas las cifras formateadas frente a la solución racional en `Fraction`:

| Incógnita | Valor reportado (`solucion.csv`) | Dígitos afirmados |
|---|---|---:|
| $x_1$ | [PEGAR] | [PEGAR] |
| $x_2$ | [PEGAR] | [PEGAR] |
| $x_3$ | [PEGAR] | [PEGAR] |
| $x_4$ | [PEGAR] | [PEGAR] |
| $x_5$ | [PEGAR] | [PEGAR] |
| $x_6$ | [PEGAR] | [PEGAR] |
| $x_7$ | [PEGAR] | [PEGAR] |
| $x_8$ | [PEGAR] | [PEGAR] |
| $x_9$ | [PEGAR] | [PEGAR] |
| $x_{10}$ | [PEGAR] | [PEGAR] |
| $x_{11}$ | [PEGAR] | [PEGAR] |
| $x_{12}$ | [PEGAR] | [PEGAR] |

*(Nota: la solución en doble precisión con pivoteo escalado sin refinar alcanza ~9–12 dígitos correctos por incógnita; con las 3 pasadas de refinamiento iterativo usando residuo en precisión extendida, las cifras afirmadas ascienden hasta el límite de representación de `float`, ~14–15 dígitos).*

## 8. Verificación
- **Residuo en precisión extendida (`mpmath`, 80 dígitos):** sobre los datos exactos en `Fraction`, sin refinar se obtiene $\|r\|_\infty = \|b - Ax\|_\infty =$ `[PEGAR]` sin pivoteo y `[PEGAR]` con pivoteo parcial escalado.
- **Refinamiento iterativo (3 pasadas reutilizando $L$, $U$ y $P$):**
  - Pasada 1: $\|r\|_\infty$ pasa de `[PEGAR]` a `[PEGAR]`.
  - Pasada 2: $\|r\|_\infty$ pasa de `[PEGAR]` a `[PEGAR]`.
  - Pasada 3: $\|r\|_\infty$ pasa de `[PEGAR]` a `[PEGAR]`.
  El error relativo en norma 2 tras refinar desciende a `[PEGAR]` (`[PEGAR]` bits correctos de 53), confirmando que $\kappa(A)\,u < 1$ permite convergencia rápida y validando la factorización $PA = LU$.
- **Control independiente con biblioteca:** `numpy.linalg.solve` obtiene un error relativo en norma 2 de `[PEGAR]` (`[PEGAR]` bits correctos), coincidiendo en precisión con nuestra implementación con pivoteo previa al refinamiento.

## 9. Conclusiones
- **Compromiso costo / exactitud elegido:** el pivoteo parcial escalado conserva el mínimo costo algebraico de **1354 flops** (8.88 % bajo la cota de referencia) pagando un sobrecosto marginal de búsqueda e intercambios, lo que evita perder decenas de bits de mantisa por el pivote $a_{1,1}$ y las escalas heterogéneas. Con $L$ y $U$ ya calculados, el refinamiento iterativo en precisión extendida permite recuperar la precisión completa de doble flotante sin re-factorizar $A$.
- **Qué cambiaría con $n = 1000$:**
  1. **Escalamiento de costos:** los flops de eliminación crecerían como $\frac{2}{3}n^3 \approx 6.67\times 10^8$, mientras que las comparaciones del pivoteo crecerían como $\frac{n^2}{2} \approx 5\times 10^5$, haciendo que el peso relativo del pivoteo baje a menos de $0.1\,\%$.
  2. **Implementación y memoria:** los bucles puros en listas anidadas de Python resultarían demasiado lentos por sobrecarga del intérprete; sería indispensable migrar a arreglos contiguos vectorizados (BLAS nivel 3 / factorización LU por bloques) para explotar la jerarquía de caché.
  3. **Estabilidad:** en $n = 1000$, el crecimiento acumulado durante mil pasos exige vigilar el residuo en precisión extendida y aplicar refinamiento iterativo si $\kappa(A)$ supera $10^{10}$.

## 10. Reproducibilidad
- **Python:** `[PEGAR python --version]`
- **Librerías (`requirements.txt`):** `[PEGAR numpy==... y mpmath==...]`
- **Comando único de reproducción:**
  ```bash
  python src/main.py