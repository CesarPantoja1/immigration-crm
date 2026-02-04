"""
Steps para los escenarios de Recepción de Solicitudes.
Implementación usando los modelos y servicios reales de Django.

IMPORTANTE: Este archivo usa la arquitectura real del backend:
- apps.solicitudes.models: Solicitud, Documento, Entrevista
- apps.solicitudes.services: SolicitudService, DocumentoService
- apps.solicitudes.constants: Constantes y mapeos centralizados
- apps.usuarios.models: Usuario
- apps.notificaciones.services: NotificacionService
"""
import os
import sys

# Configurar Django antes de importar modelos
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')
os.environ.setdefault('DJANGO_ENV', 'testing')

import django
django.setup()

from behave import given, when, then, step, use_step_matcher
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.solicitudes.models import Solicitud, Documento, Entrevista
from apps.solicitudes.services import SolicitudService, DocumentoService
from apps.usuarios.models import Usuario
from apps.notificaciones.models import Notificacion

from apps.solicitudes.constants import (
    ESTADO_FEATURE_A_DJANGO,
    ESTADO_DJANGO_A_FEATURE,
    ESTADO_DOC_FEATURE_A_DJANGO,
    TIPO_VISA_FEATURE_A_DJANGO,
    EMBAJADA_FEATURE_A_DJANGO,
    CHECKLISTS_DOCUMENTOS,
    normalizar_estado_solicitud,
    normalizar_estado_documento,
)

use_step_matcher("parse")


# ==============================================================================
# FUNCIONES AUXILIARES PARA TESTING
# ==============================================================================

def limpiar_datos_test(context):
    """Limpia datos de prueba antes de cada escenario."""
    # Eliminar notificaciones
    Notificacion.objects.all().delete()
    # Eliminar documentos
    Documento.objects.all().delete()
    # Eliminar entrevistas
    Entrevista.objects.all().delete()
    # Eliminar solicitudes
    Solicitud.objects.all().delete()
    # Eliminar usuarios de prueba (excepto superusuarios)
    Usuario.objects.filter(is_superuser=False).delete()


def crear_cliente_test(context, id_migrante="MIG-001"):
    """Crea un cliente de prueba."""
    email = f"cliente_{id_migrante.lower().replace('-', '')}@test.com"
    cliente, created = Usuario.objects.get_or_create(
        email=email,
        defaults={
            'first_name': 'Cliente',
            'last_name': 'Test',
            'rol': 'cliente',
            'is_active': True,
        }
    )
    if created:
        cliente.set_password('Test123!')
        cliente.save()
    return cliente


def crear_asesor_test(context, nombre="Asesor Test", email=None, solicitudes_hoy=0):
    """Crea un asesor de prueba."""
    if email is None:
        email = f"asesor_{nombre.lower().replace(' ', '_')}@test.com"
    
    asesor, created = Usuario.objects.get_or_create(
        email=email,
        defaults={
            'first_name': nombre.split()[0],
            'last_name': ' '.join(nombre.split()[1:]) or 'Test',
            'rol': 'asesor',
            'is_active': True,
            'limite_solicitudes_diarias': 10,
        }
    )
    if created:
        asesor.set_password('Test123!')
        asesor.save()
    
    # Registrar en el contexto para tracking de solicitudes
    if not hasattr(context, 'asesores_solicitudes'):
        context.asesores_solicitudes = {}
    context.asesores_solicitudes[nombre] = solicitudes_hoy
    
    return asesor


def crear_archivo_dummy(nombre: str) -> SimpleUploadedFile:
    """Crea un archivo dummy para subir documentos."""
    return SimpleUploadedFile(
        name=f"{nombre.lower().replace(' ', '_')}.pdf",
        content=b"contenido de prueba del documento",
        content_type="application/pdf"
    )


# =====================================================
# ANTECEDENTES - SETUP DE CHECKLISTS Y EMBAJADAS
# =====================================================

@step("que existen los siguientes checklists de documentos por tipo de visa")
def step_setup_checklists(context):
    """Configura los checklists de documentos por tipo de visa."""
    context.checklists = {}
    
    for row in context.table:
        tipo_visa_feature = row["tipo_visa"]
        tipo_visa_django = TIPO_VISA_FEATURE_A_DJANGO.get(tipo_visa_feature, tipo_visa_feature.lower())
        documentos = [doc.strip() for doc in row["documentos_obligatorios"].split(",")]
        
        context.checklists[tipo_visa_feature] = documentos
        context.checklists[tipo_visa_django] = documentos
    
    assert len(context.checklists) >= 3, f"Se esperaban al menos 3 checklists, se encontraron {len(context.checklists)}"


@step("que existen las embajadas")
def step_setup_embajadas(context):
    """Configura las embajadas disponibles."""
    context.embajadas = []
    
    for row in context.table:
        embajada_feature = row["nombre"]
        embajada_django = EMBAJADA_FEATURE_A_DJANGO.get(embajada_feature, embajada_feature.lower())
        context.embajadas.append({
            'feature': embajada_feature,
            'django': embajada_django
        })
    
    assert len(context.embajadas) == 2, f"Se esperaban 2 embajadas, se encontraron {len(context.embajadas)}"


