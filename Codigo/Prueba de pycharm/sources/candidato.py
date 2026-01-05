class Candidato:
    nombre: str
    partido: str
    votos: int

    def __init__(self, nombre: str, partido: str, votos: int = 0):
        self.nombre = nombre
        self.partido = partido
        self.votos = votos

    def obtener_votos(self) -> int:
        return self.votos

    def aumentar_voto(self):
        self.votos += 1

    def reasignar_votos(self, votos: int):
        self.votos = votos