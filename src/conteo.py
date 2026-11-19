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

    def iniciar_paso():
        return

    def total_eliminacion_mul_div():
        return

    def total_eliminacion_sumas_resta():
        return

    def total_elimin():
        return

    def total_susti_reg_mul_div():
        return

    def total_susti_reg():
        return

    def total_multi_divi_sistema():
        return

    def total_suma_resta_sistema():
        return

    def total_flops_sistema():
        return

    def total_comparaciones_en_pasos():
        return

    def total_divisiones_escala():
        return

    def total_intercambios_de_filas():
        return