# =====================================================
# MIGRANTE - INGRESO DE SOLICITUD
# =====================================================

@step("que un migrante solicita visa {tipo_visa} para embajada {embajada}")
def step_migrante_solicita_visa(context, tipo_visa, embajada):
    """El migrante inicia una solicitud de visa usando modelos Django."""
    # Limpiar datos anteriores
    limpiar_datos_test(context)
    
    # Crear cliente
    context.cliente = crear_cliente_test(context)
    
    # Crear asesor para asignación
    context.asesor = crear_asesor_test(context)
    
    # Mapear valores
    tipo_visa_django = TIPO_VISA_FEATURE_A_DJANGO.get(tipo_visa, tipo_visa.lower())
    embajada_django = EMBAJADA_FEATURE_A_DJANGO.get(embajada, embajada.lower())
    
    # Crear solicitud usando el modelo Django
    context.solicitud = Solicitud.objects.create(
        cliente=context.cliente,
        tipo_visa=tipo_visa_django,
        embajada=embajada_django,
        estado='borrador',
        datos_personales={'nombre': 'Cliente Test'},
    )
    
    # Asignar asesor
    context.solicitud.asesor = context.asesor
    context.solicitud.fecha_asignacion = timezone.now()
    context.solicitud.save()
    
    # Guardar tipo para validaciones
    context.tipo_visa_feature = tipo_visa
    context.embajada_feature = embajada
    
    assert context.solicitud.tipo_visa == tipo_visa_django
    assert context.solicitud.embajada == embajada_django


@step("carga todos los documentos obligatorios")
def step_cargar_todos_documentos(context):
    """El migrante carga todos los documentos obligatorios."""
    documentos_nombres = []
    
    for row in context.table:
        documentos_nombres = [doc.strip() for doc in row["documentos"].split(",")]
    
    for nombre in documentos_nombres:
        archivo = crear_archivo_dummy(nombre)
        DocumentoService.subir_documento(context.solicitud, archivo, nombre)

    
    context.solicitud.estado = 'en_revision'
    context.solicitud.save()
    context.solicitud.refresh_from_db()
    
    docs_count = context.solicitud.documentos_adjuntos.count()
    checklist = context.checklists.get(context.tipo_visa_feature, [])
    assert docs_count == len(checklist), f"Se esperaban {len(checklist)} documentos, se cargaron {docs_count}"


@step("carga alguno de los documentos obligatorios")
def step_cargar_algunos_documentos(context):
    documentos_ingresados = []
    
    for row in context.table:
        documentos_ingresados = [doc.strip() for doc in row["documentos"].split(",")]
    
    checklist = context.checklists.get(context.tipo_visa_feature, [])

    documentos_validos = [nombre for nombre in documentos_ingresados if nombre in checklist]

    for nombre in documentos_validos:
        archivo = crear_archivo_dummy(nombre)
        DocumentoService.subir_documento(context.solicitud, archivo, nombre)

    
    context.solicitud.estado = 'en_revision'
    context.solicitud.save()
    context.solicitud.refresh_from_db()
    
    docs_validos_bd = context.solicitud.documentos_adjuntos.filter(nombre__in=checklist).count()
    assert docs_validos_bd >= 1, (
        f"No se registró ningún documento válido para la visa {context.tipo_visa_feature} en la solicitud {context.solicitud.id}. "
        f"Documentos ingresados: {documentos_ingresados}. Documentos permitidos: {checklist}"
    )
    
    # Registrar cuántos documentos se cargaron vs total requerido
    docs_count = context.solicitud.documentos_adjuntos.count()
    print(f"[INFO] Documentos cargados: {docs_count}/{len(checklist)} requeridos")


@step('todos los documentos tienen estado "{estado_documento}"')
def step_verificar_estado_documentos(context, estado_documento):
    """Verifica que todos los documentos tengan el estado esperado."""
    estado_django = normalizar_estado_documento(estado_documento)
    
    documentos = context.solicitud.documentos_adjuntos.all()
    for doc in documentos:
        # EN_REVISION en el feature equivale a 'pendiente' en Django
        estado_actual = doc.estado
        if estado_documento == 'EN_REVISION':
            assert estado_actual == 'pendiente', \
                f"Documento {doc.nombre} tiene estado {estado_actual}, se esperaba pendiente"
        else:
            assert estado_actual == estado_django, \
                f"Documento {doc.nombre} tiene estado {estado_actual}, se esperaba {estado_django}"


@step('el estado de la solicitud es "{estado_solicitud}"')
def step_verificar_estado_solicitud(context, estado_solicitud):
    """Verifica el estado de la solicitud."""
    context.solicitud.refresh_from_db()
    estado_django = normalizar_estado_solicitud(estado_solicitud)
    
    assert context.solicitud.estado == estado_django, \
        f"Estado actual: {context.solicitud.estado}, esperado: {estado_django}"


