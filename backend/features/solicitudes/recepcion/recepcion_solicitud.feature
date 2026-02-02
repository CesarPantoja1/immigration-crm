# language: es

Característica: Recepcion de solicitudes
  Como migrante de la agencia de migracion
  quiero registrar mi solicitud de visa
  para garantizar una entrevista con la embajada

#=====================================
#  MIGRANTE
#=====================================
  Antecedentes:
    Dado que existen los siguientes checklists de documentos por tipo de visa
      | tipo_visa | documentos_obligatorios                                         |
      | VIVIENDA  | Pasaporte, Antecedentes penales, Foto, Escritura de propiedad   |
      | TRABAJO   | Pasaporte, Antecedentes penales, Foto, Contrato de trabajo      |
      | ESTUDIO   | Pasaporte, Antecedentes penales, Foto, Certificado de matricula |
    Y que existen las embajadas
      | nombre         |
      | ESTADOUNIDENSE |
      | BRASILENA      |


  Esquema del escenario: Migrante ingresa solicitud completa correctamente
    Dado que un migrante solicita visa <tipo_visa> para embajada <embajada>
    Cuando carga todos los documentos obligatorios
      | documentos            |
      | <documentos_cargados> |
    Entonces todos los documentos tienen estado "EN_REVISION"
    Y el estado de la solicitud es "EN_REVISION"
    Y el sistema registra la solicitud

    Ejemplos:
      | tipo_visa | embajada       | documentos_cargados                                             |
      | VIVIENDA  | ESTADOUNIDENSE | Pasaporte, Antecedentes penales, Foto, Escritura de propiedad   |
      | TRABAJO   | BRASILENA      | Pasaporte, Antecedentes penales, Foto, Contrato de trabajo      |
      | ESTUDIO   | ESTADOUNIDENSE | Pasaporte, Antecedentes penales, Foto, Certificado de matricula |


#=====================================
#  ASESOR
#=====================================
#    Como asesor de la agencia de migracion
#    quiero revisar las solicitudes de visa
#    para validar que los documentos esten correctos antes de enviarlas a la embajada
#=====================================

#=====================================
#  ASESOR APRUEBA
#=====================================

  Esquema del escenario: Asesor aprueba solicitud de visa con todos los documentos correctos
    Dado que existe una solicitud de visa <tipo_visa> con embajada <embajada> con id <id_solicitud>
    Y todos los documentos estan en estado "EN_REVISION"
    Cuando el asesor revisa todos los documentos de la solicitud
    Y todos los documentos son "Correcto"
    Entonces todos los documentos deben cambiar a estado "APROBADO"
    Y el estado de la solicitud debe ser "APROBADO"
    Y los documentos quedan almacenados en el sistema
    Y el migrante recibe la notificacion "VISA_<tipo_visa>_APROBADA"

    Ejemplos:
      | tipo_visa | id_solicitud | embajada       |
      | VIVIENDA  | VVE01        | ESTADOUNIDENSE |
      | TRABAJO   | VTB01        | BRASILENA      |
      | ESTUDIO   | VEB01        | BRASILENA      |

#=====================================
#  ASESOR DESAPRUEBA
#=====================================
  Esquema del escenario: Asesor rechaza solicitud por documento incorrecto
    Dado que existe una solicitud de visa <tipo_visa> con embajada <embajada> con id "<id_solicitud>"
    Y todos los documentos estan en estado "EN_REVISION"
    Cuando el asesor revisa todos los documentos de la solicitud
    Y el documento "<documento_rechazado>" es "Incorrecto"
    Entonces el documento "<documento_rechazado>" debe cambiar a estado "DESAPROBADO"
    Y el estado de la solicitud debe ser "DESAPROBADO"
    Y el migrante recibe la notificacion "DOCUMENTO_RECHAZADO: <documento_rechazado>"

    Ejemplos:
      | tipo_visa | id_solicitud | embajada       | documento_rechazado      |
      | VIVIENDA  | VVE01        | ESTADOUNIDENSE | Pasaporte                |
      | TRABAJO   | VTE01        | BRASILENA      | Contrato de trabajo      |
      | ESTUDIO   | VEE01        | BRASILENA      | Certificado de matricula |

#=====================================
#  RE-EVALUACION DE DOCUMENTOS (IDEMPOTENCIA)
#=====================================
  Esquema del escenario: Asesor puede re-evaluar documentos mientras solicitud esta en revision
    Dado que existe una solicitud de visa <tipo_visa> con estado "EN_REVISION"
    Y el documento "<documento>" tiene estado "<estado_actual>"
    Cuando el asesor cambia la evaluacion del documento "<documento>" a "<nuevo_estado>"
    Entonces el documento "<documento>" debe cambiar a estado "<nuevo_estado>"
    Y la solicitud permanece en estado "EN_REVISION"
    Y se registra la nueva fecha de revision del documento

    Ejemplos:
      | tipo_visa | documento   | estado_actual | nuevo_estado |
      | TRABAJO   | Pasaporte   | RECHAZADO     | APROBADO     |
      | ESTUDIO   | Foto        | APROBADO      | RECHAZADO    |
      | VIVIENDA  | Pasaporte   | PENDIENTE     | APROBADO     |

  Escenario: No se puede re-evaluar documentos si la solicitud ya fue enviada a embajada
    Dado que existe una solicitud con estado "ENVIADA_EMBAJADA"
    Y el documento "Pasaporte" tiene estado "APROBADO"
    Cuando el asesor intenta cambiar la evaluacion del documento "Pasaporte"
    Entonces el sistema rechaza la modificacion
    Y muestra el mensaje "No se pueden modificar documentos de una solicitud enviada a la embajada"

