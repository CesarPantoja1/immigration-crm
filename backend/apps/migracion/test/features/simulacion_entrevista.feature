#language: es
Característica: Simulación de entrevista
  Como migrante en proceso de preparación
  quiero realizar simulacros de entrevistas adaptados a mi caso específico - visado
  para familiarizarme con el formato de preguntas antes de la cita con la embajada

  Antecedentes:
    Dado que el migrante "Oscar" tiene una cita real en la embajada programada para el "2026-02-20"
    Y se ofrecen los tipos de visado: "Vivienda", "Estudiante", "Trabajo"

  Esquema del escenario: Acuerdo de fecha para simulacro con Asesor
    Dado que el cliente ha realizado <intentos_previos> simulacros con asesor
    Cuando el asesor intenta agendar un nuevo simulacro para la fecha "<fecha_simulacro>" en modalidad "<modalidad>"
    Entonces el sistema debe <accion_sistema> el agendamiento
    Y mostrar el mensaje "<mensaje>"

    Ejemplos:
      | intentos_previos | fecha_simulacro | modalidad  | accion_sistema | mensaje                                             |
      | 0                | 2026-02-10      | Virtual    | Permitir       | Simulacro agendado exitosamente                     |
      | 1                | 2026-02-15      | Presencial | Permitir       | Segundo y último simulacro agendado                 |
      | 2                | 2026-02-18      | Virtual    | Bloquear       | Error: Límite de 2 simulacros alcanzado             |
      | 0                | 2026-02-25      | Virtual    | Bloquear       | Error: La simulación debe ser antes de la cita real |


  Escenario: Ejecución de simulacro guiado
    Dado que es el día y hora del simulacro agendado
    Y el asesor inicia la sesión de "Simulación de Entrevista"
    Cuando el asesor realiza las preguntas y el migrante responde
    Y al finalizar presionan "Terminar Simulación"
    Entonces se debe guardar el archivo de transcripción asociado a este intento
    Y cambiar el estado del proceso a "Pendiente de Feedback"

  Esquema del escenario: Práctica de auto-preparación por tipo de visa
    Dado que el migrante "Oscar" accede a la sección de "Práctica Individual"
    Cuando selecciona que quiere practicar para el visado "<tipo_visado>"
    Entonces el sistema debe cargar un cuestionario con preguntas específicas de "<tema_pregunta>"
    Y permitirle seleccionar una de las 4 respuestas posibles

    Ejemplos:
      | tipo_visado | tema_pregunta                   |
      | Estudiante  | Financiación y Universidad      |
      | Turismo     | Lazos familiares y motivo viaje |
