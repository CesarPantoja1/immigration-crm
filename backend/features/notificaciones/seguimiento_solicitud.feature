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