"""
Steps para la feature de Generación de Recomendaciones.
"""
import os
import sys

# Agregar el directorio backend al path para importar los módulos
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from behave import given, when, then, step, use_step_matcher
from datetime import datetime

# Importar dominio de recomendaciones
from apps.preparacion.recomendaciones.domain import (
    NivelIndicador,
    NivelPreparacion,
    NivelImpacto,
    CategoriaRecomendacion,
    TipoPregunta,
    EstadoSimulacro,
    FormatoDocumento,
    IndicadorDesempeno,
    PuntoMejora,
    Fortaleza,
    RecomendacionAccionable,
    PreguntaSimulacro,
    MetadatosDocumento,
    AccionSugerida,
    TranscripcionSimulacro,
    AnalisisIA,
    DocumentoRecomendaciones,
    SimulacroParaRecomendaciones,
    calcular_nivel_preparacion,
    SECCIONES_DOCUMENTO,
)

use_step_matcher("re")


# =============================================================================
# ANTECEDENTES
# =============================================================================

@given(r'que existen simulacros de entrevista consular registrados en el sistema')
def step_existen_simulacros(context):
    """Configura que existen simulacros en el sistema."""
    context.simulacros = {}
    context.documentos = {}
    context.analisis = {}


@given(r'cada simulacro puede contar con una transcripción de preguntas y respuestas almacenada en el sistema')
def step_simulacros_pueden_tener_transcripcion(context):
    """Indica que los simulacros pueden tener transcripciones."""
    context.transcripciones_habilitadas = True


@given(r'existe un agente de IA habilitado en el sistema para analizar transcripciones de simulacros')
def step_agente_ia_habilitado(context):
    """Configura el agente de IA."""
    context.agente_ia_habilitado = True


@given(r'el sistema permite generar documentos de recomendaciones asociados a un simulacro')
def step_sistema_permite_documentos(context):
    """Configura que el sistema permite generar documentos."""
    context.generacion_documentos_habilitada = True


# =============================================================================
# ESCENARIO: GENERACIÓN DE DOCUMENTO DE RECOMENDACIONES
# =============================================================================

@given(r'que existe un simulacro identificado como "([^"]*)" registrado en el sistema')
def step_existe_simulacro_id(context, id_simulacro):
    """Registra un simulacro con el ID dado."""
    if not hasattr(context, 'simulacros'):
        context.simulacros = {}
    
    simulacro = SimulacroParaRecomendaciones(
        id=id_simulacro,
        migrante_id="migrante-001",
        migrante_nombre="Oscar",
    )
    context.simulacros[id_simulacro] = simulacro
    context.simulacro_actual = simulacro


@given(r'el simulacro "([^"]*)" tiene una transcripción de preguntas y respuestas registrada en el sistema')
def step_simulacro_tiene_transcripcion(context, id_simulacro):
    """Agrega transcripción al simulacro."""
    simulacro = context.simulacros.get(id_simulacro)
    if simulacro:
        transcripcion = TranscripcionSimulacro(
            simulacro_id=id_simulacro,
            contenido="""
            Entrevistador: ¿Cuál es el motivo de su viaje?
            Migrante: Quiero estudiar una maestría.
            Entrevistador: ¿Cómo financiará sus estudios?
            Migrante: Tengo una beca y apoyo familiar.
            """,
            fecha_simulacro=datetime.now()
        )
        simulacro.transcripcion = transcripcion


@given(r'el agente de IA ha analizado la transcripción del simulacro "([^"]*)"')
def step_ia_ha_analizado_transcripcion(context, id_simulacro):
    """Marca que la IA ha analizado el simulacro."""
    simulacro = context.simulacros.get(id_simulacro)
    if simulacro:
        analisis = AnalisisIA(simulacro_id=id_simulacro)
        simulacro.analisis = analisis
        context.analisis_actual = analisis