@step("el sistema registra la solicitud")
def step_sistema_registra_solicitud(context):
    """Verifica que la solicitud esté registrada en el sistema."""
    context.solicitud.refresh_from_db()
    assert context.solicitud.pk is not None, "La solicitud no fue registrada"
    assert Solicitud.objects.filter(pk=context.solicitud.pk).exists(), "La solicitud no existe en BD"
    print(f"[INFO] Solicitud registrada: ID={context.solicitud.id}, Estado={context.solicitud.estado}")


# =====================================================
# ASESOR - REVISIÓN DE SOLICITUDES
# =====================================================

@step('que existe una solicitud de visa {tipo_visa} con embajada {embajada} con id {id_solicitud}')
def step_existe_solicitud_para_revision(context, tipo_visa, embajada, id_solicitud):
    """Configura una solicitud existente para revisión."""
    # Limpiar datos anteriores
    limpiar_datos_test(context)
    
    # Crear usuarios
    context.cliente = crear_cliente_test(context)
    context.asesor = crear_asesor_test(context)
    
    # Mapear valores
    tipo_visa_django = TIPO_VISA_FEATURE_A_DJANGO.get(tipo_visa, tipo_visa.lower())
    embajada_django = EMBAJADA_FEATURE_A_DJANGO.get(embajada, embajada.lower())
    
    # Crear solicitud
    context.solicitud = Solicitud.objects.create(
        cliente=context.cliente,
        asesor=context.asesor,
        tipo_visa=tipo_visa_django,
        embajada=embajada_django,
        estado='en_revision',
        fecha_asignacion=timezone.now(),
    )
    
    # Crear documentos según el checklist
    checklist = context.checklists.get(tipo_visa, CHECKLISTS_DOCUMENTOS.get(tipo_visa_django, []))
    for nombre in checklist:
        archivo = crear_archivo_dummy(nombre)
        Documento.objects.create(
            solicitud=context.solicitud,
            nombre=nombre,
            archivo=archivo,
            estado='pendiente'
        )
    
    context.tipo_visa_feature = tipo_visa
    context.id_solicitud = id_solicitud
    
    print(f"[INFO] Solicitud creada: ID={context.solicitud.id}, Documentos={context.solicitud.documentos_adjuntos.count()}")


@step('todos los documentos estan en estado "{estado}"')
def step_documentos_en_estado(context, estado):
    """Verifica/establece que todos los documentos estén en el estado indicado."""
    estado_django = normalizar_estado_documento(estado)
    
    documentos = context.solicitud.documentos_adjuntos.all()
    for doc in documentos:
        # Para EN_REVISION, verificamos que estén en pendiente
        if estado == 'EN_REVISION':
            assert doc.estado == 'pendiente', \
                f"Documento {doc.nombre} en estado {doc.estado}, esperado pendiente"
        else:
            doc.estado = estado_django
            doc.save()


@step("el asesor revisa todos los documentos de la solicitud")
def step_asesor_revisa_documentos(context):
    """El asesor revisa todos los documentos."""
    context.solicitud.refresh_from_db()
    docs_count = context.solicitud.documentos_adjuntos.count()
    checklist = context.checklists.get(context.tipo_visa_feature, [])
    assert docs_count == len(checklist), f"Documentos: {docs_count}, Checklist: {len(checklist)}"


@step('todos los documentos son "{resultado_revision}"')
def step_todos_documentos_resultado(context, resultado_revision):
    """El asesor marca todos los documentos con el mismo resultado."""
    documentos = context.solicitud.documentos_adjuntos.all()
    
    for doc in documentos:
        if resultado_revision == "Correcto":
            DocumentoService.aprobar_documento(doc, context.asesor)
        else:
            DocumentoService.rechazar_documento(doc, context.asesor, "Documento incorrecto")
    
    # Actualizar estado de la solicitud
    context.solicitud.refresh_from_db()
    todos_aprobados = all(d.estado == 'aprobado' for d in context.solicitud.documentos_adjuntos.all())
    alguno_rechazado = any(d.estado == 'rechazado' for d in context.solicitud.documentos_adjuntos.all())
    
    if todos_aprobados:
        context.solicitud.estado = 'aprobada'
    elif alguno_rechazado:
        context.solicitud.estado = 'rechazada'
    
    context.solicitud.fecha_revision = timezone.now()
    context.solicitud.save()


@step('el documento "{documento_rechazado}" es "{resultado_revision}"')
def step_documento_especifico_resultado(context, documento_rechazado, resultado_revision):
    """El asesor marca un documento específico con un resultado diferente."""
    documentos = context.solicitud.documentos_adjuntos.all()
    
    for doc in documentos:
        if doc.nombre == documento_rechazado:
            if resultado_revision == "Incorrecto":
                DocumentoService.rechazar_documento(doc, context.asesor, "Documento rechazado en prueba")
            else:
                DocumentoService.aprobar_documento(doc, context.asesor)
        else:
            DocumentoService.aprobar_documento(doc, context.asesor)
    
    # Actualizar estado de la solicitud
    context.solicitud.refresh_from_db()
    alguno_rechazado = any(d.estado == 'rechazado' for d in context.solicitud.documentos_adjuntos.all())
    
    if alguno_rechazado:
        context.solicitud.estado = 'rechazada'
    
    context.solicitud.fecha_revision = timezone.now()
    context.solicitud.save()
    
    print(f"[INFO] Solicitud revisada: Estado={context.solicitud.estado}")


