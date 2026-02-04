
from datetime import date
from typing import List, Tuple, Optional



# SERVICE: NotificacionService

class NotificacionService:
    """
    Lógica de negocio de NotificacionService.
    
    POLÍTICA DE NOTIFICACIONES (apps/notificaciones/services.py líneas 7-27):
    =========================================================================
    Solo se generan notificaciones para eventos CRÍTICOS o ACCIONABLES.
    
    ❌ ELIMINADOS (ruido, no requieren acción):
       - documento_subido (informativo, no accionable)
       - solicitud_asignada (informativo, no crítico)
       - solicitud_en_revision (informativo, no accionable)
       - solicitud_creada (confirmación, no accionable)
       - contrato_firmado (confirmación, no accionable)
       - documento_aprobado (confirmación positiva, no accionable)
    """
    
    # Notificaciones SUPRIMIDAS según política real (services.py líneas 18-27)
    NOTIFICACIONES_SUPRIMIDAS = [
        'documento_subido',
        'solicitud_asignada',
        'solicitud_en_revision',
        'solicitud_creada',
        'contrato_firmado',
        'documento_aprobado',
    ]
    
    @staticmethod
    def debe_generar_notificacion(tipo_notificacion: str) -> bool:
        """
        Determina si un tipo de notificación debe generarse o suprimirse.
        Basado en la política real de services.py
        """
        tipo_normalizado = tipo_notificacion.lower().replace(' ', '_')
        # Manejar variantes con tildes
        tipo_normalizado = (tipo_normalizado
            .replace('ó', 'o')
            .replace('í', 'i')
            .replace('á', 'a')
            .replace('é', 'e')
            .replace('ú', 'u'))
        return tipo_normalizado not in NotificacionService.NOTIFICACIONES_SUPRIMIDAS
    
    @staticmethod
    def es_notificacion_critica(tipo: str) -> bool:
        """Determina si una notificación es crítica según la política."""
        tipos_criticos = [
            'solicitud_aprobada', 'solicitud_rechazada',
            'embajada_aprobada', 'embajada_rechazada',
            'documento_rechazado',
            'entrevista_agendada', 'entrevista_reprogramada', 'entrevista_cancelada',
            'recordatorio_entrevista',
        ]
        return tipo.lower() in tipos_criticos
    
    @staticmethod
    def es_notificacion_accionable(tipo: str) -> bool:
        """Determina si una notificación requiere acción del usuario."""
        tipos_accionables = [
            'documento_rechazado',      # Cliente DEBE corregir
            'contrato_generado',        # Cliente debe revisar y firmar
            'contrato_pendiente',       # Cliente DEBE firmar
            'simulacro_propuesto',      # Debe aceptar o rechazar
            'preparacion_recomendada',  # Debería agendar simulacro
        ]
        return tipo.lower() in tipos_accionables

# SERVICE: SolicitudService

class SolicitudService:
    """Lógica de negocio para operaciones de Solicitud."""
    
    @staticmethod
    def puede_agendar_entrevista(estado: str) -> bool:
        """
        Verifica si la solicitud puede tener entrevista agendada.
        Fuente: apps/solicitudes/models.py línea 155
        """
        return estado == 'aprobada_embajada'
    
    @staticmethod
    def puede_modificar_documentos(estado: str) -> bool:
        """
        Verifica si se pueden modificar documentos.
        Fuente: apps/solicitudes/models.py líneas 161-171
        """
        estados_bloqueados = [
            'enviada_embajada', 'esperando_decision_embajada',
            'aprobada_embajada', 'rechazada_embajada',
            'entrevista_agendada', 'completada'
        ]
        return estado not in estados_bloqueados
    
    @staticmethod
    def puede_ser_asignada(estado: str, tiene_asesor: bool) -> bool:
        """
        Verifica si la solicitud puede ser asignada a un asesor.
        Fuente: apps/solicitudes/models.py línea 141
        """
        return estado in ['pendiente', 'borrador'] and not tiene_asesor
    
    @staticmethod
    def es_estado_final_positivo(estado: str) -> bool:
        """Determina si el estado representa éxito."""
        return estado in ['aprobada', 'aprobada_embajada', 'completada']
    
    @staticmethod
    def es_estado_final_negativo(estado: str) -> bool:
        """Determina si el estado representa rechazo."""
        return estado in ['rechazada', 'rechazada_embajada']
    
    @staticmethod
    def requiere_accion_cliente(estado: str) -> bool:
        """Determina si el estado requiere acción del cliente."""
        return estado in ['borrador', 'pendiente']

