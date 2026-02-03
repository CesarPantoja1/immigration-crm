# -*- coding: utf-8 -*-
"""
Steps para los escenarios de Generacion de Recomendaciones.
Implementacion de los pasos BDD definidos en generacion_recomendaciones.feature

Usa los modelos Django REALES instanciados sin persistencia en base de datos.
Valida la logica de negocio pura (POO) sin conexion a base de datos.
"""
import os
import sys

# Configurar Django ANTES de importar modelos
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')

import django
django.setup()

from behave import given, when, then, step, use_step_matcher
from datetime import date, time
from typing import Dict, Optional

# Importar modelos REALES de Django
from apps.usuarios.models import Usuario
from apps.preparacion.models import Simulacro, Recomendacion, ConfiguracionIA
from apps.notificaciones.models import Notificacion

use_step_matcher("parse")


# ==============================================================================
# SERVICIOS DE LÓGICA DE NEGOCIO PARA TESTING
# Estos servicios simulan la lógica que normalmente iría al backend
# pero sin tocar la base de datos
# ==============================================================================

class GeneradorRecomendacionesService:
    """
    Servicio para generar recomendaciones con IA (simulado para testing).
    En producción esto usaría el servicio real de IA.
    """
    
    @staticmethod
    def generar_recomendacion_simulada(simulacro: Simulacro) -> Recomendacion:
        """
        Genera una recomendación simulada para testing.
        Simula lo que haría la IA real.
        """
        recomendacion = Recomendacion(
            simulacro=simulacro,
            estado_feedback='generado',
            claridad='alto',
            coherencia='medio',
            seguridad='alto',
            pertinencia='medio',
            nivel_preparacion='medio',
            fortalezas=[
                {
                    'categoria': 'Claridad',
                    'descripcion': 'Respuestas claras y directas',
                    'pregunta_relacionada': 'Proposito del viaje',
                    'impacto': 'alto'
                }
            ],
            puntos_mejora=[
                {
                    'categoria': 'Seguridad',
                    'descripcion': 'Mostrar mas confianza al responder',
                    'pregunta_relacionada': 'Vinculos familiares',
                    'impacto': 'medio'
                }
            ],
            recomendaciones=[
                {
                    'titulo': 'Practicar respuestas',
                    'descripcion': 'Ensayar las respuestas frente a un espejo',
                    'accion_concreta': 'Dedicar 30 minutos diarios a practicar',
                    'impacto': 'alto'
                }
            ],
            accion_sugerida='Reforzar los puntos de mejora identificados',
            publicada=True
        )
        # Calcular nivel basado en indicadores
        recomendacion.nivel_preparacion = recomendacion.calcular_nivel_preparacion()
        return recomendacion


# ==============================================================================
# HELPERS PARA CREAR INSTANCIAS DE MODELOS (SIN PERSISTIR EN BD)
# ==============================================================================

def crear_usuario(id: int, nombre: str, apellido: str, rol: str) -> Usuario:
    """
    Crea una instancia de Usuario sin guardar en BD.
    Usa el modelo REAL de Django.
    """
    usuario = Usuario(
        id=id,
        email=f"{nombre.lower().replace(' ', '.')}@test.com",
        first_name=nombre,
        last_name=apellido,
        rol=rol,
        is_active=True
    )
    return usuario


def crear_simulacro(
    id: int, 
    codigo: str, 
    asesor: Usuario, 
    cliente: Usuario, 
    estado: str = 'completado'
) -> Simulacro:
    """
    Crea una instancia de Simulacro sin guardar en BD.
    Usa el modelo REAL de Django.
    """
    # Nota: Para testing sin BD, asignamos el ID manualmente
    # y usamos los objetos relacionados directamente
    simulacro = Simulacro(
        id=id,
        fecha=date.today(),
        hora=time(10, 0),
        modalidad='virtual',
        estado=estado
    )
    # Asignamos las relaciones directamente (sin FK real)
    simulacro._cliente = cliente
    simulacro._asesor = asesor
    simulacro._codigo = codigo
    
    return simulacro