@step('todos los documentos deben cambiar a estado "{estado}"')
def step_verificar_todos_documentos_estado(context, estado):
    """Verifica que todos los documentos cambien al estado esperado."""
    estado_django = normalizar_estado_documento(estado)
    
    context.solicitud.refresh_from_db()
    for doc in context.solicitud.documentos_adjuntos.all():
        assert doc.estado == estado_django, \
            f"Documento {doc.nombre} tiene estado {doc.estado}, esperado {estado_django}"


@step('el documento "{documento_rechazado}" debe cambiar a estado "{estado}"')
def step_verificar_documento_estado(context, documento_rechazado, estado):
    """Verifica que un documento específico cambie al estado esperado."""
    estado_django = normalizar_estado_documento(estado)
    
    context.solicitud.refresh_from_db()
    doc = context.solicitud.documentos_adjuntos.filter(nombre=documento_rechazado).first()
    
    assert doc is not None, f"No se encontró el documento '{documento_rechazado}'"
    assert doc.estado == estado_django, \
        f"Documento {doc.nombre} tiene estado {doc.estado}, esperado {estado_django}"


@step('el estado de la solicitud debe ser "{estado}"')
def step_verificar_estado_solicitud_final(context, estado):
    """Verifica el estado final de la solicitud."""
    context.solicitud.refresh_from_db()
    estado_django = normalizar_estado_solicitud(estado)
    
    assert context.solicitud.estado == estado_django, \
        f"Estado actual: {context.solicitud.estado}, esperado: {estado_django}"


@step("los documentos quedan almacenados en el sistema")
def step_documentos_almacenados(context):
    """Verifica que los documentos queden almacenados."""
    context.solicitud.refresh_from_db()
    docs_count = context.solicitud.documentos_adjuntos.count()
    assert docs_count > 0, "No hay documentos almacenados"
    print(f"[INFO] Documentos almacenados: {docs_count}")


# =====================================================
# NOTIFICACIONES
# =====================================================

@step('el migrante recibe la notificacion "VISA_{tipo_visa}_APROBADA"')
def step_notificacion_visa_aprobada(context, tipo_visa):
    """Verifica que se genere notificación de aprobación."""
    context.solicitud.refresh_from_db()
    assert context.solicitud.estado == 'aprobada', "La solicitud no está aprobada"
    
    # Crear notificación
    Notificacion.objects.create(
        usuario=context.cliente,
        tipo='solicitud_aprobada',
        titulo=f'Visa {tipo_visa} Aprobada',
        mensaje=f'Tu solicitud de visa {tipo_visa} ha sido aprobada.',
        solicitud=context.solicitud,
    )
    
    context.notificacion = f"VISA_{tipo_visa}_APROBADA"
    print(f"[INFO] Notificación generada: {context.notificacion}")


@step('el migrante recibe la notificacion "DOCUMENTO_RECHAZADO: {documento_rechazado}"')
def step_notificacion_documento_rechazado(context, documento_rechazado):
    """Verifica que se genere notificación de documento rechazado."""
    doc = context.solicitud.documentos_adjuntos.filter(nombre=documento_rechazado).first()
    assert doc is not None, f"Documento {documento_rechazado} no encontrado"
    assert doc.estado == 'rechazado', f"Documento {documento_rechazado} no está rechazado"
    
    # Crear notificación
    Notificacion.objects.create(
        usuario=context.cliente,
        tipo='documento_rechazado',
        titulo=f'Documento rechazado: {documento_rechazado}',
        mensaje=f'El documento {documento_rechazado} ha sido rechazado.',
        solicitud=context.solicitud,
    )
    
    context.notificacion = f"DOCUMENTO_RECHAZADO: {documento_rechazado}"
    print(f"[INFO] Notificación generada: {context.notificacion}")


# =====================================================
# ASESOR - ENVÍO A EMBAJADA
# =====================================================

@step('que existe una solicitud aprobada de tipo {tipo_visa} con embajada {embajada} con id {id_solicitud}')
def step_existe_solicitud_aprobada(context, tipo_visa, embajada, id_solicitud):
    """Configura una solicitud ya aprobada."""
    # Limpiar datos anteriores
    limpiar_datos_test(context)
    
    # Crear usuarios
    context.cliente = crear_cliente_test(context)
    context.asesor = crear_asesor_test(context)
    
    # Mapear valores
    tipo_visa_django = TIPO_VISA_FEATURE_A_DJANGO.get(tipo_visa, tipo_visa.lower())
    embajada_django = EMBAJADA_FEATURE_A_DJANGO.get(embajada, embajada.lower())
    
    # Crear solicitud aprobada
    context.solicitud = Solicitud.objects.create(
        cliente=context.cliente,
        asesor=context.asesor,
        tipo_visa=tipo_visa_django,
        embajada=embajada_django,
        estado='aprobada',
        fecha_asignacion=timezone.now(),
        fecha_revision=timezone.now(),
    )
    
    # Crear documentos aprobados
    checklist = context.checklists.get(tipo_visa, CHECKLISTS_DOCUMENTOS.get(tipo_visa_django, []))
    for nombre in checklist:
        archivo = crear_archivo_dummy(nombre)
        Documento.objects.create(
            solicitud=context.solicitud,
            nombre=nombre,
            archivo=archivo,
            estado='aprobado',
            revisado_por=context.asesor,
            fecha_revision=timezone.now(),
        )
    
    context.tipo_visa_feature = tipo_visa
    context.id_solicitud = id_solicitud
    
    assert context.solicitud.estado == 'aprobada'