@given(r'se han identificado los siguientes indicadores de desempeño:')
def step_indicadores_desempeno(context):
    """Configura los indicadores de desempeño desde la tabla."""
    if not hasattr(context, 'analisis_actual'):
        context.analisis_actual = AnalisisIA(simulacro_id="temp")
    
    nivel_map = {
        "Alta": NivelIndicador.ALTA,
        "Alto": NivelIndicador.ALTO,
        "Media": NivelIndicador.MEDIA,
        "Medio": NivelIndicador.MEDIO,
        "Baja": NivelIndicador.BAJA,
        "Bajo": NivelIndicador.BAJO,
    }
    
    for row in context.table:
        nombre = row['indicador']
        valor_str = row['valor']
        valor = nivel_map.get(valor_str, NivelIndicador.MEDIA)
        
        indicador = IndicadorDesempeno(nombre=nombre, valor=valor)
        context.analisis_actual.agregar_indicador(indicador)
    
    context.analisis_actual.marcar_completado()
    
    # Asociar al simulacro actual
    if hasattr(context, 'simulacro_actual') and context.simulacro_actual:
        context.simulacro_actual.analisis = context.analisis_actual


@when(r'el asesor solicita generar el documento de recomendaciones para el simulacro "([^"]*)"')
def step_asesor_solicita_generar_documento(context, id_simulacro):
    """El asesor solicita generar el documento."""
    simulacro = context.simulacros.get(id_simulacro)
    
    if simulacro and simulacro.puede_generar_documento():
        documento = simulacro.generar_documento_recomendaciones()
        
        if not hasattr(context, 'documentos'):
            context.documentos = {}
        
        context.documentos[id_simulacro] = documento
        context.documento_actual = documento


@then(r'el sistema debe crear un documento de recomendaciones asociado al simulacro "([^"]*)" con los siguientes metadatos:')
def step_documento_con_metadatos(context, id_simulacro):
    """Verifica que se cree el documento con metadatos correctos."""
    documento = context.documentos.get(id_simulacro)
    assert documento is not None, f"No se creó documento para {id_simulacro}"
    
    # Verificar metadatos
    metadatos_esperados = {}
    for row in context.table:
        metadatos_esperados[row['campo']] = row['valor']
    
    assert documento.metadatos is not None, "El documento no tiene metadatos"
    
    metadatos_doc = documento.metadatos.a_dict()
    
    for campo, valor_esperado in metadatos_esperados.items():
        assert campo in metadatos_doc, f"Campo '{campo}' no encontrado en metadatos"
        assert metadatos_doc[campo] == valor_esperado, \
            f"Metadato '{campo}': esperado '{valor_esperado}', actual '{metadatos_doc[campo]}'"


@then(r'el documento debe incluir las siguientes secciones:')
def step_documento_incluye_secciones(context):
    """Verifica que el documento incluya las secciones requeridas."""
    documento = context.documento_actual
    assert documento is not None, "No hay documento actual"
    
    for row in context.table:
        seccion = row['seccion']
        assert documento.tiene_seccion(seccion), \
            f"Sección '{seccion}' no encontrada en el documento"


# =============================================================================
# ESCENARIO: RECOMENDACIONES ACCIONABLES POR CATEGORÍA
# =============================================================================

@given(r'el agente de IA ha identificado los siguientes puntos de mejora en el simulacro "([^"]*)":')
def step_ia_identifico_puntos_mejora(context, id_simulacro):
    """Configura los puntos de mejora identificados."""
    simulacro = context.simulacros.get(id_simulacro)
    
    if not simulacro:
        simulacro = SimulacroParaRecomendaciones(id=id_simulacro)
        context.simulacros[id_simulacro] = simulacro
    
    if not simulacro.analisis:
        simulacro.analisis = AnalisisIA(simulacro_id=id_simulacro)
    
    categoria_map = {
        "Claridad": CategoriaRecomendacion.CLARIDAD,
        "Coherencia": CategoriaRecomendacion.COHERENCIA,
        "Seguridad": CategoriaRecomendacion.SEGURIDAD,
        "Pertinencia": CategoriaRecomendacion.PERTINENCIA,
    }
    
    for row in context.table:
        categoria_str = row['categoria']
        descripcion = row['descripcion']
        
        categoria = categoria_map.get(categoria_str, CategoriaRecomendacion.CLARIDAD)
        
        punto = PuntoMejora(
            categoria=categoria,
            descripcion=descripcion
        )
        simulacro.analisis.agregar_punto_mejora(punto)
    
    simulacro.analisis.marcar_completado()
    
    # Asegurar que tiene transcripción
    if not simulacro.transcripcion:
        simulacro.transcripcion = TranscripcionSimulacro(
            simulacro_id=id_simulacro,
            contenido="Transcripción de prueba"
        )
    
    context.simulacro_actual = simulacro