def crear_configuracion_ia(asesor: Usuario, con_api_key: bool = True) -> Optional[ConfiguracionIA]:
    """
    Crea una instancia de ConfiguracionIA sin guardar en BD.
    """
    if not con_api_key:
        return None
    
    config = ConfiguracionIA(
        id=1,
        api_key='test-api-key-12345' if con_api_key else '',
        modelo='gemini-2.0-flash',
        activo=True
    )
    config._asesor = asesor
    return config


# ==============================================================================
# ANTECEDENTES
# ==============================================================================

@step("que el asesor tiene simulacros completados")
def step_asesor_tiene_simulacros(context):
    """Configura los simulacros completados segun la tabla."""
    context.asesores: Dict[str, Usuario] = {}
    context.clientes: Dict[str, Usuario] = {}
    context.simulacros: Dict[str, Simulacro] = {}
    context.configuraciones_ia: Dict[str, ConfiguracionIA] = {}
    context.recomendaciones: Dict[str, Recomendacion] = {}
    
    user_id = 1
    sim_id = 1
    
    for row in context.table:
        nombre_asesor = row['asesor']
        nombre_cliente = row['cliente']
        estado = row['estado']
        codigo = row['codigo']
        
        # Crear asesor si no existe
        if nombre_asesor not in context.asesores:
            parts = nombre_asesor.split(' ', 1)
            context.asesores[nombre_asesor] = crear_usuario(
                user_id, parts[0], parts[1] if len(parts) > 1 else '', 'asesor'
            )
            user_id += 1
        
        # Crear cliente si no existe
        if nombre_cliente not in context.clientes:
            parts = nombre_cliente.split(' ', 1)
            context.clientes[nombre_cliente] = crear_usuario(
                user_id, parts[0], parts[1] if len(parts) > 1 else '', 'cliente'
            )
            user_id += 1
        
        # Crear simulacro usando el modelo REAL
        simulacro = crear_simulacro(
            sim_id, codigo,
            context.asesores[nombre_asesor],
            context.clientes[nombre_cliente],
            estado
        )
        context.simulacros[codigo] = simulacro
        sim_id += 1


# ==============================================================================
# FLUJO DEL ASESOR: SUBIR TRANSCRIPCION
# ==============================================================================

@step('que el asesor "{nombre_asesor}" tiene un simulacro completado con "{nombre_cliente}"')
def step_asesor_tiene_simulacro_con_cliente(context, nombre_asesor, nombre_cliente):
    """El asesor tiene un simulacro completado con el cliente."""
    context.asesor_actual = context.asesores[nombre_asesor]
    context.cliente_actual = context.clientes[nombre_cliente]
    
    # Buscar el simulacro correspondiente
    for codigo, sim in context.simulacros.items():
        if sim._asesor == context.asesor_actual and sim._cliente == context.cliente_actual:
            context.simulacro_actual = sim
            break
    
    assert context.simulacro_actual is not None, "No se encontro simulacro"
    # Usar el método REAL del modelo
    assert context.simulacro_actual.esta_completado(), "El simulacro no esta completado"


@step('sube el archivo "{nombre_archivo}" con la conversacion del simulacro')
def step_sube_archivo_txt(context, nombre_archivo):
    """El asesor sube un archivo .txt de transcripcion."""
    # Usar el método REAL del modelo Simulacro para validar extensión
    valido, error = Simulacro.validar_extension_archivo(nombre_archivo)
    
    if not valido:
        context.upload_exitoso = False
        context.mensaje_sistema = error
        return
    
    # Contenido de prueba
    contenido = """
    Entrevistador: Buenos dias, cual es el proposito de su viaje?
    Cliente: Buenos dias, mi proposito es estudiar una maestria en administracion.
    Entrevistador: Como financiara sus estudios?
    Cliente: Cuento con una beca parcial y mis padres cubriran el resto.
    Entrevistador: Tiene vinculos en su pais de origen?
    Cliente: Si, mi familia vive aqui y tengo propiedades a mi nombre.
    """ * 3
    
    # Usar el método REAL del modelo para validar contenido
    valido, error = Simulacro.validar_contenido_transcripcion(contenido)
    if not valido:
        context.upload_exitoso = False
        context.mensaje_sistema = error
        return
    
    # Asignar transcripción al simulacro
    context.simulacro_actual.transcripcion_texto = contenido
    
    # Obtener estadísticas usando el método REAL del modelo
    stats = context.simulacro_actual.obtener_estadisticas_transcripcion()
    
    context.upload_exitoso = True
    context.mensaje_sistema = "Transcripcion subida exitosamente"
    context.caracteres = stats['caracteres']
    context.lineas = stats['lineas']