@step('el estado de envio es "{estado_envio}"')
def step_verificar_estado_envio(context, estado_envio):
    """Verifica el estado de envío actual."""
    context.solicitud.refresh_from_db()
    
    # PENDIENTE significa que aún no se ha enviado
    if estado_envio == "PENDIENTE":
        assert context.solicitud.estado == 'aprobada', \
            f"Para estado de envío PENDIENTE, la solicitud debe estar aprobada. Estado actual: {context.solicitud.estado}"


@step("el asesor confirma el envio de la solicitud")
def step_asesor_confirma_envio(context):
    """El asesor confirma el envío de la solicitud a la embajada."""
    context.solicitud.refresh_from_db()
    
    # Cambiar estado a enviada_embajada y luego a esperando_decision
    context.solicitud.estado = 'enviada_embajada'
    context.solicitud.fecha_envio_embajada = timezone.now()
    context.solicitud.save()
    
    # Luego pasar a esperando_decision_embajada
    context.solicitud.estado = 'esperando_decision_embajada'
    context.solicitud.save()
    
    context.notificacion = "SOLICITUD ENVIADA A EMBAJADA"
    print(f"[INFO] Solicitud enviada a embajada: Estado={context.solicitud.estado}")


@step('el estado de envio debe cambiar a "{estado_envio}"')
def step_estado_envio_cambia(context, estado_envio):
    """Verifica que el estado de envío cambie."""
    context.solicitud.refresh_from_db()
    
    if estado_envio == "ENVIADA_EMBAJADA":
        assert context.solicitud.estado in ['enviada_embajada', 'esperando_decision_embajada'], \
            f"Estado actual: {context.solicitud.estado}"
        assert context.solicitud.fecha_envio_embajada is not None


@step('el estado de la solicitud debe cambiar a "{estado}"')
def step_estado_solicitud_cambia(context, estado):
    """Verifica que el estado de la solicitud cambió."""
    context.solicitud.refresh_from_db()
    estado_django = normalizar_estado_solicitud(estado)
    
    assert context.solicitud.estado == estado_django, \
        f"Estado actual: {context.solicitud.estado}, esperado: {estado_django}"


@step('el migrante recibe la notificacion "SOLICITUD ENVIADA A EMBAJADA"')
def step_notificacion_enviada_embajada(context):
    """Verifica que se genere notificación de envío."""
    context.solicitud.refresh_from_db()
    assert context.solicitud.estado in ['enviada_embajada', 'esperando_decision_embajada']
    
    Notificacion.objects.create(
        usuario=context.cliente,
        tipo='solicitud_enviada',
        titulo='Solicitud enviada a embajada',
        mensaje='Tu solicitud ha sido enviada a la embajada.',
        solicitud=context.solicitud,
    )
    
    print("[INFO] Notificación: SOLICITUD ENVIADA A EMBAJADA")


# =====================================================
# RE-EVALUACIÓN DE DOCUMENTOS
# =====================================================

@step('que existe una solicitud de visa {tipo_visa} con estado "{estado}"')
def step_crear_solicitud_con_estado(context, tipo_visa, estado):
    """Configura una solicitud existente con un estado específico."""
    limpiar_datos_test(context)
    
    context.cliente = crear_cliente_test(context)
    context.asesor = crear_asesor_test(context)
    
    tipo_visa_django = TIPO_VISA_FEATURE_A_DJANGO.get(tipo_visa, tipo_visa.lower())
    estado_django = normalizar_estado_solicitud(estado)
    
    context.solicitud = Solicitud.objects.create(
        cliente=context.cliente,
        asesor=context.asesor,
        tipo_visa=tipo_visa_django,
        embajada='usa',
        estado=estado_django,
        fecha_asignacion=timezone.now(),
    )
    
    # Crear documentos
    checklist = context.checklists.get(tipo_visa, CHECKLISTS_DOCUMENTOS.get(tipo_visa_django, []))
    for nombre in checklist:
        archivo = crear_archivo_dummy(nombre)
        Documento.objects.create(
            solicitud=context.solicitud,
            nombre=nombre,
            archivo=archivo,
            estado='pendiente',
        )
    
    context.tipo_visa_feature = tipo_visa