@when(r'se genera el documento de recomendaciones del simulacro "([^"]*)"')
def step_se_genera_documento(context, id_simulacro):
    """Se genera el documento de recomendaciones."""
    simulacro = context.simulacros.get(id_simulacro)
    
    if simulacro and simulacro.puede_generar_documento():
        documento = simulacro.generar_documento_recomendaciones()
        
        # Agregar recomendaciones basadas en puntos de mejora
        categorias_con_mejora = set(
            pm.categoria for pm in simulacro.analisis.puntos_mejora
        )
        
        for categoria in categorias_con_mejora:
            puntos = simulacro.analisis.obtener_puntos_mejora_por_categoria(categoria)
            for i, punto in enumerate(puntos):
                rec = RecomendacionAccionable(
                    id=f"REC-{id_simulacro}-{categoria.value}-{i+1}",
                    categoria=categoria,
                    descripcion=f"Mejorar {categoria.value.lower()}",
                    accion_concreta=f"Practicar técnicas de {categoria.value.lower()}",
                    metrica_exito=f"Lograr nivel Alto en próximo simulacro",
                    impacto=NivelImpacto.MEDIO
                )
                documento.agregar_recomendacion(rec)
        
        if not hasattr(context, 'documentos'):
            context.documentos = {}
        
        context.documentos[id_simulacro] = documento
        context.documento_actual = documento


@then(r'el documento debe contener recomendaciones accionables clasificadas por categoría:')
def step_documento_recomendaciones_por_categoria(context):
    """Verifica que las recomendaciones estén clasificadas por categoría."""
    documento = context.documento_actual
    assert documento is not None, "No hay documento actual"
    
    categorias_esperadas = [row['categoria'] for row in context.table]
    categorias_documento = documento.agrupar_recomendaciones_por_categoria()
    
    categoria_map = {
        "Claridad": CategoriaRecomendacion.CLARIDAD,
        "Coherencia": CategoriaRecomendacion.COHERENCIA,
        "Seguridad": CategoriaRecomendacion.SEGURIDAD,
        "Pertinencia": CategoriaRecomendacion.PERTINENCIA,
    }
    
    for cat_str in categorias_esperadas:
        cat = categoria_map.get(cat_str)
        assert cat in categorias_documento, \
            f"Categoría '{cat_str}' no encontrada en el documento"


@then(r'cada categoría debe contener al menos una recomendación concreta y medible')
def step_cada_categoria_tiene_recomendacion(context):
    """Verifica que cada categoría tenga al menos una recomendación."""
    documento = context.documento_actual
    categorias = documento.agrupar_recomendaciones_por_categoria()
    
    for categoria, recomendaciones in categorias.items():
        assert len(recomendaciones) > 0, \
            f"Categoría {categoria.value} no tiene recomendaciones"
        
        # Verificar que sean concretas y medibles
        for rec in recomendaciones:
            assert rec.accion_concreta, "La recomendación no tiene acción concreta"
            assert rec.metrica_exito, "La recomendación no tiene métrica de éxito"


@then(r'el documento debe registrar la fecha de generación del feedback')
def step_documento_tiene_fecha_generacion(context):
    """Verifica que el documento tenga fecha de generación."""
    documento = context.documento_actual
    assert documento.fecha_generacion is not None, \
        "El documento no tiene fecha de generación"


# =============================================================================
# ESCENARIO: NIVEL DE PREPARACIÓN
# =============================================================================

