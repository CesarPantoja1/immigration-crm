# language: es
Característica: Simulacion de entrevista para migrantes
  Como migrante en proceso de preparacion
  quiero realizar simulacros de entrevistas adaptados a mi visado
  para familiarizarme con el formato de preguntas antes de la cita con la embajada

  Antecedentes:
    Dado que el sistema tiene configurados los siguientes limites
      | parametro                     | valor |
      | maximo_simulacros_por_cliente | 2     |
      | minutos_anticipacion_entrada  | 15    |
      | horas_cancelacion_anticipada  | 24    |

#=====================================
#  ROLES Y PERMISOS EN SIMULACROS
#=====================================

  Escenario: Asesor crea propuesta de simulacro para cliente
    Dado que soy el asesor "Carlos Ruiz" con ID "ASE-001"
    Y tengo asignado al cliente "Oscar Perez" con ID "MIG-12345"
    Cuando creo una propuesta de simulacro con los siguientes datos
      | fecha      | hora  | modalidad |
      | 2026-02-10 | 15:00 | Virtual   |
    Entonces se crea el simulacro con estado "Pendiente de respuesta"
    Y el cliente "Oscar Perez" recibe la notificacion "Nueva propuesta de simulacro"

  Escenario: Cliente acepta propuesta de simulacro del asesor
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y mi contador de simulacros realizados es 0
    Y tengo una propuesta de simulacro con los siguientes datos
      | id      | fecha      | hora  | modalidad | estado                 | propuesto_por |
      | SIM-001 | 2026-02-10 | 15:00 | Virtual   | Pendiente de respuesta | asesor        |
    Cuando acepto la propuesta de simulacro "SIM-001"
    Entonces el estado del simulacro debe cambiar a "Confirmado"
    Y mi contador de simulacros debe ser 1

  Escenario: Cliente NO puede aceptar propuesta que el mismo creo
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y tengo una propuesta de simulacro con los siguientes datos
      | id      | fecha      | hora  | modalidad | estado    | propuesto_por |
      | SIM-002 | 2026-02-12 | 10:00 | Virtual   | Solicitado| cliente       |
    Cuando intento aceptar la propuesta de simulacro "SIM-002"
    Entonces el sistema rechaza la accion
    Y muestra el mensaje "No puedes aceptar una propuesta que tu mismo creaste"
    Y el estado del simulacro permanece "Solicitado"

  Escenario: Asesor acepta solicitud de simulacro del cliente
    Dado que soy el asesor "Carlos Ruiz" con ID "ASE-001"
    Y existe una solicitud de simulacro del cliente "Oscar Perez" con los siguientes datos
      | id      | fecha      | hora  | modalidad | estado    | propuesto_por |
      | SIM-002 | 2026-02-12 | 10:00 | Virtual   | Solicitado| cliente       |
    Cuando acepto la propuesta de simulacro "SIM-002"
    Entonces el estado del simulacro debe cambiar a "Confirmado"
    Y el cliente recibe la notificacion "Tu solicitud de simulacro fue confirmada"

#=====================================
#  PROPUESTAS Y CONTRAPROPUESTAS
#=====================================

  Escenario: Proponer fecha alternativa para simulacro
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y mi contador de simulacros realizados es 0
    Y tengo una propuesta de simulacro con ID "SIM-001" para "2026-02-10 15:00"
    Cuando propongo la fecha alternativa "2026-02-12 16:00" para el simulacro "SIM-001"
    Entonces el estado del simulacro debe cambiar a "Contrapropuesta pendiente"
    Y la fecha propuesta debe ser "2026-02-12 16:00"
    Y mi contador de simulacros debe permanecer en 0

  Escenario: Asesor puede ver modalidad de solicitud del cliente
    Dado que soy el asesor "Carlos Ruiz" con ID "ASE-001"
    Y existe una solicitud de simulacro del cliente "Oscar Perez" con los siguientes datos
      | id      | fecha      | hora  | modalidad  | estado     | propuesto_por |
      | SIM-003 | 2026-02-15 | 11:00 | Presencial | Solicitado | cliente       |
    Cuando consulto las propuestas pendientes
    Entonces debo ver el simulacro "SIM-003" con modalidad "Presencial"

  Escenario: Asesor propone fecha alternativa a solicitud del cliente
    Dado que soy el asesor "Carlos Ruiz" con ID "ASE-001"
    Y existe una solicitud de simulacro del cliente "Oscar Perez" con los siguientes datos
      | id      | fecha      | hora  | modalidad | estado     | propuesto_por |
      | SIM-004 | 2026-02-15 | 11:00 | Virtual   | Solicitado | cliente       |
    Cuando propongo la fecha alternativa "2026-02-17 14:00" para el simulacro "SIM-004"
    Entonces el estado del simulacro debe cambiar a "Contrapropuesta pendiente"
    Y la fecha propuesta debe ser "2026-02-17 14:00"
    Y el cliente debe recibir la notificacion "El asesor ha propuesto una nueva fecha"

