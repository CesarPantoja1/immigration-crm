#language: es
Característica: Generación de recomendaciones
  Como migrante en preparación para una entrevista consular
  Quiero recibir recomendaciones específicas basadas en mis respuestas del simulacro
  Para mejorar mi desempeño antes de la entrevista real

  Antecedentes:
    Dado que existen simulacros de entrevista consular registrados en el sistema
    Y cada simulacro puede contar con una transcripción de preguntas y respuestas almacenada en el sistema
    Y existe un agente de IA habilitado en el sistema para analizar transcripciones de simulacros
    Y el sistema permite generar documentos de recomendaciones asociados a un simulacro

  Esquema del escenario: Generación del documento de recomendaciones basado en la evaluación del desempeño
    Dado que existe un simulacro identificado como "<id_simulacro>" registrado en el sistema
    Y el simulacro "<id_simulacro>" tiene una transcripción de preguntas y respuestas registrada en el sistema
    Y el agente de IA ha analizado la transcripción del simulacro "<id_simulacro>"
    Y se han identificado los siguientes indicadores de desempeño:
      | indicador                     | valor          |
      | Claridad en respuestas        | <claridad>     |
      | Coherencia del discurso       | <coherencia>   |
      | Seguridad al responder        | <seguridad>    |
      | Pertinencia de la información | <pertinencia>  |
    Cuando el asesor solicita generar el documento de recomendaciones para el simulacro "<id_simulacro>"
    Entonces el sistema debe crear un documento de recomendaciones asociado al simulacro "<id_simulacro>" con los siguientes metadatos:
      | campo                | valor                |
      | Nivel de preparación | <nivel_preparacion> |
      | Estado del simulacro | Feedback generado    |
    Y el documento debe incluir las siguientes secciones:
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

  Esquema del escenario: Generación de recomendaciones accionables por categoría de mejora
    Dado que existe un simulacro identificado como "<id_simulacro>" registrado en el sistema
    Y el agente de IA ha identificado los siguientes puntos de mejora en el simulacro "<id_simulacro>":
      | categoria   | descripcion                                                  |
      | Claridad    | Las respuestas incluyen pausas largas y frases incompletas  |
      | Seguridad   | El tono de voz refleja inseguridad en preguntas críticas    |
      | Pertinencia | Algunas respuestas no responden directamente lo solicitado  |
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

  Esquema del escenario: Asignación del nivel de preparación en función del desempeño
    Dado que existe un simulacro identificado como "<id_simulacro>" registrado en el sistema
    Y el análisis del simulacro "<id_simulacro>" tiene los siguientes resultados:
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

  Esquema del escenario: Trazabilidad de recomendaciones a preguntas del simulacro
    Dado que existe un simulacro identificado como "<id_simulacro>" registrado en el sistema
    Y el simulacro "<id_simulacro>" tiene las siguientes preguntas y respuestas:
      | numero_pregunta | tipo_pregunta           |
      | 1               | Motivo del viaje        |
      | 2               | Situación económica     |
      | 3               | Planes de permanencia   |
    Y el agente de IA ha generado recomendaciones asociadas al simulacro "<id_simulacro>"
    Cuando el asesor revisa el documento de recomendaciones del simulacro "<id_simulacro>"
    Entonces cada recomendación debe estar asociada a una pregunta del simulacro
    Y el documento debe permitir identificar para cada recomendación:
      | atributo               |
      | numero_pregunta_origen |
      | tipo_pregunta_origen   |

    Ejemplos:
      | id_simulacro |
      | SIM-009      |
      | SIM-010      |

  Esquema del escenario: Clasificación de recomendaciones según impacto
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

  Esquema del escenario: Recomendación de acciones posteriores según nivel de preparación
    Dado que existe un documento de recomendaciones generado para el simulacro "<id_simulacro>"
    Y el documento de recomendaciones del simulacro "<id_simulacro>" tiene nivel de preparación "<nivel>"
    Cuando el migrante consulta su documento de recomendaciones
    Entonces el sistema debe sugerir la siguiente acción posterior: "<accion_sugerida>"

    Ejemplos:
      | id_simulacro | nivel | accion_sugerida                             |
      | SIM-013      | Bajo  | Realizar un nuevo simulacro con asesor      |
      | SIM-014      | Medio | Reforzar los puntos de mejora identificados |
      | SIM-015      | Alto  | Mantener el plan actual de preparación      |

  Esquema del escenario: Consulta del documento de recomendaciones por parte del migrante
    Dado que existe un documento de recomendaciones publicado para el simulacro "<id_simulacro>"
    Cuando el migrante accede a la sección "Recomendaciones de entrevista"
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
