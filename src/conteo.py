from dataclasses import dataclass, field

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
        return self.divisiones + self.multiplicaciones

    def total_arithmetic_operations(self) -> int:
        return self.divisiones + self.multiplicaciones + self.sumasyrestas
    
@dataclass
class ContadorOperaciones:
    n:int
    pasos: list[RegistroPaso] = field(default_factory=list)
    comparaciones_iniciales_escala:int = 0
    susti_reg_multiplicaciones:int = 0
    susti_reg_divisiones:int = 0
    susti_reg_restas:int = 0
    susti_prog_reutilizacion_flops: int = 0
    susti_reg_reutilizaicones_flops: int = 0

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

    def total_susti_reg_mul_div(self) -> int:
        return self.susti_reg_multiplicaciones + self.susti_reg_divisiones

    def total_susti_reg(self) -> int:
        return self.total_susti_reg_mul_div() + self.susti_reg_restas

    def total_multi_divi_sistema(self) -> int:
        return self.total_eliminacion_mul_div() + self.total_susti_reg_mul_div()

    def total_suma_resta_sistema(self) -> int:
        return self.total_eliminacion_sumas_resta() + self.susti_reg_restas

    def total_flops_sistema(self) -> int:
        return self.total_elimin() + self.total_susti_reg()

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