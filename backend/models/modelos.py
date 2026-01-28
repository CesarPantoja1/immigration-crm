"""
Modelos para los tests BDD de simulacion de entrevistas.
Adaptados a las necesidades del feature simulacion_entrevista.feature
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class TipoVisa(Enum):
    """Tipos de visa disponibles."""
    ESTUDIANTE = "Estudiante"
    TRABAJO = "Trabajo"
    TURISMO = "Turismo"
    VIVIENDA = "Vivienda"


class Modalidad(Enum):
    """Modalidad del simulacro."""
    VIRTUAL = "Virtual"
    PRESENCIAL = "Presencial"


class EstadoSimulacro(Enum):
    """Estados posibles de un simulacro."""
    PENDIENTE_RESPUESTA = "Pendiente de respuesta"
    CONFIRMADO = "Confirmado"
    EN_SALA_ESPERA = "En sala de espera"
    EN_PROGRESO = "En progreso"
    COMPLETADO = "Completado"
    CONTRAPROPUESTA_PENDIENTE = "Contrapropuesta pendiente"
    CANCELADO = "Cancelado"


@dataclass
class ConfiguracionSistema:
    """Configuracion del sistema para simulacros."""
    maximo_simulacros: int = 2
    minutos_anticipacion_entrada: int = 15
    horas_cancelacion_anticipada: int = 24


@dataclass
class Simulacro:
    """Representa un simulacro de entrevista."""
    id_simulacro: str
    fecha: str
    hora: str
    modalidad: Modalidad
    asesor: str
    estado: EstadoSimulacro = EstadoSimulacro.PENDIENTE_RESPUESTA
    fecha_propuesta: Optional[str] = None
    duracion_minutos: int = 0
    grabacion_activa: bool = False
    hora_inicio: Optional[datetime] = None
    mensaje_error: Optional[str] = None

    @property
    def id(self) -> str:
        return self.id_simulacro

    def ingresar_sala_espera(self, hora_actual: datetime, minutos_anticipacion: int) -> bool:
        """Intenta ingresar a la sala de espera."""
        hora_simulacro = datetime.strptime(f"{self.fecha} {self.hora}", "%Y-%m-%d %H:%M")
        diferencia = hora_simulacro - hora_actual
        minutos_restantes = diferencia.total_seconds() / 60

        if 0 <= minutos_restantes <= minutos_anticipacion:
            self.estado = EstadoSimulacro.EN_SALA_ESPERA
            return True
        return False

    def iniciar_sesion(self) -> bool:
        """Inicia la sesion del simulacro."""
        if self.estado in [EstadoSimulacro.EN_SALA_ESPERA, EstadoSimulacro.CONFIRMADO]:
            self.estado = EstadoSimulacro.EN_PROGRESO
            self.grabacion_activa = True
            self.hora_inicio = datetime.now()
            return True
        return False

    def finalizar(self, duracion: int, migrante: 'Migrante') -> bool:
        """Finaliza el simulacro."""
        if self.estado == EstadoSimulacro.EN_PROGRESO:
            self.estado = EstadoSimulacro.COMPLETADO
            self.duracion_minutos = duracion
            self.grabacion_activa = False
            migrante.contador_simulacros += 1
            return True
        return False

    def cancelar(self, fecha_actual: datetime, horas_minimas: int) -> tuple:
        """Intenta cancelar el simulacro."""
        hora_simulacro = datetime.strptime(f"{self.fecha} {self.hora}", "%Y-%m-%d %H:%M")
        diferencia = hora_simulacro - fecha_actual
        horas_restantes = diferencia.total_seconds() / 3600

        if horas_restantes >= horas_minimas:
            self.estado = EstadoSimulacro.CANCELADO
            return True, False  # exito, sin penalizacion
        else:
            self.mensaje_error = "No puedes cancelar con menos de 24 horas de anticipacion"
            return False, True  # fallo, con penalizacion


@dataclass
class Migrante:
    """Representa un migrante en el sistema."""
    id_migrante: str
    nombre: str
    tipo_visa: TipoVisa = TipoVisa.ESTUDIANTE
    fecha_cita_embajada: Optional[datetime] = None
    contador_simulacros: int = 0
    ha_accedido_practica: bool = False
    simulacros: List[Simulacro] = field(default_factory=list)
    maximo_simulacros: int = 2

    @property
    def id(self) -> str:
        return self.id_migrante

    def agregar_simulacro(self, simulacro: Simulacro) -> None:
        """Agrega un simulacro a la lista."""
        self.simulacros.append(simulacro)

    def buscar_simulacro(self, id_simulacro: str) -> Optional[Simulacro]:
        """Busca un simulacro por ID."""
        for sim in self.simulacros:
            if sim.id == id_simulacro:
                return sim
        return None

    def aceptar_propuesta(self, id_simulacro: str) -> bool:
        """Acepta una propuesta de simulacro."""
        simulacro = self.buscar_simulacro(id_simulacro)
        if simulacro and simulacro.estado == EstadoSimulacro.PENDIENTE_RESPUESTA:
            simulacro.estado = EstadoSimulacro.CONFIRMADO
            self.contador_simulacros += 1
            return True
        return False

    def proponer_fecha_alternativa(self, id_simulacro: str, nueva_fecha: str) -> bool:
        """Propone una fecha alternativa para el simulacro."""
        simulacro = self.buscar_simulacro(id_simulacro)
        if simulacro:
            simulacro.estado = EstadoSimulacro.CONTRAPROPUESTA_PENDIENTE
            simulacro.fecha_propuesta = nueva_fecha
            return True
        return False

    def puede_solicitar_simulacro(self) -> bool:
        """Verifica si puede solicitar un nuevo simulacro."""
        return self.contador_simulacros < self.maximo_simulacros

    def obtener_mensaje_disponibilidad(self) -> str:
        """Obtiene el mensaje de disponibilidad."""
        if self.contador_simulacros == 0:
            return "Puede solicitar hasta 2 simulacros en total"
        elif self.contador_simulacros == 1:
            return "Tiene 1 simulacro disponible restante"
        else:
            return "Ha alcanzado el limite de 2 simulacros por proceso"


@dataclass
class Cuestionario:
    """Representa un cuestionario de practica."""
    tipo_visa: TipoVisa
    total_preguntas: int
    respuestas_correctas: int = 0
    completado: bool = False

    def completar(self, correctas: int) -> None:
        """Marca el cuestionario como completado."""
        self.respuestas_correctas = correctas
        self.completado = True

    def obtener_porcentaje(self) -> int:
        """Calcula el porcentaje de aciertos."""
        if self.total_preguntas == 0:
            return 0
        return int((self.respuestas_correctas / self.total_preguntas) * 100)

    def obtener_calificacion(self) -> str:
        """Obtiene la calificacion basada en el porcentaje."""
        porcentaje = self.obtener_porcentaje()
        if porcentaje >= 90:
            return "Excelente"
        elif porcentaje >= 70:
            return "Bueno"
        elif porcentaje >= 50:
            return "Regular"
        else:
            return "Insuficiente"

    def obtener_mensaje(self) -> str:
        """Obtiene el mensaje de retroalimentacion."""
        porcentaje = self.obtener_porcentaje()
        if porcentaje >= 90:
            return "¡Muy bien! Estas muy preparado"
        elif porcentaje >= 70:
            return "Buen trabajo, repasa las preguntas incorrectas"
        elif porcentaje >= 50:
            return "Necesitas practicar mas antes del simulacro real"
        else:
            return "Te recomendamos estudiar mas este tema"


@dataclass
class PreguntaIncorrecta:
    """Representa una pregunta respondida incorrectamente."""
    texto: str
    respuesta_usuario: str
    respuesta_correcta: str
    explicacion: str
