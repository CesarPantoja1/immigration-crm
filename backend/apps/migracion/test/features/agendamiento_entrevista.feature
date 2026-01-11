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

Esquema del escenario: Agendamiento con selección de horario específico
  Dado que existe una fecha de entrevista "<fecha_entrevista>" con los siguientes horarios disponibles:
    | horario | estado     |
    | 08:00   | Disponible |
    | 09:00   | Disponible |
    | 10:00   | Disponible |
    | 11:00   | Disponible |
  Cuando el solicitante selecciona la fecha "<fecha_entrevista>" y el horario "09:00"
  Entonces el sistema registra la entrevista asociada a la solicitud
  Y el horario "09:00" queda registrado como no disponible
  Y muestra el mensaje "Entrevista agendada para el <fecha_legible> a las 09:00"

Ejemplos:
  | fecha_entrevista | fecha_legible           |
  | 2026-02-15       | 15 de febrero de 2026   |
  # Fechas futuras de la embajada
  # | 2026-03-20       | 20 de marzo de 2026     |
  # | 2026-04-10       | 10 de abril de 2026     |


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
  Y la entrevista ha sido reprogramada <cantidad_reprogramaciones> veces
  Y la embajada permite un máximo de 2 reprogramaciones por solicitud
  Cuando el solicitante solicita una nueva reprogramación de la entrevista
  Entonces el sistema <accion> la reprogramación
  Y muestra el mensaje "<mensaje>"

Ejemplos:
  | cantidad_reprogramaciones | accion  | mensaje                                                             |
  | 1                         | permite  | Esta es su última reprogramación permitida                          |
  | 2                         | rechaza | Error: ha alcanzado el límite máximo de reprogramaciones permitidas |
# ===============================
# CANCELACIÓN
# ===============================

Esquema del escenario: Cancelación de entrevista según reglas de tiempo por embajada
  Dado que el solicitante tiene una entrevista agendada en la embajada "<embajada>"
  Y la embajada "<embajada>" define un mínimo de <minimo_horas_cancelacion> horas de anticipación para cancelaciones
  Y el tiempo restante hasta la entrevista es de <horas_restantes> horas
  Cuando el solicitante solicita la cancelación de la entrevista
  Entonces el sistema <accion> la cancelación
  Y la entrevista queda en estado "<estado_final>"
  Y muestra el mensaje "<mensaje>"

Ejemplos:
  | embajada | minimo_horas_cancelacion | horas_restantes | accion  | estado_final | mensaje                                                                                                |
  | USA      | 24                       | 48              | permite  | Cancelada    | Cancelación confirmada exitosamente                                                                    |
  | USA      | 24                       | 12              | rechaza | Programada   | Error: no es posible cancelar la entrevista debido a que no se cumple el tiempo mínimo de anticipación |
  | España   | 48                       | 72              | permite  | Cancelada    | Cancelación confirmada exitosamente                                                                    |
  | España   | 48                       | 36              | rechaza | Programada   | Error: no es posible cancelar la entrevista debido a que no se cumple el tiempo mínimo de anticipación |
  | Canadá   | 72                       | 96              | permite  | Cancelada    | Cancelación confirmada exitosamente                                                                    |
  | Canadá   | 72                       | 48              | rechaza | Programada   | Error: no es posible cancelar la entrevista debido a que no se cumple el tiempo mínimo de anticipación |