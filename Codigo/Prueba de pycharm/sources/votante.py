from sources.estado_votante import EstadoVotante

class Votante:
    cedula: str
    nombre: str
    correo: str
    estado_voto: EstadoVotante


    def __init__(self, cedula, nombre, correo):
        self.cedula = cedula
        self.nombre = nombre
        self.correo = correo
        self.estado_voto = EstadoVotante.NO_AUTORIZADO

    def esta_autorizado(self) -> bool:
        return self.estado_voto == EstadoVotante.AUTORIZADO

    def autorizar_voto(self):
        self.estado_voto = EstadoVotante.AUTORIZADO

    def desactivar_autorizacion_voto(self):
        self.estado_voto = EstadoVotante.NO_AUTORIZADO

    def obtener_correo(self) -> str:
        return self.correo