@step('intenta subir el archivo "{nombre_archivo}"')
def step_intenta_subir_archivo(context, nombre_archivo):
    """El asesor intenta subir un archivo (puede no ser .txt)."""
    # Usar el método REAL del modelo
    valido, error = Simulacro.validar_extension_archivo(nombre_archivo)
    
    if not valido:
        context.upload_exitoso = False
        context.mensaje_sistema = error
    else:
        context.upload_exitoso = True


@step('el sistema confirma "{mensaje}"')
def step_sistema_confirma(context, mensaje):
    """Verifica que el sistema muestre un mensaje de confirmacion."""
    assert context.mensaje_sistema == mensaje, \
        f"Esperado: '{mensaje}', Obtenido: '{context.mensaje_sistema}'"


@step('el sistema muestra "{mensaje}"')
def step_sistema_muestra(context, mensaje):
    """Verifica que el sistema muestre un mensaje."""
    assert context.mensaje_sistema == mensaje, \
        f"Esperado: '{mensaje}', Obtenido: '{context.mensaje_sistema}'"


@step("muestra la cantidad de caracteres y lineas del archivo")
def step_muestra_caracteres_lineas(context):
    """Verifica que se muestren las estadisticas del archivo."""
    assert context.caracteres > 0, "Debe haber caracteres"
    assert context.lineas > 0, "Debe haber lineas"


@step("el simulacro no cuenta con transcripcion subida")
def step_simulacro_sin_transcripcion(context):
    """Verifica que el simulacro no tiene transcripcion usando el método REAL."""
    assert not context.simulacro_actual.tiene_transcripcion(), \
        "El simulacro no deberia tener transcripcion"


# ==============================================================================
# FLUJO DEL ASESOR: GENERAR RECOMENDACIONES CON IA
# ==============================================================================

@step('que el asesor "{nombre_asesor}" tiene un simulacro con transcripcion subida exitosamente')
def step_asesor_tiene_simulacro_con_transcripcion(context, nombre_asesor):
    """El asesor tiene un simulacro con transcripcion."""
    context.asesor_actual = context.asesores[nombre_asesor]
    
    for codigo, sim in context.simulacros.items():
        if sim._asesor == context.asesor_actual:
            context.simulacro_actual = sim
            context.cliente_actual = sim._cliente
            break
    
    # Agregar transcripcion de prueba
    context.simulacro_actual.transcripcion_texto = """
    Entrevistador: Buenos dias, cual es el proposito de su viaje?
    Cliente: Buenos dias, mi proposito es estudiar una maestria.
    Entrevistador: Como financiara sus estudios?
    Cliente: Tengo una beca y apoyo de mi familia.
    """ * 5
    
    # Verificar usando el método REAL
    assert context.simulacro_actual.tiene_transcripcion(), \
        "El simulacro debe tener transcripcion valida"


@step("tiene configurada su API key de Gemini")
def step_tiene_api_key(context):
    """El asesor tiene configurada su API key."""
    config = crear_configuracion_ia(context.asesor_actual, con_api_key=True)
    context.configuraciones_ia[context.asesor_actual.email] = config
    context.config_ia = config
    
    # Verificar usando el método REAL del modelo
    assert context.config_ia.esta_configurada(), \
        "La configuracion de IA debe estar activa"