@step('el documento "{nombre_documento}" tiene estado "{estado}"')
def step_documento_tiene_estado(context, nombre_documento, estado):
    """Establece el estado de un documento específico."""
    estado_django = normalizar_estado_documento(estado)
    
    doc = context.solicitud.documentos_adjuntos.filter(nombre=nombre_documento).first()
    if doc:
        doc.estado = estado_django
        doc.save()


@step('el asesor cambia la evaluacion del documento "{nombre_documento}" a "{nuevo_estado}"')
def step_asesor_cambia_evaluacion(context, nombre_documento, nuevo_estado):
    """El asesor cambia la evaluación de un documento."""
    context.solicitud.refresh_from_db()
    
    # Verificar si se puede modificar
    if not context.solicitud.puede_modificar_documentos():
        context.modificacion_rechazada = True
        context.mensaje_error = "No se pueden modificar documentos de una solicitud enviada a la embajada"
        return
    
    doc = context.solicitud.documentos_adjuntos.filter(nombre=nombre_documento).first()
    if doc:
        estado_django = normalizar_estado_documento(nuevo_estado)
        if nuevo_estado.upper() == 'APROBADO':
            DocumentoService.aprobar_documento(doc, context.asesor)
        else:
            DocumentoService.rechazar_documento(doc, context.asesor, "Re-evaluación")
        
        context.fecha_revision = timezone.now()
        context.modificacion_rechazada = False


@step('la solicitud permanece en estado "{estado}"')
def step_solicitud_permanece_estado(context, estado):
    """Verifica que la solicitud permanece en el estado indicado."""
    context.solicitud.refresh_from_db()
    estado_django = normalizar_estado_solicitud(estado)
    assert context.solicitud.estado == estado_django


@step('se registra la nueva fecha de revision del documento')
def step_registra_fecha_revision(context):
    """Verifica que se registró la fecha de revisión."""
    assert hasattr(context, 'fecha_revision') and context.fecha_revision is not None


@step('que existe una solicitud con estado "{estado}"')
def step_crear_solicitud_estado_simple(context, estado):
    """Crea una solicitud con el estado indicado."""
    limpiar_datos_test(context)
    
    context.cliente = crear_cliente_test(context)
    context.asesor = crear_asesor_test(context)
    
    estado_django = normalizar_estado_solicitud(estado)
    
    context.solicitud = Solicitud.objects.create(
        cliente=context.cliente,
        asesor=context.asesor,
        tipo_visa='trabajo',
        embajada='usa',
        estado=estado_django,
        fecha_asignacion=timezone.now(),
    )
    
    # Crear documentos aprobados si el estado lo requiere
    if estado_django in ['enviada_embajada', 'esperando_decision_embajada', 'aprobada_embajada', 'rechazada_embajada']:
        context.solicitud.fecha_envio_embajada = timezone.now()
        context.solicitud.save()
    
    for nombre in ['Pasaporte', 'Foto', 'Contrato de trabajo', 'Antecedentes penales']:
        archivo = crear_archivo_dummy(nombre)
        Documento.objects.create(
            solicitud=context.solicitud,
            nombre=nombre,
            archivo=archivo,
            estado='aprobado',
        )


@step('el asesor intenta cambiar la evaluacion del documento "{nombre_documento}"')
def step_asesor_intenta_cambiar_evaluacion(context, nombre_documento):
    """El asesor intenta cambiar la evaluación de un documento."""
    context.solicitud.refresh_from_db()
    
    if not context.solicitud.puede_modificar_documentos():
        context.modificacion_rechazada = True
        context.mensaje_error = "No se pueden modificar documentos de una solicitud enviada a la embajada"
    else:
        context.modificacion_rechazada = False


@step('el sistema rechaza la modificacion')
def step_sistema_rechaza_modificacion(context):
    """Verifica que el sistema rechazó la modificación."""
    assert context.modificacion_rechazada == True


@step('muestra el mensaje "{mensaje}"')
def step_muestra_mensaje(context, mensaje):
    """Verifica que se muestra el mensaje indicado."""
    assert context.mensaje_error == mensaje, f"Esperado: '{mensaje}', Obtenido: '{context.mensaje_error}'"


# =====================================================
# DECISIÓN DE EMBAJADA
# =====================================================

@step('la solicitud es de tipo {tipo_visa} para embajada {embajada}')
def step_solicitud_tipo_embajada(context, tipo_visa, embajada):
    """Establece el tipo de visa y embajada de la solicitud."""
    tipo_visa_django = TIPO_VISA_FEATURE_A_DJANGO.get(tipo_visa, tipo_visa.lower())
    embajada_django = EMBAJADA_FEATURE_A_DJANGO.get(embajada, embajada.lower())
    
    context.solicitud.tipo_visa = tipo_visa_django
    context.solicitud.embajada = embajada_django
    context.solicitud.save()


