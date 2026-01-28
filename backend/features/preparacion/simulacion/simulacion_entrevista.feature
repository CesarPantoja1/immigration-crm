#language: es
Característica: Simulación de entrevista para migrantes
  Como migrante en proceso de preparación
  quiero realizar simulacros de entrevistas adaptados a mi visado
  para familiarizarme con el formato de preguntas antes de la cita con la embajada

  Antecedentes:
    Dado que el sistema tiene configurados los siguientes límites
      | parámetro                    | valor |
      | máximo_simulacros_por_cliente| 2     |
      | minutos_anticipación_entrada | 15    |
      | horas_cancelación_anticipada | 24    |

  Escenario: Aceptar propuesta de simulacro del asesor
    Dado que soy el migrante "Oscar Pérez" con ID "MIG-12345"
    Y mi contador de simulacros realizados es 0
    Y tengo una propuesta de simulacro con los siguientes datos:
      | id      | fecha      | hora  | modalidad | estado                 |
      | SIM-001 | 2026-02-10 | 15:00 | Virtual   | Pendiente de respuesta |
    Cuando acepto la propuesta de simulacro "SIM-001"
    Entonces el estado del simulacro debe cambiar a "Confirmado"
    Y mi contador de simulacros debe ser 1

  Escenario: Proponer fecha alternativa para simulacro
    Dado que soy el migrante "Oscar Pérez" con ID "MIG-12345"
    Y mi contador de simulacros realizados es 0
    Y tengo una propuesta de simulacro con ID "SIM-001" para "2026-02-10 15:00"
    Cuando propongo la fecha alternativa "2026-02-12 16:00" para el simulacro "SIM-001"
    Entonces el estado del simulacro debe cambiar a "Contrapropuesta pendiente"
    Y la fecha propuesta debe ser "2026-02-12 16:00"
    Y mi contador de simulacros debe permanecer en 0

  Esquema del escenario: Consultar disponibilidad según simulacros realizados
    Dado que soy el migrante "Oscar Pérez" con ID "MIG-12345"
    Y mi contador de simulacros realizados es <simulacros_realizados>
    Cuando consulto la disponibilidad para nuevo simulacro
    Entonces la disponibilidad debe ser "<disponibilidad>"
    Y el mensaje informativo debe ser "<mensaje>"

    Ejemplos:
      | simulacros_realizados | disponibilidad | mensaje                                            |
      | 0                     | disponible     | Puede solicitar hasta 2 simulacros en total        |
      | 1                     | disponible     | Tiene 1 simulacro disponible restante              |
      | 2                     | no_disponible  | Ha alcanzado el límite de 2 simulacros por proceso |

  Escenario: Ingresar a sala de espera dentro del tiempo permitido
    Dado que soy el migrante "Oscar Pérez" con ID "MIG-12345"
    Y tengo un simulacro confirmado con ID "SIM-001" para hoy "2026-02-10 15:00"
    Y la modalidad del simulacro es "Virtual"
    Y la hora actual del sistema es "14:50"
    Cuando ingreso al simulacro "SIM-001"
    Entonces el estado del simulacro debe ser "En sala de espera"
    Y el tiempo restante para inicio debe ser 10 minutos

  Escenario: Iniciar sesión cuando asesor activa el simulacro
    Dado que soy el migrante "Oscar Pérez" con ID "MIG-12345"
    Y estoy en sala de espera del simulacro "SIM-001"
    Y el simulacro está programado para "15:00"
    Y la hora actual es "15:00"
    Cuando el asesor "Carlos Ruiz" inicia la sesión del simulacro "SIM-001"
    Entonces el estado del simulacro debe cambiar a "En progreso"
    Y la grabación debe estar activa
    Y el temporizador debe iniciar en 0

  Escenario: Finalizar simulacro por el asesor
    Dado que soy el migrante "Oscar Pérez" con ID "MIG-12345"
    Y mi contador de simulacros realizados es 0
    Y estoy en sesión activa del simulacro "SIM-001"
    Y el temporizador marca 28 minutos
    Y la grabación está activa
    Cuando el asesor "Carlos Ruiz" finaliza el simulacro "SIM-001"
    Entonces el estado del simulacro debe cambiar a "Completado"
    Y la duración registrada debe ser 28 minutos
    Y mi contador de simulacros debe ser 1
    Y la grabación debe estar detenida

  Escenario: Acceder por primera vez a práctica individual
    Dado que soy el migrante "Oscar Pérez" con ID "MIG-12345"
    Y mi tipo de visa asignado es "Estudiante"
    Y nunca he accedido a "Práctica Individual"
    Cuando accedo a la sección de práctica individual
    Entonces debo ver 4 tipos de visa disponibles
    Y el tipo "Estudiante" debe estar marcado como "Sugerido"

  Esquema del escenario: Completar cuestionario de práctica
    Dado que soy el migrante "Oscar Pérez" con ID "MIG-12345"
    Y inicié un cuestionario de práctica para visa "<tipo_visa>"
    Y el cuestionario tiene 10 preguntas
    Cuando completo el cuestionario con <correctas> respuestas correctas
    Entonces mi puntuación debe ser <porcentaje>
    Y la calificación debe ser "<calificacion>"
    Y el mensaje debe ser "<mensaje>"

    Ejemplos:
      | tipo_visa  | correctas | porcentaje | calificacion | mensaje                                          |
      | Estudiante | 9         | 90         | Excelente    | ¡Muy bien! Estás muy preparado                   |
      | Estudiante | 7         | 70         | Bueno        | Buen trabajo, repasa las preguntas incorrectas   |
      | Estudiante | 5         | 50         | Regular      | Necesitas practicar más antes del simulacro real |
      | Trabajo    | 3         | 30         | Insuficiente | Te recomendamos estudiar más este tema           |

  Escenario: Revisar preguntas incorrectas del cuestionario
    Dado que soy el migrante "Oscar Pérez" con ID "MIG-12345"
    Y completé un cuestionario con 3 respuestas incorrectas
    Cuando solicito ver las respuestas incorrectas
    Entonces debo ver exactamente 3 preguntas
    Y cada pregunta debe mostrar mi respuesta como incorrecta
    Y cada pregunta debe mostrar la respuesta correcta
    Y cada pregunta debe incluir una explicación

  Escenario: Cancelar simulacro con menos de 24 horas de anticipación
    Dado que soy el migrante "Oscar Pérez" con ID "MIG-12345"
    Y mi contador de simulacros realizados es 0
    Y tengo un simulacro confirmado con ID "SIM-001" para "2026-02-10 15:00"
    Y hoy es "2026-02-10" a las "10:00"
    Cuando cancelo el simulacro "SIM-001"
    Entonces la cancelación debe ser rechazada
    Y el mensaje de error debe ser "No puedes cancelar con menos de 24 horas de anticipación"
    Y mi contador de simulacros debe permanecer en 0
    Y el estado del simulacro debe permanecer "Confirmado"