@step('que el asesor "{nombre_asesor}" no ha configurado su API key de Gemini')
def step_asesor_sin_api_key(context, nombre_asesor):
    """El asesor no tiene API key configurada."""
    context.asesor_actual = context.asesores[nombre_asesor]
    # Sin configuración = None
    context.config_ia = None


@step("tiene un simulacro con transcripcion disponible")
def step_tiene_simulacro_con_transcripcion(context):
    """El asesor tiene un simulacro con transcripcion."""
    for codigo, sim in context.simulacros.items():
        if sim._asesor == context.asesor_actual:
            context.simulacro_actual = sim
            context.cliente_actual = sim._cliente
            break
    
    context.simulacro_actual.transcripcion_texto = "Transcripcion de prueba con contenido suficiente " * 5
    
    # Verificar usando método REAL
    assert context.simulacro_actual.tiene_transcripcion()


@step('hace clic en "Generar con IA"')
def step_generar_con_ia(context):
    """El asesor hace clic en generar con IA."""
    # Validar configuracion de IA usando el método REAL
    if context.config_ia is None:
        context.mensaje_sistema = ConfiguracionIA.MENSAJE_API_KEY_NO_CONFIGURADA
        context.generacion_exitosa = False
        return
    
    valido, error = context.config_ia.validar_configuracion()
    if not valido:
        context.mensaje_sistema = error
        context.generacion_exitosa = False
        return
    
    # Validar que el simulacro puede generar recomendaciones (método REAL)
    if not context.simulacro_actual.puede_generar_recomendaciones():
        context.mensaje_sistema = f"No es posible generar recomendaciones: la transcripcion del simulacro no esta disponible"
        context.generacion_exitosa = False
        return
    
    # Generar recomendación usando el servicio
    recomendacion = GeneradorRecomendacionesService.generar_recomendacion_simulada(
        context.simulacro_actual
    )
    context.recomendacion_actual = recomendacion
    context.recomendaciones[context.simulacro_actual._codigo] = recomendacion
    
    context.generacion_exitosa = True
    context.mensaje_sistema = "Recomendaciones generadas exitosamente"
    
    # Crear notificación (modelo REAL, sin persistir)
    context.notificacion = Notificacion(
        id=1,
        mensaje="Recomendaciones disponibles"
    )
    context.notificacion._usuario = context.cliente_actual


@step("el sistema analiza la transcripcion con Gemini")
def step_analiza_con_gemini(context):
    """Verifica que se analice con Gemini."""
    assert context.generacion_exitosa, "La generacion debio ser exitosa"


@step("genera el documento de recomendaciones")
def step_genera_documento(context):
    """Verifica que se genere el documento."""
    assert context.recomendacion_actual is not None, "Debe existir recomendacion"
    # Usar método REAL del modelo
    assert context.recomendacion_actual.esta_generada(), "Estado debe ser 'generado'"


@step('el cliente "{nombre_cliente}" recibe la notificacion "{mensaje}"')
def step_cliente_recibe_notificacion(context, nombre_cliente, mensaje):
    """Verifica que el cliente reciba notificacion."""
    assert context.recomendacion_actual.publicada, "Recomendacion debe estar publicada"
    assert context.notificacion is not None, "Debe existir notificacion"


@step("el simulacro tiene la opcion de ver feedback disponible")
def step_simulacro_tiene_feedback(context):
    """Verifica que el simulacro tenga feedback disponible."""
    # Verificar que existe una recomendación para este simulacro
    codigo = context.simulacro_actual._codigo
    assert codigo in context.recomendaciones, "Simulacro debe tener recomendaciones"


# ==============================================================================
# FLUJO DEL CLIENTE: CONSULTAR RECOMENDACIONES
# ==============================================================================

@step('que el cliente "{nombre_cliente}" completo un simulacro')
def step_cliente_completo_simulacro(context, nombre_cliente):
    """El cliente completo un simulacro."""
    context.cliente_actual = context.clientes[nombre_cliente]
    
    for codigo, sim in context.simulacros.items():
        if sim._cliente == context.cliente_actual:
            context.simulacro_actual = sim
            break