@given(r'el análisis del simulacro "([^"]*)" tiene los siguientes resultados:')
def step_analisis_simulacro_resultados(context, id_simulacro):
    """Configura los resultados del análisis."""
    simulacro = context.simulacros.get(id_simulacro)
    
    if not simulacro:
        simulacro = SimulacroParaRecomendaciones(id=id_simulacro)
        context.simulacros[id_simulacro] = simulacro
    
    analisis = AnalisisIA(simulacro_id=id_simulacro)
    
    nivel_map = {
        "Alta": NivelIndicador.ALTA,
        "Alto": NivelIndicador.ALTO,
        "Media": NivelIndicador.MEDIA,
        "Medio": NivelIndicador.MEDIO,
        "Baja": NivelIndicador.BAJA,
        "Bajo": NivelIndicador.BAJO,
    }
    
    for row in context.table:
        nombre = row['indicador']
        valor_str = row['valor']
        valor = nivel_map.get(valor_str, NivelIndicador.MEDIA)
        
        indicador = IndicadorDesempeno(nombre=nombre, valor=valor)
        analisis.agregar_indicador(indicador)
    
    analisis.marcar_completado()
    simulacro.analisis = analisis
    context.analisis_actual = analisis


@when(r'el sistema calcula el nivel global de preparación')
def step_sistema_calcula_nivel(context):
    """El sistema calcula el nivel de preparación."""
    analisis = context.analisis_actual
    context.nivel_calculado = analisis.obtener_nivel_preparacion()


@then(r'el nivel de preparación asignado debe ser "([^"]*)"')
def step_nivel_preparacion_asignado(context, nivel_esperado):
    """Verifica el nivel de preparación asignado."""
    nivel_map = {
        "Alto": NivelPreparacion.ALTO,
        "Medio": NivelPreparacion.MEDIO,
        "Bajo": NivelPreparacion.BAJO,
    }
    
    nivel_esperado_enum = nivel_map.get(nivel_esperado)
    
    assert context.nivel_calculado == nivel_esperado_enum, \
        f"Nivel esperado: {nivel_esperado}, calculado: {context.nivel_calculado.value}"


# =============================================================================
# ESCENARIO: TRAZABILIDAD
# =============================================================================

@given(r'el simulacro "([^"]*)" tiene las siguientes preguntas y respuestas:')
def step_simulacro_tiene_preguntas(context, id_simulacro):
    """Configura las preguntas del simulacro."""
    simulacro = context.simulacros.get(id_simulacro)
    
    if not simulacro:
        simulacro = SimulacroParaRecomendaciones(id=id_simulacro)
        context.simulacros[id_simulacro] = simulacro
    
    tipo_map = {
        "Motivo del viaje": TipoPregunta.MOTIVO_VIAJE,
        "Situación económica": TipoPregunta.SITUACION_ECONOMICA,
        "Planes de permanencia": TipoPregunta.PLANES_PERMANENCIA,
    }
    
    preguntas = []
    for row in context.table:
        numero = int(row['numero_pregunta'])
        tipo_str = row['tipo_pregunta']
        tipo = tipo_map.get(tipo_str, TipoPregunta.MOTIVO_VIAJE)
        
        pregunta = PreguntaSimulacro(
            numero=numero,
            tipo=tipo,
            texto=tipo_str
        )
        preguntas.append(pregunta)
    
    # Crear transcripción con preguntas
    simulacro.transcripcion = TranscripcionSimulacro(
        simulacro_id=id_simulacro,
        preguntas=preguntas,
        contenido="Transcripción con preguntas"
    )
    
    context.preguntas_simulacro = preguntas


@given(r'el agente de IA ha generado recomendaciones asociadas al simulacro "([^"]*)"')
def step_ia_genero_recomendaciones(context, id_simulacro):
    """La IA ha generado recomendaciones."""
    simulacro = context.simulacros.get(id_simulacro)
    
    if not simulacro.analisis:
        simulacro.analisis = AnalisisIA(simulacro_id=id_simulacro)
        simulacro.analisis.marcar_completado()
    
    # Generar documento con recomendaciones trazables
    documento = DocumentoRecomendaciones(simulacro_id=id_simulacro)
    
    # Crear recomendaciones asociadas a las preguntas
    if hasattr(context, 'preguntas_simulacro'):
        for pregunta in context.preguntas_simulacro:
            rec = RecomendacionAccionable(
                id=f"REC-{id_simulacro}-{pregunta.numero}",
                categoria=CategoriaRecomendacion.CLARIDAD,
                descripcion=f"Mejorar respuesta a {pregunta.tipo.value}",
                accion_concreta="Practicar la respuesta",
                metrica_exito="Lograr coherencia",
                impacto=NivelImpacto.ALTO,
                numero_pregunta_origen=pregunta.numero,
                tipo_pregunta_origen=pregunta.tipo,
            )
            documento.agregar_recomendacion(rec)
    
    simulacro.documento = documento
    context.documentos[id_simulacro] = documento
    context.documento_actual = documento


