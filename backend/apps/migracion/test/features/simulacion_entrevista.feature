#language: es
Característica: Simulación de entrevista para migrantes
  Como migrante en proceso de preparación
  quiero realizar simulacros de entrevistas adaptados a mi visado
  para familiarizarme con el formato de preguntas antes de la cita con la embajada

  Antecedentes:
    Dado que soy el migrante "Oscar Pérez" con ID "MIG-12345"
    Y tengo una cita en la embajada programada para "2026-02-20 10:00"
    Y mi tipo de visa es "Estudiante"
    Y mi contador de simulacros realizados es 0

  # ============================================
  # COORDINACIÓN DE SIMULACROS
  # ============================================

  Escenario: Visualización propuesta de simulacro pendiente de mi asesor
    Dado que mi asesor "Carlos Ruiz" envió una propuesta de simulacro con ID "SIM-001"
    Y la propuesta tiene fecha "2026-02-10 15:00" y modalidad "Virtual"
    Y la propuesta fue enviada hace 10 minutos
    Cuando accedo a la sección "Notificaciones"
    Entonces debo ver exactamente 1 notificación sin leer
    Y la notificación debe contener:
      | Campo         | Valor                    |
      | Tipo          | Propuesta de simulacro   |
      | ID            | SIM-001                  |
      | Fecha         | 2026-02-10               |
      | Hora          | 15:00                    |
      | Modalidad     | Virtual                  |
      | Asesor        | Carlos Ruiz              |
      | Estado        | Pendiente de respuesta   |
    Y debo ver el botón "Aceptar" habilitado
    Y debo ver el botón "Proponer otra fecha" habilitado

  Escenario: Acepto propuesta de simulacro de mi asesor
    Dado que tengo una propuesta de simulacro con ID "SIM-001" para "2026-02-10 15:00"
    Y el estado de la propuesta es "Pendiente de respuesta"
    Cuando presiono el botón "Aceptar" en la propuesta "SIM-001"
    Entonces debo ver el mensaje de éxito "Simulacro confirmado exitosamente"
    Y el estado del simulacro "SIM-001" debe cambiar a "Confirmado"
    Y mi contador de simulacros debe incrementarse a 1
    Y debo ver el simulacro en "Próximos simulacros" con:
      | Campo         | Valor        |
      | Fecha         | 2026-02-10   |
      | Hora          | 15:00        |
      | Modalidad     | Virtual      |
      | Estado        | Confirmado   |
    Y el sistema debe haber enviado email de confirmación a mi correo registrado
    Y el asesor "Carlos Ruiz" debe haber recibido notificación de aceptación

  Escenario: Propongo fecha alternativa a propuesta del asesor
    Dado que tengo una propuesta de simulacro con ID "SIM-001" para "2026-02-10 15:00"
    Y estoy visualizando los detalles de la propuesta
    Cuando selecciono "Proponer otra fecha"
    Y ingreso la fecha "2026-02-12" y hora "16:00"
    Y presiono "Enviar contrapropuesta"
    Entonces debo ver el mensaje "Contrapropuesta enviada a tu asesor"
    Y el estado del simulacro "SIM-001" debe cambiar a "Contrapropuesta pendiente"
    Y mi contrapropuesta debe mostrar fecha "2026-02-12 16:00"
    Y el asesor debe haber recibido notificación de contrapropuesta
    Y mi contador de simulacros debe permanecer en 0

  Esquema del escenario: Intento solicitar simulacro adicional según límite permitido
    Dado que mi contador de simulacros realizados es <simulacros_realizados>
    Cuando accedo a la sección "Solicitar simulacro"
    Entonces el botón "Solicitar nuevo simulacro" debe estar <estado_boton>
    Y debo ver el mensaje "<mensaje_informativo>"

    Ejemplos:
      | simulacros_realizados | estado_boton | mensaje_informativo                                    |
      | 0                     | habilitado   | Puede solicitar hasta 2 simulacros en total            |
      | 1                     | habilitado   | Tiene 1 simulacro disponible restante                  |
      | 2                     | deshabilitado| Ha alcanzado el límite de 2 simulacros por proceso     |

  # ============================================
  # PARTICIPACIÓN EN SIMULACRO VIRTUAL
  # ============================================

  Escenario: Me conecto a simulacro virtual 10 minutos antes
    Dado que tengo un simulacro confirmado con ID "SIM-001"
    Y el simulacro es hoy a las "15:00" en modalidad "Virtual"
    Y la hora actual del sistema es "14:50"
    Cuando ingreso al enlace del simulacro desde mi panel
    Entonces debo ver la sala de espera con título "Preparando tu simulacro"
    Y debo ver un temporizador que indica "Inicia en 10 minutos"
    Y debo poder ver la vista previa de mi cámara
    Y debo poder probar mi micrófono con indicador de nivel de audio
    Y debo ver el botón "Probar audio/video" habilitado
    Y debo ver el mensaje "Espera a que tu asesor inicie la sesión"

  Escenario: El asesor inicia el simulacro y entro automáticamente
    Dado que estoy en la sala de espera del simulacro "SIM-001"
    Y el simulacro está programado para "15:00"
    Y la hora actual es "15:00"
    Cuando el asesor "Carlos Ruiz" inicia la sesión
    Entonces debo entrar automáticamente a la sala de entrevista
    Y debo ver el video del asesor en pantalla
    Y debo ver mi video en miniatura en esquina superior derecha
    Y debo ver el indicador "Grabación en progreso" activo
    Y debo ver el temporizador de sesión iniciado en "00:00"
    Y debo ver el botón "Finalizar" habilitado solo para el asesor

  Escenario: Finalizo participación en simulacro cuando asesor termina sesión
    Dado que estoy en una sesión activa de simulacro "SIM-001"
    Y han transcurrido 28 minutos de sesión
    Cuando el asesor presiona "Finalizar simulacro"
    Entonces debo ver el mensaje "Simulacro finalizado - Duración: 28 minutos"
    Y debo ser redirigido a la página de resumen
    Y la página debe mostrar:
      | Campo              | Valor                          |
      | Duración           | 28 minutos                     |
      | Fecha              | 2026-02-10                     |
      | Asesor             | Carlos Ruiz                    |
      | Estado             | Pendiente de feedback          |
    Y debo ver el mensaje "Recibirás el feedback en las próximas 24 horas"
    Y el estado del simulacro "SIM-001" debe cambiar a "Completado"
    Y mi contador de simulacros debe incrementarse a 1

  # ============================================
  # RECEPCIÓN DE FEEDBACK
  # ============================================

  Escenario: Recibo notificación cuando feedback está disponible
    Dado que completé el simulacro "SIM-001" hace 3 horas
    Y el estado del simulacro es "Completado"
    Cuando el asesor publica el feedback del simulacro
    Entonces debo recibir una notificación push con título "Feedback disponible"
    Y debo recibir un email con asunto "Tu feedback del simulacro está listo"
    Y el estado del simulacro debe cambiar a "Feedback disponible"

  Escenario: Accedo y descargo feedback del simulacro
    Dado que el simulacro "SIM-001" tiene estado "Feedback disponible"
    Cuando accedo a "Mis simulacros"
    Y selecciono el simulacro "SIM-001"
    Entonces debo ver el estado "Feedback disponible" destacado en verde
    Y debo ver el botón "Ver feedback" habilitado
    Cuando presiono "Ver feedback"
    Entonces debo ver el documento de feedback en pantalla con:
      | Sección                     | Contenido visible                          |
      | Fortalezas                  | Lista de al menos 2 puntos positivos       |
      | Áreas de mejora             | Lista de al menos 2 puntos a mejorar       |
      | Recomendaciones             | Sugerencias específicas del asesor         |
      | Observaciones del asesor    | Comentarios personalizados                 |
    Y debo ver el botón "Descargar PDF" habilitado
    Y debo ver el enlace "Escuchar grabación" si está disponible

  # ============================================
  # PRÁCTICA INDIVIDUAL
  # ============================================

  Escenario: Accedo por primera vez a práctica individual
    Dado que nunca he accedido a "Práctica Individual"
    Cuando selecciono el menú "Práctica Individual"
    Entonces debo ver una pantalla de bienvenida con título "Prepárate a tu ritmo"
    Y debo ver los tipos de visa disponibles:
      | Tipo de visa | Estado     |
      | Estudiante   | Sugerido   |
      | Trabajo      | Disponible |
      | Turismo      | Disponible |
      | Vivienda     | Disponible |
    Y el tipo "Estudiante" debe estar destacado
    Y debo ver el botón "Iniciar práctica - Estudiante" habilitado

  Esquema del escenario: Completo cuestionario de práctica y veo resultados
    Dado que inicié un cuestionario de práctica para visa "<tipo_visa>"
    Y el cuestionario tiene 10 preguntas
    Cuando respondo <correctas> preguntas correctamente de 10 totales
    Y presiono "Finalizar cuestionario"
    Entonces debo ver la pantalla de resultados con:
      | Campo                | Valor                |
      | Respuestas correctas | <correctas> de 10    |
      | Porcentaje           | <porcentaje>%        |
      | Calificación         | <calificacion>       |
    Y debo ver el mensaje "<mensaje_resultado>"
    Y el sistema debe guardar mi progreso con fecha y hora actual

    Ejemplos:
      | tipo_visa  | correctas | porcentaje | calificacion | mensaje_resultado                                |
      | Estudiante | 9         | 90         | Excelente    | ¡Muy bien! Estás muy preparado                   |
      | Estudiante | 7         | 70         | Bueno        | Buen trabajo, repasa las preguntas incorrectas   |
      | Estudiante | 5         | 50         | Regular      | Necesitas practicar más antes del simulacro real |
      | Trabajo    | 3         | 30         | Insuficiente | Te recomendamos estudiar más este tema           |

  Escenario: Reviso preguntas incorrectas después de práctica
    Dado que completé un cuestionario con 3 respuestas incorrectas
    Y estoy en la pantalla de resultados
    Cuando presiono "Ver preguntas incorrectas"
    Entonces debo ver exactamente 3 preguntas
    Y cada pregunta debe mostrar:
      | Elemento                | Estado                           |
      | Texto de la pregunta    | Visible                          |
      | Mi respuesta            | Marcada en rojo con ícono "X"    |
      | Respuesta correcta      | Marcada en verde con ícono "✓"   |
      | Explicación             | Texto explicativo visible        |
    Y debo ver el botón "Practicar nuevamente estas preguntas"

  Escenario: Consulto mi historial de prácticas
    Dado que he realizado 4 prácticas individuales en los últimos 7 días:
      | Fecha      | Tipo visa  | Correctas | Total |
      | 2026-02-03 | Estudiante | 6         | 10    |
      | 2026-02-05 | Estudiante | 8         | 10    |
      | 2026-02-07 | Trabajo    | 7         | 10    |
      | 2026-02-09 | Estudiante | 9         | 10    |
    Cuando accedo a "Mi Progreso"
    Entonces debo ver un gráfico de línea con mi evolución
    Y debo ver las siguientes estadísticas:
      | Métrica              | Valor calculado |
      | Total de prácticas   | 4               |
      | Mejor puntuación     | 90%             |
      | Promedio general     | 75%             |
      | Tipo más practicado  | Estudiante (3)  |
    Y debo ver la tabla completa de mi historial de prácticas


  # ============================================
  # CANCELACIONES
  # ============================================

  Esquema del escenario: Cancelo simulacro según tiempo restante
    Dado que tengo un simulacro confirmado con ID "SIM-001" para "2026-02-10 15:00"
    Y hoy es "<fecha_actual>" a las "10:00"
    Cuando intento cancelar el simulacro "SIM-001"
    Entonces el sistema debe <permitir_accion>
    Y debo ver el mensaje "<mensaje>"
    Y mi contador de simulacros debe ser <contador_final>

    Ejemplos:
      | fecha_actual | permitir_accion                | mensaje                                                  | contador_final |
      | 2026-02-07   | permitir cancelación sin penalización | Simulacro cancelado exitosamente                         | 0              |
      | 2026-02-09   | permitir cancelación con penalización | Simulacro cancelado - Este intento cuenta en tu límite   | 1              |
      | 2026-02-10   | bloquear cancelación           | No puedes cancelar con menos de 24 horas de anticipación | 0              |