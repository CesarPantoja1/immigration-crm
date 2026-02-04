# language: es
Característica: Generacion de recomendaciones personalizadas basadas en analisis de IA
  Como migrante que completo un simulacro de entrevista consular
  Quiero recibir recomendaciones personalizadas generadas por IA
  Para identificar mis fortalezas, corregir debilidades y prepararme mejor para mi entrevista real

  Antecedentes:
    Dado que el asesor tiene simulacros completados
      | asesor       | cliente       | estado     | codigo   |
      | Asesor Demo  | Maria Garcia  | completado | SIM-001  |
      | Asesor Demo  | Juan Perez    | completado | SIM-002  |
      | Asesor Demo | Pedro Ruiz    | completado | SIM-003  |

  # =============================================================================
  # FLUJO DEL ASESOR: SUBIR TRANSCRIPCION
  # =============================================================================

  Escenario: Subir un archivo en formato .txt
    Dado que el asesor "Asesor Demo" tiene un simulacro completado con "Maria Garcia"
    Cuando sube el archivo "transcripcion_maria.txt" con la conversacion del simulacro
    Entonces el sistema confirma "Transcripcion subida exitosamente"
    Y muestra la cantidad de caracteres y lineas del archivo

  Escenario: Subir un archivo que no es .txt
    Dado que el asesor "Asesor Demo" tiene un simulacro completado con "Maria Garcia"
    Cuando intenta subir el archivo "transcripcion_maria.pdf"
    Entonces el sistema muestra "El archivo debe ser de texto (.txt)"
    Y el simulacro no cuenta con transcripcion subida

  # =============================================================================
  # FLUJO DEL ASESOR: GENERAR RECOMENDACIONES CON IA
  # =============================================================================

  Escenario: Asesor genera recomendaciones con IA exitosamente
    Dado que el asesor "Asesor Demo" tiene un simulacro con transcripcion subida exitosamente
    Y tiene configurada su API key de Gemini
    Cuando hace clic en "Generar con IA"
    Entonces el sistema analiza la transcripcion con Gemini
    Y genera el documento de recomendaciones
    Y el cliente "Maria Garcia" recibe la notificacion "Recomendaciones disponibles"
    Y el simulacro tiene la opcion de ver feedback disponible

  Escenario: Asesor intenta generar recomendaciones sin API key configurada
    Dado que el asesor "Asesor Demo" no ha configurado su API key de Gemini
    Y tiene un simulacro con transcripcion disponible
    Cuando hace clic en "Generar con IA"
    Entonces el sistema muestra "No se ha configurado una API key de IA valida. Por favor, configura tu API key de Gemini."

  # =============================================================================
  # FLUJO DEL CLIENTE: CONSULTAR RECOMENDACIONES
  # =============================================================================

  Escenario: Cliente consulta sus recomendaciones
    Dado que el cliente "Maria Garcia" completo un simulacro
    Y el asesor ya genero las recomendaciones con IA
    Cuando el cliente accede a "Ver Resumen" en la seccion de simulacros completados y "Ver Recomendaciones"
    Entonces puede ver la lista de recomendaciones disponibles
      | campo                | descripcion                                    |
      | Fecha del simulacro  | Fecha en que se realizo el simulacro           |
      | Nivel de preparacion | Segun nivel (alto/medio/bajo)  |
    Y puede expandir las secciones colapsables
      | seccion                  |
      | Indicadores de Desempeno |
      | Fortalezas Identificadas |
      | Puntos de Mejora         |
      | Recomendaciones          |

  Escenario: Cliente sin recomendaciones intenta descargar PDF
    Dado que el cliente "Juan Perez" tiene un simulacro completado
    Pero el simulacro no tiene recomendaciones generadas
    Cuando intenta descargar el PDF de recomendaciones
    Entonces el sistema muestra "Este simulacro no tiene recomendaciones"


  # =============================================================================
  # ANALISIS DE IA: INDICADORES DE DESEMPENO
  # =============================================================================

  Escenario: La IA evalua los 4 indicadores de desempeno
    Dado que el asesor "Asesor Demo" genero recomendaciones con IA para "Maria Garcia"
    Cuando el cliente consulta sus recomendaciones
    Entonces la recomendacion incluye los indicadores
      | indicador   | descripcion                              | valores_posibles   |
      | Claridad    | Que tan claras son las respuestas        | alto, medio, bajo  |
      | Coherencia  | Si el discurso es logico y estructurado  | alto, medio, bajo  |
      | Seguridad   | Nivel de confianza al responder          | alto, medio, bajo  |
      | Pertinencia | Si las respuestas abordan lo preguntado  | alto, medio, bajo  |

  # =============================================================================
  # ANALISIS DE IA: CONTENIDO GENERADO
  # =============================================================================

  Escenario: La IA genera fortalezas identificadas
    Dado que el asesor "Asesor Demo" genero recomendaciones con IA para "Maria Garcia"
    Entonces cada fortaleza identificada contiene
      | campo                | descripcion                                      |
      | Categoria            | Area de la fortaleza                             |
      | Descripcion          | Explicacion de por que es una fortaleza          |
      | Pregunta relacionada | Referencia a la pregunta del simulacro           |
      | Impacto              | Nivel de impacto positivo (alto, medio, bajo)    |

  Escenario: La IA genera puntos de mejora
    Dado que el asesor "Asesor Demo" genero recomendaciones con IA para "Maria Garcia"
    Entonces cada punto de mejora contiene
      | campo                | descripcion                                       |
      | Categoria            | Area a mejorar                                    |
      | Descripcion          | Explicacion del aspecto a mejorar                 |
      | Pregunta relacionada | Referencia a la pregunta donde se detecto         |
      | Impacto              | Nivel de impacto en la entrevista                 |

  Escenario: La IA genera recomendaciones accionables
    Dado que el asesor "Asesor Demo" genero recomendaciones con IA para "Maria Garcia"
    Entonces cada recomendacion contiene
      | campo           | descripcion                                    |
      | Titulo          | Nombre corto de la recomendacion               |
      | Descripcion     | Explicacion detallada                          |
      | Accion concreta | Paso especifico que el cliente debe realizar   |
      | Impacto         | Nivel de impacto si se implementa              |
