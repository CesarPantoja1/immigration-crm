# -*- coding: utf-8 -*-
"""
Steps para los escenarios de Generacion de Recomendaciones.
Implementacion de los pasos BDD definidos en generacion_recomendaciones.feature

Usa los modelos REALES de Django instanciados SIN persistencia en base de datos.
Valida la logica de negocio pura (metodos del modelo) sin conexion a base de datos.
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
from typing import Dict

# Importar modelos REALES de Django (se usan sin persistir en BD)
from apps.usuarios.models import Usuario
from apps.preparacion.models import Simulacro, Recomendacion, ConfiguracionIA
from apps.notificaciones.models import Notificacion

# Importar helpers para crear instancias en memoria
from features.preparacion.recomendaciones.steps.helpers import (
    crear_usuario_en_memoria,
    crear_simulacro_en_memoria,
    crear_configuracion_ia_en_memoria,
    crear_recomendacion_en_memoria
)

use_step_matcher("parse")


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
        
        # Crear asesor si no existe (en memoria, sin BD)
        if nombre_asesor not in context.asesores:
            parts = nombre_asesor.split(' ', 1)
            asesor = crear_usuario_en_memoria(
                user_id,
                parts[0],
                parts[1] if len(parts) > 1 else '',
                'asesor'
            )
            context.asesores[nombre_asesor] = asesor
            user_id += 1
        
        # Crear cliente si no existe (en memoria, sin BD)
        if nombre_cliente not in context.clientes:
            parts = nombre_cliente.split(' ', 1)
            cliente = crear_usuario_en_memoria(
                user_id,
                parts[0],
                parts[1] if len(parts) > 1 else '',
                'cliente'
            )
            context.clientes[nombre_cliente] = cliente
            user_id += 1
        
        # Crear simulacro en memoria usando el modelo REAL
        simulacro = crear_simulacro_en_memoria(
            sim_id,
            codigo,
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
        if sim.asesor == context.asesor_actual and sim.cliente == context.cliente_actual:
            context.simulacro_actual = sim
            break
    
    assert context.simulacro_actual is not None, "No se encontro simulacro"
    # Usar el metodo REAL del modelo Django
    assert context.simulacro_actual.esta_completado(), "El simulacro no esta completado"


@step('sube el archivo "{nombre_archivo}" con la conversacion del simulacro')
def step_sube_archivo_txt(context, nombre_archivo):
    """El asesor sube un archivo .txt de transcripcion."""
    # Usar el metodo REAL del modelo Simulacro para validar extension
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
    
    # Usar el metodo REAL del modelo para validar contenido
    valido, error = Simulacro.validar_contenido_transcripcion(contenido)
    if not valido:
        context.upload_exitoso = False
        context.mensaje_sistema = error
        return
    
    # Asignar transcripcion al simulacro (sin guardar en BD)
    context.simulacro_actual.transcripcion_texto = contenido
    
    # Obtener estadisticas usando el metodo REAL del modelo
    stats = context.simulacro_actual.obtener_estadisticas_transcripcion()
    
    context.upload_exitoso = True
    context.mensaje_sistema = "Transcripcion subida exitosamente"
    context.caracteres = stats['caracteres']
    context.lineas = stats['lineas']


@step('intenta subir el archivo "{nombre_archivo}"')
def step_intenta_subir_archivo(context, nombre_archivo):
    """El asesor intenta subir un archivo (puede no ser .txt)."""
    # Usar el metodo REAL del modelo
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
    """Verifica que el simulacro no tiene transcripcion usando el metodo REAL."""
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
        if sim.asesor == context.asesor_actual:
            context.simulacro_actual = sim
            context.cliente_actual = sim.cliente
            break
    
    # Agregar transcripcion de prueba (sin guardar en BD)
    contenido = """
    Entrevistador: Buenos dias, cual es el proposito de su viaje?
    Cliente: Buenos dias, mi proposito es estudiar una maestria.
    Entrevistador: Como financiara sus estudios?
    Cliente: Tengo una beca y apoyo de mi familia.
    """ * 5
    
    context.simulacro_actual.transcripcion_texto = contenido
    
    # Verificar usando el metodo REAL del modelo Django
    assert context.simulacro_actual.tiene_transcripcion(), \
        "El simulacro debe tener transcripcion valida"


@step("tiene configurada su API key de Gemini")
def step_tiene_api_key(context):
    """El asesor tiene configurada su API key."""
    # Crear configuracion en memoria usando el modelo REAL
    config = crear_configuracion_ia_en_memoria(context.asesor_actual, con_api_key=True)
    context.configuraciones_ia[context.asesor_actual.email] = config
    context.config_ia = config
    
    # Verificar usando el metodo REAL del modelo Django
    assert context.config_ia.esta_configurada(), \
        "La configuracion de IA debe estar activa"


@step('que el asesor "{nombre_asesor}" no ha configurado su API key de Gemini')
def step_asesor_sin_api_key(context, nombre_asesor):
    """El asesor no tiene API key configurada."""
    context.asesor_actual = context.asesores[nombre_asesor]
    # Sin configuracion = None
    context.config_ia = None


@step("tiene un simulacro con transcripcion disponible")
def step_tiene_simulacro_con_transcripcion(context):
    """El asesor tiene un simulacro con transcripcion."""
    for codigo, sim in context.simulacros.items():
        if sim.asesor == context.asesor_actual:
            context.simulacro_actual = sim
            context.cliente_actual = sim.cliente
            break
    
    contenido = "Transcripcion de prueba con contenido suficiente " * 5
    context.simulacro_actual.transcripcion_texto = contenido
    
    # Verificar usando metodo REAL del modelo Django
    assert context.simulacro_actual.tiene_transcripcion()


@step('hace clic en "Generar con IA"')
def step_generar_con_ia(context):
    """El asesor hace clic en generar con IA."""
    # Validar configuracion de IA usando el metodo REAL del modelo Django
    if context.config_ia is None:
        context.mensaje_sistema = ConfiguracionIA.MENSAJE_API_KEY_NO_CONFIGURADA
        context.generacion_exitosa = False
        return
    
    valido, error = context.config_ia.validar_configuracion()
    if not valido:
        context.mensaje_sistema = error
        context.generacion_exitosa = False
        return
    
    # Validar que el simulacro puede generar recomendaciones (metodo REAL)
    if not context.simulacro_actual.puede_generar_recomendaciones():
        context.mensaje_sistema = f"No es posible generar recomendaciones: la transcripcion del simulacro no esta disponible"
        context.generacion_exitosa = False
        return
    
    # Generar recomendacion usando el modelo REAL de Django (sin persistir)
    recomendacion = crear_recomendacion_en_memoria(context.simulacro_actual)
    
    context.recomendacion_actual = recomendacion
    context.recomendaciones[context.simulacro_actual._codigo] = recomendacion
    
    context.generacion_exitosa = True
    context.mensaje_sistema = "Recomendaciones generadas exitosamente"
    
    # Crear notificacion usando el modelo REAL de Django (sin persistir)
    context.notificacion = Notificacion(
        id=1,
        tipo='recomendaciones_listas',
        titulo='Recomendaciones disponibles',
        mensaje='Tus recomendaciones del simulacro estan listas'
    )
    context.notificacion.usuario = context.cliente_actual


@step("el sistema analiza la transcripcion con Gemini")
def step_analiza_con_gemini(context):
    """Verifica que se analice con Gemini."""
    assert context.generacion_exitosa, "La generacion debio ser exitosa"


@step("genera el documento de recomendaciones")
def step_genera_documento(context):
    """Verifica que se genere el documento."""
    assert context.recomendacion_actual is not None, "Debe existir recomendacion"
    # Usar metodo REAL del modelo Django
    assert context.recomendacion_actual.esta_generada(), "Estado debe ser 'generado'"


@step('el cliente "{nombre_cliente}" recibe la notificacion "{mensaje}"')
def step_cliente_recibe_notificacion(context, nombre_cliente, mensaje):
    """Verifica que el cliente reciba notificacion."""
    assert context.recomendacion_actual.publicada, "Recomendacion debe estar publicada"
    assert context.notificacion is not None, "Debe existir notificacion"


@step("el simulacro tiene la opcion de ver feedback disponible")
def step_simulacro_tiene_feedback(context):
    """Verifica que el simulacro tenga feedback disponible."""
    # Verificar que existe una recomendacion para este simulacro
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
        if sim.cliente == context.cliente_actual:
            context.simulacro_actual = sim
            break


@step("el asesor ya genero las recomendaciones con IA")
def step_asesor_genero_recomendaciones(context):
    """El asesor genero las recomendaciones."""
    # Agregar transcripcion primero (sin guardar en BD)
    contenido = "Transcripcion de prueba " * 20
    context.simulacro_actual.transcripcion_texto = contenido
    
    # Generar recomendacion usando el modelo REAL de Django (sin persistir)
    recomendacion = crear_recomendacion_en_memoria(context.simulacro_actual)
    
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


@then("puede ver la lista de recomendaciones disponibles")
def step_ve_lista_recomendaciones(context):
    """Verifica que pueda ver la lista."""
    assert context.recomendaciones_lista is not None, "Debe haber lista de recomendaciones"
    assert len(context.recomendaciones_lista) > 0, "La lista no debe estar vacia"
    
    # Verificar campos segun la tabla usando modelo REAL de Django
    rec = context.recomendacion_actual
    assert rec.simulacro.fecha is not None, "Debe tener fecha del simulacro"
    assert rec.nivel_preparacion in Recomendacion.VALORES_INDICADOR_VALIDOS, \
        "Debe tener nivel de preparacion valido"


@then("puede expandir las secciones colapsables")
def step_expandir_secciones(context):
    """Verifica las secciones colapsables disponibles."""
    secciones_esperadas = [row['seccion'] for row in context.table]
    
    # Usar metodo REAL del modelo Django para obtener secciones
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
        if sim.cliente == context.cliente_actual:
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
# ANALISIS DE IA: INDICADORES DE DESEMPENO
# ==============================================================================

@step('que el asesor "{nombre_asesor}" genero recomendaciones con IA para "{nombre_cliente}"')
def step_asesor_genero_recomendaciones_para_cliente(context, nombre_asesor, nombre_cliente):
    """El asesor genero recomendaciones para el cliente."""
    context.asesor_actual = context.asesores[nombre_asesor]
    context.cliente_actual = context.clientes[nombre_cliente]
    
    for codigo, sim in context.simulacros.items():
        if sim.asesor == context.asesor_actual and sim.cliente == context.cliente_actual:
            context.simulacro_actual = sim
            break
    
    # Agregar transcripcion (sin guardar en BD)
    contenido = "Transcripcion de prueba " * 20
    context.simulacro_actual.transcripcion_texto = contenido
    
    # Generar recomendacion usando el modelo REAL de Django (sin persistir)
    recomendacion = crear_recomendacion_en_memoria(context.simulacro_actual)
    
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


@then("la recomendacion incluye los indicadores")
def step_recomendacion_incluye_indicadores(context):
    """Verifica que la recomendacion tenga los indicadores."""
    rec = context.recomendacion_actual
    
    # Usar metodo REAL del modelo Django para obtener indicadores
    indicadores = rec.obtener_indicadores()
    
    for indicador in indicadores:
        valor = getattr(rec, indicador)
        assert valor in Recomendacion.VALORES_INDICADOR_VALIDOS, \
            f"Indicador {indicador} tiene valor invalido: {valor}"


# ==============================================================================
# ANALISIS DE IA: CONTENIDO GENERADO
# ==============================================================================

@then("cada fortaleza identificada contiene")
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
    
    # Usar constante del modelo REAL de Django
    assert len(rec.fortalezas) > 0, "No hay fortalezas"
    
    for fortaleza in rec.fortalezas:
        for campo in campos_requeridos:
            assert campo in fortaleza, f"Falta campo {campo} en fortaleza"
    
    # Validar estructura completa usando metodo REAL del modelo Django
    assert rec.validar_estructura_fortalezas(), "Estructura de fortalezas invalida"


@then("cada punto de mejora contiene")
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
    
    # Validar estructura completa usando metodo REAL del modelo Django
    assert rec.validar_estructura_puntos_mejora(), "Estructura de puntos de mejora invalida"


@then("cada recomendacion contiene")
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
    
    # Validar estructura completa usando metodo REAL del modelo Django
    assert rec.validar_estructura_recomendaciones(), "Estructura de recomendaciones invalida"