@step("el asesor ya genero las recomendaciones con IA")
def step_asesor_genero_recomendaciones(context):
    """El asesor genero las recomendaciones."""
    recomendacion = GeneradorRecomendacionesService.generar_recomendacion_simulada(
        context.simulacro_actual
    )
    context.recomendacion_actual = recomendacion
    context.recomendaciones[context.simulacro_actual._codigo] = recomendacion


@step('el cliente accede a "Ver Resumen" en la seccion de simulacros completados y "Ver Recomendaciones"')
def step_cliente_accede_ver_resumen_recomendaciones(context):
    """El cliente navega a Ver Resumen y luego Ver Recomendaciones."""
    codigo = context.simulacro_actual._codigo
    if codigo in context.recomendaciones:
        context.recomendacion_actual = context.recomendaciones[codigo]
        context.recomendaciones_lista = [context.recomendacion_actual]
    else:
        context.recomendaciones_lista = []


@then("puede ver la lista de recomendaciones disponibles:")
def step_ve_lista_recomendaciones(context):
    """Verifica que pueda ver la lista."""
    assert context.recomendaciones_lista is not None, "Debe haber lista de recomendaciones"
    assert len(context.recomendaciones_lista) > 0, "La lista no debe estar vacia"
    
    # Verificar campos segun la tabla usando modelo REAL
    rec = context.recomendacion_actual
    assert rec.simulacro.fecha is not None, "Debe tener fecha del simulacro"
    assert rec.nivel_preparacion in Recomendacion.VALORES_INDICADOR_VALIDOS, \
        "Debe tener nivel de preparacion valido"


@then("puede expandir las secciones colapsables:")
def step_expandir_secciones(context):
    """Verifica las secciones colapsables disponibles."""
    secciones_esperadas = [row['seccion'] for row in context.table]
    
    # Usar método REAL del modelo para obtener secciones
    rec = context.recomendacion_actual
    secciones_disponibles = rec.obtener_secciones_disponibles()
    
    for seccion in secciones_esperadas:
        assert seccion in secciones_disponibles, f"Seccion '{seccion}' no disponible"


# ==============================================================================
# CLIENTE SIN RECOMENDACIONES / DESCARGA PDF
# ==============================================================================

@step('que el cliente "{nombre_cliente}" tiene un simulacro completado')
def step_cliente_tiene_simulacro_completado(context, nombre_cliente):
    """El cliente tiene simulacro completado."""
    context.cliente_actual = context.clientes[nombre_cliente]
    
    for codigo, sim in context.simulacros.items():
        if sim._cliente == context.cliente_actual:
            context.simulacro_actual = sim
            break


@step("el simulacro no tiene recomendaciones generadas")
def step_simulacro_sin_recomendaciones(context):
    """El simulacro no tiene recomendaciones."""
    codigo = context.simulacro_actual._codigo
    if codigo in context.recomendaciones:
        del context.recomendaciones[codigo]
    context.tiene_recomendaciones = False


@step("intenta descargar el PDF de recomendaciones")
def step_intenta_descargar_pdf(context):
    """El cliente intenta descargar el PDF."""
    codigo = context.simulacro_actual._codigo
    tiene_recomendaciones = codigo in context.recomendaciones
    
    if not tiene_recomendaciones:
        context.mensaje_sistema = "Este simulacro no tiene recomendaciones"
    else:
        context.mensaje_sistema = "PDF descargado exitosamente"


# ==============================================================================
# ANALISIS DE IA: INDICADORES DE DESEMPEÑO
# ==============================================================================

@step('que el asesor "{nombre_asesor}" genero recomendaciones con IA para "{nombre_cliente}"')
def step_asesor_genero_recomendaciones_para_cliente(context, nombre_asesor, nombre_cliente):
    """El asesor genero recomendaciones para el cliente."""
    context.asesor_actual = context.asesores[nombre_asesor]
    context.cliente_actual = context.clientes[nombre_cliente]
    
    for codigo, sim in context.simulacros.items():
        if sim._asesor == context.asesor_actual and sim._cliente == context.cliente_actual:
            context.simulacro_actual = sim
            break
    
    # Agregar transcripción
    context.simulacro_actual.transcripcion_texto = "Transcripcion de prueba " * 20
    
    # Generar recomendación
    recomendacion = GeneradorRecomendacionesService.generar_recomendacion_simulada(
        context.simulacro_actual
    )
    context.recomendacion_actual = recomendacion
    context.recomendaciones[context.simulacro_actual._codigo] = recomendacion


