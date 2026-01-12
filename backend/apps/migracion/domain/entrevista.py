class Entrevista:
    MAX_REPROGRAMACIONES = 2

    def __init__(self, fecha):
        self.fecha = fecha
        self.estado = "Programada"
        self.horarios_disponibles = set()
        self.horarios_ocupados = set()
        self.reprogramaciones = 0
    def modificar_directamente(self):
        """
        No se permite modificar una entrevista programada
        fuera del proceso de reprogramación.
        """
        raise ValueError("Modificación directa no permitida")

    def reprogramar(self, nueva_fecha):
        if self.reprogramaciones >= self.MAX_REPROGRAMACIONES:
            raise ValueError("Límite máximo de reprogramaciones alcanzado")

        self.fecha = nueva_fecha
        self.estado = "Reprogramada"
        self.reprogramaciones += 1