#=====================================
#  ASESOR ENVIA A EMBAJADA
#    Como asesor de la agencia de migracion
#    quiero registrar el envio de la solicitud a la embajada
#    para informar al migrante que su tramite fue enviado correctamente
#=====================================

  Esquema del escenario: Envio exitoso de solicitud aprobada
    Dado que existe una solicitud aprobada de tipo <tipo_visa> con embajada <embajada> con id <id_solicitud>
    Y el estado de envio es "PENDIENTE"
    Cuando el asesor confirma el envio de la solicitud
    Entonces el estado de envio debe cambiar a "ENVIADA_EMBAJADA"
    Y el estado de la solicitud debe cambiar a "ESPERANDO_DECISION_EMBAJADA"
    Y el migrante recibe la notificacion "SOLICITUD ENVIADA A EMBAJADA"

    Ejemplos:
      | tipo_visa | id_solicitud | embajada       |
      | VIVIENDA  | VVE01        | ESTADOUNIDENSE |
      | TRABAJO   | VTB01        | BRASILENA      |
      | ESTUDIO   | VEB01        | BRASILENA      |

#=====================================
#  DECISION DE LA EMBAJADA (NUEVO FLUJO CRITICO)
#=====================================
  Esquema del escenario: Embajada aprueba solicitud para agendar entrevista
    Dado que existe una solicitud con estado "ESPERANDO_DECISION_EMBAJADA"
    Y la solicitud es de tipo <tipo_visa> para embajada <embajada>
    Cuando la embajada comunica decision "APROBADA" para la solicitud
    Entonces el estado de la solicitud debe cambiar a "APROBADA_EMBAJADA"
    Y el migrante recibe la notificacion "Tu solicitud fue aprobada por la embajada"
    Y se habilita la opcion de agendar entrevista consular

    Ejemplos:
      | tipo_visa | embajada       |
      | VIVIENDA  | ESTADOUNIDENSE |
      | TRABAJO   | BRASILENA      |
      | ESTUDIO   | ESTADOUNIDENSE |

  Esquema del escenario: Embajada rechaza solicitud
    Dado que existe una solicitud con estado "ESPERANDO_DECISION_EMBAJADA"
    Y la solicitud es de tipo <tipo_visa> para embajada <embajada>
    Cuando la embajada comunica decision "RECHAZADA" para la solicitud
    Entonces el estado de la solicitud debe cambiar a "RECHAZADA_EMBAJADA"
    Y el migrante recibe la notificacion "Tu solicitud fue rechazada por la embajada"
    Y se incluye el motivo del rechazo en la notificacion
    Y NO se puede agendar entrevista consular

    Ejemplos:
      | tipo_visa | embajada       |
      | TRABAJO   | ESTADOUNIDENSE |
      | ESTUDIO   | BRASILENA      |

  Escenario: No se puede agendar entrevista sin aprobacion de embajada
    Dado que existe una solicitud con estado "ENVIADA_EMBAJADA"
    Cuando se intenta agendar una entrevista para la solicitud
    Entonces el sistema rechaza el agendamiento
    Y muestra el mensaje "La embajada aun no ha aprobado la solicitud"

  Escenario: Solo se puede agendar entrevista con solicitud aprobada por embajada
    Dado que existe una solicitud con estado "APROBADA_EMBAJADA"
    Cuando se intenta agendar una entrevista para la solicitud
    Entonces el sistema permite el agendamiento
    Y el estado cambia a "ENTREVISTA_AGENDADA"

#=====================================
#  ASIGNACION DE SOLICITUD A ASESOR
#=====================================

  Escenario: Asignacion automatica de solicitud a asesor con disponibilidad
    Dado que existen los siguientes asesores con solicitudes asignadas hoy
      | asesor       | solicitudes_hoy |
      | Juan Perez   | 8               |
      | Maria Garcia | 3               |
      | Carlos Lopez | 5               |
    Y cada asesor tiene un limite de 10 solicitudes diarias
    Cuando se registra una nueva solicitud
    Entonces el sistema asigna la solicitud al asesor con menos carga
    Y el asesor "Maria Garcia" tiene 4 solicitudes asignadas hoy
    Y la solicitud queda en estado "pendiente"

  Escenario: Error cuando no hay asesores disponibles
    Dado que todos los asesores han alcanzado su limite de solicitudes diarias
    Cuando se registra una nueva solicitud
    Entonces la solicitud queda sin asesor asignado
    Y el sistema notifica a los administradores
    Y la solicitud queda en estado "pendiente_asignacion"
