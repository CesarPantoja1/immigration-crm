"""POLÍTICA DE NOTIFICACIONES
   - simulacro_propuesto, simulacro_confirmado, simulacion_completada
   - recomendaciones_listas
   - solicitud_aprobada, solicitud_rechazada
   - embajada_aprobada, embajada_rechazada
   - documento_rechazado (requiere corrección)
   - contrato_generado, contrato_pendiente, contrato_aprobado
   - entrevista_agendada, entrevista_reprogramada, entrevista_cancelada
   - recordatorio_entrevista
   - preparacion_recomendada
"""

from django.utils import timezone
from datetime import datetime, timedelta
from .models import Notificacion


class NotificacionService:

    #Servicio para crear notificaciones de forma centralizada.

    # NOTIFICACIONES DE ENTREVISTA
    @staticmethod
    def notificar_entrevista_agendada(solicitud, fecha, hora):
        cliente = solicitud.cliente
        asesor = solicitud.asesor
        
        # Manejar strings o objetos date/time
        if isinstance(fecha, str):
            from datetime import datetime as dt
            fecha_obj = dt.strptime(fecha, '%Y-%m-%d').date()
            fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
        else:
            fecha_formateada = fecha.strftime('%d/%m/%Y')
        
        if isinstance(hora, str):
            hora_formateada = hora
        else:
            hora_formateada = hora.strftime('%H:%M')
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='entrevista_agendada',
            titulo='📅 Tu entrevista ha sido agendada',
            mensaje=f'Tu entrevista para la solicitud de visa {solicitud.get_tipo_visa_display()} ha sido programada para el {fecha_formateada} a las {hora_formateada}.',
            detalle=f'Asesor asignado: {asesor.get_full_name() if asesor else "Por asignar"}. Prepárate con tiempo y revisa toda tu documentación.',
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}',
            datos={
                'fecha': str(fecha),
                'hora': str(hora),
                'tipo_visa': solicitud.tipo_visa,
                'asesor_nombre': asesor.get_full_name() if asesor else None,
                'solicitud_id': solicitud.id
            }
        )
    
    @staticmethod
    def notificar_entrevista_reprogramada(solicitud, fecha_anterior, hora_anterior, nueva_fecha, nueva_hora, motivo=''):
        cliente = solicitud.cliente
        
        fecha_ant_fmt = fecha_anterior.strftime('%d/%m/%Y') if fecha_anterior else 'N/A'
        hora_ant_fmt = hora_anterior.strftime('%H:%M') if hora_anterior else 'N/A'
        fecha_nueva_fmt = nueva_fecha.strftime('%d/%m/%Y')
        hora_nueva_fmt = nueva_hora.strftime('%H:%M')
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='entrevista_reprogramada',
            titulo='Tu entrevista ha sido reprogramada',
            mensaje=f'Tu entrevista ha sido movida del {fecha_ant_fmt} al {fecha_nueva_fmt} a las {hora_nueva_fmt}.',
            detalle=f'Motivo: {motivo}' if motivo else 'Por favor, actualiza tu agenda.',
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}',
            datos={
                'fecha_anterior': str(fecha_anterior) if fecha_anterior else None,
                'hora_anterior': str(hora_anterior) if hora_anterior else None,
                'nueva_fecha': str(nueva_fecha),
                'nueva_hora': str(nueva_hora),
                'motivo': motivo,
                'solicitud_id': solicitud.id
            }
        )
    
    @staticmethod
    def notificar_entrevista_cancelada(solicitud, motivo=''):
        cliente = solicitud.cliente
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='entrevista_cancelada',
            titulo='Tu entrevista ha sido cancelada',
            mensaje=f'La entrevista para tu solicitud de visa {solicitud.tipo_visa} ha sido cancelada.',
            detalle=f'Motivo: {motivo}. Tu asesor se comunicará contigo para reagendar.' if motivo else 'Tu asesor se comunicará contigo pronto.',
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}',
            datos={
                'motivo': motivo,
                'tipo_visa': solicitud.tipo_visa,
                'solicitud_id': solicitud.id
            }
        )

    # RECORDATORIOS
    @staticmethod
    def notificar_recordatorio_entrevista(solicitud, horas_restantes, fecha_entrevista, hora_entrevista):
        cliente = solicitud.cliente
        
        if horas_restantes == 24:
            titulo = 'Recordatorio: Tu entrevista es mañana'
            mensaje = 'Tu entrevista es mañana. Asegúrate de tener todos los documentos listos.'
            detalle = 'Recomendaciones: Revisa tu documentación, prepárate con las preguntas frecuentes y descansa bien esta noche.'
        elif horas_restantes == 2:
            titulo = 'Tu entrevista es en 2 horas'
            mensaje = f'Tu entrevista comienza a las {hora_entrevista.strftime("%H:%M")}. ¡Éxito!'
            detalle = 'Llega con tiempo, mantén la calma y sé claro en tus respuestas.'
        else:
            titulo = f'Recordatorio: Entrevista en {horas_restantes} horas'
            mensaje = f'Tu entrevista está programada para pronto.'
            detalle = 'Prepárate con tiempo.'
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='recordatorio_entrevista',
            titulo=titulo,
            mensaje=mensaje,
            detalle=detalle,
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}',
            datos={
                'horas_restantes': horas_restantes,
                'fecha_entrevista': str(fecha_entrevista),
                'hora_entrevista': str(hora_entrevista),
                'solicitud_id': solicitud.id
            }
        )

    # PREPARACIÓN Y SIMULACROS
    @staticmethod
    def notificar_preparacion_recomendada(solicitud, dias_para_entrevista):
        cliente = solicitud.cliente
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='preparacion_recomendada',
            titulo='Te recomendamos prepararte para tu entrevista',
            mensaje=f'Tu entrevista es en {dias_para_entrevista} días y aún no has realizado un simulacro de entrevista.',
            detalle='Los clientes que realizan simulacros tienen mayor éxito en sus entrevistas. Agenda uno con tu asesor.',
            solicitud=solicitud,
            url_accion='/simulacros',
            datos={
                'dias_para_entrevista': dias_para_entrevista,
                'tipo_visa': solicitud.tipo_visa,
                'solicitud_id': solicitud.id
            }
        )
    
    @staticmethod
    def notificar_simulacion_completada(simulacro):
        asesor = simulacro.asesor
        cliente = simulacro.cliente
        
        return Notificacion.objects.create(
            usuario=asesor,
            tipo='simulacion_completada',
            titulo=f'Simulacro completado con {cliente.get_full_name()}',
            mensaje=f'Has completado un simulacro de {simulacro.duracion_minutos or 0} minutos.',
            detalle='Recuerda agregar las recomendaciones para el cliente.',
            url_accion=f'/asesor/simulacros/{simulacro.id}',
            datos={
                'simulacro_id': simulacro.id,
                'cliente_nombre': cliente.get_full_name(),
                'cliente_email': cliente.email,
                'duracion_minutos': simulacro.duracion_minutos,
                'solicitud_id': simulacro.solicitud_id if hasattr(simulacro, 'solicitud_id') else None
            }
        )
    
    @staticmethod
    def notificar_recomendaciones_listas(simulacro):
        cliente = simulacro.cliente
        asesor = simulacro.asesor
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='recomendaciones_listas',
            titulo='Tus recomendaciones de simulacro están listas',
            mensaje=f'{asesor.get_full_name()} ha publicado las recomendaciones de tu último simulacro.',
            detalle='Revisa las recomendaciones para prepararte mejor para tu entrevista.',
            url_accion=f'/simulacros/{simulacro.id}/resumen',
            datos={
                'simulacro_id': simulacro.id,
                'asesor_nombre': asesor.get_full_name(),
                'fecha_simulacro': str(simulacro.fecha) if simulacro.fecha else None
            }
        )

    # SIMULACROS
    @staticmethod
    def notificar_simulacro_propuesto(simulacro, propuesto_por='asesor'):
        if propuesto_por == 'asesor':
            destinatario = simulacro.cliente
            proponente = simulacro.asesor.get_full_name()
        else:
            destinatario = simulacro.asesor
            proponente = simulacro.cliente.get_full_name()
        
        fecha_fmt = simulacro.fecha.strftime('%d/%m/%Y') if simulacro.fecha else 'Por definir'
        hora_fmt = simulacro.hora.strftime('%H:%M') if simulacro.hora else 'Por definir'
        
        return Notificacion.objects.create(
            usuario=destinatario,
            tipo='simulacro_propuesto',
            titulo='Nueva propuesta de simulacro',
            mensaje=f'{proponente} te ha propuesto un simulacro para el {fecha_fmt} a las {hora_fmt}.',
            detalle='Revisa la propuesta y confirma o propón una nueva fecha.',
            url_accion=f'/simulacros/{simulacro.id}',
            datos={
                'simulacro_id': simulacro.id,
                'fecha_propuesta': str(simulacro.fecha) if simulacro.fecha else None,
                'hora_propuesta': str(simulacro.hora) if simulacro.hora else None,
                'propuesto_por': propuesto_por
            }
        )
    
    @staticmethod
    def notificar_simulacro_confirmado(simulacro):
        fecha_fmt = simulacro.fecha.strftime('%d/%m/%Y') if simulacro.fecha else 'Por definir'
        hora_fmt = simulacro.hora.strftime('%H:%M') if simulacro.hora else 'Por definir'
        
        notificaciones = []
        
        # Notificar al cliente
        notificaciones.append(Notificacion.objects.create(
            usuario=simulacro.cliente,
            tipo='simulacro_confirmado',
            titulo='Simulacro confirmado',
            mensaje=f'Tu simulacro ha sido confirmado para el {fecha_fmt} a las {hora_fmt}.',
            detalle=f'Asesor: {simulacro.asesor.get_full_name()}. Te enviaremos un recordatorio antes de la sesión.',
            url_accion=f'/simulacros/{simulacro.id}',
            datos={
                'simulacro_id': simulacro.id,
                'fecha': str(simulacro.fecha) if simulacro.fecha else None,
                'hora': str(simulacro.hora) if simulacro.hora else None
            }
        ))
        
        # Notificar al asesor
        notificaciones.append(Notificacion.objects.create(
            usuario=simulacro.asesor,
            tipo='simulacro_confirmado',
            titulo='Simulacro confirmado',
            mensaje=f'El simulacro con {simulacro.cliente.get_full_name()} ha sido confirmado para el {fecha_fmt} a las {hora_fmt}.',
            detalle='El cliente ha sido notificado.',
            url_accion=f'/asesor/simulacros/{simulacro.id}',
            datos={
                'simulacro_id': simulacro.id,
                'cliente_nombre': simulacro.cliente.get_full_name(),
                'fecha': str(simulacro.fecha) if simulacro.fecha else None,
                'hora': str(simulacro.hora) if simulacro.hora else None
            }
        ))
        
        return notificaciones
    

    # DOCUMENTOS
    @staticmethod
    def notificar_documento_rechazado(documento, solicitud, observaciones=''):
        cliente = solicitud.cliente
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='documento_rechazado',
            titulo=f'Documento requiere correcciones: {documento.tipo}',
            mensaje=f'Tu documento "{documento.tipo}" necesita correcciones.',
            detalle=observaciones if observaciones else 'Por favor, revisa las observaciones y vuelve a subir el documento corregido.',
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}/documentos',
            datos={
                'documento_id': documento.id,
                'documento_tipo': documento.tipo,
                'observaciones': observaciones,
                'solicitud_id': solicitud.id
            }
        )
    

    # SOLICITUDES
    @staticmethod
    def notificar_solicitud_aprobada(solicitud):
        cliente = solicitud.cliente
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='solicitud_aprobada',
            titulo='¡Felicitaciones! Tu solicitud ha sido aprobada',
            mensaje=f'Tu solicitud de visa {solicitud.tipo_visa} ha sido aprobada.',
            detalle='Revisa los próximos pasos en el detalle de tu solicitud.',
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}',
            datos={
                'tipo_visa': solicitud.tipo_visa,
                'solicitud_id': solicitud.id
            }
        )
    
    @staticmethod
    def notificar_solicitud_rechazada(solicitud, motivo=''):
        cliente = solicitud.cliente
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='solicitud_rechazada',
            titulo='Actualización sobre tu solicitud',
            mensaje=f'Tu solicitud de visa {solicitud.tipo_visa} no fue aprobada en esta ocasión.',
            detalle=motivo if motivo else 'Consulta con tu asesor sobre los siguientes pasos.',
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}',
            datos={
                'tipo_visa': solicitud.tipo_visa,
                'motivo': motivo,
                'solicitud_id': solicitud.id
            }
        )

    # CONTRATOS
    @staticmethod
    def notificar_contrato_generado(solicitud, contrato_url=''):

        cliente = solicitud.cliente
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='contrato_generado',
            titulo='Tu contrato está listo',
            mensaje=f'Se ha generado el contrato de servicios para tu solicitud de visa {solicitud.get_tipo_visa_display()}.',
            detalle='Revisa los términos y condiciones antes de firmar.',
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}/contrato',
            datos={
                'tipo_visa': solicitud.tipo_visa,
                'contrato_url': contrato_url,
                'solicitud_id': solicitud.id
            }
        )
    
    @staticmethod
    def notificar_contrato_pendiente(solicitud):

        cliente = solicitud.cliente
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='contrato_pendiente',
            titulo='Recordatorio: Contrato pendiente de firma',
            mensaje='Tu contrato de servicios aún no ha sido firmado.',
            detalle='Firma el contrato para continuar con el proceso de tu visa.',
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}/contrato',
            datos={
                'tipo_visa': solicitud.tipo_visa,
                'solicitud_id': solicitud.id
            }
        )
    
    @staticmethod
    def notificar_contrato_aprobado(solicitud):

        cliente = solicitud.cliente
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='contrato_aprobado',
            titulo='Tu contrato ha sido aprobado',
            mensaje=f'El contrato para tu solicitud de visa {solicitud.get_tipo_visa_display()} ha sido aprobado.',
            detalle='Ya puedes comenzar a subir tu documentación.',
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}/documentos',
            datos={
                'tipo_visa': solicitud.tipo_visa,
                'solicitud_id': solicitud.id
            }
        )

    
    @staticmethod
    def notificar_embajada_aprobada(solicitud):
        cliente = solicitud.cliente
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='embajada_aprobada',
            titulo='🎉 ¡Tu solicitud fue aprobada por la embajada!',
            mensaje=f'¡Felicitaciones! La embajada ha aprobado tu solicitud de visa {solicitud.get_tipo_visa_display()}.',
            detalle='El siguiente paso es agendar tu entrevista consular. Tu asesor te contactará pronto con las fechas disponibles.',
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}',
            datos={
                'tipo_visa': solicitud.tipo_visa,
                'embajada': solicitud.embajada,
                'fecha_aprobacion': str(timezone.now().date()),
                'solicitud_id': solicitud.id
            }
        )
    
    @staticmethod
    def notificar_embajada_rechazada(solicitud, motivo=''):
        """
        Crea notificación cuando la embajada rechaza una solicitud.
        Destinatario: Cliente
        CRÍTICO: Decisión final negativa.
        """
        cliente = solicitud.cliente
        
        return Notificacion.objects.create(
            usuario=cliente,
            tipo='embajada_rechazada',
            titulo='Actualización sobre tu solicitud de visa',
            mensaje=f'Lamentamos informarte que la embajada no ha aprobado tu solicitud de visa {solicitud.get_tipo_visa_display()} en esta ocasión.',
            detalle=f'Motivo: {motivo}' if motivo else 'Tu asesor se pondrá en contacto contigo para explicarte las opciones disponibles.',
            solicitud=solicitud,
            url_accion=f'/solicitudes/{solicitud.id}',
            datos={
                'tipo_visa': solicitud.tipo_visa,
                'embajada': solicitud.embajada,
                'motivo': motivo,
                'fecha_rechazo': str(timezone.now().date()),
                'solicitud_id': solicitud.id
            }
        )

    
    @staticmethod
    def crear_notificacion_general(usuario, titulo, mensaje, detalle='', url_accion='', datos=None):
        return Notificacion.objects.create(
            usuario=usuario,
            tipo='general',
            titulo=titulo,
            mensaje=mensaje,
            detalle=detalle,
            url_accion=url_accion,
            datos=datos or {}
        )


# Instancia singleton del servicio
notificacion_service = NotificacionService()
