"""
Servicios de la app Preparación.
Contiene toda la lógica de negocio relacionada con simulacros, práctica y recomendaciones.
"""
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, date, time

from .models import Simulacro, Recomendacion, Practica, ConfiguracionIA

Usuario = get_user_model()

# Constantes
MAX_SIMULACROS_POR_PROCESO = 2


class SimulacroService:
    """Servicio para gestión de simulacros."""
    
    @staticmethod
    def obtener_simulacro(simulacro_id: int, usuario=None) -> Simulacro | None:
        """Obtiene un simulacro por ID, verificando permisos."""
        try:
            filtros = {'pk': simulacro_id, 'is_deleted': False}
            
            if usuario:
                if usuario.rol == 'cliente':
                    filtros['cliente'] = usuario
                elif usuario.rol == 'asesor':
                    filtros['asesor'] = usuario
            
            return Simulacro.objects.select_related('cliente', 'asesor', 'solicitud').get(**filtros)
        except Simulacro.DoesNotExist:
            return None
    
    @staticmethod
    def listar_simulacros(usuario, estado: str = None, modalidad: str = None, fecha: str = None):
        """Lista simulacros según el rol del usuario."""
        if usuario.rol == 'cliente':
            queryset = Simulacro.objects.filter(cliente=usuario, is_deleted=False)
        elif usuario.rol == 'asesor':
            queryset = Simulacro.objects.filter(asesor=usuario, is_deleted=False)
        else:
            queryset = Simulacro.objects.filter(is_deleted=False)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        if modalidad:
            queryset = queryset.filter(modalidad=modalidad)
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        
        return queryset.select_related('cliente', 'asesor', 'solicitud').order_by('-fecha', '-hora')
    
    @staticmethod
    def verificar_disponibilidad(usuario, solicitud=None) -> dict:
        """
        Verifica si el cliente puede solicitar más simulacros.
        El contador es POR SOLICITUD, no global.
        """
        # Si se proporciona una solicitud, filtrar por ella
        filtros = {
            'cliente': usuario,
            'is_deleted': False
        }
        if solicitud:
            filtros['solicitud'] = solicitud
        
        simulacros_activos = Simulacro.objects.filter(
            **filtros
        ).exclude(estado='cancelado').count()
        
        disponibles = max(0, MAX_SIMULACROS_POR_PROCESO - simulacros_activos)
        
        if solicitud:
            tipo_visa = solicitud.get_tipo_visa_display() if hasattr(solicitud, 'get_tipo_visa_display') else 'esta visa'
            if disponibles > 0:
                if simulacros_activos == 0:
                    mensaje = f'Puede solicitar hasta {MAX_SIMULACROS_POR_PROCESO} simulacros para {tipo_visa}'
                else:
                    mensaje = f'Tiene {disponibles} simulacro(s) disponible(s) para esta solicitud'
            else:
                mensaje = f'Ha alcanzado el límite de {MAX_SIMULACROS_POR_PROCESO} simulacros para {tipo_visa}'
        else:
            mensaje = f'Tiene {disponibles} simulacro(s) disponible(s)' if disponibles > 0 \
                      else f'Ha alcanzado el límite de {MAX_SIMULACROS_POR_PROCESO} simulacros por proceso'
        
        return {
            'disponibilidad': 'disponible' if disponibles > 0 else 'no_disponible',
            'simulacros_activos': simulacros_activos,
            'simulacros_disponibles': disponibles,
            'mensaje': mensaje
        }
    
    @staticmethod
    def obtener_contador(usuario, solicitud=None) -> dict:
        """
        Obtiene el contador de simulacros del cliente.
        El contador es POR SOLICITUD si se proporciona una.
        """
        filtros_base = {
            'cliente': usuario,
            'is_deleted': False
        }
        if solicitud:
            filtros_base['solicitud'] = solicitud
        
        completados = Simulacro.objects.filter(
            estado='completado',
            **filtros_base
        ).count()
        
        activos = Simulacro.objects.filter(
            estado__in=['solicitado', 'propuesto', 'pendiente_respuesta', 'contrapropuesta', 'contrapropuesta_final', 'confirmado', 'en_progreso'],
            **filtros_base
        ).count()
        
        total = completados + activos
        
        return {
            'completados': completados,
            'activos': activos,
            'total_usados': total,
            'total_permitidos': MAX_SIMULACROS_POR_PROCESO,
            'disponibles': max(0, MAX_SIMULACROS_POR_PROCESO - total)
        }
    
    @staticmethod
    def validar_fecha_antes_cita_embajada(fecha_simulacro, solicitud) -> tuple[bool, str | None]:
        """
        Valida que la fecha del simulacro sea ANTERIOR a la cita con la embajada.
        Solo valida si existe una entrevista agendada con fecha.
        """
        if not solicitud:
            return True, None  # Sin solicitud, no validar
        
        # Obtener la fecha de entrevista de la solicitud
        try:
            # Verificar si tiene entrevista asociada
            entrevista = getattr(solicitud, 'entrevista', None)
            if entrevista and hasattr(entrevista, 'fecha') and entrevista.fecha:
                fecha_entrevista = entrevista.fecha
                # Solo validar si es una fecha válida
                if fecha_simulacro and fecha_simulacro >= fecha_entrevista:
                    return False, 'La fecha del simulacro debe ser anterior a su cita con la embajada'
        except Exception:
            pass  # Si no hay entrevista o error, permitir (no bloquear)
        
        return True, None
    
    @staticmethod
    def solicitar_simulacro(cliente, solicitud, modalidad: str = 'virtual',
                            fecha_propuesta=None, hora_propuesta=None,
                            observaciones: str = '') -> tuple[Simulacro | None, str | None]:
        """Permite al cliente solicitar un simulacro."""
        # Verificar que la solicitud esté aprobada por la embajada o que la entrevista esté agendada
        # Los simulacros solo están disponibles después de la aprobación de la embajada
        # Si la entrevista está agendada, implica que la embajada ya aprobó la solicitud
        estados_permitidos = ['aprobada_embajada', 'entrevista_agendada']
        
        if solicitud.estado not in estados_permitidos:
            return None, ('Solo puede solicitar un simulacro cuando su solicitud haya sido '
                          'aprobada por la embajada o cuando la entrevista esté agendada. '
                          'Estado actual: ' + 
                          (solicitud.get_estado_display() if hasattr(solicitud, 'get_estado_display') else solicitud.estado))
        
        # Verificar disponibilidad POR SOLICITUD
        info = SimulacroService.verificar_disponibilidad(cliente, solicitud)
        if info['disponibilidad'] != 'disponible':
            return None, f'Ha alcanzado el límite de {MAX_SIMULACROS_POR_PROCESO} simulacros para esta solicitud.'
        
        # Crear simulacro (CLIENTE solicita -> propuesto_por='cliente')
        fecha_default = date.today()
        hora_default = time(9, 0)
        
        # Parse fecha_propuesta if it's a string
        if fecha_propuesta:
            if isinstance(fecha_propuesta, str):
                try:
                    fecha_propuesta = datetime.strptime(fecha_propuesta, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    return None, 'Formato de fecha inválido. Use YYYY-MM-DD'
                fecha_default = fecha_propuesta
            elif isinstance(fecha_propuesta, date):
                fecha_default = fecha_propuesta
        
        # Parse hora_propuesta if it's a string
        if hora_propuesta:
            if isinstance(hora_propuesta, str):
                try:
                    hora_propuesta = datetime.strptime(hora_propuesta, '%H:%M').time()
                except (ValueError, TypeError):
                    try:
                        hora_propuesta = datetime.strptime(hora_propuesta, '%H:%M:%S').time()
                    except (ValueError, TypeError):
                        return None, 'Formato de hora inválido. Use HH:MM o HH:MM:SS'
                hora_default = hora_propuesta
            elif isinstance(hora_propuesta, time):
                hora_default = hora_propuesta

        simulacro = Simulacro.objects.create(
            cliente=cliente,
            solicitud=solicitud,
            asesor=solicitud.asesor,
            modalidad=modalidad,
            fecha=fecha_default,
            hora=hora_default,
            fecha_propuesta=fecha_propuesta if isinstance(fecha_propuesta, date) else None,
            hora_propuesta=hora_propuesta if isinstance(hora_propuesta, time) else None,
            estado='solicitado',
            propuesto_por='cliente',  # El cliente inició la propuesta
            notas=f"Solicitud del cliente: {observaciones}" if observaciones else ""
        )

        return simulacro, None
    
    @staticmethod
    def crear_propuesta(asesor, cliente_id: int, fecha, hora,
                        modalidad: str = 'virtual', ubicacion: str = '',
                        solicitud_id: int = None) -> tuple[Simulacro | None, str | None]:
        """Crea una propuesta de simulacro (ASESOR propone -> propuesto_por='asesor')."""
        try:
            cliente = Usuario.objects.get(id=cliente_id, rol='cliente')
        except Usuario.DoesNotExist:
            return None, 'Cliente no encontrado'

        # Parse fecha if it's a string
        if isinstance(fecha, str):
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return None, 'Formato de fecha inválido. Use YYYY-MM-DD'
        
        # Parse hora if it's a string
        if isinstance(hora, str):
            try:
                hora = datetime.strptime(hora, '%H:%M').time()
            except (ValueError, TypeError):
                try:
                    hora = datetime.strptime(hora, '%H:%M:%S').time()
                except (ValueError, TypeError):
                    return None, 'Formato de hora inválido. Use HH:MM o HH:MM:SS'

        simulacro = Simulacro.objects.create(
            cliente=cliente,
            asesor=asesor,
            solicitud_id=solicitud_id,
            fecha=fecha,
            hora=hora,
            modalidad=modalidad,
            ubicacion=ubicacion,
            estado='pendiente_respuesta',
            propuesto_por='asesor'  # El asesor inició la propuesta
        )

        return simulacro, None
    
    @staticmethod
    def aceptar_propuesta(simulacro: Simulacro, usuario_que_acepta=None) -> tuple[bool, str | None]:
        """
        Acepta una propuesta de simulacro.
        
        - Si el CLIENTE acepta (propuesto_por='asesor') → notifica al asesor
        - Si el ASESOR acepta (propuesto_por='cliente') → notifica al cliente
        """
        # Estados donde se puede aceptar (incluye contrapropuestas)
        estados_aceptables = ['solicitado', 'propuesto', 'pendiente_respuesta', 'contrapropuesta', 'contrapropuesta_final']
        
        if simulacro.estado not in estados_aceptables:
            return False, f'El simulacro no puede ser aceptado en estado {simulacro.estado}'
        
        simulacro.estado = 'confirmado'
        simulacro.save()
        
        # Enviar notificación según quién propuso originalmente
        try:
            from apps.notificaciones.services import NotificacionService
            
            if simulacro.propuesto_por == 'cliente':
                # El asesor aceptó la solicitud del cliente → notificar al cliente
                NotificacionService.notificar_simulacro_confirmado(simulacro)
            elif simulacro.propuesto_por == 'asesor':
                # El cliente aceptó la propuesta del asesor → notificar al asesor
                NotificacionService.notificar_simulacro_confirmado(simulacro)
        except Exception as e:
            # No fallar si la notificación falla
            pass
        
        return True, None
    
    @staticmethod
    def contrapropuesta(simulacro: Simulacro, fecha, hora, quien_propone: str = None) -> tuple[bool, str | None]:
        """
        Propone fecha alternativa para un simulacro.
        
        Permite contrapropuesta en los siguientes estados:
        - 'pendiente_respuesta': Cliente propone fecha alternativa a propuesta del asesor
        - 'solicitado': Asesor propone fecha alternativa a solicitud del cliente
        - 'contrapropuesta': Se permite otra contrapropuesta (negociación)
        - 'contrapropuesta_final': El asesor puede aceptar o definir fecha final
        
        Args:
            simulacro: El simulacro a modificar
            fecha: Nueva fecha propuesta
            hora: Nueva hora propuesta
            quien_propone: 'cliente' o 'asesor' - quién está haciendo esta contrapropuesta
        """
        estados_permitidos = ['pendiente_respuesta', 'solicitado', 'contrapropuesta', 'contrapropuesta_final']
        
        if simulacro.estado not in estados_permitidos:
            return False, f'No se puede proponer fecha alternativa en estado {simulacro.get_estado_display()}'
        
        # Parse fecha if it's a string
        if isinstance(fecha, str):
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return False, 'Formato de fecha inválido. Use YYYY-MM-DD'
        
        # Parse hora if it's a string
        if isinstance(hora, str):
            try:
                hora = datetime.strptime(hora, '%H:%M').time()
            except (ValueError, TypeError):
                try:
                    hora = datetime.strptime(hora, '%H:%M:%S').time()
                except (ValueError, TypeError):
                    return False, 'Formato de hora inválido. Use HH:MM o HH:MM:SS'
        
        # Validar que la fecha sea anterior a la cita con la embajada
        if simulacro.solicitud:
            valido, error = SimulacroService.validar_fecha_antes_cita_embajada(fecha, simulacro.solicitud)
            if not valido:
                return False, error
        
        simulacro.fecha_propuesta = fecha
        simulacro.hora_propuesta = hora
        simulacro.estado = 'contrapropuesta'
        
        # Actualizar quién hizo la última propuesta (importante para determinar turno)
        if quien_propone:
            simulacro.propuesto_por = quien_propone
        
        simulacro.save()
        return True, None
    
    @staticmethod
    def cancelar(simulacro: Simulacro, motivo: str = '') -> tuple[bool, str | None]:
        """Cancela un simulacro."""
        if not simulacro.puede_cancelar():
            return False, 'No se puede cancelar este simulacro'
        
        simulacro.estado = 'cancelado'
        simulacro.motivo_cancelacion = motivo
        simulacro.save()
        return True, None
    
    @staticmethod
    def ingresar_sala_espera(simulacro: Simulacro) -> tuple[bool, str | None]:
        """Permite al cliente ingresar a la sala de espera."""
        if simulacro.estado not in ['confirmado']:
            return False, 'El simulacro debe estar confirmado'
        
        if not simulacro.puede_ingresar_sala():
            return False, 'Aún no puede ingresar a la sala de espera'
        
        simulacro.estado = 'en_sala_espera'
        simulacro.save()
        return True, None
    
    @staticmethod
    def iniciar(simulacro: Simulacro) -> tuple[bool, str | None]:
        """Inicia un simulacro."""
        if simulacro.estado not in ['confirmado', 'en_sala_espera']:
            return False, 'El simulacro debe estar confirmado o en sala de espera'
        
        simulacro.estado = 'en_progreso'
        simulacro.fecha_inicio = timezone.now()
        simulacro.save()
        return True, None
    
    @staticmethod
    def finalizar(simulacro: Simulacro, transcripcion_texto: str = '',
                  duracion_minutos: int = 0) -> tuple[bool, str | None]:
        """Finaliza un simulacro."""
        if simulacro.estado != 'en_progreso':
            return False, 'El simulacro no está en progreso'
        
        simulacro.estado = 'completado'
        simulacro.fecha_fin = timezone.now()
        simulacro.duracion_minutos = duracion_minutos or (
            int((simulacro.fecha_fin - simulacro.fecha_inicio).total_seconds() / 60)
            if simulacro.fecha_inicio else 0
        )
        if transcripcion_texto:
            simulacro.transcripcion_texto = transcripcion_texto
        simulacro.save()
        return True, None
    
    @staticmethod
    def listar_completados_para_asesor(asesor):
        """Lista simulacros completados para análisis de IA."""
        return Simulacro.objects.filter(
            asesor=asesor,
            estado='completado',
            is_deleted=False
        ).select_related('cliente', 'solicitud').order_by('-fecha_fin')


class RecomendacionService:
    """Servicio para gestión de recomendaciones."""
    
    @staticmethod
    def obtener_recomendacion(recomendacion_id: int) -> Recomendacion | None:
        """Obtiene una recomendación por ID."""
        try:
            return Recomendacion.objects.select_related('simulacro').get(pk=recomendacion_id)
        except Recomendacion.DoesNotExist:
            return None
    
    @staticmethod
    def obtener_por_simulacro(simulacro_id: int) -> Recomendacion | None:
        """Obtiene la recomendación de un simulacro."""
        try:
            return Recomendacion.objects.get(simulacro_id=simulacro_id)
        except Recomendacion.DoesNotExist:
            return None
    
    @staticmethod
    def listar_para_cliente(usuario):
        """Lista recomendaciones publicadas para un cliente."""
        return Recomendacion.objects.filter(
            simulacro__cliente=usuario,
            publicada=True
        ).select_related('simulacro').order_by('-fecha_publicacion')
    
    @staticmethod
    def crear_o_actualizar(simulacro: Simulacro, datos: dict) -> Recomendacion:
        """Crea o actualiza una recomendación para un simulacro."""
        # IMPORTANTE: estado_feedback solo debe ser 'generado' si viene explícitamente
        # Por defecto usamos 'pendiente' para no interferir con el flujo de IA
        estado = datos.get('estado_feedback', 'pendiente')
        
        recomendacion, created = Recomendacion.objects.update_or_create(
            simulacro=simulacro,
            defaults={
                'estado_feedback': estado,
                'claridad': datos.get('claridad', 'medio'),
                'coherencia': datos.get('coherencia', 'medio'),
                'seguridad': datos.get('seguridad', 'medio'),
                'pertinencia': datos.get('pertinencia', 'medio'),
                'nivel_preparacion': datos.get('nivel_preparacion', 'medio'),
                'fortalezas': datos.get('fortalezas', []),
                'puntos_mejora': datos.get('puntos_mejora', []),
                'recomendaciones': datos.get('recomendaciones', []),
                'accion_sugerida': datos.get('accion_sugerida', ''),
                'resumen_ejecutivo': datos.get('resumen_ejecutivo', ''),
                'analisis_raw': datos.get('analisis_raw', {}),
            }
        )
        return recomendacion
    
    @staticmethod
    def publicar(recomendacion: Recomendacion) -> None:
        """Publica una recomendación para el cliente."""
        recomendacion.publicada = True
        recomendacion.fecha_publicacion = timezone.now()
        recomendacion.save()


class PracticaService:
    """Servicio para gestión de prácticas individuales."""
    
    # Preguntas de práctica por tipo de visa
    PREGUNTAS = {
        'estudio': [
            {'pregunta': '¿Cuál es el propósito principal de su viaje?', 
             'respuesta_correcta': 'Estudiar en una institución educativa acreditada'},
            {'pregunta': '¿Tiene vínculos familiares en su país de origen?',
             'respuesta_correcta': 'Sí, tengo familia cercana y propiedades'},
            {'pregunta': '¿Cómo financiará sus estudios?',
             'respuesta_correcta': 'Mediante beca/recursos propios/patrocinador'},
            {'pregunta': '¿Planea trabajar durante sus estudios?',
             'respuesta_correcta': 'Solo trabajos permitidos por la visa de estudiante'},
            {'pregunta': '¿Qué hará después de terminar sus estudios?',
             'respuesta_correcta': 'Regresaré a mi país para aplicar mis conocimientos'},
        ],
        'trabajo': [
            {'pregunta': '¿Por qué la empresa eligió contratarlo a usted?',
             'respuesta_correcta': 'Por mis habilidades y experiencia específica'},
            {'pregunta': '¿Cuál es su especialización profesional?',
             'respuesta_correcta': 'Describir área de expertise específica'},
            {'pregunta': '¿Cuánto tiempo planea trabajar en el país?',
             'respuesta_correcta': 'El tiempo especificado en el contrato'},
            {'pregunta': '¿Tiene familia que viajará con usted?',
             'respuesta_correcta': 'Respuesta clara sobre situación familiar'},
            {'pregunta': '¿Cuáles son sus planes a largo plazo?',
             'respuesta_correcta': 'Desarrollarme profesionalmente y contribuir'},
        ],
        'vivienda': [
            {'pregunta': '¿Por qué desea residir en este país?',
             'respuesta_correcta': 'Por calidad de vida/reunificación familiar/inversión'},
            {'pregunta': '¿Cuáles son sus fuentes de ingreso?',
             'respuesta_correcta': 'Demostrar solvencia económica clara'},
            {'pregunta': '¿Dónde planea vivir exactamente?',
             'respuesta_correcta': 'Tener dirección o plan de vivienda definido'},
            {'pregunta': '¿Tiene propiedades en su país de origen?',
             'respuesta_correcta': 'Describir bienes y vínculos'},
            {'pregunta': '¿Cómo planea integrarse a la comunidad?',
             'respuesta_correcta': 'Planes concretos de integración'},
        ],
    }
    
    @staticmethod
    def obtener_tipos_visa() -> list:
        """Obtiene los tipos de visa disponibles para práctica."""
        return [
            {'id': 'estudio', 'nombre': 'Visa de Estudio', 'preguntas': 5},
            {'id': 'trabajo', 'nombre': 'Visa de Trabajo', 'preguntas': 5},
            {'id': 'vivienda', 'nombre': 'Visa de Vivienda', 'preguntas': 5},
        ]
    
    @staticmethod
    def iniciar_practica(usuario, tipo_visa: str) -> tuple[Practica | None, list | None, str | None]:
        """Inicia una nueva sesión de práctica."""
        preguntas = PracticaService.PREGUNTAS.get(tipo_visa)
        
        if not preguntas:
            return None, None, 'Tipo de visa no válido'
        
        practica = Practica.objects.create(
            cliente=usuario,
            tipo_visa=tipo_visa,
            total_preguntas=len(preguntas)
        )
        
        return practica, preguntas, None
    
    @staticmethod
    def finalizar_practica(practica: Practica, respuestas: list) -> tuple[bool, str | None]:
        """Finaliza una práctica y calcula el resultado."""
        if practica.completado:
            return False, 'La práctica ya fue completada'
        
        preguntas = PracticaService.PREGUNTAS.get(practica.tipo_visa, [])
        correctas = 0
        
        for i, respuesta in enumerate(respuestas):
            if i < len(preguntas):
                # Simplificación: comparar si contiene palabras clave
                es_correcta = respuesta.get('es_correcta', False)
                if es_correcta:
                    correctas += 1
        
        practica.respuestas = respuestas
        practica.respuestas_correctas = correctas
        practica.completado = True
        practica.fecha_completado = timezone.now()
        practica.calcular_resultado()
        
        return True, None
    
    @staticmethod
    def obtener_historial(usuario, limite: int = 10):
        """Obtiene el historial de prácticas del usuario."""
        return Practica.objects.filter(
            cliente=usuario,
            completado=True
        ).order_by('-fecha_completado')[:limite]
    
    @staticmethod
    def obtener_estadisticas(usuario) -> dict:
        """Obtiene estadísticas de práctica del usuario."""
        practicas = Practica.objects.filter(cliente=usuario, completado=True)
        
        total = practicas.count()
        if total == 0:
            return {
                'total_practicas': 0,
                'promedio_porcentaje': 0,
                'mejor_tipo_visa': None,
                'practicas_por_tipo': {}
            }
        
        stats = practicas.aggregate(
            promedio=Avg('porcentaje')
        )
        
        # Estadísticas por tipo de visa
        por_tipo = {}
        for tipo in ['estudio', 'trabajo', 'vivienda']:
            tipo_practicas = practicas.filter(tipo_visa=tipo)
            if tipo_practicas.exists():
                tipo_stats = tipo_practicas.aggregate(
                    promedio=Avg('porcentaje'),
                    total=Count('id')
                )
                por_tipo[tipo] = {
                    'total': tipo_stats['total'],
                    'promedio': round(tipo_stats['promedio'] or 0)
                }
        
        # Mejor tipo de visa
        mejor_tipo = max(por_tipo.items(), key=lambda x: x[1].get('promedio', 0))[0] if por_tipo else None
        
        return {
            'total_practicas': total,
            'promedio_porcentaje': round(stats['promedio'] or 0),
            'mejor_tipo_visa': mejor_tipo,
            'practicas_por_tipo': por_tipo
        }


class ConfiguracionIAService:
    """Servicio para gestión de configuración de IA."""
    
    @staticmethod
    def obtener_configuracion(asesor) -> ConfiguracionIA | None:
        """Obtiene la configuración de IA del asesor."""
        try:
            return ConfiguracionIA.objects.get(asesor=asesor)
        except ConfiguracionIA.DoesNotExist:
            return None
    
    @staticmethod
    def crear_o_actualizar(asesor, api_key: str, modelo: str = 'gemini-2.5-flash') -> ConfiguracionIA:
        """Crea o actualiza la configuración de IA."""
        config, created = ConfiguracionIA.objects.update_or_create(
            asesor=asesor,
            defaults={
                'api_key': api_key,
                'modelo': modelo,
                'activo': True
            }
        )
        return config
    
    @staticmethod
    def validar_api_key(api_key: str, modelo: str = 'gemini-2.5-flash') -> tuple[bool, str | None]:
        """Valida una API key de Gemini."""
        import requests
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
        
        try:
            response = requests.post(
                f"{url}?key={api_key}",
                json={"contents": [{"parts": [{"text": "test"}]}]},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, None
            elif response.status_code == 400:
                return True, None  # API key válida, solo error en el request
            else:
                return False, f'Error: {response.status_code}'
        except Exception as e:
            return False, str(e)

