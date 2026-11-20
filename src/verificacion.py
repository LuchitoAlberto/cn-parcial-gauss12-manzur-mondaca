from typing import Tuple, list, Dict
from decimal import Decimal

import numpy as np
from mpmath import mp

digitos_extendidos = 50

def decimal_a_mpf(valor_decimal: Decimal) -> mp.mpf:
    return mp.mpf(str(valor_decimal))

def float_a_mpf(valor_float: float) -> mp.mpf:
    decimal_exacto = Decimal.from_float(valor_float)
    return mp.mpf(str(decimal_exacto))

def matriz_dec_a_mpf(A_dec: list[list[Decimal]]) -> list[list[mp.mpf]]:
    A_mp = list[list[mp.mpf]] = []
    for fila in A_dec:
        fila_mpf: list[mp.mpf] = []
        for valor in fila:
            fila_mpf.append(decimal_a_mpf(valor))
        A_mp.append(fila_mpf)
    return A_mp

def vector_dec_a_mpf(b_dec: list[Decimal]) -> list[mp.mpf]:
    b_mp = list[mp.mpf] = []
    for valor in b_dec:
        b_mp.append(decimal_a_mpf(valor))
    return b_mp

def residuo_extendido(A_dec: list[list[mp.mpf]], b_dec: list[mp.mpf], x_mp: list[mp.mpf]) -> Tuple[list[mp.mpf], mp.mpf]:
    mp.dps = digitos_extendidos
    n = len(b_dec)
    A_mp = matriz_dec_a_mpf(A_dec)
    b_mp = vector_dec_a_mpf(b_dec)

    r: list[mp.mpf] = []
    norma_inf = mp.mpf("0")

    for i in range(n):
        producto = mp.mpf("0")
        for j in range(n):
            producto = producto + A_mp[i][j] * x_mp[j]
        ri = b_mp[i] - producto
        r.append(ri)
        abs_ri = abs(ri)
        if abs_ri > norma_inf:
            norma_inf = abs_ri 
    return r, norma_inf
   