@when(r'el asesor revisa el documento de recomendaciones del simulacro "([^"]*)"')
def step_asesor_revisa_documento(context, id_simulacro):
    """El asesor revisa el documento."""
    documento = context.documentos.get(id_simulacro)
    context.documento_revisado = documento


@then(r'cada recomendación debe estar asociada a una pregunta del simulacro')
def step_recomendaciones_asociadas_preguntas(context):
    """Verifica que las recomendaciones estén asociadas a preguntas."""
    documento = context.documento_revisado
    
    for rec in documento.recomendaciones:
        assert rec.es_trazable(), \
            f"Recomendación {rec.id} no está asociada a una pregunta"


@then(r'el documento debe permitir identificar para cada recomendación:')
def step_documento_permite_identificar(context):
    """Verifica que se puedan identificar los atributos de trazabilidad."""
    documento = context.documento_revisado
    atributos_esperados = [row['atributo'] for row in context.table]
    atributos_disponibles = documento.obtener_atributos_trazabilidad()
    
    for atributo in atributos_esperados:
        assert atributo in atributos_disponibles, \
            f"Atributo '{atributo}' no disponible en el documento"


# =============================================================================
# ESCENARIO: CLASIFICACIÓN POR IMPACTO
# =============================================================================

@given(r'que existe un documento de recomendaciones generado para el simulacro "([^"]*)"')
def step_existe_documento_generado(context, id_simulacro):
    """Existe un documento de recomendaciones."""
    if not hasattr(context, 'documentos'):
        context.documentos = {}
    
    documento = DocumentoRecomendaciones(simulacro_id=id_simulacro)
    
    # Agregar recomendaciones con diferentes impactos
    for impacto in [NivelImpacto.ALTO, NivelImpacto.MEDIO, NivelImpacto.BAJO]:
        rec = RecomendacionAccionable(
            id=f"REC-{id_simulacro}-{impacto.value}",
            categoria=CategoriaRecomendacion.CLARIDAD,
            descripcion=f"Recomendación de impacto {impacto.value}",
            accion_concreta="Acción concreta",
            metrica_exito="Métrica de éxito",
            impacto=impacto
        )
        documento.agregar_recomendacion(rec)
    
    context.documentos[id_simulacro] = documento
    context.documento_actual = documento


@given(r'el documento de recomendaciones del simulacro "([^"]*)" contiene recomendaciones con impacto clasificado')
def step_documento_tiene_impactos(context, id_simulacro):
    """El documento tiene recomendaciones con impacto clasificado."""
    documento = context.documentos.get(id_simulacro)
    assert documento is not None, "Documento no encontrado"
    assert len(documento.recomendaciones) > 0, "El documento no tiene recomendaciones"


@when(r'el sistema organiza las recomendaciones por impacto')
def step_sistema_organiza_por_impacto(context):
    """El sistema organiza las recomendaciones por impacto."""
    documento = context.documento_actual
    context.recomendaciones_por_impacto = documento.agrupar_recomendaciones_por_impacto()


@then(r'las recomendaciones deben quedar agrupadas por nivel de impacto:')
def step_recomendaciones_agrupadas_impacto(context):
    """Verifica que las recomendaciones estén agrupadas por impacto."""
    impactos_esperados = [row['impacto'] for row in context.table]
    
    impacto_map = {
        "Alto": NivelImpacto.ALTO,
        "Medio": NivelImpacto.MEDIO,
        "Bajo": NivelImpacto.BAJO,
    }
    
    for impacto_str in impactos_esperados:
        impacto = impacto_map.get(impacto_str)
        assert impacto in context.recomendaciones_por_impacto, \
            f"Nivel de impacto '{impacto_str}' no encontrado"


@then(r'cada recomendación debe registrar su nivel de impacto')
def step_recomendaciones_registran_impacto(context):
    """Verifica que cada recomendación tenga nivel de impacto."""
    documento = context.documento_actual
    
    for rec in documento.recomendaciones:
        assert rec.impacto is not None, \
            f"Recomendación {rec.id} no tiene nivel de impacto"