# SERVICE: SeguimientoService

class SeguimientoService:
    """Servicio de lógica de negocio para seguimiento de solicitudes."""
    
    @staticmethod
    def calcular_progreso(documentos_aprobados: int, total_requeridos: int) -> int:
        """Calcula el porcentaje de progreso documental."""
        if total_requeridos == 0:
            return 0
        return int((documentos_aprobados / total_requeridos) * 100)
    
    @staticmethod
    def calcular_documentos_pendientes(documentos_aprobados: int, total_requeridos: int) -> int:
        """Calcula la cantidad de documentos pendientes."""
        return total_requeridos - documentos_aprobados
    
    @staticmethod
    def verificar_acceso(usuario_solicitante, solicitud) -> Tuple[bool, Optional[str]]:
        """
        Verifica si un usuario tiene acceso a una solicitud.
        Un cliente solo puede ver sus propias solicitudes.
        """
        if solicitud.cliente_email == usuario_solicitante.email:
            return True, None
        return False, "No tiene permisos para acceder a este expediente"
    
    @staticmethod
    def calcular_dias_vencimiento(fecha_vencimiento: date, fecha_actual: date) -> int:
        """Calcula los días hasta el vencimiento de un documento."""
        return (fecha_vencimiento - fecha_actual).days
    
    @staticmethod
    def determinar_nivel_alerta(dias_restantes: int) -> str:
        """Determina el nivel de alerta según los días restantes."""
        if dias_restantes <= 7:
            return "CRITICO"
        elif dias_restantes <= 14:
            return "URGENTE"
        elif dias_restantes <= 30:
            return "ADVERTENCIA"
        return "INFO"
    
    @staticmethod
    def generar_mensaje_vencimiento(nombre_documento: str, dias: int) -> str:
        """Genera el mensaje de alerta de vencimiento."""
        return f"{nombre_documento} vence en {dias} días"

# SERVICE: BuzonNotificacionesService

class BuzonNotificacionesService:
    """Servicio de lógica de negocio para gestión del buzón de notificaciones."""
    
    @staticmethod
    def contar_no_leidas(notificaciones: List) -> int:
        """Cuenta las notificaciones no leídas."""
        return sum(1 for n in notificaciones if not n.leida)
    
    @staticmethod
    def marcar_como_leida(notificacion) -> None:
        """Marca una notificación como leída."""
        notificacion.marcar_como_leida()
    
    @staticmethod
    def marcar_todas_leidas(notificaciones: List) -> int:
        """Marca todas las notificaciones como leídas. Retorna cantidad actualizada."""
        count = 0
        for n in notificaciones:
            if not n.leida:
                n.marcar_como_leida()
                count += 1
        return count
    
    @staticmethod
    def verificar_enlace_valido(notificacion, solicitud_existe: bool) -> Tuple[bool, Optional[str]]:
        """
        Verifica si el enlace de una notificación es válido.
        Retorna (es_valido, mensaje_error)
        """
        if not solicitud_existe:
            return False, "El expediente referenciado ya no está disponible"
        return True, None


# ============================================================
# SERVICIOS PARA ALERTAS DE ENTREVISTA (BDD)
# ============================================================

from datetime import datetime, timedelta