#=====================================
#  VALIDACION: FECHA ANTES DE CITA EMBAJADA
#=====================================

  Escenario: Cliente NO puede proponer fecha posterior a cita con embajada
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y mi cita con la embajada esta programada para "2026-02-20"
    Y tengo una propuesta de simulacro con ID "SIM-001" para "2026-02-10 15:00"
    Cuando propongo la fecha alternativa "2026-02-25 16:00" para el simulacro "SIM-001"
    Entonces el sistema rechaza la fecha propuesta
    Y muestra el mensaje "La fecha del simulacro debe ser anterior a su cita con la embajada"

  Escenario: Asesor NO puede proponer fecha posterior a cita con embajada del cliente
    Dado que soy el asesor "Carlos Ruiz" con ID "ASE-001"
    Y el cliente "Oscar Perez" tiene cita con embajada para "2026-02-20"
    Y existe una solicitud de simulacro del cliente "Oscar Perez" con los siguientes datos
      | id      | fecha      | hora  | modalidad | estado     | propuesto_por |
      | SIM-005 | 2026-02-15 | 11:00 | Virtual   | Solicitado | cliente       |
    Cuando propongo la fecha alternativa "2026-02-22 14:00" para el simulacro "SIM-005"
    Entonces el sistema rechaza la fecha propuesta
    Y muestra el mensaje "La fecha del simulacro debe ser anterior a la cita del cliente con la embajada"

#=====================================
#  FLUJO COMPLETO DE CONTRAPROPUESTAS
#=====================================

  Escenario: Flujo completo - Cliente acepta contrapropuesta del asesor
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y solicite un simulacro para "2026-02-10 10:00"
    Y el asesor propuso la fecha alternativa "2026-02-12 14:00"
    Y el simulacro tiene estado "Contrapropuesta pendiente" con turno del "cliente"
    Cuando acepto la propuesta de simulacro
    Entonces el estado del simulacro debe cambiar a "Confirmado"
    Y se debe agendar el simulacro para "2026-02-12 14:00"

  Escenario: Flujo completo - Cliente envia contrapropuesta final
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y solicite un simulacro para "2026-02-10 10:00"
    Y el asesor propuso la fecha alternativa "2026-02-12 14:00"
    Y el simulacro tiene estado "Contrapropuesta pendiente" con turno del "cliente"
    Cuando propongo mi ultima fecha alternativa "2026-02-13 09:00"
    Entonces el estado del simulacro debe cambiar a "Contrapropuesta final"
    Y el asesor debe responder aceptando o definiendo fecha final

  Escenario: Flujo completo - Asesor acepta contrapropuesta final del cliente
    Dado que soy el asesor "Carlos Ruiz" con ID "ASE-001"
    Y el cliente "Oscar Perez" envio su contrapropuesta final "2026-02-13 09:00"
    Y el simulacro tiene estado "Contrapropuesta final" con turno del "asesor"
    Cuando acepto la propuesta del cliente
    Entonces el estado del simulacro debe cambiar a "Confirmado"
    Y se debe agendar el simulacro para "2026-02-13 09:00"

  Escenario: Flujo completo - Asesor define fecha final diferente
    Dado que soy el asesor "Carlos Ruiz" con ID "ASE-001"
    Y el cliente "Oscar Perez" envio su contrapropuesta final "2026-02-13 09:00"
    Y el simulacro tiene estado "Contrapropuesta final" con turno del "asesor"
    Cuando defino la fecha final "2026-02-14 10:00"
    Entonces el estado del simulacro debe cambiar a "Confirmado"
    Y se debe agendar el simulacro para "2026-02-14 10:00"
    Y el cliente recibe notificacion de la fecha final agendada

