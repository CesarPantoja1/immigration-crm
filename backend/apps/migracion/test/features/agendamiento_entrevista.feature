#language: es

Característica: Agendamiento de entrevista
  Como solicitante de un trámite migratorio con solicitud previamente aprobada,
  quiero agendar una entrevista asociada a mi solicitud,
  para cumplir una etapa obligatoria del proceso y continuar con mi trámite.

Antecedentes:
  Dado que el solicitante cuenta con una solicitud migratoria aprobada
  Y el sistema presenta opciones de fecha y horario para entrevistas


# ===============================
# AGENDAMIENTO DE ENTREVISTA
# ===============================

Escenario: Agendamiento con selección de horario específico
  Dado que existe una fecha de entrevista "<fecha_entrevista>" con los siguientes horarios disponibles:
    | horario           | estado       |
    | 08:00             | Disponible   |
    | 09:00             | Disponible   |
    | 10:00             | Disponible   |
    | 11:00             | Disponible   |
  Cuando el solicitante selecciona la fecha "<fecha_entrevista>" y el horario "09:00"
  Entonces el sistema registra la entrevista asociada a la solicitud
  Y el horario "09:00" queda registrado como no disponible
  Y muestra el mensaje "Entrevista agendada para el <fecha_entrevista (formato_legible)> a las 09:00"



  ## CADA ESCENARIO DEBE REFLEJAR UN CAMBIO EN EL SISTEMA....

# ===============================
# PROTECCIÓN E INTEGRIDAD
# ===============================

Escenario: Rechazo de modificación directa de entrevista programada
  Dado que el solicitante tiene una entrevista en estado "Programada"
  Cuando el solicitante solicita la modificación de la fecha o el horario de la entrevista fuera del proceso de reprogramación
  Entonces el sistema rechaza la solicitud de modificación
  Y mantiene la entrevista en su estado original


# ===============================
# REPROGRAMACIÓN
# ===============================

Escenario: Reprogramación exitosa de entrevista
  Dado que el solicitante tiene una entrevista en estado "Programada"
  Cuando el solicitante solicita la reprogramación de la entrevista a una nueva fecha
  Entonces el sistema actualiza la fecha de la entrevista
  Y la entrevista queda en estado "Reprogramada"
  Y el solicitante recibe una confirmación de la reprogramación


Esquema del escenario: Restricción de reprogramaciones sucesivas
  Dado que el solicitante tiene una entrevista en estado "Programada"
  Y la entrevista ha sido reprogramada "<cantidad_reprogramaciones>" veces
  Y la embajada permite un máximo de 2 reprogramaciones por solicitud
  Cuando el solicitante solicita una nueva reprogramación de la entrevista
  Entonces el sistema "<resultado_reprogramacion>" la reprogramación
  Y muestra el mensaje "<mensaje>"

Ejemplos:
  | cantidad_reprogramaciones | resultado_reprogramacion | mensaje |
  | 1                          | permite                  | Esta es su última reprogramación permitida |
  | 2                          | rechaza                  | Error: ha alcanzado el límite máximo de reprogramaciones permitidas |

# ===============================
# CANCELACIÓN
# ===============================

Esquema del escenario: Cancelación de entrevista según reglas de tiempo
  Dado que el solicitante tiene una entrevista agendada
  Y la embajada define las siguientes reglas de cancelación:
    | minimo_horas_cancelacion |
    | 24                       |
  Y el tiempo restante hasta la entrevista es de "<horas_restantes>" horas
  Cuando el solicitante solicita la cancelación de la entrevista
  Entonces el sistema "<resultado_cancelacion>" la entrevista
  Y muestra el mensaje "<mensaje>"

Ejemplos:
  | horas_restantes | resultado_cancelacion | mensaje |
  | 48              | cancela               | Cancelación confirmada exitosamente |
  | 12              | rechaza               | Error: no se puede cancelar con menos de <minimo_horas_cancelacion> horas de anticipación |
