#language: es

Característica: Agendamiento de entrevista
  Como solicitante de un trámite migratorio con solicitud previamente aprobada,
  quiero agendar una entrevista asociada a mi solicitud,
  para cumplir una etapa obligatoria del proceso y continuar con mi trámite.

Antecedentes:
  Dado que el solicitante cuenta con una solicitud migratoria aprobada
  Y el sistema presenta opciones de fecha y horario para entrevistas
  Y la fecha actual del sistema es "<fecha_actual>"


# ===============================
# AGENDAMIENTO DE ENTREVISTA
# ===============================

Escenario: Registro de fecha y horario seleccionados por el solicitante
  Dado que el solicitante accede al agendamiento de entrevista
  Cuando el solicitante selecciona una fecha y un horario disponibles
  Entonces el sistema registra la entrevista asociada a su solicitud
  Y la entrevista queda en estado "Programada"
  Y la selección queda protegida frente a modificaciones no autorizadas


Escenario: Agendamiento con selección de horario específico
  Dado que existe una fecha de entrevista con horarios disponibles
  Cuando el solicitante selecciona la fecha "<fecha_actual + 35 días>" y el horario "<config.horario_inicio>"
  Entonces el sistema agenda la entrevista exitosamente
  Y el horario seleccionado queda registrado como no disponible
  Y muestra el mensaje "Entrevista agendada para el <fecha_actual + 35 días (formato_legible)> a las <config.horario_inicio>"


Escenario: Visualización de entrevista programada en el seguimiento del trámite
  Dado que el solicitante tiene una entrevista en estado "Programada"
  Cuando consulta el seguimiento de su trámite
  Entonces el sistema muestra la fecha y horario de la entrevista
  Y no presenta la opción de agendamiento nuevamente


# ===============================
# PROTECCIÓN E INTEGRIDAD
# ===============================

Escenario: Protección de la entrevista frente a cambios fuera del proceso de reprogramación
  Dado que el solicitante tiene una entrevista en estado "Programada"
  Cuando realiza una acción que no corresponde al proceso de reprogramación
  Entonces el sistema no permite modificar la fecha ni el horario
  Y la entrevista se mantiene sin cambios


Escenario: Intento de agendar una nueva entrevista cuando ya existe una programada
  Dado que el solicitante tiene una entrevista en estado "Programada"
  Cuando intenta agendar una nueva entrevista
  Entonces el sistema no permite crear una nueva entrevista
  Y mantiene la entrevista existente sin cambios
  Y muestra el mensaje "Ya existe una entrevista programada para esta solicitud"


# ===============================
# REPROGRAMACIÓN
# ===============================

Esquema del escenario: Restricción de reprogramaciones sucesivas
  Dado que el solicitante tiene una entrevista que ha sido reprogramada "<cantidad_reprogramaciones>" veces
  Y la embajada define un máximo de "<config.max_reprogramaciones>" reprogramaciones por solicitud
  Cuando el solicitante solicita un nuevo cambio de fecha
  Entonces el sistema debe "<accion_sistema>" la reprogramación
  Y mostrar el mensaje "<mensaje>"

Ejemplos:
  | cantidad_reprogramaciones         | accion_sistema | mensaje |
  | <config.max_reprogramaciones - 1> | permitir       | Esta es su última reprogramación permitida |
  | <config.max_reprogramaciones>     | bloquear       | Error: ha alcanzado el límite máximo de reprogramaciones |


# ===============================
# CANCELACIÓN
# ===============================

Esquema del escenario: Cancelación de entrevista según tiempo disponible
  Dado que el solicitante tiene una entrevista agendada
  Y el tiempo restante hasta la entrevista es de "<horas_restantes>" horas
  Cuando el solicitante decide cancelar la entrevista
  Entonces el sistema debe "<accion_sistema>" la cancelación
  Y mostrar el mensaje "<mensaje>"

Ejemplos:
  | horas_restantes                    | accion_sistema | mensaje |
  | ><config.minimo_horas_cancelacion> | permitir       | Cancelación confirmada exitosamente |
  | <<config.minimo_horas_cancelacion> | bloquear       | Error: no se puede cancelar con menos de <config.minimo_horas_cancelacion> horas |


Escenario: Cancelación exitosa de entrevista
  Dado que el solicitante tiene una entrevista agendada
  Y el tiempo restante hasta la entrevista es mayor a "<config.minimo_horas_cancelacion>" horas
  Cuando el solicitante decide cancelar la entrevista
  Entonces la entrevista cambia a estado "Cancelada"
  Y el solicitante recibe una confirmación de la cancelación
  Y la entrevista deja de aparecer como pendiente en el seguimiento del trámite
  Y la cancelación queda registrada en el historial


Escenario: Restricción de cancelación con tiempo insuficiente
  Dado que el solicitante tiene una entrevista agendada
  Y faltan menos de "<config.minimo_horas_cancelacion>" horas para la entrevista
  Cuando el solicitante intenta cancelar la entrevista
  Entonces el sistema bloquea la cancelación
  Y muestra el mensaje "Error: no se puede cancelar con menos de <config.minimo_horas_cancelacion> horas de anticipación"
  Y sugiere contactar directamente con "<config.telefono_oficina>" o "<config.email_oficina>"