#=====================================
#  DISPONIBILIDAD DE SIMULACROS (POR SOLICITUD)
#=====================================

  Esquema del escenario: Consultar disponibilidad segun simulacros realizados para una solicitud
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y tengo una solicitud de visa "Estudiante" con ID "SOL-001"
    Y mi contador de simulacros para la solicitud "SOL-001" es <simulacros_realizados>
    Cuando consulto la disponibilidad para nuevo simulacro de la solicitud "SOL-001"
    Entonces la disponibilidad debe ser "<disponibilidad>"
    Y el mensaje informativo debe ser "<mensaje>"

    Ejemplos:
      | simulacros_realizados | disponibilidad | mensaje                                              |
      | 0                     | disponible     | Puede solicitar hasta 2 simulacros para esta visa    |
      | 1                     | disponible     | Tiene 1 simulacro disponible para esta solicitud     |
      | 2                     | no_disponible  | Ha alcanzado el limite de 2 simulacros para esta visa|

  Escenario: Contador de simulacros es independiente por solicitud
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y tengo una solicitud de visa "Estudiante" con ID "SOL-001" con 2 simulacros usados
    Y tengo una solicitud de visa "Trabajo" con ID "SOL-002" con 0 simulacros usados
    Cuando consulto la disponibilidad para nuevo simulacro de la solicitud "SOL-002"
    Entonces la disponibilidad debe ser "disponible"
    Y el mensaje informativo debe ser "Puede solicitar hasta 2 simulacros para esta visa"

#=====================================
#  REQUISITO: SOLICITUD APROBADA POR EMBAJADA
#=====================================

  Escenario: Cliente puede solicitar simulacro con solicitud aprobada por embajada
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y tengo una solicitud de visa con estado "aprobada_embajada"
    Y mi contador de simulacros realizados es 0
    Cuando solicito un simulacro de entrevista para esa solicitud
    Entonces el simulacro debe crearse correctamente con estado "Solicitado"
    Y el asesor debe recibir la notificacion "Nueva solicitud de simulacro"

  Escenario: Cliente puede solicitar simulacro cuando la entrevista esta agendada
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y tengo una solicitud de visa con estado "entrevista_agendada"
    Y mi contador de simulacros realizados es 0
    Cuando solicito un simulacro de entrevista para esa solicitud
    Entonces el simulacro debe crearse correctamente con estado "Solicitado"
    Y el asesor debe recibir la notificacion "Nueva solicitud de simulacro"

  Esquema del escenario: Cliente NO puede solicitar simulacro si solicitud no esta aprobada por embajada
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y tengo una solicitud de visa con estado "<estado_solicitud>"
    Y mi contador de simulacros realizados es 0
    Cuando intento solicitar un simulacro de entrevista para esa solicitud
    Entonces el sistema rechaza la solicitud de simulacro
    Y muestra el mensaje "Solo puede solicitar un simulacro cuando su solicitud haya sido aprobada por la embajada o cuando la entrevista este agendada"

    Ejemplos:
      | estado_solicitud        |
      | borrador                |
      | pendiente               |
      | en_revision             |
      | aprobada                |
      | enviada_embajada        |
      | esperando_decision_embajada |
      | rechazada_embajada      |