class EntrevistaAlertasService:
    """
    Servicio de lógica de negocio para operaciones de Entrevista.
    Específico para BDD de Alertas de Entrevista.
    """

    @staticmethod
    def registrar_entrevista(solicitud_id: str, fecha_hora: str):
        """
        Registra una nueva entrevista para una solicitud.
        Retorna dict con datos para crear notificación.
        """
        return {
            'solicitud_id': solicitud_id,
            'fecha_hora': fecha_hora,
            'estado': 'Programada',
            'tipo_notificacion': 'Entrevista agendada'
        }

    @staticmethod
    def reprogramar_entrevista(fecha_hora_actual: str, nueva_fecha_hora: str):
        """
        Reprograma una entrevista.
        Retorna dict con datos para crear notificación.
        """
        return {
            'fecha_hora_anterior': fecha_hora_actual,
            'nueva_fecha_hora': nueva_fecha_hora,
            'estado': 'Reprogramada',
            'tipo_notificacion': 'Entrevista reprogramada'
        }

    @staticmethod
    def cancelar_entrevista(fecha_hora: str):
        """
        Cancela una entrevista.
        Retorna dict con datos para crear notificación.
        """
        return {
            'fecha_hora': fecha_hora,
            'estado': 'Cancelada',
            'tipo_notificacion': 'Entrevista cancelada'
        }

    @staticmethod
    def puede_recibir_recordatorio(estado_entrevista: str) -> bool:
        """Determina si una entrevista puede recibir recordatorios."""
        return estado_entrevista in ['Programada', 'Reprogramada']


