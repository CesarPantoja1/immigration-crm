"""
Servicios de Dominio para Seguimiento de Solicitudes.
"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Tuple

from .value_objects import (
    TipoEvento,
    EstadoSolicitudSeguimiento,
    NivelAlerta,
    TipoAlerta,
    EventoHistorial,
    ProgresoSolicitud,
    Alerta,
    PasoSiguiente,
    ResumenSolicitud,
    ValidacionDocumento,
)
from .entities import (
    TimelineSolicitud,
    SeguimientoSolicitud,
    PortafolioMigrante,
)


@dataclass
class ResultadoConsulta:
    """Resultado de una consulta de seguimiento."""
    exito: bool
    mensaje: str
    datos: dict = None


class ConsultaSolicitudService:
    """
    Servicio para consultas de solicitudes.
    """
    
    def consultar_detalle(
        self,
        seguimiento: SeguimientoSolicitud
    ) -> dict:
        """
        Consulta el detalle completo de una solicitud.
        """
        return {
            'solicitud_id': seguimiento.solicitud_id,
            'codigo': seguimiento.codigo,
            'tipo_visa': seguimiento.tipo_visa,
            'embajada': seguimiento.embajada,
            'estado': seguimiento.estado.value,
            'fecha_creacion': seguimiento.fecha_creacion,
            'progreso': {
                'porcentaje': seguimiento.obtener_porcentaje_progreso(),
                'validaciones_restantes': seguimiento.obtener_validaciones_restantes()
            },
            'documentos': [
                {
                    'nombre': d.nombre,
                    'estado': d.estado,
                    'motivo_rechazo': d.motivo_rechazo
                }
                for d in seguimiento.documentos
            ],
            'siguiente_paso': {
                'descripcion': seguimiento.obtener_siguiente_paso().descripcion,
                'tiempo_estimado': seguimiento.obtener_siguiente_paso().tiempo_estimado
            },
            'alertas_urgentes': len(seguimiento.obtener_alertas_urgentes())
        }
    
    def consultar_cronologia(
        self,
        seguimiento: SeguimientoSolicitud,
        cantidad: int = None
    ) -> List[dict]:
        """
        Consulta la cronología de eventos.
        """
        eventos = seguimiento.timeline.obtener_cronologia()
        
        if cantidad:
            eventos = eventos[:cantidad]
        
        return [
            {
                'tipo': e.tipo.value,
                'fecha': e.formato_fecha(),
                'descripcion': e.descripcion,
                'datos': e.datos_adicionales
            }
            for e in eventos
        ]


class PortafolioService:
    """
    Servicio para gestión del portafolio de solicitudes.
    """
    
    def obtener_dashboard(
        self,
        portafolio: PortafolioMigrante
    ) -> dict:
        """
        Obtiene los datos para el dashboard del migrante.
        """
        solicitudes_activas = portafolio.obtener_solicitudes_activas()
        solicitudes_priorizadas = portafolio.obtener_solicitudes_priorizadas()
        
        return {
            'total_solicitudes': portafolio.contar_solicitudes(),
            'solicitudes_activas': len(solicitudes_activas),
            'alertas_urgentes': len(portafolio.obtener_alertas_urgentes()),
            'solicitudes': [
                {
                    'codigo': s.codigo,
                    'tipo_visa': s.tipo_visa,
                    'embajada': s.embajada,
                    'estado': s.estado.value,
                    'progreso': s.obtener_porcentaje_progreso()
                }
                for s in solicitudes_priorizadas
            ]
        }
    
    def verificar_acceso(
        self,
        portafolio: PortafolioMigrante,
        solicitud_id: str
    ) -> Tuple[bool, str]:
        """
        Verifica si el migrante tiene acceso a una solicitud.
        """
        if portafolio.tiene_solicitud(solicitud_id):
            return True, "Acceso permitido"
        return False, "Acceso denegado por falta de permisos"


class AlertaService:
    """
    Servicio para gestión de alertas.
    """
    
    def evaluar_vencimientos(
        self,
        seguimiento: SeguimientoSolicitud,
        documentos_con_fecha: List[dict]
    ) -> List[Alerta]:
        """
        Evalúa vencimientos y genera alertas.
        
        Args:
            documentos_con_fecha: Lista de dicts con 'nombre' y 'fecha_vencimiento'
        """
        return seguimiento.verificar_vencimientos(documentos_con_fecha)
    
    def generar_alerta_rechazo(
        self,
        documento_nombre: str,
        motivo: str,
        solicitud_id: str
    ) -> Alerta:
        """
        Genera alerta por documento rechazado.
        """
        return Alerta(
            tipo=TipoAlerta.DOCUMENTO_RECHAZADO,
            nivel=NivelAlerta.URGENTE,
            titulo=f"Documento rechazado: {documento_nombre}",
            mensaje=f"El documento '{documento_nombre}' fue rechazado",
            accion_sugerida=f"Cargue una nueva versión. Motivo: {motivo}",
            solicitud_id=solicitud_id
        )
    
    def generar_alerta_entrevista_proxima(
        self,
        fecha_entrevista: date,
        solicitud_id: str
    ) -> Alerta:
        """
        Genera alerta de entrevista próxima.
        """
        dias = (fecha_entrevista - date.today()).days
        
        if dias <= 1:
            nivel = NivelAlerta.CRITICO
        elif dias <= 3:
            nivel = NivelAlerta.URGENTE
        else:
            nivel = NivelAlerta.ADVERTENCIA
        
        return Alerta(
            tipo=TipoAlerta.ENTREVISTA_PROXIMA,
            nivel=nivel,
            titulo="Entrevista próxima",
            mensaje=f"Su entrevista es en {dias} día(s)",
            fecha_vencimiento=fecha_entrevista,
            accion_sugerida="Prepare los documentos originales para la entrevista",
            solicitud_id=solicitud_id
        )


class ProgresoService:
    """
    Servicio para cálculo y monitoreo del progreso.
    """
    
    def calcular_progreso_detallado(
        self,
        seguimiento: SeguimientoSolicitud
    ) -> dict:
        """
        Calcula el progreso detallado de una solicitud.
        """
        progreso = seguimiento.calcular_progreso()
        
        return {
            'porcentaje': progreso.porcentaje,
            'total_requeridos': progreso.total_documentos_requeridos,
            'aprobados': progreso.documentos_aprobados,
            'pendientes': progreso.documentos_pendientes,
            'rechazados': progreso.documentos_rechazados,
            'validaciones_restantes': progreso.validaciones_restantes(),
            'esta_completo': progreso.esta_completo,
            'tiene_problemas': progreso.tiene_rechazados
        }
    
    def obtener_mensaje_progreso(
        self,
        seguimiento: SeguimientoSolicitud
    ) -> str:
        """
        Genera un mensaje legible sobre el progreso.
        """
        progreso = seguimiento.calcular_progreso()
        
        if progreso.esta_completo:
            return "Todos los documentos han sido validados"
        
        restantes = progreso.validaciones_restantes()
        
        if progreso.tiene_rechazados:
            return (f"Avance del {progreso.porcentaje}%. "
                   f"{progreso.documentos_rechazados} documento(s) requieren corrección")
        
        return f"Avance del {progreso.porcentaje}%. {restantes} validación(es) restante(s)"


class PrivacidadService:
    """
    Servicio para control de privacidad y acceso.
    """
    
    def verificar_propiedad(
        self,
        solicitud: SeguimientoSolicitud,
        migrante_id: str
    ) -> bool:
        """
        Verifica si el migrante es propietario de la solicitud.
        """
        return solicitud.migrante_id == migrante_id
    
    def filtrar_solicitudes_propias(
        self,
        todas_solicitudes: List[SeguimientoSolicitud],
        migrante_id: str
    ) -> List[SeguimientoSolicitud]:
        """
        Filtra para mostrar solo solicitudes del migrante.
        """
        return [s for s in todas_solicitudes if s.migrante_id == migrante_id]
    
    def denegar_acceso(self, recurso_id: str) -> dict:
        """
        Genera respuesta de acceso denegado.
        """
        return {
            'acceso': False,
            'mensaje': 'Acceso denegado por falta de permisos',
            'recurso': recurso_id
        }


class ExpectativasService:
    """
    Servicio para gestión de expectativas del usuario.
    """
    
    def obtener_siguientes_pasos(
        self,
        seguimiento: SeguimientoSolicitud
    ) -> dict:
        """
        Obtiene información sobre siguientes pasos.
        """
        paso = seguimiento.obtener_siguiente_paso()
        
        return {
            'paso': paso.descripcion,
            'tiempo_estimado': paso.tiempo_estimado,
            'requiere_accion_usuario': paso.es_accion_usuario,
            'detalle': paso.detalle
        }
    
    def obtener_mensaje_expectativas(
        self,
        estado: EstadoSolicitudSeguimiento
    ) -> str:
        """
        Genera mensaje para reducir incertidumbre del usuario.
        """
        mensajes = {
            EstadoSolicitudSeguimiento.APROBADA: 
                "Su solicitud está aprobada. Espere la asignación de fecha de entrevista en 3-5 días hábiles.",
            EstadoSolicitudSeguimiento.PENDIENTE_REVISION:
                "Su solicitud está en cola para revisión. Un asesor la revisará en 1-3 días hábiles.",
            EstadoSolicitudSeguimiento.EN_REVISION:
                "Un asesor está revisando su solicitud actualmente.",
            EstadoSolicitudSeguimiento.REQUIERE_CORRECCIONES:
                "Su solicitud requiere correcciones. Revise los documentos observados.",
            EstadoSolicitudSeguimiento.ENVIADA_EMBAJADA:
                "Su solicitud ha sido enviada a la embajada. El tiempo de respuesta es de 5-15 días hábiles.",
            EstadoSolicitudSeguimiento.RECHAZADA:
                "Su solicitud fue rechazada. Puede apelar o iniciar una nueva solicitud.",
            EstadoSolicitudSeguimiento.COMPLETADA:
                "Su trámite ha sido completado exitosamente."
        }
        
        return mensajes.get(estado, "Estado de solicitud actualizado.")
