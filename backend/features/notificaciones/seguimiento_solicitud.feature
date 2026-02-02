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

  Escenario: Visualización del portafolio de solicitudes en el dashboard
    Dado que tengo registrados los siguientes trámites:
      | tipo_visa | embajada       | estado             | fecha_creacion |
      | TRABAJO   | ESTADOUNIDENSE | APROBADA           | 2024-01-15     |
      | ESTUDIO   | ESPAÑOLA       | EN_REVISION        | 2024-02-10     |
      | VIVIENDA  | CANADIENSE     | PENDIENTE_REVISION | 2024-02-20     |
    Cuando accedo al dashboard de seguimiento
    Entonces veo una lista con 3 solicitudes ordenadas por fecha de actualización descendente
    Y cada tarjeta de solicitud muestra los campos "tipo_visa", "embajada" y "estado"

  Escenario: Consulta del detalle de una solicitud aprobada
    Dado que existe la solicitud "SOL-2024-00001" con estado "APROBADA"
    Cuando selecciono ver el detalle de "SOL-2024-00001"
    Entonces la pantalla de detalle muestra el estado "APROBADA" con indicador visual verde
    Y se muestra la sección "Historial de Documentos" con al menos 1 registro
    Y se muestra la sección "Validaciones Consulares" con el resultado de cada documento

  # ============================================================
  # GESTIÓN DE PROGRESO
  # ============================================================

  Escenario: Cálculo del porcentaje de avance documental
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

  # ============================================================
  # NAVEGACIÓN CONTEXTUAL DESDE NOTIFICACIONES (Deep Linking)
  # ============================================================

  Escenario: Acceso directo al expediente tras notificación de aprobación
    Dado que la solicitud "SOL-2024-00042" ha sido aprobada por la embajada
    Y el migrante recibe una notificación de "Solicitud Aprobada"
    Cuando accedo a la notificación de decisión favorable
    Entonces soy redirigido automáticamente a la vista de detalle de "SOL-2024-00042"
    Y visualizo el estado "APROBADA" con indicador visual de éxito
    Y la notificación queda marcada como leída en el buzón

  Escenario: Acceso directo al expediente tras notificación de rechazo
    Dado que la solicitud "SOL-2024-00043" ha sido rechazada por la embajada
    Y el migrante recibe una notificación de "Solicitud Rechazada"
    Cuando accedo a la notificación de decisión desfavorable
    Entonces soy redirigido automáticamente a la vista de detalle de "SOL-2024-00043"
    Y visualizo el estado "RECHAZADA" con el motivo del rechazo
    Y se muestra la sección "Opciones de Apelación" con los plazos legales

  Escenario: Acceso directo a corrección de documento desde notificación crítica
    Dado que existe la solicitud "SOL-2024-00050" en estado "PENDIENTE_CORRECCION"
    Y el documento "Certificado de Antecedentes" fue rechazado por "Imagen ilegible"
    Cuando accedo a la notificación de "Documento Rechazado - Acción Requerida"
    Entonces soy redirigido a la sección de documentos de "SOL-2024-00050"
    Y visualizo la alerta crítica indicando el documento a corregir
    Y el campo de carga del documento rechazado está habilitado para resubida

  Escenario: Acceso directo a firma de contrato desde notificación
    Dado que la solicitud "SOL-2024-00055" tiene un contrato generado pendiente de firma
    Cuando accedo a la notificación de "Contrato Listo para Firma"
    Entonces soy redirigido a la vista de contrato de "SOL-2024-00055"
    Y visualizo el documento del contrato con opción de firma digital
    Y se muestra el plazo límite para completar la firma

  # ============================================================
  # SUPRESIÓN DE NOTIFICACIONES TRIVIALES (Reducción de Ruido)
  # ============================================================

  Escenario: No generar notificación al subir documento exitosamente
    Dado que el migrante tiene la solicitud "SOL-2024-00060" en estado "EN_PROCESO"
    Y el buzón de notificaciones contiene 3 mensajes no leídos
    Cuando el migrante carga el documento "Pasaporte" en la solicitud
    Entonces la carga se confirma visualmente en la interfaz de documentos
    Y el contador de notificaciones permanece en 3 mensajes
    Y NO se genera una notificación de tipo "Documento Subido"

  Escenario: No generar notificación al cambiar a estado de revisión
    Dado que la solicitud "SOL-2024-00061" está en estado "EN_PROCESO"
    Y el buzón del migrante contiene 2 notificaciones
    Cuando el asesor marca la solicitud como "EN_REVISION"
    Entonces el estado de la solicitud se actualiza a "EN_REVISION"
    Y el contador de notificaciones del migrante permanece en 2
    Y NO se genera una notificación de tipo "Solicitud en Revisión"

  Escenario: No generar notificación al aprobar documento
    Dado que la solicitud "SOL-2024-00062" tiene el documento "Visa Anterior" pendiente de validación
    Y el buzón del migrante contiene 1 notificación
    Cuando el asesor aprueba el documento "Visa Anterior"
    Entonces el documento muestra estado "APROBADO" en el panel de documentos
    Y el contador de notificaciones permanece en 1
    Y solo se notifica cuando hay rechazo que requiere acción del migrante

  # ============================================================
  # GESTIÓN DEL BUZÓN DE NOTIFICACIONES
  # ============================================================

  Escenario: Marcar notificación como leída al consultar detalle
    Dado que el migrante tiene 5 notificaciones no leídas en su buzón
    Y una de ellas es sobre la decisión de "SOL-2024-00070"
    Cuando accedo a la notificación de decisión de "SOL-2024-00070"
    Entonces el contador de notificaciones no leídas disminuye a 4
    Y la notificación consultada aparece con indicador visual de "leída"

  Escenario: Marcar todas las notificaciones como leídas
    Dado que el migrante tiene 8 notificaciones no leídas acumuladas
    Cuando solicito marcar todas las notificaciones como leídas
    Entonces el contador de notificaciones no leídas se establece en 0
    Y todas las notificaciones del buzón muestran estado "leída"

  Escenario: Manejo de notificación con enlace expirado o inválido
    Dado que existe una notificación antigua referenciando "SOL-2023-00001"
    Y la solicitud "SOL-2023-00001" fue archivada del sistema
    Cuando accedo a la notificación del expediente archivado
    Entonces visualizo el mensaje de expediente no disponible "El expediente referenciado ya no está disponible"
    Y permanezco en el buzón de notificaciones
    Y se ofrece la opción de eliminar la notificación obsoleta