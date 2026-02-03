# language: es
Característica: Alertas de entrevistas
  Como migrante
  Quiero recibir alertas oportunas sobre mi entrevista consular y mi preparación
  Para reducir el riesgo de inasistencia y cumplir el proceso sin retrasos

  Antecedentes:
    Dado que soy un solicitante autenticado en el sistema de gestión migratoria
    Y gestiono la solicitud "SOL-2026-00001" en estado "APROBADA"
    Y tengo asignado al asesor "Carlos Ruiz"
    Y el catálogo de tipos de notificación incluye
      | tipo                    | propósito                                                        |
      | Entrevista agendada     | Confirmar que ya existe una cita consular registrada             |
      | Entrevista reprogramada | Informar un cambio de fecha u hora de una cita ya registrada     |
      | Entrevista cancelada    | Informar que la cita registrada quedó sin efecto                 |
      | Recordatorio entrevista | Reducir inasistencia con recordatorios por ventana               |
      | Preparación recomendada | Alertar preparación faltante antes de la entrevista              |
      | Simulación completada   | Aviso operativo al asesor para dar continuidad (recomendaciones) |
      | Recomendaciones listas  | Avisar al migrante que su feedback ya está disponible            |
    Y el sistema tiene configuradas ventanas de recordatorio de entrevista
      | ventana |
      | 24h     |
      | 2h      |
    Y el sistema tiene configurada una ventana de control de preparación
      | ventana |
      | 7d      |

  # =========================================================
  # Entrevista agendada
  # =========================================================

  Escenario: Notificar entrevista agendada al migrante
    Dado que la solicitud "SOL-2026-00001" no tiene entrevista registrada
    Cuando el asesor "Carlos Ruiz" registra una entrevista para "SOL-2026-00001" en "2026-02-15 09:00"
    Entonces en el centro de notificaciones del migrante aparece una notificación nueva con
      | tipo                | id_solicitud   | fecha_hora_entrevista |
      | Entrevista agendada | SOL-2026-00001 | 2026-02-15 09:00      |
    Y la notificación queda asociada a la solicitud "SOL-2026-00001" al abrir su detalle

  # =========================================================
  # Recordatorios
  # =========================================================

  Esquema del escenario: Recordatorio antes de la entrevista
    Dado que la solicitud "SOL-2026-00001" tiene una entrevista "Programada" para "2026-02-15 09:00"
    Y la fecha y hora actual del sistema es "<fecha_hora_actual>"
    Cuando el sistema evalúa recordatorios configurados para la entrevista de "SOL-2026-00001"
    Entonces en el centro de notificaciones del migrante aparece una notificación nueva con:
      | tipo                    | id_solicitud   | fecha_hora_entrevista |
      | Recordatorio entrevista | SOL-2026-00001 | 2026-02-15 09:00      |
    Y el detalle de la notificación es "Faltan <ventana>"

    Ejemplos:
      | ventana | fecha_hora_actual |
      | 24h     | 2026-02-14 09:00  |
      | 2h      | 2026-02-15 07:00  |

  # =========================================================
  # Reprogramación
  # =========================================================

  Escenario: Reprogramación de una entrevista
    Dado que la solicitud "SOL-2026-00001" tiene una entrevista "Programada" para "2026-02-15 09:00"
    Cuando el asesor "Carlos Ruiz" reprograma la entrevista de "SOL-2026-00001" a "2026-02-20 10:00"
    Entonces en el centro de notificaciones del migrante aparece una notificación nueva con:
      | tipo                    | id_solicitud   | fecha_hora_anterior | nueva_fecha_hora |
      | Entrevista reprogramada | SOL-2026-00001 | 2026-02-15 09:00    | 2026-02-20 10:00 |

  Esquema del escenario: No emitir recordatorios basados en la fecha anterior tras reprogramación
    Dado que la solicitud "SOL-2026-00001" tiene una entrevista "Reprogramada" para "2026-02-20 10:00"
    Y previamente estuvo "Programada" para "2026-02-15 09:00"
    Y la fecha y hora actual del sistema es "<fecha_hora_actual>"
    Cuando el sistema evalúa recordatorios configurados para la entrevista de "SOL-2026-00001"
    Entonces no aparece ninguna notificación nueva de tipo "Recordatorio entrevista" asociada a "2026-02-15 09:00"
    Y el contador de notificaciones de tipo "Recordatorio entrevista" para la solicitud "SOL-2026-00001" no aumenta

    Ejemplos:
      | fecha_hora_actual |
      | 2026-02-14 09:00  |
      | 2026-02-15 07:00  |

  # =========================================================
  # Cancelación
  # =========================================================

  Escenario: Cancelación de entrevista
    Dado que la solicitud "SOL-2026-00001" tiene una entrevista "Programada" para "2026-02-15 09:00"
    Cuando el asesor "Carlos Ruiz" cancela la entrevista de "SOL-2026-00001"
    Entonces en el centro de notificaciones del migrante aparece una notificación nueva con:
      | tipo                 | id_solicitud   | fecha_hora_entrevista |
      | Entrevista cancelada | SOL-2026-00001 | 2026-02-15 09:00      |

  Esquema del escenario: No emitir recordatorios si la entrevista está cancelada
    Dado que la solicitud "SOL-2026-00001" tiene una entrevista en estado "Cancelada"
    Y la entrevista cancelada correspondía a "2026-02-15 09:00"
    Y la fecha y hora actual del sistema es "<fecha_hora_actual>"
    Cuando el sistema evalúa recordatorios configurados para la entrevista de "SOL-2026-00001"
    Entonces no aparece ninguna notificación nueva de tipo "Recordatorio entrevista"
    Y el contador de notificaciones no aumenta para la solicitud "SOL-2026-00001"

    Ejemplos:
      | fecha_hora_actual |
      | 2026-02-14 09:00  |
      | 2026-02-15 07:00  |

  # =========================================================
  # Preparación
  # =========================================================

  Escenario: Alerta cuando falta una semana y no existe simulacro confirmado
    Dado que la solicitud "SOL-2026-00001" tiene una entrevista "Programada" para "2026-02-15 09:00"
    Y no existe un simulacro en estado "Confirmado" asociado a "SOL-2026-00001"
    Y la fecha y hora actual del sistema es "2026-02-08 09:00"
    Cuando el sistema evalúa el estado de preparación para la entrevista de "SOL-2026-00001"
    Entonces en el centro de notificaciones del migrante aparece una notificación nueva con:
      | tipo                    | id_solicitud   |
      | Preparación recomendada | SOL-2026-00001 |
    Y el detalle de la notificación es "Realizar simulación de entrevista"

  # =========================================================
  # Continuidad con Simulación/Recomendaciones
  # =========================================================

  Escenario: Aviso al asesor cuando un simulacro ha sido completado
    Dado que el asesor "Carlos Ruiz" está autenticado en el sistema
    Y existe un simulacro "SIM-001" asociado a la solicitud "SOL-2026-00001"
    Y el simulacro "SIM-001" está en estado "En progreso"
    Cuando el simulacro "SIM-001" cambia a estado "Completado"
    Entonces en el centro de notificaciones del asesor aparece una notificación nueva con
      | tipo                  | id_simulacro |
      | Simulación completada | SIM-001      |
    Y el detalle de la notificación es "Generar recomendaciones"

  Escenario: Notificar las recomendaciones publicadas al migrante
    Dado que existe un documento de recomendaciones para el simulacro "SIM-001" en estado "Publicado"
    Cuando el documento de recomendaciones del simulacro "SIM-001" se publica en el sistema
    Entonces en el centro de notificaciones del migrante aparece una notificación nueva con
      | tipo                   | id_simulacro |
      | Recomendaciones listas | SIM-001      |

  # =========================================================
  # NAVEGACIÓN CONTEXTUAL DESDE NOTIFICACIONES (Deep Linking)
  # =========================================================

  Escenario: Acceso directo a detalles de entrevista desde notificación de agendamiento
    Dado que la solicitud "SOL-2026-00001" tiene una entrevista programada para "2026-02-15 09:00"
    Y el migrante recibe la notificación de "Entrevista Agendada"
    Cuando accedo a la notificación de cita consular asignada
    Entonces soy redirigido a la vista de entrevista de "SOL-2026-00001"
    Y visualizo la fecha "15 de febrero de 2026" y hora "09:00" de la cita
    Y se muestra la dirección del consulado y documentos requeridos para el día
    Y la notificación queda marcada como leída

  Escenario: Acceso directo desde notificación de reprogramación
    Dado que la entrevista de "SOL-2026-00001" fue reprogramada de "2026-02-15" a "2026-02-20 10:00"
    Y el migrante recibe la notificación de "Entrevista Reprogramada"
    Cuando accedo a la notificación de cambio de fecha
    Entonces soy redirigido a la vista de entrevista de "SOL-2026-00001"
    Y visualizo la nueva fecha "20 de febrero de 2026" claramente destacada
    Y se muestra un comparativo con la fecha anterior tachada

  Escenario: Acceso a preparación desde recordatorio de 24 horas
    Dado que faltan 24 horas para la entrevista de "SOL-2026-00001"
    Y el migrante recibe el recordatorio de proximidad de cita
    Cuando accedo al recordatorio de entrevista próxima
    Entonces soy redirigido a la vista de entrevista de "SOL-2026-00001"
    Y visualizo el checklist de preparación con los elementos pendientes
    Y se destaca la cuenta regresiva "Faltan 24 horas para su cita"

  Escenario: Acceso directo a simulacro confirmado desde notificación
    Dado que existe un simulacro "SIM-015" confirmado para "SOL-2026-00001"
    Y el migrante recibe la notificación de "Simulacro Confirmado"
    Cuando accedo a la notificación de práctica programada
    Entonces soy redirigido a la vista de detalle del simulacro "SIM-015"
    Y visualizo la fecha, hora y enlace de videoconferencia del simulacro
    Y se muestra el botón para unirse a la sesión cuando esté activa

  Escenario: Acceso a propuesta de simulacro pendiente de confirmación
    Dado que el asesor propuso el simulacro "SIM-016" para "SOL-2026-00001"
    Y el simulacro está en estado "Propuesto" pendiente de aceptación
    Cuando accedo a la notificación de "Nueva Propuesta de Simulacro"
    Entonces soy redirigido a la vista del simulacro "SIM-016"
    Y visualizo las opciones para "Confirmar" o "Solicitar otro horario"
    Y se muestran los horarios alternativos disponibles

  Escenario: Acceso directo a feedback de simulacro desde notificación
    Dado que el simulacro "SIM-001" fue completado y evaluado
    Y las recomendaciones están publicadas para el migrante
    Cuando accedo a la notificación de "Recomendaciones Disponibles"
    Entonces soy redirigido a la vista de recomendaciones del simulacro "SIM-001"
    Y visualizo el análisis de fortalezas y áreas de mejora
    Y se muestran las preguntas frecuentes sugeridas para practicar

  # =========================================================
  # SUPRESIÓN DE NOTIFICACIONES EN FLUJO DE ENTREVISTA
  # =========================================================

  Escenario: No notificar asignación interna de solicitud al asesor
    Dado que la solicitud "SOL-2026-00005" está sin asesor asignado
    Y el buzón del sistema contiene 10 notificaciones totales
    Cuando el coordinador asigna "SOL-2026-00005" al asesor "Carlos Ruiz"
    Entonces la asignación se registra en el expediente
    Y NO se genera notificación al migrante por esta acción administrativa
    Y el asesor visualiza la solicitud en su bandeja de trabajo

  # =========================================================
  # MANEJO DE ENLACES INVÁLIDOS EN NOTIFICACIONES
  # =========================================================

  Escenario: Acceso a notificación de entrevista que ya no existe
    Dado que la entrevista de "SOL-2026-00010" fue cancelada definitivamente
    Y existe una notificación antigua de recordatorio para esa entrevista
    Cuando accedo a la notificación del recordatorio obsoleto
    Entonces visualizo el mensaje de entrevista cancelada "Esta entrevista fue cancelada"
    Y se muestra la opción de contactar al asesor para reagendar
    Y permanezco en el buzón con la notificación marcada como leída