# =============================================================================
# ESCENARIO: ACCIÓN SUGERIDA
# =============================================================================

@given(r'el documento de recomendaciones del simulacro "([^"]*)" tiene nivel de preparación "([^"]*)"')
def step_documento_tiene_nivel(context, id_simulacro, nivel_str):
    """El documento tiene un nivel de preparación."""
    documento = context.documentos.get(id_simulacro)
    
    if not documento:
        documento = DocumentoRecomendaciones(simulacro_id=id_simulacro)
        context.documentos[id_simulacro] = documento
    
    nivel_map = {
        "Alto": NivelPreparacion.ALTO,
        "Medio": NivelPreparacion.MEDIO,
        "Bajo": NivelPreparacion.BAJO,
    }
    
    documento.nivel_preparacion = nivel_map.get(nivel_str, NivelPreparacion.MEDIO)
    documento.accion_sugerida = AccionSugerida.para_nivel(documento.nivel_preparacion)
    context.documento_actual = documento


@when(r'el migrante consulta su documento de recomendaciones')
def step_migrante_consulta_documento(context):
    """El migrante consulta el documento."""
    context.documento_consultado = context.documento_actual


@then(r'el sistema debe sugerir la siguiente acción posterior: "([^"]*)"')
def step_sistema_sugiere_accion(context, accion_esperada):
    """Verifica la acción sugerida."""
    documento = context.documento_consultado
    
    assert documento.accion_sugerida is not None, "No hay acción sugerida"
    assert documento.accion_sugerida.descripcion == accion_esperada, \
        f"Acción esperada: '{accion_esperada}', actual: '{documento.accion_sugerida.descripcion}'"


# =============================================================================
# ESCENARIO: CONSULTA Y DESCARGA
# =============================================================================

@given(r'que existe un documento de recomendaciones publicado para el simulacro "([^"]*)"')
def step_documento_publicado(context, id_simulacro):
    """Existe un documento publicado."""
    documento = DocumentoRecomendaciones(simulacro_id=id_simulacro)
    documento.metadatos = MetadatosDocumento(
        simulacro_id=id_simulacro,
        nivel_preparacion=NivelPreparacion.MEDIO,
        estado_simulacro=EstadoSimulacro.PUBLICADO,
    )
    documento.publicar()
    
    # Agregar contenido
    documento.fortalezas.append(Fortaleza(descripcion="Buena claridad"))
    documento.puntos_mejora.append(PuntoMejora(
        categoria=CategoriaRecomendacion.SEGURIDAD,
        descripcion="Mejorar seguridad"
    ))
    
    if not hasattr(context, 'documentos'):
        context.documentos = {}
    
    context.documentos[id_simulacro] = documento
    context.documento_actual = documento


@when(r'el migrante accede a la sección "([^"]*)"')
def step_migrante_accede_seccion(context, seccion):
    """El migrante accede a una sección."""
    context.seccion_accedida = seccion


@then(r'el sistema debe mostrar el documento de recomendaciones asociado al simulacro "([^"]*)" con las secciones:')
def step_sistema_muestra_documento_secciones(context, id_simulacro):
    """Verifica que se muestre el documento con las secciones."""
    documento = context.documentos.get(id_simulacro)
    assert documento is not None, f"No hay documento para {id_simulacro}"
    assert documento.esta_publicado(), "El documento no está publicado"
    
    for row in context.table:
        seccion = row['seccion']
        assert documento.tiene_seccion(seccion), \
            f"Sección '{seccion}' no encontrada"


@then(r'debe permitir descargar el documento en formato "([^"]*)"')
def step_permitir_descargar_formato(context, formato_str):
    """Verifica que se pueda descargar en el formato."""
    documento = context.documento_actual
    
    assert documento.puede_descargarse(), "El documento no puede descargarse"
    
    formato_map = {
        "PDF": FormatoDocumento.PDF,
        "HTML": FormatoDocumento.HTML,
    }
    
    formato = formato_map.get(formato_str, FormatoDocumento.PDF)
    
    # Verificar que se puede exportar (la implementación real generaría el archivo)
    try:
        documento.exportar_formato(formato)
    except Exception as e:
        assert False, f"Error al exportar: {e}"
