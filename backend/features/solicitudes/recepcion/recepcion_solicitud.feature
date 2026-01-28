  # language: es

  Característica: Recepción de solicitudes
    Como migrante de la agencia de migración
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
        | ESTUDIO   | Pasaporte, Antecedentes penales, Foto, Certificado de matrícula |
      Y que existen las embajadas
        | nombre         |
        | ESTADOUNIDENSE |
        | BRASILEÑA      |


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
        | TRABAJO   | BRASILEÑA      | Pasaporte, Antecedentes penales, Foto, Contrato de trabajo      |
        | ESTUDIO   | ESTADOUNIDENSE | Pasaporte, Antecedentes penales, Foto, Certificado de matrícula |


  #=====================================
  #  ASESOR
  #=====================================
  #    Como asesor de la agencia de migración
  #    quiero revisar las solicitudes de visa
  #    para validar que los documentos estén correctos antes de enviarlas a la embajada
  #=====================================

  #=====================================
  #  ASESOR APRUEBA
  #=====================================

    Esquema del escenario: Asesor aprueba solicitud de visa con todos los documentos correctos
      Dado que existe una solicitud de visa <tipo_visa> con embajada <embajada> con id <id_solicitud>
      Y todos los documentos están en estado "EN_REVISION"
      Cuando el asesor revisa todos los documentos de la solicitud
      Y todos los documentos son "Correcto"
      Entonces todos los documentos deben cambiar a estado "APROBADO"
      Y el estado de la solicitud debe ser "APROBADO"
      Y los documentos quedan almacenados en el sistema
      Y el migrante recibe la notificación "VISA_<tipo_visa>_APROBADA"

      Ejemplos:
        | tipo_visa | id_solicitud | embajada       |
        | VIVIENDA  | VVE01        | ESTADOUNIDENSE |
        | TRABAJO   | VTB01        | BRASILEÑA      |
        | ESTUDIO   | VEB01        | BRASILEÑA      |

  #=====================================
  #  ASESOR DESAPRUEBA
  #=====================================
    Esquema del escenario: Asesor rechaza solicitud por documento incorrecto
      Dado que existe una solicitud de visa <tipo_visa> con embajada <embajada> con id "<id_solicitud>"
      Y todos los documentos están en estado "EN_REVISION"
      Cuando el asesor revisa todos los documentos de la solicitud
      Y el documento "<documento_rechazado>" es "Incorrecto"
      Entonces el documento "<documento_rechazado>" debe cambiar a estado "DESAPROBADO"
      Y el estado de la solicitud debe ser "DESAPROBADO"
      Y el migrante recibe la notificación "DOCUMENTO_RECHAZADO: <documento_rechazado>"

      Ejemplos:
        | tipo_visa | id_solicitud | embajada       | documento_rechazado      |
        | VIVIENDA  | VVE01        | ESTADOUNIDENSE | Pasaporte                |
        | TRABAJO   | VTE01        | BRASILEÑA      | Contrato de trabajo      |
        | ESTUDIO   | VEE01        | BRASILEÑA      | Certificado de matrícula |

  #=====================================
  #  ASESOR ENVIA A EMBAJADA
  #    Como asesor de la agencia de migración
  #    quiero registrar el envío de la solicitud a la embajada
  #    para informar al migrante que su trámite fue enviado correctamente
  #=====================================

    Esquema del escenario: Envío exitoso de solicitud aprobada
      Dado que existe una solicitud aprobada de tipo <tipo_visa> con embajada <embajada> con id <id_solicitud>
      Y el estado de envío es "PENDIENTE"
      Cuando el asesor confirma el envío de la solicitud
      Entonces el estado de envío debe cambiar a "ENVIADO"
      Y el migrante recibe la notificación "SOLICITUD ENVIADA A EMBAJADA"
#    Y la fecha de envío queda registrada

      Ejemplos:
        | tipo_visa | id_solicitud | embajada       |
        | VIVIENDA  | VVE01        | ESTADOUNIDENSE |
        | TRABAJO   | VTB01        | BRASILEÑA      |
        | ESTUDIO   | VEB01        | BRASILEÑA      |

    #=====================================
  #  ASIGNACIÓN DE SOLICITUD A ASESOR
  #=====================================

    Escenario: Asignación automática de solicitud a asesor con disponibilidad
      Dado que existen los siguientes asesores con solicitudes asignadas hoy
        | asesor       | solicitudes_hoy |
        | Juan Pérez   | 8               |
        | María García | 3               |
        | Carlos López | 5               |
      Y cada asesor tiene un límite de 10 solicitudes diarias
      Cuando se registra una nueva solicitud
      Entonces el sistema asigna la solicitud al asesor con menos carga
      Y el asesor "María García" tiene 4 solicitudes asignadas hoy
      Y la solicitud queda en estado "pendiente"

  ## ESCENARIO CUANDO NOS DA ERROR?