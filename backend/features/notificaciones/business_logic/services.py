
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
