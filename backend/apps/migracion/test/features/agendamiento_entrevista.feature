#language: es

Característica: Agendamiento de entrevista
  Como solicitante de un trámite migratorio ## Aclarar solicitud aprobada
  quiero agendar una entrevista asociada a mi solicitud
  para cumplir una etapa obligatoria del proceso y continuar con mi trámite.

Antecedentes:
  Dado que el solicitante ha logrado iniciar sesión en el sistema ## No
  Y existe una solicitud migratoria registrada a su nombre
  Y el sistema dispone de fechas de entrevista configuradas
  Y la fecha actual del sistema es "<fecha_actual>"

  ## Caracteristica de solicitud aprobadas , enfocar en seguridad , conjunto seleccion ddescarte, registrar eleccion usuairo
Esquema del escenario: Agendamiento de entrevista según estado de la solicitud
  Dado que la solicitud se encuentra en estado "<estado_solicitud>"
  Cuando el solicitante intenta agendar una entrevista en la fecha "<fecha_entrevista>" ## DO, DONT TRY YODA
  Entonces el sistema debe "<accion_sistema>" el agendamiento
  Y mostrar el mensaje "<mensaje>"

Ejemplos:
  | estado_solicitud | fecha_entrevista              | accion_sistema | mensaje |
  | Aprobada         | <fecha_actual + 35 días>      | permitir       | Entrevista agendada exitosamente |
  | En revisión      | <fecha_actual + 35 días>      | bloquear       | Error: la solicitud aún no está habilitada para entrevista |
  | Observada        | <fecha_actual + 37 días>      | bloquear       | Error: debe corregir la solicitud antes de agendar la entrevista |
  | Aprobada         | <fecha_actual - 30 días>      | bloquear       | Error: la fecha seleccionada no está disponible para entrevistas |


Esquema del escenario: Validación de disponibilidad de fechas para entrevistas
  Dado que la solicitud se encuentra en estado "Aprobada"
  Y el sistema tiene configuradas las siguientes restricciones:
    | anticipacion_minima_dias | anticipacion_maxima_dias | dias_laborables |
    | <config.anticipacion_min>| <config.anticipacion_max>| <config.dias_laborables> |
  Cuando el solicitante intenta agendar una entrevista en la fecha "<fecha_entrevista>"
  Entonces el sistema debe "<accion_sistema>" el agendamiento
  Y mostrar el mensaje "<mensaje>"

Ejemplos:
  | fecha_entrevista                                    | accion_sistema | mensaje |
  | <fecha_actual + (config.anticipacion_min - 1) días> | bloquear       | Error: debe agendar con al menos <config.anticipacion_min> días de anticipación |
  | <fecha_actual + (config.anticipacion_max + 1) días> | bloquear       | Error: no se pueden agendar entrevistas con más de <config.anticipacion_max> días de anticipación |
  | <fecha_actual + 5 días (sábado)>                    | bloquear       | Error: la fecha seleccionada corresponde a un día no laborable (sábado) |
  | <fecha_actual + 6 días (domingo)>                   | bloquear       | Error: la fecha seleccionada corresponde a un día no laborable (domingo) |
  | <fecha_actual + config.anticipacion_min días>       | permitir       | Entrevista agendada exitosamente |


Esquema del escenario: Validación de capacidad disponible en fechas de entrevista
  Dado que la solicitud se encuentra en estado "Aprobada"
  Y la fecha "<fecha_entrevista>" tiene "<cupos_disponibles>" cupos disponibles
  Y la fecha "<fecha_entrevista>" tiene "<cupos_totales>" cupos totales
  Cuando el solicitante intenta agendar una entrevista en la fecha "<fecha_entrevista>"
  Entonces el sistema debe "<accion_sistema>" el agendamiento
  Y mostrar el mensaje "<mensaje>"

Ejemplos:
  | fecha_entrevista                         | cupos_disponibles              | cupos_totales              | accion_sistema | mensaje |
  | <fecha_actual + 35 días>                 | <config.cupos_total * 0.25>    | <config.cupos_total>       | permitir       | Entrevista agendada exitosamente |
  | <fecha_actual + 40 días>                 | 0                              | <config.cupos_total>       | bloquear       | Error: no hay cupos disponibles para la fecha seleccionada |
  | <fecha_actual + 45 días>                 | 1                              | <config.cupos_total>       | permitir       | Entrevista agendada exitosamente |


Escenario: Agendamiento con selección de horario específico
  Dado que la solicitud se encuentra en estado "Aprobada"
  Y la fecha "<fecha_actual + 35 días>" tiene los siguientes horarios disponibles:
    | horario                     | estado      |
    | <config.horario_inicio>     | Disponible  |
    | <config.horario_inicio + 1h>| Disponible  |
    | <config.horario_inicio + 2h>| Agotado     |
    | <config.horario_tarde>      | Disponible  |
  Cuando el solicitante selecciona la fecha "<fecha_actual + 35 días>" y el horario "<config.horario_inicio>"
  Entonces el sistema agenda la entrevista exitosamente
  Y el horario "<config.horario_inicio>" cambia a estado "Agotado"
  Y muestra el mensaje "Entrevista agendada para el <fecha_actual + 35 días (formato_legible)> a las <config.horario_inicio>"


