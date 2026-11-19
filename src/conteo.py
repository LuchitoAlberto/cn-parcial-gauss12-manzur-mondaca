from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class RegistroPaso:
    paso: int
    divisiones:int = 0
    multiplicaciones:int = 0
    sumasyrestas:int = 0
    comparaciones_pivoteo:int = 0
    divisiones_escala:int = 0
    intercambios_de_filas:int = 0
    fila_pivote_elegida:int = 0
    multiplicador_max_paso:int = 0

    def multi_divi(self) -> int: 
        return self.divisiones + self.multiplicaciones # Multiplicaciones + divisiones del paso

    def total_arithmetic_operations(self) -> int:
        return self.divisiones + self.multiplicaciones + self.sumasyrestas # Total de flops aritmeticos del paso (sin el pivoteo)
    
@dataclass
class ContadorOperaciones:
    n:int
    pasos: list[RegistroPaso] = field(default_factory=list)
    comparaciones_iniciales_escala:int = 0
    sust_reg_multiplicaciones:int = 0
    sust_reg_divisiones:int = 0
    sust_reg_restas:int = 0
    sust_prog_reutilizacion_flops: int = 0
    sust_reg_reutilizacion_flops: int = 0

    def iniciar_paso(self, numero_paso:int) -> RegistroPaso:
        registro = RegistroPaso(paso=numero_paso, fila_pivote_elegida=numero_paso)
        self.pasos.append(registro)
        return registro

    def total_eliminacion_mul_div(self) -> int:
        acumulado = 0
        for registro in self.pasos:
            acumulado = acumulado + registro.multi_divi()
        return acumulado

    def total_eliminacion_sumas_resta(self) -> int:
        acumulado = 0
        for registro in self.pasos:
            acumulado = acumulado + registro.sumasyrestas
        return acumulado

    def total_elimin(self) -> int:
        return self.total_eliminacion_mul_div() + self.total_eliminacion_sumas_resta()

    def total_sust_reg_mul_div(self) -> int:
        return self.sust_reg_multiplicaciones + self.sust_reg_divisiones

    def total_sust_reg(self) -> int:
        return self.total_sust_reg_mul_div() + self.sust_reg_restas

    def total_multi_divi_sistema(self) -> int: # Mult/div de todo el sistema (eliminacion + sustitucion)
        return self.total_eliminacion_mul_div() + self.total_sust_reg_mul_div()

    def total_suma_resta_sistema(self) -> int: # Sumas/restas de todo el sistema
        return self.total_eliminacion_sumas_resta() + self.sust_reg_restas

    def total_flops_sistema(self) -> int: # Flops totales del sistema(sin contar el pivoteo)
        return self.total_elimin() + self.total_sust_reg()

    def total_comparaciones_en_pasos(self) -> int:
        acumulado = 0
        for registro in self.pasos:
            acumulado = acumulado + registro.comparaciones_pivoteo
        return acumulado

    def total_comparaciones_pivoteo(self) -> int:
        return self.comparaciones_iniciales_escala + self.total_comparaciones_en_pasos()

    def total_divisiones_escala(self) -> int:
        acumulado = 0
        for registro in self.pasos:
            acumulado = acumulado + registro.divisiones_escala
        return acumulado

    def total_intercambios_de_filas(self) -> int:
        acumulado = 0
        for registro in self.pasos:
            acumulado = acumulado + registro.intercambios_de_filas
        return acumulado

def generar_reporte_flops(contador_sin: ContadorOperaciones, contador_con: ContadorOperaciones, ruta_salida: Path) -> str:
    cota_referencia = 1486
    total_con = contador_con.total_flops_sistema()
    diferencia_pct = ((total_con - cota_referencia) / cota_referencia) * 100
    reuso_lu = contador_con.sust_prog_reutilizacion_flops + contador_con.sust_reg_reutilizacion_flops

    lineas: list[str] = []
    lineas.append(f"== Conteo de Operaciones == ")

    # Tabla por paso
    lineas.append("==== Costo por paso =====")
    lineas.append("")
    lineas.append("| Paso k | Filas por eliminar | Divisiones | Multiplicaciones | Total mul/div | Total sumas/restas | Total flops del paso | Comparaciones de pivote | Divisiones de escala | Intercambios de fila |")
    lineas.append("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")

    for reg in contador_con.pasos:
        filas_restantes = contador_con.n - reg.paso
        fila_md = f"| {reg.paso} | {filas_restantes} | {reg.divisiones} | {reg.multiplicaciones} | {reg.multi_divi()} | {reg.sumasyrestas} | {reg.total_aritmeticas()} | {reg.comparaciones_pivoteo} | {reg.divisiones_escala} | {reg.intercambios_de_filas} |"
        lineas.append(fila_md)

    lineas.extend([
        "",
        "==== Totales ====",
        "",
        "| Fase / corrida | Multi/div | Sumas/restas | Total|",
        "| ---: | ---: | ---: | ---: |",
        f"| Eliminación (11 pasos) | {contador_con.total.eliminacion_mul_div()} | {contador_con.total_eliminacion_sumas_resta()} | {contador_con.total_elimin()} |",
        f"| Sustitución regresiva | {contador_con.total_sust_reg_mul_div()} | {contador_con.sust_reg_restas} | {contador_con.total_sust_reg()} |",
        f"| Total sin pivoteo | {contador_sin.total_multi_divi_sistema()} | {contador_sin.total_suma_resta_sistema()} | {contador_sin.total_flops_sistema()} |",
        f"| Total con pivoteo | {contador_con.total_multi_divi_sistema()} | {contador_con.total_suma_resta_sistema()} | {total_con} |",
        f"Comparaciones pivoteo: {contador_con.total_comparaciones_iniciales_escala} + {contador_con.total_comparaciones_en_pasos()} = {contador_con.total_comparaciones_pivoteo()}",
        f"Divisiones de escala: {contador_con.total_divisiones_escala()}",
        f"Intercambios de fila: {contador_con.total_intercambios_de_filas()}",
        f"Cota referencia: {cota_referencia}: {total_con} ({diferencia_pct:.2f}%)",
        f"Reutilizacion LU: {reuso_lu} flops"
       ])
    return 