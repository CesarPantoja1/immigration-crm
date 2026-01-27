"""
Servicios de Dominio para Recepción de Solicitudes.
Lógica de negocio que no pertenece a una entidad específica.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .entities import SolicitudVisa, Documento, Asesor
from .value_objects import EstadoSolicitud, EstadoDocumento, TipoNotificacion


class ValidacionDocumentoService:
    """Servicio de validación de documentos."""
    
    EXTENSIONES_PERMITIDAS = ['.pdf', '.jpg', '.jpeg', '.png']
    TAMANO_MAXIMO_MB = 5
    
    @classmethod
    def validar_extension(cls, nombre_archivo: str) -> bool:
        """Valida que la extensión del archivo sea permitida."""
        extension = nombre_archivo.lower().split('.')[-1] if '.' in nombre_archivo else ''
        return f'.{extension}' in cls.EXTENSIONES_PERMITIDAS
    
    @classmethod
    def validar_tamano(cls, tamano_bytes: int) -> bool:
        """Valida que el tamaño del archivo no exceda el máximo."""
        tamano_mb = tamano_bytes / (1024 * 1024)
        return tamano_mb <= cls.TAMANO_MAXIMO_MB
    
    @classmethod
    def generar_motivo_rechazo_minimo(cls, motivo: str) -> str:
        """Asegura que el motivo de rechazo tenga al menos 10 caracteres."""
        if len(motivo) < 10:
            return motivo + " - " + "Por favor revise el documento"
        return motivo


class RevisionSolicitudService:
    """Servicio para la revisión de solicitudes por el asesor."""
    
    @staticmethod
    def revisar_documentos(solicitud: SolicitudVisa, 
                          resultados: Dict[str, str],
                          asesor_id: str) -> Dict[str, str]:
        """
        Revisa todos los documentos de una solicitud y retorna el estado final.
        
        Args:
            solicitud: La solicitud a revisar
            resultados: Dict con nombre_documento -> "Correcto" o "Incorrecto"
            asesor_id: ID del asesor que revisa
            
        Returns:
            Dict con el resumen de la revisión
        """
        documentos_aprobados = 0
        documentos_rechazados = 0
        
        for doc in solicitud.obtener_documentos():
            resultado = resultados.get(doc.obtener_nombre(), "Correcto")
            
            if resultado == "Correcto":
                doc.aprobar(revisor_id=asesor_id)
                documentos_aprobados += 1
            else:
                motivo = ValidacionDocumentoService.generar_motivo_rechazo_minimo(
                    f"Documento {doc.obtener_nombre()} marcado como incorrecto"
                )
                doc.rechazar(motivo=motivo, revisor_id=asesor_id)
                documentos_rechazados += 1
        
        # Actualizar estado de la solicitud
        solicitud.actualizar_estado()
        
        return {
            "total_documentos": len(solicitud.obtener_documentos()),
            "aprobados": documentos_aprobados,
            "rechazados": documentos_rechazados,
            "estado_solicitud": solicitud.obtener_estado()
        }


class EnvioEmbajadaService:
    """Servicio para gestionar el envío de solicitudes a la embajada."""
    
    @staticmethod
    def puede_enviar(solicitud: SolicitudVisa) -> tuple[bool, str]:
        """
        Verifica si una solicitud puede ser enviada a la embajada.
        
        Returns:
            Tupla (puede_enviar, mensaje)
        """
        if solicitud.obtener_estado() != EstadoSolicitud.APROBADO.value:
            return False, "La solicitud debe estar aprobada para ser enviada"
        
        if solicitud.obtener_estado_envio() != "PENDIENTE":
            return False, "La solicitud ya fue enviada anteriormente"
        
        if not solicitud.todos_documentos_aprobados():
            return False, "Todos los documentos deben estar aprobados"
        
        return True, "La solicitud puede ser enviada"
    
    @staticmethod
    def enviar(solicitud: SolicitudVisa) -> Dict[str, str]:
        """
        Envía la solicitud a la embajada.
        
        Returns:
            Dict con el resultado del envío
        """
        puede_enviar, mensaje = EnvioEmbajadaService.puede_enviar(solicitud)
        
        if not puede_enviar:
            raise ValueError(mensaje)
        
        solicitud.marcar_como_enviada()
        
        return {
            "estado": "ENVIADO",
            "mensaje": "SOLICITUD ENVIADA A EMBAJADA",
            "fecha_envio": datetime.now().isoformat()
        }


class NotificacionService:
    """Servicio para gestionar notificaciones."""
    
    @staticmethod
    def generar_notificacion_aprobacion(solicitud: SolicitudVisa) -> Dict[str, str]:
        """Genera notificación de aprobación de visa."""
        return {
            "tipo": TipoNotificacion.VISA_APROBADA.value,
            "titulo": f"VISA_{solicitud.obtener_tipo_visa()}_APROBADA",
            "mensaje": f"Su solicitud de visa {solicitud.obtener_tipo_visa()} ha sido aprobada",
            "solicitud_id": solicitud.id_solicitud,
            "fecha": datetime.now().isoformat()
        }
    
    @staticmethod
    def generar_notificacion_rechazo_documento(documento: Documento, 
                                               solicitud: SolicitudVisa) -> Dict[str, str]:
        """Genera notificación de rechazo de documento."""
        return {
            "tipo": TipoNotificacion.DOCUMENTO_RECHAZADO.value,
            "titulo": f"DOCUMENTO_RECHAZADO: {documento.obtener_nombre()}",
            "mensaje": f"El documento {documento.obtener_nombre()} ha sido rechazado. "
                      f"Motivo: {documento.motivo_rechazo}",
            "solicitud_id": solicitud.id_solicitud,
            "fecha": datetime.now().isoformat()
        }
    
    @staticmethod
    def generar_notificacion_envio(solicitud: SolicitudVisa) -> Dict[str, str]:
        """Genera notificación de envío a embajada."""
        return {
            "tipo": TipoNotificacion.SOLICITUD_ENVIADA.value,
            "titulo": "SOLICITUD ENVIADA A EMBAJADA",
            "mensaje": f"Su solicitud ha sido enviada a la embajada {solicitud.obtener_embajada()}",
            "solicitud_id": solicitud.id_solicitud,
            "fecha": datetime.now().isoformat()
        }


class VencimientoDocumentoService:
    """Servicio para gestionar vencimientos de documentos."""
    
    # Días de anticipación para alertas
    DIAS_ALERTA_PASAPORTE = 180  # 6 meses
    DIAS_MAXIMOS_ANTECEDENTES = 90  # 3 meses
    DIAS_ALERTA_VENCIMIENTO = 30
    
    @classmethod
    def verificar_vencimiento_pasaporte(cls, fecha_vencimiento: datetime) -> Dict[str, any]:
        """
        Verifica si el pasaporte está próximo a vencer.
        
        Returns:
            Dict con alerta si está próximo a vencer
        """
        hoy = datetime.now()
        dias_restantes = (fecha_vencimiento - hoy).days
        
        if dias_restantes < 0:
            return {
                "alerta": True,
                "nivel": "CRITICO",
                "mensaje": "El pasaporte está vencido",
                "dias_restantes": dias_restantes
            }
        elif dias_restantes <= cls.DIAS_ALERTA_VENCIMIENTO:
            return {
                "alerta": True,
                "nivel": "URGENTE",
                "mensaje": f"Tu pasaporte vence en {dias_restantes} días",
                "dias_restantes": dias_restantes
            }
        elif dias_restantes <= cls.DIAS_ALERTA_PASAPORTE:
            return {
                "alerta": True,
                "nivel": "ADVERTENCIA",
                "mensaje": f"Tu pasaporte vence en {dias_restantes} días",
                "dias_restantes": dias_restantes
            }
        
        return {
            "alerta": False,
            "nivel": "OK",
            "mensaje": "El pasaporte tiene vigencia suficiente",
            "dias_restantes": dias_restantes
        }
    
    @classmethod
    def verificar_antiguedad_antecedentes(cls, fecha_emision: datetime) -> Dict[str, any]:
        """
        Verifica si los antecedentes penales no son muy antiguos.
        
        Returns:
            Dict con alerta si son muy antiguos
        """
        hoy = datetime.now()
        dias_desde_emision = (hoy - fecha_emision).days
        
        if dias_desde_emision > cls.DIAS_MAXIMOS_ANTECEDENTES:
            return {
                "alerta": True,
                "nivel": "CRITICO",
                "mensaje": f"Documento vencido, fecha de emisión muy antigua ({dias_desde_emision} días)",
                "dias_desde_emision": dias_desde_emision
            }
        
        return {
            "alerta": False,
            "nivel": "OK",
            "mensaje": "Los antecedentes están vigentes",
            "dias_desde_emision": dias_desde_emision
        }


class ProgresoSolicitudService:
    """Servicio para calcular el progreso de una solicitud."""
    
    @staticmethod
    def calcular_progreso(solicitud: SolicitudVisa) -> Dict[str, any]:
        """
        Calcula el progreso de una solicitud.
        
        Returns:
            Dict con información del progreso
        """
        total = len(solicitud.obtener_documentos())
        if total == 0:
            return {
                "porcentaje": 0,
                "aprobados": 0,
                "total": 0,
                "pendientes": 0,
                "mensaje": "No hay documentos cargados"
            }
        
        aprobados = sum(1 for doc in solicitud.obtener_documentos() if doc.esta_aprobado())
        pendientes = total - aprobados
        porcentaje = int((aprobados / total) * 100)
        
        return {
            "porcentaje": porcentaje,
            "aprobados": aprobados,
            "total": total,
            "pendientes": pendientes,
            "mensaje": f"Avance del {porcentaje}%, {pendientes} validaciones restantes"
        }
    
    @staticmethod
    def obtener_siguiente_paso(solicitud: SolicitudVisa) -> Dict[str, str]:
        """
        Obtiene el siguiente paso recomendado para la solicitud.
        
        Returns:
            Dict con información del siguiente paso
        """
        estado = solicitud.obtener_estado()
        
        pasos = {
            "BORRADOR": {
                "paso": "Cargar documentos obligatorios",
                "tiempo_estimado": "1-2 días"
            },
            "EN_REVISION": {
                "paso": "Esperar revisión del asesor",
                "tiempo_estimado": "2-3 días hábiles"
            },
            "DESAPROBADO": {
                "paso": "Corregir documentos rechazados y recargar",
                "tiempo_estimado": "Depende del documento"
            },
            "REQUIERE_CORRECCIONES": {
                "paso": "Corregir documentos rechazados y recargar",
                "tiempo_estimado": "Depende del documento"
            },
            "APROBADO": {
                "paso": "Esperar envío a embajada por el asesor",
                "tiempo_estimado": "1-2 días hábiles"
            },
            "ENVIADO_EMBAJADA": {
                "paso": "Esperar asignación de fecha de entrevista",
                "tiempo_estimado": "3-5 días hábiles"
            },
            "APROBADO_EMBAJADA": {
                "paso": "Prepararse para la entrevista asignada",
                "tiempo_estimado": "Variable según fecha asignada"
            },
            "RECHAZADO_EMBAJADA": {
                "paso": "Revisar motivos de rechazo y evaluar opciones",
                "tiempo_estimado": "N/A"
            }
        }
        
        return pasos.get(estado, {
            "paso": "Contactar al asesor para más información",
            "tiempo_estimado": "N/A"
        })