Escenario: Intento de agendar en horario no disponible
  Dado que la solicitud se encuentra en estado "Aprobada"
  Y la fecha "<fecha_actual + 35 días>" tiene el horario "<horario_agotado>" en estado "Agotado"
  Cuando el solicitante intenta agendar la entrevista en "<fecha_actual + 35 días>" a las "<horario_agotado>"
  Entonces el sistema bloquea el agendamiento
  Y muestra el mensaje "Error: el horario seleccionado ya no está disponible"
  Y sugiere los horarios alternativos disponibles para esa fecha


# Escenario: Reprogramación de entrevista agendada
#   Dado que el solicitante tiene una entrevista en estado "Programada" para el "<fecha_entrevista_original>"
#   Y existen fechas disponibles posteriores a "<fecha_entrevista_original>"
#   Cuando solicita el cambio de fecha de la entrevista a "<fecha_entrevista_original + 10 días>"
#   Entonces la entrevista debe cambiar a estado "Reprogramada"
#   Y la nueva fecha queda registrada como "<fecha_entrevista_original + 10 días>"
#   Y se libera el cupo de la fecha "<fecha_entrevista_original>"
#   Y se registra el cambio en el historial de la actividad con la razón del cambio


Esquema del escenario: Restricción de reprogramaciones sucesivas
  Dado que el solicitante tiene una entrevista que ha sido reprogramada "<cantidad_reprogramaciones>" veces
  Y el sistema permite un máximo de "<config.max_reprogramaciones>" reprogramaciones por solicitud
  Cuando solicita el cambio de fecha de la entrevista nuevamente
  Entonces el sistema debe "<accion_sistema>" la reprogramación
  Y mostrar el mensaje "<mensaje>"

Ejemplos:
  | cantidad_reprogramaciones              | accion_sistema | mensaje |
  | <config.max_reprogramaciones - 1>      | permitir       | Esta es su última reprogramación permitida |
  | <config.max_reprogramaciones>          | bloquear       | Error: ha alcanzado el límite máximo de reprogramaciones (<config.max_reprogramaciones>) |


##Horas/fechalimite cancelacion entrevista
Esquema del escenario: Cancelación de entrevista agendada según tiempo disponible
  Dado que el solicitante tiene una entrevista agendada para "<fecha_entrevista> <horario_entrevista>"
  Y la fecha actual es "<fecha_actual> <hora_actual>"
  Y el tiempo restante hasta la entrevista es de "<horas_restantes>" horas
  Cuando el solicitante decide cancelar la entrevista
  Entonces el sistema debe "<accion_sistema>" la cancelación
  Y mostrar el mensaje "<mensaje>"

Ejemplos:
  | horas_restantes                              | accion_sistema | mensaje |
  | ><config.minimo_horas_cancelacion>           | permitir       | Cancelación confirmada exitosamente |
  | <<config.minimo_horas_cancelacion>           | bloquear       | Error: no se puede cancelar con menos de <config.minimo_horas_cancelacion> horas de anticipación |


Escenario: Cancelación exitosa con liberación de recursos
  Dado que el solicitante tiene una entrevista agendada para "<fecha_entrevista> <horario_entrevista>"
  Y el tiempo restante hasta la entrevista es mayor a "<config.minimo_horas_cancelacion>" horas
  Cuando el solicitante decide cancelar la entrevista
  Entonces la entrevista debe cambiar a estado "Cancelada"
  Y se libera el cupo de la fecha "<fecha_entrevista>" horario "<horario_entrevista>"
  Y el solicitante recibe una confirmación de la cancelación
  Y la entrevista ya no aparece en el seguimiento del trámite como pendiente
  Y se registra la cancelación en el historial con fecha "<fecha_actual>" hora "<hora_actual>"


Escenario: Restricción de cancelación con tiempo insuficiente
  Dado que el solicitante tiene una entrevista agendada para "<fecha_actual + 1 día> <config.horario_inicio>"
  Y la fecha y hora actual es "<fecha_actual> <hora_actual>"
  Y faltan menos de "<config.minimo_horas_cancelacion>" horas para la entrevista
  Cuando el solicitante intenta cancelar la entrevista
  Entonces el sistema bloquea la cancelación
  Y muestra el mensaje "Error: no se puede cancelar con menos de <config.minimo_horas_cancelacion> horas de anticipación"
  Y sugiere contactar directamente con "<config.telefono_oficina>" o "<config.email_oficina>"