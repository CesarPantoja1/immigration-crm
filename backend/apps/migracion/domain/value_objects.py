class ReglaCancelacion:
    def __init__(self, minimo_horas):
        self.minimo_horas = minimo_horas

    def permite_cancelar(self, horas_restantes):
        return horas_restantes >= self.minimo_horas