@step("el cliente consulta sus recomendaciones")
def step_cliente_consulta_recomendaciones(context):
    """El cliente consulta sus recomendaciones."""
    codigo = context.simulacro_actual._codigo
    if codigo in context.recomendaciones:
        context.recomendaciones_lista = [context.recomendaciones[codigo]]
    else:
        context.recomendaciones_lista = []


@then("la recomendacion incluye los indicadores:")
def step_recomendacion_incluye_indicadores(context):
    """Verifica que la recomendacion tenga los indicadores."""
    rec = context.recomendacion_actual
    
    # Usar método REAL del modelo para obtener indicadores
    indicadores = rec.obtener_indicadores()
    
    for indicador in indicadores:
        valor = getattr(rec, indicador)
        assert valor in Recomendacion.VALORES_INDICADOR_VALIDOS, \
            f"Indicador {indicador} tiene valor invalido: {valor}"


# ==============================================================================
# ANALISIS DE IA: CONTENIDO GENERADO
# ==============================================================================

@then("cada fortaleza identificada contiene:")
def step_fortaleza_contiene_campos(context):
    """Verifica estructura de fortalezas."""
    rec = context.recomendacion_actual
    
    # Mapear campos de la tabla a campos reales del modelo
    campos_mapping = {
        'Categoria': 'categoria',
        'Descripcion': 'descripcion',
        'Pregunta relacionada': 'pregunta_relacionada',
        'Impacto': 'impacto'
    }
    
    campos_requeridos = [campos_mapping[row['campo']] for row in context.table]
    
    # Usar constante del modelo REAL
    assert len(rec.fortalezas) > 0, "No hay fortalezas"
    
    for fortaleza in rec.fortalezas:
        for campo in campos_requeridos:
            assert campo in fortaleza, f"Falta campo {campo} en fortaleza"
    
    # Validar estructura completa usando método REAL
    assert rec.validar_estructura_fortalezas(), "Estructura de fortalezas invalida"


@then("cada punto de mejora contiene:")
def step_punto_mejora_contiene_campos(context):
    """Verifica estructura de puntos de mejora."""
    rec = context.recomendacion_actual
    
    campos_mapping = {
        'Categoria': 'categoria',
        'Descripcion': 'descripcion',
        'Pregunta relacionada': 'pregunta_relacionada',
        'Impacto': 'impacto'
    }
    
    campos_requeridos = [campos_mapping[row['campo']] for row in context.table]
    
    assert len(rec.puntos_mejora) > 0, "No hay puntos de mejora"
    
    for punto in rec.puntos_mejora:
        for campo in campos_requeridos:
            assert campo in punto, f"Falta campo {campo} en punto de mejora"
    
    # Validar estructura completa usando método REAL
    assert rec.validar_estructura_puntos_mejora(), "Estructura de puntos de mejora invalida"


@then("cada recomendacion contiene:")
def step_recomendacion_contiene_campos(context):
    """Verifica estructura de recomendaciones."""
    rec = context.recomendacion_actual
    
    campos_mapping = {
        'Titulo': 'titulo',
        'Descripcion': 'descripcion',
        'Accion concreta': 'accion_concreta',
        'Impacto': 'impacto'
    }
    
    campos_requeridos = [campos_mapping[row['campo']] for row in context.table]
    
    assert len(rec.recomendaciones) > 0, "No hay recomendaciones"
    
    for recomendacion in rec.recomendaciones:
        for campo in campos_requeridos:
            assert campo in recomendacion, f"Falta campo {campo} en recomendacion"
    
    # Validar estructura completa usando método REAL
    assert rec.validar_estructura_recomendaciones(), "Estructura de recomendaciones invalida"