#=====================================
#  SALA DE ESPERA Y SESION
#=====================================

  Escenario: Ingresar a sala de espera dentro del tiempo permitido
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y tengo un simulacro confirmado con ID "SIM-001" para hoy "2026-02-10 15:00"
    Y la modalidad del simulacro es "Virtual"
    Y la hora actual del sistema es "14:50"
    Cuando ingreso al simulacro "SIM-001"
    Entonces el estado del simulacro debe ser "En sala de espera"
    Y el tiempo restante para inicio debe ser 10 minutos

  Escenario: Iniciar sesion cuando asesor activa el simulacro
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y estoy en sala de espera del simulacro "SIM-001"
    Y el simulacro esta programado para "15:00"
    Y la hora actual es "15:00"
    Cuando el asesor "Carlos Ruiz" inicia la sesion del simulacro "SIM-001"
    Entonces el estado del simulacro debe cambiar a "En progreso"
    Y la grabacion debe estar activa
    Y el temporizador debe iniciar en 0

  Escenario: Finalizar simulacro por el asesor
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y mi contador de simulacros realizados es 0
    Y estoy en sesion activa del simulacro "SIM-001"
    Y el temporizador marca 28 minutos
    Y la grabacion esta activa
    Cuando el asesor "Carlos Ruiz" finaliza el simulacro "SIM-001"
    Entonces el estado del simulacro debe cambiar a "Completado"
    Y la duracion registrada debe ser 28 minutos
    Y mi contador de simulacros debe ser 1
    Y la grabacion debe estar detenida

#=====================================
#  PRACTICA INDIVIDUAL
#=====================================

  Escenario: Acceder por primera vez a practica individual
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y mi tipo de visa asignado es "Estudiante"
    Y nunca he accedido a "Practica Individual"
    Cuando accedo a la seccion de practica individual
    Entonces debo ver 4 tipos de visa disponibles
    Y el tipo "Estudiante" debe estar marcado como "Sugerido"

  Esquema del escenario: Completar cuestionario de practica
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y inicie un cuestionario de practica para visa "<tipo_visa>"
    Y el cuestionario tiene 10 preguntas
    Cuando completo el cuestionario con <correctas> respuestas correctas
    Entonces mi puntuacion debe ser <porcentaje>
    Y la calificacion debe ser "<calificacion>"
    Y el mensaje debe ser "<mensaje>"

    Ejemplos:
      | tipo_visa  | correctas | porcentaje | calificacion | mensaje                                          |
      | Estudiante | 9         | 90         | Excelente    | Muy bien! Estas muy preparado                    |
      | Estudiante | 7         | 70         | Bueno        | Buen trabajo, repasa las preguntas incorrectas   |

  Escenario: Revisar preguntas incorrectas del cuestionario
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y complete un cuestionario con 3 respuestas incorrectas
    Cuando solicito ver las respuestas incorrectas
    Entonces debo ver exactamente 3 preguntas
    Y cada pregunta debe mostrar mi respuesta como incorrecta
    Y cada pregunta debe mostrar la respuesta correcta
    Y cada pregunta debe incluir una explicacion

#=====================================
#  CANCELACIONES
#=====================================

  Escenario: Cancelar simulacro con menos de 24 horas de anticipacion
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y mi contador de simulacros realizados es 0
    Y tengo un simulacro confirmado con ID "SIM-001" para "2026-02-10 15:00"
    Y hoy es "2026-02-10" a las "10:00"
    Cuando cancelo el simulacro "SIM-001"
    Entonces la cancelacion debe ser rechazada
    Y el mensaje de error debe ser "No puedes cancelar con menos de 24 horas de anticipacion"
    Y mi contador de simulacros debe permanecer en 0
    Y el estado del simulacro debe permanecer "Confirmado"

  Escenario: Cancelar simulacro con mas de 24 horas de anticipacion
    Dado que soy el migrante "Oscar Perez" con ID "MIG-12345"
    Y mi contador de simulacros realizados es 0
    Y tengo un simulacro confirmado con ID "SIM-001" para "2026-02-12 15:00"
    Y hoy es "2026-02-10" a las "10:00"
    Cuando cancelo el simulacro "SIM-001"
    Entonces la cancelacion debe ser aceptada
    Y el estado del simulacro debe cambiar a "Cancelado"
    Y mi contador de simulacros debe permanecer en 0