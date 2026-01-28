# language: es

Característica: Seguimiento de Solicitudes Migratorias
  Como migrante
  Quiero mantenerme informado acerca del estado de mi tramite migratorio
  Para tomar decisiones informadas según el progreso de mi solicitud

  Antecedentes:
    Dado que estoy autenticado como solicitante con email "usuario@ejemplo.com"

  # ============================================================
  # CONSULTA DE DASHBOARD
  # ============================================================

<<<<<<< HEAD
  Escenario: Visualización del portafolio de solicitudes en el dashboard
    Dado que tengo registrados los siguientes trámites:
      | tipo_visa | embajada       | estado             | fecha_creacion |
      | TRABAJO   | ESTADOUNIDENSE | APROBADA           | 2024-01-15     |
      | ESTUDIO   | ESPAÑOLA       | EN_REVISION        | 2024-02-10     |
      | VIVIENDA  | CANADIENSE     | PENDIENTE_REVISION | 2024-02-20     |
    Cuando accedo al dashboard de seguimiento
    Entonces veo una lista con 3 solicitudes ordenadas por fecha de actualización descendente
    Y cada tarjeta de solicitud muestra los campos "tipo_visa", "embajada" y "estado"
=======
  Escenario: Supervisión global del portafolio de solicitudes
    Dado que gestiono los siguientes trámites activos
      | tipo_visa | embajada        | estado                 | fecha_creacion |
      | TRABAJO   | ESTADOUNIDENSE  | APROBADA               | 2024-01-15     |
      | ESTUDIO   | ESPAÑOLA        | REQUIERE_CORRECCIONES  | 2024-02-10     |
      | VIVIENDA  | CANADIENSE      | PENDIENTE_REVISION     | 2024-02-20     |
    Cuando reviso mi situación migratoria actual
    Entonces se presenta mis 3 solicitudes priorizando la actividad más reciente
    Y cada solicitud expone el tipo de visa, la autoridad consular y su situación técnica actual
>>>>>>> 8eef31228e22fadb267aab3bfd8526f7ce060626

  Escenario: Consulta del detalle de una solicitud aprobada
    Dado que existe la solicitud "SOL-2024-00001" con estado "APROBADA"
    Cuando selecciono ver el detalle de "SOL-2024-00001"
    Entonces la pantalla de detalle muestra el estado "APROBADA" con indicador visual verde
    Y se muestra la sección "Historial de Documentos" con al menos 1 registro
    Y se muestra la sección "Validaciones Consulares" con el resultado de cada documento

<<<<<<< HEAD
  # ============================================================
  # GESTIÓN DE PROGRESO
  # ============================================================

  Escenario: Cálculo del porcentaje de avance documental
=======
  Escenario: Reconstrucción histórica de hitos operativos
    Dado que la solicitud "SOL-2024-00002" registra los siguientes hitos
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
    Y presenta las siguientes validaciones documentales
      | nombre               | estado                | motivo_rechazo                                    |
      | Pasaporte            | APROBADO              |                                                   |
      | Antecedentes penales | RECHAZADO             | Documento vencido, fecha de emisión muy antigua   |
    Cuando analizo los requisitos pendientes de mi solicitud
    Entonces el sistema me alerta sobre el estado "RECHAZADO" de "Antecedentes penales"
    Y justifica la incidencia como: "Documento vencido, fecha de emisión muy antigua"
    Y permite la carga inmediata de una nueva versión del documento

  Escenario: Monitoreo del nivel de completitud del trámite
>>>>>>> 8eef31228e22fadb267aab3bfd8526f7ce060626
    Dado que la solicitud "SOL-2024-00004" de tipo "TRABAJO" requiere 4 documentos validados
    Y la solicitud tiene 3 documentos con estado "APROBADO"
    Cuando consulto el progreso de "SOL-2024-00004"
    Entonces la barra de progreso muestra "75%" de completitud
    Y el contador indica "1 documento pendiente de validación"

  # ============================================================
  # PRIVACIDAD Y CONTROL DE ACCESO
  # ============================================================

  Escenario: Filtrado de solicitudes por propietario autenticado
    Dado que en el sistema existe una solicitud del usuario "pedro.lopez@ejemplo.com"
    Cuando consulto la lista de mis solicitudes
    Entonces la respuesta contiene únicamente solicitudes asociadas a "usuario@ejemplo.com"
    Y la cantidad de solicitudes de "pedro.lopez@ejemplo.com" en la respuesta es 0

  Escenario: Bloqueo de acceso a expediente de tercero
    Dado que el expediente "SOL-2024-00099" pertenece al usuario "otro@ejemplo.com"
    Cuando intento acceder al recurso "SOL-2024-00099"
    Entonces el sistema responde con código de error "403 FORBIDDEN"
    Y el mensaje de error indica "No tiene permisos para acceder a este expediente"

  # ============================================================
  # ALERTAS PROACTIVAS
  # ============================================================

  Escenario: Generación de alerta por documento próximo a vencer
    Dado que la solicitud "SOL-2024-00015" tiene el documento "Pasaporte" con vencimiento "2024-03-08"
    Y la fecha actual del sistema es "2024-02-23"
    Cuando el sistema ejecuta la verificación de vencimientos
    Entonces se genera una alerta de nivel "URGENTE" con el mensaje "Pasaporte vence en 14 días"
    Y la alerta incluye la acción sugerida "Renueva tu documento antes de la cita consular"

  # ============================================================
  # GESTIÓN DE EXPECTATIVAS
  # ============================================================

  Escenario: Información de siguientes pasos tras aprobación
    Dado que la solicitud "SOL-2024-00016" tiene estado "APROBADA"
    Cuando consulto los siguientes pasos de "SOL-2024-00016"
    Entonces el panel de próximos pasos muestra "Esperar asignación de fecha de entrevista"
    Y el tiempo estimado de espera indica "3-5 días hábiles"