class RecordatorioAlertasService:
    """
    Servicio de lógica de negocio para recordatorios de entrevista.
    Encapsula las reglas de ventanas temporales.
    """

    # Ventanas de recordatorio configuradas (en horas)
    VENTANAS_HORAS = {
        '24h': 24,
        '2h': 2,
    }

    # Tolerancia para cada ventana (en horas)
    TOLERANCIA = {
        '24h': 1,  # 23-25 horas
        '2h': 1,   # 1-3 horas
    }

    @staticmethod
    def calcular_horas_restantes(fecha_hora_entrevista: str, fecha_hora_actual: str) -> float:
        """
        Calcula las horas restantes hasta la entrevista.
        Formatos esperados: 'YYYY-MM-DD HH:MM'
        """
        formato = "%Y-%m-%d %H:%M"
        entrevista = datetime.strptime(fecha_hora_entrevista, formato)
        actual = datetime.strptime(fecha_hora_actual, formato)
        diferencia = entrevista - actual
        return diferencia.total_seconds() / 3600

    @staticmethod
    def determinar_ventana_aplicable(horas_restantes: float, ventanas_configuradas: List[str]) -> Optional[str]:
        """
        Determina qué ventana de recordatorio aplica según las horas restantes.
        Retorna la ventana ('24h', '2h') o None si ninguna aplica.
        """
        for ventana in ventanas_configuradas:
            horas_ventana = RecordatorioAlertasService.VENTANAS_HORAS.get(ventana, 0)
            tolerancia = RecordatorioAlertasService.TOLERANCIA.get(ventana, 1)

            min_horas = horas_ventana - tolerancia
            max_horas = horas_ventana + tolerancia

            if min_horas <= horas_restantes <= max_horas:
                return ventana

        return None

    @staticmethod
    def debe_emitir_recordatorio(estado_entrevista: str, fecha_hora_entrevista: str,
                                  fecha_hora_actual: str, ventanas_configuradas: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Determina si se debe emitir un recordatorio.
        Retorna (debe_emitir, ventana_aplicable).
        """
        # No emitir para entrevistas canceladas
        if not EntrevistaAlertasService.puede_recibir_recordatorio(estado_entrevista):
            return False, None

        horas_restantes = RecordatorioAlertasService.calcular_horas_restantes(
            fecha_hora_entrevista, fecha_hora_actual
        )

        # No emitir si la entrevista ya pasó
        if horas_restantes < 0:
            return False, None

        ventana = RecordatorioAlertasService.determinar_ventana_aplicable(
            horas_restantes, ventanas_configuradas
        )

        return ventana is not None, ventana

    @staticmethod
    def generar_detalle_recordatorio(ventana: str) -> str:
        """Genera el detalle del recordatorio según la ventana."""
        return f"Faltan {ventana}"


class PreparacionAlertasService:
    """
    Servicio de lógica de negocio para alertas de preparación.
    Evalúa si el migrante debería prepararse para su entrevista.
    """

    # Ventana de preparación (en días)
    VENTANA_DIAS = 7

    @staticmethod
    def calcular_dias_restantes(fecha_hora_entrevista: str, fecha_hora_actual: str) -> int:
        """Calcula los días restantes hasta la entrevista."""
        formato = "%Y-%m-%d %H:%M"
        entrevista = datetime.strptime(fecha_hora_entrevista, formato)
        actual = datetime.strptime(fecha_hora_actual, formato)
        diferencia = entrevista - actual
        return diferencia.days

    @staticmethod
    def tiene_simulacro_confirmado(solicitud_id: str, simulacros: dict) -> bool:
        """Verifica si la solicitud tiene un simulacro confirmado."""
        for sim in simulacros.values():
            if sim.solicitud_id == solicitud_id and sim.estado == 'Confirmado':
                return True
        return False

    @staticmethod
    def debe_alertar_preparacion(fecha_hora_entrevista: str, fecha_hora_actual: str,
                                  solicitud_id: str, simulacros: dict,
                                  ventana_dias: int = 7) -> bool:
        """
        Determina si se debe alertar sobre preparación.
        Alerta cuando falta `ventana_dias` o menos y no hay simulacro confirmado.
        """
        dias_restantes = PreparacionAlertasService.calcular_dias_restantes(
            fecha_hora_entrevista, fecha_hora_actual
        )

        if dias_restantes > ventana_dias:
            return False

        if PreparacionAlertasService.tiene_simulacro_confirmado(solicitud_id, simulacros):
            return False

        return True


class SimulacroAlertasService:
    """
    Servicio de lógica de negocio para alertas de simulacro.
    """

    @staticmethod
    def puede_notificar_completado(estado_anterior: str, estado_nuevo: str) -> bool:
        """Determina si se debe notificar que un simulacro fue completado."""
        return estado_anterior != 'Completado' and estado_nuevo == 'Completado'

    @staticmethod
    def puede_notificar_recomendaciones(estado_recomendaciones: str) -> bool:
        """Determina si se debe notificar que las recomendaciones están listas."""
        return estado_recomendaciones == 'Publicado'


class AlertasEntrevistaService:
    """
    Servicio orquestador para generación de alertas de entrevista.
    Centraliza la creación de notificaciones para el dominio de Alertas.
    """

    @staticmethod
    def crear_notificacion_entrevista(tipo: str, solicitud_id: str,
                                       fecha_hora: str = None,
                                       fecha_hora_anterior: str = None,
                                       nueva_fecha_hora: str = None,
                                       detalle: str = None) -> dict:
        """
        Crea datos de notificación para entrevista.
        Retorna un dict con los campos de la notificación.
        """
        notif_data = {
            'tipo': tipo,
            'id_solicitud': solicitud_id,
        }

        if fecha_hora:
            notif_data['fecha_hora_entrevista'] = fecha_hora
        if fecha_hora_anterior:
            notif_data['fecha_hora_anterior'] = fecha_hora_anterior
        if nueva_fecha_hora:
            notif_data['nueva_fecha_hora'] = nueva_fecha_hora
        if detalle:
            notif_data['detalle'] = detalle

        return notif_data

    @staticmethod
    def crear_notificacion_simulacro(tipo: str, simulacro_id: str,
                                      detalle: str = None) -> dict:
        """
        Crea datos de notificación para simulacro.
        Retorna un dict con los campos de la notificación.
        """
        notif_data = {
            'tipo': tipo,
            'id_simulacro': simulacro_id,
        }

        if detalle:
            notif_data['detalle'] = detalle

        return notif_data

