#language: es
Característica: Generación de recomendaciones personalizadas basadas en análisis de IA
  Como migrante que ha completado un simulacro de entrevista consular
  Quiero recibir un documento con recomendaciones específicas generadas por IA a partir de la transcripción de mi entrevista
  Para identificar mis fortalezas, corregir debilidades concretas y aumentar mis probabilidades de éxito en la entrevista real

  Antecedentes:
    Dado que el módulo de simulacros de entrevista consular está operativo
    Y el sistema almacena transcripciones en formato .txt de cada simulacro completado
    Y el agente de IA para análisis de entrevistas está habilitado
    Y la generación de documentos de recomendaciones está disponible

  # =============================================================================
  # ESCENARIO 1: GENERACIÓN DEL DOCUMENTO DE RECOMENDACIONES
  # =============================================================================
  Esquema del escenario: El migrante recibe documento de retroalimentación tras análisis de IA
    Dado que el migrante completó el simulacro "<id_simulacro>" con transcripción disponible
    Y la IA analizó la transcripción del simulacro "<id_simulacro>" con los siguientes resultados:
      | indicador                     | valor          |
      | Claridad en respuestas        | <claridad>     |
      | Coherencia del discurso       | <coherencia>   |
      | Seguridad al responder        | <seguridad>    |
      | Pertinencia de la información | <pertinencia>  |
    Cuando se genera el documento de recomendaciones para el simulacro "<id_simulacro>"
    Entonces el documento tiene estado "Feedback generado"
    Y el nivel de preparación calculado es "<nivel_preparacion>"
    Y el documento contiene las siguientes secciones:
      | seccion              |
      | Fortalezas           |
      | Puntos de mejora     |
      | Recomendaciones      |
      | Nivel de preparación |

    Ejemplos:
      | id_simulacro | claridad | coherencia | seguridad | pertinencia | nivel_preparacion |
      | SIM-001      | Alta     | Alta       | Media     | Alta        | Alto              |
      | SIM-002      | Media    | Media      | Media     | Baja        | Medio             |
      | SIM-003      | Baja     | Media      | Baja      | Media       | Bajo              |

  # =============================================================================
  # ESCENARIO 2: RECOMENDACIONES ACCIONABLES POR CATEGORÍA
  # =============================================================================
  Esquema del escenario: Las recomendaciones son accionables y clasificadas por área de mejora
    Dado que el migrante completó el simulacro "<id_simulacro>" con transcripción procesada
    Y la IA identificó los siguientes puntos de mejora en el simulacro "<id_simulacro>":
      | categoria   | descripcion                                                  |
      | Claridad    | Las respuestas incluyen frases incompletas                   |
      | Seguridad   | Se detecta inseguridad en respuestas a preguntas críticas    |
      | Pertinencia | Algunas respuestas no abordan directamente lo solicitado     |
    Cuando se genera el documento de recomendaciones del simulacro "<id_simulacro>"
    Entonces el documento debe contener recomendaciones accionables clasificadas por categoría:
      | categoria   |
      | Claridad    |
      | Seguridad   |
      | Pertinencia |
    Y cada categoría debe contener al menos una recomendación concreta y medible
    Y el documento debe registrar la fecha de generación del feedback

    Ejemplos:
      | id_simulacro |
      | SIM-004      |
      | SIM-005      |

  # =============================================================================
  # ESCENARIO 3: CÁLCULO DEL NIVEL DE PREPARACIÓN
  # =============================================================================
  Esquema del escenario: El nivel de preparación refleja el desempeño global del migrante
    Dado el análisis del simulacro "<id_simulacro>" tiene los siguientes resultados:
      | indicador                     | valor          |
      | Claridad en respuestas        | <claridad>     |
      | Coherencia del discurso       | <coherencia>   |
      | Seguridad al responder        | <seguridad>    |
      | Pertinencia de la información | <pertinencia>  |
    Cuando el sistema calcula el nivel global de preparación
    Entonces el nivel de preparación asignado debe ser "<nivel_preparacion>"

    Ejemplos:
      | id_simulacro | claridad | coherencia | seguridad | pertinencia | nivel_preparacion |
      | SIM-006      | Alta     | Alta       | Alta      | Alta        | Alto              |
      | SIM-007      | Media    | Media      | Media     | Media       | Medio             |
      | SIM-008      | Baja     | Media      | Baja      | Media       | Bajo              |

  # =============================================================================
  # ESCENARIO 4: TRAZABILIDAD DE RECOMENDACIONES
  # =============================================================================
  Esquema del escenario: Cada recomendación está vinculada a una pregunta específica del simulacro
    Dado que el simulacro "<id_simulacro>" tiene las siguientes preguntas y respuestas:
      | numero_pregunta | tipo_pregunta           |
      | 1               | Motivo del viaje        |
      | 2               | Situación económica     |
      | 3               | Planes de permanencia   |
    Y el agente de IA ha generado recomendaciones asociadas al simulacro "<id_simulacro>"
    Cuando el asesor revisa el documento de recomendaciones del simulacro "<id_simulacro>"
    Entonces cada recomendación debe estar asociada a una pregunta del simulacro
    Y el documento debe permitir identificar para cada recomendación:
      | atributo                 |
      | Número de pregunta       |
      | Tipo de pregunta         |

    Ejemplos:
      | id_simulacro |
      | SIM-009      |
      | SIM-010      |

  # =============================================================================
  # ESCENARIO 5: PRIORIZACIÓN POR IMPACTO
  # =============================================================================
  Esquema del escenario: Las recomendaciones están priorizadas según su impacto en la entrevista
    Dado que existe un documento de recomendaciones generado para el simulacro "<id_simulacro>"
    Y el documento de recomendaciones del simulacro "<id_simulacro>" contiene recomendaciones con impacto clasificado
    Cuando el sistema organiza las recomendaciones por impacto
    Entonces las recomendaciones deben quedar agrupadas por nivel de impacto:
      | impacto |
      | Alto    |
      | Medio   |
      | Bajo    |
    Y cada recomendación debe registrar su nivel de impacto

    Ejemplos:
      | id_simulacro |
      | SIM-011      |
      | SIM-012      |

  # =============================================================================
  # ESCENARIO 6: SUGERENCIA DE PRÓXIMOS PASOS
  # =============================================================================
  Esquema del escenario: El migrante recibe sugerencia de próximo paso según su nivel
    Dado que el documento de recomendaciones del simulacro "<id_simulacro>" tiene nivel de preparación "<nivel>"
    Cuando el migrante consulta su documento de recomendaciones
    Entonces el sistema debe sugerir la siguiente acción posterior: "<accion_sugerida>"

    Ejemplos:
      | id_simulacro | nivel | accion_sugerida                             |
      | SIM-013      | Bajo  | Realizar un nuevo simulacro con asesor      |
      | SIM-014      | Medio | Reforzar los puntos de mejora identificados |
      | SIM-015      | Alto  | Mantener el plan actual de preparación      |

  # =============================================================================
  # ESCENARIO 7: CONSULTA Y DESCARGA DEL DOCUMENTO
  # =============================================================================
  Esquema del escenario: El migrante puede consultar y descargar su documento de recomendaciones
    Dado que existe un documento de recomendaciones publicado para el simulacro "<id_simulacro>"
    Cuando el migrante accede a la sección "Mis recomendaciones"
    Entonces el sistema debe mostrar el documento de recomendaciones asociado al simulacro "<id_simulacro>" con las secciones:
      | seccion              |
      | Fortalezas           |
      | Puntos de mejora     |
      | Recomendaciones      |
      | Nivel de preparación |
    Y debe permitir descargar el documento en formato "<formato>"

    Ejemplos:
      | id_simulacro | formato |
      | SIM-016      | PDF     |
      | SIM-017      | PDF     |

  # =============================================================================
  # ESCENARIO 8: MANEJO DE ERRORES - TRANSCRIPCIÓN NO DISPONIBLE
  # =============================================================================
  Escenario: El sistema notifica cuando la transcripción no está disponible para análisis
    Dado que el migrante completó el simulacro "SIM-ERR-001" sin transcripción generada
    Cuando se intenta generar el documento de recomendaciones para el simulacro "SIM-ERR-001"
    Entonces el sistema debe mostrar el mensaje de error "No es posible generar recomendaciones: la transcripción del simulacro SIM-ERR-001 no está disponible"
    Y el documento no debe ser generado

  # =============================================================================
  # ESCENARIO 9: MANEJO DE ERRORES - ANÁLISIS DE IA INCOMPLETO
  # =============================================================================
  Escenario: El sistema notifica cuando el análisis de IA no se completó
    Dado que el migrante completó el simulacro "SIM-ERR-002" con transcripción disponible
    Y el análisis de IA del simulacro "SIM-ERR-002" está incompleto
    Cuando se intenta generar el documento de recomendaciones para el simulacro "SIM-ERR-002"
    Entonces el sistema debe mostrar el mensaje de error "No es posible generar recomendaciones: el análisis de IA del simulacro SIM-ERR-002 no se ha completado"
    Y el documento no debe ser generado
