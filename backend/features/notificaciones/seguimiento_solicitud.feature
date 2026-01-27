# language: es

Característica: Seguimiento de Solicitudes Migratorias
  Como migrante
  Quiero mantener visibilidad total sobre el progreso de mi trámite
  Para reducir la incertidumbre y gestionar mis obligaciones legales oportunamente

  Antecedentes:
    Dado que soy un solicitante autenticado en el sistema de gestión migratoria

# Consulta de dashboard

  Escenario: Supervisión global del portafolio de solicitudes
    Dado que gestiono los siguientes trámites activos:
      | tipo_visa | embajada        | estado                 | fecha_creacion |
      | TRABAJO   | ESTADOUNIDENSE  | APROBADA               | 2024-01-15     |
      | ESTUDIO   | ESPAÑOLA        | REQUIERE_CORRECCIONES  | 2024-02-10     |
      | VIVIENDA  | CANADIENSE      | PENDIENTE_REVISION     | 2024-02-20     |
    Cuando reviso mi situación migratoria actual
    Entonces se presenta mis 3 solicitudes priorizando la actividad más reciente
    Y cada solicitud expone el tipo de visa, la autoridad consular y su situación técnica actual

  Escenario: Auditoría de detalles y trazabilidad de una solicitud específica
    Dado que la solicitud "SOL-2024-00001" ha alcanzado el estado "APROBADA"
    Cuando exploro el expediente detallado del trámite "SOL-2024-00001"
    Entonces el sistema confirma la resolución final como "APROBADA"
    Y garantiza el acceso a la trazabilidad documental y validaciones de la embajada

  Escenario: Reconstrucción histórica de hitos operativos
    Dado que la solicitud "SOL-2024-00002" registra los siguientes hitos:
      | evento                | fecha               | descripcion               |
      | SOLICITUD_CREADA      | 2024-02-01 10:00:00 | Solicitud creada          |
      | DOCUMENTO_CARGADO     | 2024-02-01 10:15:00 | Pasaporte cargado         |
      | DOCUMENTO_APROBADO    | 2024-02-03 14:30:00 | Pasaporte validado        |
      | DOCUMENTO_RECHAZADO   | 2024-02-03 14:35:00 | Antecedentes rechazados   |
      | SOLICITUD_APROBADA    | 2024-02-10 09:00:00 | Solicitud aprobada        |
    Cuando audito la cronología de "SOL-2024-00002"
    Entonces el sistema presenta los 5 eventos en orden cronológico inverso
    Y cada hito detalla la naturaleza del cambio, fecha y descripción técnica


  # Gestión de subsanaciones y errores

  Escenario: Identificación de bloqueos y motivos de rechazo documental
    Dado que la solicitud "SOL-2024-00003" se encuentra en estado "REQUIERE_CORRECCIONES"
    Y presenta las siguientes validaciones documentales:
      | nombre               | estado                | motivo_rechazo                                    |
      | Pasaporte            | APROBADO              |                                                   |
      | Antecedentes penales | RECHAZADO             | Documento vencido, fecha de emisión muy antigua   |
    Cuando analizo los requisitos pendientes de mi solicitud
    Entonces el sistema me alerta sobre el estado "RECHAZADO" de "Antecedentes penales"
    Y justifica la incidencia como: "Documento vencido, fecha de emisión muy antigua"
    Y permite la carga inmediata de una nueva versión del documento

  Escenario: Monitoreo del nivel de completitud del trámite
    Dado que la solicitud "SOL-2024-00004" de tipo "TRABAJO" requiere 4 documentos validados
    Y cuenta actualmente con 3 documentos en estado "APROBADO"
    Cuando consulto el progreso de mi gestión
    Entonces el sistema informa un avance del 75%
    Y especifica la cantidad de validaciones restantes para completar el proceso

# Privacidad de la información

  Escenario: Aislamiento de información sensible entre usuarios
    Dado que existe información de otro solicitante identificado como "pedro.lopez@ejemplo.com"
    Cuando accedo a mis servicios privados
    Entonces el sistema garantiza la privacidad mostrando exclusivamente mis trámites vinculados
    Y restringe cualquier visibilidad sobre el expediente de "pedro.lopez@ejemplo.com"

  Escenario: Protección de recursos ajenos mediante control de acceso
    Dado que el expediente "SOL-2024-00099" pertenece a un tercero
    Cuando intento acceder directamente al recurso "SOL-2024-00099"
    Entonces el sistema deniega el acceso por falta de permisos y protege la integridad de la información

# Alertas proactivas y gestión de expectativas

  Escenario: Notificación de riesgos críticos por vencimiento
    Dado que en la solicitud "SOL-2024-00015" el "Pasaporte" tiene fecha de expiración "2024-03-10"
    Y hoy es "2024-02-23"
    Cuando el sistema evalúa la vigencia de los requisitos
    Entonces el sistema emite una alerta de urgencia: "Tu pasaporte vence en 15 días"
    Y provee una recomendación proactiva para evitar retrasos en el proceso consular

  Escenario: Gestión de expectativas sobre el tiempo de resolución
    Dado que la solicitud "SOL-2024-00016" ha sido "APROBADA"
    Cuando reviso los siguientes pasos de mi trámite
    Entonces el sistema reduce mi incertidumbre informando el paso: "Esperar asignación de fecha de entrevista"
    Y proyecta una ventana estimada de resolución de "3-5 días hábiles"