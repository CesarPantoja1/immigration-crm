"""
Vistas para la característica de Agendamiento de Entrevistas.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime, date, time

from ..application.use_cases import (
    ProcesarAprobacionEmbajadaUseCase,
    SeleccionarOpcionHorarioUseCase,
    ReprogramarEntrevistaUseCase,
    CancelarEntrevistaUseCase,
    ConfirmarAsistenciaUseCase,
    ConsultarEntrevistaUseCase,
    ListarEntrevistasUseCase,
    AsignarFechaFijaDTO,
    OfrecerOpcionesDTO,
    SeleccionarOpcionDTO,
    ReprogramarEntrevistaDTO,
    CancelarEntrevistaDTO,
)
from ..infrastructure.repositories import DjangoEntrevistaRepository


# Repositorio compartido
entrevista_repo = DjangoEntrevistaRepository()


def parse_date(date_str: str) -> date:
    """Convierte string a date."""
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def parse_time(time_str: str) -> time:
    """Convierte string a time."""
    return datetime.strptime(time_str, '%H:%M').time()


@csrf_exempt
@require_http_methods(["POST"])
def asignar_fecha_fija(request):
    """
    Endpoint para que el asesor/embajada asigne una fecha fija a una entrevista.
    POST /api/agendamiento/asignar-fecha-fija/
    Body: {
        "solicitud_id": "SOL-001",
        "embajada": "Estados Unidos",
        "fecha": "2026-02-15",
        "hora": "10:00",
        "ubicacion": "Embajada de EE.UU. - Ciudad de México"
    }
    """
    try:
        data = json.loads(request.body)

        dto = AsignarFechaFijaDTO(
            solicitud_id=data['solicitud_id'],
            embajada=data['embajada'],
            fecha=parse_date(data['fecha']),
            hora=parse_time(data['hora']),
            ubicacion=data.get('ubicacion', '')
        )

        use_case = ProcesarAprobacionEmbajadaUseCase(
            entrevista_repo=entrevista_repo,
            respuesta_repo=None,  # Simplificado para demo
            gestor_repo=None  # Simplificado para demo
        )
        resultado = use_case.ejecutar_con_fecha_fija(dto)

        return JsonResponse({
            'success': True,
            'data': {
                'id': resultado.id,
                'codigo': resultado.codigo,
                'solicitud_id': resultado.solicitud_id,
                'embajada': resultado.embajada,
                'estado': resultado.estado,
                'fecha': resultado.fecha,
                'hora': resultado.hora,
                'ubicacion': resultado.ubicacion,
                'mensaje': resultado.mensaje
            }
        })
    except KeyError as e:
        return JsonResponse({'success': False, 'error': f'Campo requerido: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ofrecer_opciones(request):
    """
    Endpoint para que la embajada ofrezca opciones de horario.
    POST /api/agendamiento/ofrecer-opciones/
    Body: {
        "solicitud_id": "SOL-001",
        "embajada": "Estados Unidos",
        "opciones": [
            {"id": "opt1", "fecha": "2026-02-15", "hora": "10:00"},
            {"id": "opt2", "fecha": "2026-02-16", "hora": "14:00"}
        ]
    }
    """
    try:
        data = json.loads(request.body)

        # Convertir fechas y horas en las opciones
        opciones_convertidas = []
        for opt in data['opciones']:
            opciones_convertidas.append({
                'id': opt.get('id', f'opt-{len(opciones_convertidas)+1}'),
                'fecha': parse_date(opt['fecha']),
                'hora': parse_time(opt['hora']),
                'disponible': opt.get('disponible', True)
            })

        dto = OfrecerOpcionesDTO(
            solicitud_id=data['solicitud_id'],
            embajada=data['embajada'],
            opciones=opciones_convertidas
        )

        use_case = ProcesarAprobacionEmbajadaUseCase(
            entrevista_repo=entrevista_repo,
            respuesta_repo=None,
            gestor_repo=None
        )
        resultado = use_case.ejecutar_con_opciones(dto)

        return JsonResponse({
            'success': True,
            'data': {
                'id': resultado.id,
                'codigo': resultado.codigo,
                'estado': resultado.estado,
                'opciones_horario': resultado.opciones_horario,
                'mensaje': resultado.mensaje
            }
        })
    except KeyError as e:
        return JsonResponse({'success': False, 'error': f'Campo requerido: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def seleccionar_opcion(request, entrevista_id):
    """
    Endpoint para que el migrante seleccione una opción de horario.
    POST /api/agendamiento/<entrevista_id>/seleccionar-opcion/
    Body: {"opcion_id": "opt1"}
    """
    try:
        data = json.loads(request.body)

        dto = SeleccionarOpcionDTO(
            entrevista_id=entrevista_id,
            opcion_id=data['opcion_id']
        )

        use_case = SeleccionarOpcionHorarioUseCase(entrevista_repo)
        resultado = use_case.ejecutar(dto)

        return JsonResponse({
            'success': True,
            'data': {
                'id': resultado.id,
                'estado': resultado.estado,
                'fecha': resultado.fecha,
                'hora': resultado.hora,
                'mensaje': resultado.mensaje
            }
        })
    except KeyError as e:
        return JsonResponse({'success': False, 'error': f'Campo requerido: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reprogramar_entrevista(request, entrevista_id):
    """
    Endpoint para reprogramar una entrevista.
    POST /api/agendamiento/<entrevista_id>/reprogramar/
    Body: {"fecha": "2026-03-15", "hora": "11:00"}
    """
    try:
        data = json.loads(request.body)

        dto = ReprogramarEntrevistaDTO(
            entrevista_id=entrevista_id,
            nueva_fecha=parse_date(data['fecha']),
            nueva_hora=parse_time(data['hora'])
        )

        use_case = ReprogramarEntrevistaUseCase(entrevista_repo)
        resultado = use_case.ejecutar(dto)

        return JsonResponse({
            'success': True,
            'data': {
                'id': resultado.id,
                'fecha': resultado.fecha,
                'hora': resultado.hora,
                'veces_reprogramada': resultado.veces_reprogramada,
                'mensaje': resultado.mensaje
            }
        })
    except KeyError as e:
        return JsonResponse({'success': False, 'error': f'Campo requerido: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def cancelar_entrevista(request, entrevista_id):
    """
    Endpoint para cancelar una entrevista.
    POST /api/agendamiento/<entrevista_id>/cancelar/
    Body: {"motivo": "SOLICITUD_MIGRANTE", "detalle": "Viaje cancelado"}
    """
    try:
        data = json.loads(request.body)

        dto = CancelarEntrevistaDTO(
            entrevista_id=entrevista_id,
            motivo=data['motivo'],
            detalle=data.get('detalle', '')
        )

        use_case = CancelarEntrevistaUseCase(entrevista_repo)
        resultado = use_case.ejecutar(dto)

        return JsonResponse({
            'success': True,
            'data': {
                'id': resultado.id,
                'estado': resultado.estado,
                'mensaje': resultado.mensaje
            }
        })
    except KeyError as e:
        return JsonResponse({'success': False, 'error': f'Campo requerido: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def confirmar_asistencia(request, entrevista_id):
    """
    Endpoint para confirmar asistencia a una entrevista.
    POST /api/agendamiento/<entrevista_id>/confirmar/
    """
    try:
        use_case = ConfirmarAsistenciaUseCase(entrevista_repo)
        resultado = use_case.ejecutar(entrevista_id)

        return JsonResponse({
            'success': True,
            'data': {
                'id': resultado.id,
                'estado': resultado.estado,
                'mensaje': resultado.mensaje
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def consultar_entrevista(request, entrevista_id):
    """
    Endpoint para consultar información de una entrevista.
    GET /api/agendamiento/<entrevista_id>/
    """
    try:
        use_case = ConsultarEntrevistaUseCase(entrevista_repo)
        resultado = use_case.ejecutar_por_id(entrevista_id)

        if not resultado:
            return JsonResponse({'success': False, 'error': 'Entrevista no encontrada'}, status=404)

        return JsonResponse({
            'success': True,
            'data': {
                'id': resultado.id,
                'codigo': resultado.codigo,
                'solicitud_id': resultado.solicitud_id,
                'embajada': resultado.embajada,
                'estado': resultado.estado,
                'modo_asignacion': resultado.modo_asignacion,
                'fecha': resultado.fecha,
                'hora': resultado.hora,
                'ubicacion': resultado.ubicacion,
                'veces_reprogramada': resultado.veces_reprogramada,
                'opciones_horario': resultado.opciones_horario,
                'puede_reprogramar': resultado.puede_reprogramar,
                'puede_cancelar': resultado.puede_cancelar
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def consultar_por_solicitud(request, solicitud_id):
    """
    Endpoint para consultar entrevista por ID de solicitud.
    GET /api/agendamiento/solicitud/<solicitud_id>/
    """
    try:
        use_case = ConsultarEntrevistaUseCase(entrevista_repo)
        resultado = use_case.ejecutar_por_solicitud(solicitud_id)

        if not resultado:
            return JsonResponse({'success': False, 'error': 'No se encontró entrevista para esta solicitud'}, status=404)

        return JsonResponse({
            'success': True,
            'data': {
                'id': resultado.id,
                'codigo': resultado.codigo,
                'solicitud_id': resultado.solicitud_id,
                'embajada': resultado.embajada,
                'estado': resultado.estado,
                'fecha': resultado.fecha,
                'hora': resultado.hora,
                'ubicacion': resultado.ubicacion
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def listar_entrevistas(request):
    """
    Endpoint para listar entrevistas con filtros.
    GET /api/agendamiento/listar/?tipo=pendientes|proximas
    """
    try:
        tipo = request.GET.get('tipo', 'proximas')
        use_case = ListarEntrevistasUseCase(entrevista_repo)

        if tipo == 'pendientes':
            resultados = use_case.listar_pendientes()
        elif tipo == 'proximas':
            dias = int(request.GET.get('dias', 7))
            resultados = use_case.listar_proximas(dias)
        else:
            return JsonResponse({'success': False, 'error': 'Tipo de listado no válido'}, status=400)

        return JsonResponse({
            'success': True,
            'data': [
                {
                    'id': r.id,
                    'codigo': r.codigo,
                    'solicitud_id': r.solicitud_id,
                    'embajada': r.embajada,
                    'estado': r.estado,
                    'fecha': r.fecha,
                    'hora': r.hora,
                    'ubicacion': r.ubicacion,
                    'veces_reprogramada': r.veces_reprogramada
                }
                for r in resultados
            ]
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

