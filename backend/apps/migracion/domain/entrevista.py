class Entrevista:
    def __init__(self, fecha):
        self.fecha = fecha
        self.estado = "Programada"
        self.horarios_disponibles = set()
        self.horarios_ocupados = set()

    def modificar_directamente(self):
        """
        No se permite modificar una entrevista programada
        fuera del proceso de reprogramación.
        """
        raise ValueError("Modificación directa no permitida")