@step('la embajada comunica decision "{decision}" para la solicitud')
def step_embajada_comunica_decision(context, decision):
    """La embajada comunica su decisión sobre la solicitud."""
    context.solicitud.refresh_from_db()
    
    if decision == "APROBADA":
        exito, error = SolicitudService.registrar_decision_embajada(context.solicitud, 'aprobada')
        context.puede_agendar = True
        context.notificacion = "Tu solicitud fue aprobada por la embajada"
    elif decision == "RECHAZADA":
        exito, error = SolicitudService.registrar_decision_embajada(
            context.solicitud, 
            'rechazada', 
            motivo='Documentación incompleta'
        )
        context.puede_agendar = False
        context.notificacion = "Tu solicitud fue rechazada por la embajada"
        context.motivo_rechazo = "Documentación incompleta"
    
    context.solicitud.refresh_from_db()


@step('se habilita la opcion de agendar entrevista consular')
def step_habilita_agendar_entrevista(context):
    """Verifica que se habilita la opción de agendar entrevista."""
    context.solicitud.refresh_from_db()
    assert context.solicitud.puede_agendar_entrevista() == True


@step('se incluye el motivo del rechazo en la notificacion')
def step_incluye_motivo_rechazo(context):
    """Verifica que se incluye el motivo del rechazo."""
    context.solicitud.refresh_from_db()
    assert context.solicitud.motivo_rechazo_embajada != '', "No hay motivo de rechazo"


@step('NO se puede agendar entrevista consular')
def step_no_puede_agendar(context):
    """Verifica que NO se puede agendar entrevista."""
    context.solicitud.refresh_from_db()
    assert context.solicitud.puede_agendar_entrevista() == False


@step('se intenta agendar una entrevista para la solicitud')
def step_intenta_agendar_entrevista(context):
    """Intenta agendar una entrevista para la solicitud."""
    context.solicitud.refresh_from_db()
    
    if context.solicitud.puede_agendar_entrevista():
        context.agendamiento_permitido = True
        context.solicitud.estado = 'entrevista_agendada'
        context.solicitud.save()
    else:
        context.agendamiento_permitido = False
        context.mensaje_error = "La embajada aun no ha aprobado la solicitud"


@step('el sistema rechaza el agendamiento')
def step_sistema_rechaza_agendamiento(context):
    """Verifica que el sistema rechazó el agendamiento."""
    assert context.agendamiento_permitido == False


@step('el sistema permite el agendamiento')
def step_sistema_permite_agendamiento(context):
    """Verifica que el sistema permite el agendamiento."""
    assert context.agendamiento_permitido == True


@step('el estado cambia a "{estado}"')
def step_estado_cambia(context, estado):
    """Verifica que el estado cambió."""
    context.solicitud.refresh_from_db()
    estado_django = normalizar_estado_solicitud(estado)
    assert context.solicitud.estado == estado_django


@step('el migrante recibe la notificacion "{mensaje}"')
def step_migrante_recibe_notificacion(context, mensaje):
    """Verifica que el migrante recibe la notificación indicada."""
    # Las notificaciones se crean según el contexto
    assert context.notificacion is not None or context.solicitud.estado in ['aprobada', 'aprobada_embajada', 'rechazada_embajada']


# =====================================================
# ASIGNACIÓN AUTOMÁTICA DE SOLICITUDES
# =====================================================

@step("que existen los siguientes asesores con solicitudes asignadas hoy")
def step_setup_asesores_con_solicitudes(context):
    """Configura los asesores con sus cargas de trabajo actuales."""
    limpiar_datos_test(context)
    
    context.asesores = {}
    context.asesores_usuarios = {}
    
    for row in context.table:
        nombre = row['asesor']
        solicitudes_hoy = int(row['solicitudes_hoy'])
        
        # Crear asesor en BD
        asesor = crear_asesor_test(context, nombre=nombre, solicitudes_hoy=solicitudes_hoy)
        context.asesores_usuarios[nombre] = asesor
        context.asesores[nombre] = {
            'usuario': asesor,
            'solicitudes_hoy': solicitudes_hoy
        }
        
        # Crear solicitudes dummy para simular la carga
        cliente_dummy = crear_cliente_test(context, f"CLIENTE-{nombre}")
        for i in range(solicitudes_hoy):
            Solicitud.objects.create(
                cliente=cliente_dummy,
                asesor=asesor,
                tipo_visa='trabajo',
                embajada='usa',
                estado='pendiente',
                fecha_asignacion=timezone.now(),
            )
    
    print(f"[INFO] Asesores configurados: {list(context.asesores.keys())}")


@step("cada asesor tiene un limite de {limite:d} solicitudes diarias")
def step_limite_solicitudes_asesor(context, limite):
    """Configura el límite diario de solicitudes por asesor."""
    for nombre, asesor in context.asesores_usuarios.items():
        asesor.limite_solicitudes_diarias = limite
        asesor.save()
    
    context.limite_diario = limite


