from datetime import datetime
from time import sleep

from sources.candidato import Candidato
from sources.estado_votacion import EstadoVotacion
from sources.votante import Votante

class SistemaElectoral:
    candidatos: dict[str, Candidato]
    votantes: dict [str, Votante]
    fecha_inicio: datetime
    fecha_fin: datetime
    estado_proceso_electoral: EstadoVotacion
    cola_confirmaciones: list[str]

    def __init__(self, candidatos, votantes, fecha_inicio: datetime, fecha_fin: datetime):
        self.validar_candidatos(candidatos)
        self.validar_votantes(votantes)
        self.validar_fechas(fecha_inicio, fecha_fin)

        self.candidatos = candidatos
        self.votantes = votantes
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

        self.estado_proceso_electoral = EstadoVotacion.INACTIVO  # Estado inicial

        #Autorizar votantes al crear el sistema electoral
        self.autorizar_votantes()
        # Cola vacía al inicio
        self.cola_confirmaciones = []


    ## VALIDACIONES ##
    def validar_candidatos(self, candidatos):
        if not candidatos:
            raise ValueError("Debe existir al menos un candidato.")

    def validar_votantes(self, votantes):
        if not votantes:
            raise ValueError("Debe existir al menos un votante registrado.")

    def validar_fechas(self, fecha_inicio: datetime, fecha_fin: datetime):
        if fecha_inicio >= fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin.")

    ## MÉTODOS PRINCIPALES PARA LOGICA DEL NEGOCIO##
    def activar_proceso_electoral(self):
        if self.estado_proceso_electoral == EstadoVotacion.ACTIVO:
            return
        elif self.validar_puede_activarse() is False:
            return

        self.estado_proceso_electoral = EstadoVotacion.ACTIVO


    def validar_puede_activarse(self):
        return (self.candidatos is not None and self.votantes is not None
                and self.fecha_inicio is not None and self.fecha_fin is not None)

    def autorizar_votantes(self):
        for votante in self.votantes.values():
            votante.autorizar_voto()

    def esta_activo(self):
        return self.estado_proceso_electoral == EstadoVotacion.ACTIVO

    def esta_votante_autorizado(self, cedula: str) -> bool:
        votante = self.votantes.get(cedula)
        if votante is None:
            return False
        return votante.esta_autorizado()

    def emitir_voto(self, cedula_votante: str, nombre_candidato: str):
        if not self.esta_activo():
            raise ValueError("El proceso electoral no está activo.")
        elif not self.esta_votante_autorizado(cedula_votante):
            raise ValueError("El votante no está autorizado para votar.")

        votante_emisor = self.votantes.get(cedula_votante)
        candidato_escogido = self.candidatos.get(nombre_candidato)

        # --------------------------
        # 1. SNAPSHOT DEL ESTADO
        # --------------------------
        votos_previos = self.contar_votos_candidato(nombre_candidato)

        try:
            # --------------------------
            # 2. OPERACIONES CRÍTICAS
            # --------------------------
            candidato_escogido.aumentar_voto()
            votante_emisor.desactivar_autorizacion_voto()
            self.agregar_confirmacion_voto(votante_emisor.obtener_correo())
        except Exception as e:
            # --------------------------
            # 3. REVERTIR SI ALGO FALLA
            # --------------------------
            candidato_escogido.reasignar_votos(votos_previos)

            votante_emisor.autorizar_voto()
            self.quitar_confirmacion_voto(votante_emisor.obtener_correo())


            raise ValueError(f"Error al registrar el voto: {e}")

    def contar_votos_candidato(self, candidato) -> int:
        try:
            return self.candidatos[candidato].obtener_votos()
        except KeyError:
            raise ValueError(f"Error al intentar obtener los votos del candidato'{candidato}'.")

    def agregar_confirmacion_voto(self, correo_votante: str):
        self.cola_confirmaciones.append(correo_votante)

    def quitar_confirmacion_voto(self, correo_votante: str):
        if correo_votante in self.cola_confirmaciones:
            self.cola_confirmaciones.remove(correo_votante)


    def esta_confirmacion_voto_en_cola(self, correo_votante: str) -> bool:
        # Simular la verificación en la cola de envíos
        # En un sistema real, esto implicaría consultar una base de datos o una cola de mensajes
        # Aquí simplemente
        return correo_votante in self.cola_confirmaciones