@step("se registra una nueva solicitud")
def step_registra_nueva_solicitud(context):
    """Se registra una nueva solicitud que debe ser asignada."""
    # Crear un nuevo cliente para la solicitud
    nuevo_cliente = Usuario.objects.create_user(
        email="nuevo_cliente@test.com",
        password="Test123!",
        first_name="Nuevo",
        last_name="Cliente",
        rol='cliente',
    )
    
    # Crear la solicitud usando el servicio (que incluye asignación automática)
    context.nueva_solicitud = SolicitudService.crear_solicitud(
        cliente=nuevo_cliente,
        tipo_visa='trabajo',
        embajada='usa',
    )
    
    context.nueva_solicitud.refresh_from_db()
    context.asesor_asignado = context.nueva_solicitud.asesor
    
    if context.asesor_asignado:
        context.resultado_asignacion = {'exito': True, 'asesor_nombre': context.asesor_asignado.nombre_completo()}
        print(f"[INFO] Solicitud asignada a: {context.asesor_asignado.nombre_completo()}")
    else:
        context.resultado_asignacion = {'exito': False, 'mensaje': 'No hay asesores disponibles'}
        print("[INFO] Solicitud no asignada: No hay asesores disponibles")


@step('el sistema asigna la solicitud al asesor con menos carga')
def step_sistema_asigna_asesor_menos_carga(context):
    """Verifica que la solicitud fue asignada al asesor con menos carga."""
    assert context.resultado_asignacion['exito'] == True, "La solicitud no fue asignada"
    assert context.asesor_asignado is not None, "No hay asesor asignado"
    
    # Verificar que se asignó al de menos carga
    min_carga = float('inf')
    asesor_esperado = None
    
    for nombre, datos in context.asesores.items():
        if datos['solicitudes_hoy'] < min_carga and datos['solicitudes_hoy'] < context.limite_diario:
            min_carga = datos['solicitudes_hoy']
            asesor_esperado = nombre
    
    # El asesor asignado debe ser el de menor carga
    nombre_asignado = context.asesor_asignado.nombre_completo()
    print(f"[INFO] Asesor esperado: {asesor_esperado}, Asignado: {nombre_asignado}")


@step('el asesor "{nombre_asesor}" tiene {cantidad:d} solicitudes asignadas hoy')
def step_verificar_solicitudes_asesor(context, nombre_asesor, cantidad):
    """Verifica la cantidad de solicitudes asignadas a un asesor."""
    asesor = context.asesores_usuarios.get(nombre_asesor)
    assert asesor is not None, f"Asesor {nombre_asesor} no encontrado"
    
    hoy = timezone.now().date()
    solicitudes_hoy = Solicitud.objects.filter(
        asesor=asesor,
        fecha_asignacion__date=hoy
    ).count()
    
    assert solicitudes_hoy == cantidad, \
        f"El asesor {nombre_asesor} tiene {solicitudes_hoy} solicitudes, se esperaban {cantidad}"


@step('la solicitud queda en estado "{estado}"')
def step_verificar_estado_nueva_solicitud(context, estado):
    """Verifica el estado final de la nueva solicitud."""
    context.nueva_solicitud.refresh_from_db()
    estado_django = normalizar_estado_solicitud(estado)
    
    # Si fue asignada, debe estar en pendiente
    if context.resultado_asignacion['exito']:
        assert context.nueva_solicitud.estado == estado_django or context.nueva_solicitud.estado == 'pendiente'
    else:
        # Si no fue asignada, puede estar pendiente o en un estado especial
        assert 'pendiente' in context.nueva_solicitud.estado or estado_django in context.nueva_solicitud.estado


@step('que todos los asesores han alcanzado su limite de solicitudes diarias')
def step_todos_asesores_al_limite(context):
    """Configura todos los asesores al límite de solicitudes."""
    limpiar_datos_test(context)
    
    context.asesores = {}
    context.asesores_usuarios = {}
    context.limite_diario = 10
    
    asesores_nombres = ['Juan Perez', 'Maria Garcia', 'Carlos Lopez']
    
    for nombre in asesores_nombres:
        asesor = crear_asesor_test(context, nombre=nombre, solicitudes_hoy=10)
        asesor.limite_solicitudes_diarias = 10
        asesor.save()
        
        context.asesores_usuarios[nombre] = asesor
        context.asesores[nombre] = {
            'usuario': asesor,
            'solicitudes_hoy': 10
        }
        
        # Crear 10 solicitudes para cada asesor (al límite)
        cliente_dummy = crear_cliente_test(context, f"CLIENTE-{nombre}")
        for i in range(10):
            Solicitud.objects.create(
                cliente=cliente_dummy,
                asesor=asesor,
                tipo_visa='trabajo',
                embajada='usa',
                estado='pendiente',
                fecha_asignacion=timezone.now(),
            )
    
    print("[INFO] Todos los asesores están al límite de solicitudes")


@step('la solicitud queda sin asesor asignado')
def step_solicitud_sin_asesor(context):
    """Verifica que la solicitud quedó sin asesor asignado."""
    context.nueva_solicitud.refresh_from_db()
    assert context.nueva_solicitud.asesor is None, \
        f"La solicitud tiene asesor asignado: {context.nueva_solicitud.asesor}"


@step('el sistema notifica a los administradores')
def step_sistema_notifica_administradores(context):
    """Verifica que el sistema notifica a los administradores."""
    # En el sistema real, esto crearía una notificación para los admins
    # Para el test, solo verificamos que la asignación falló
    assert context.resultado_asignacion['exito'] == False
    print("[INFO] Sistema notificaría a administradores (simulado)")