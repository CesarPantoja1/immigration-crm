"""
Steps para la feature de Generación de Recomendaciones basadas en análisis de IA.

Este módulo implementa los step definitions para validar:
- Generación de documentos de recomendaciones post-simulacro
- Análisis de transcripciones de entrevistas por agente de IA
- Clasificación y priorización de recomendaciones accionables
- Trazabilidad de recomendaciones hacia preguntas específicas
- Cálculo de nivel de preparación del migrante
"""
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
# ANTECEDENTES - Configuración inicial del sistema
# =============================================================================

@given(r'que el módulo de simulacros de entrevista consular está operativo')
def step_modulo_simulacros_operativo(context):
    """Verifica que el módulo de simulacros esté disponible y funcionando."""
    context.simulacros = {}
    context.documentos = {}
    context.analisis = {}
    context.errores = []
    context.modulo_operativo = True


@given(r'el sistema almacena transcripciones en formato .txt de cada simulacro completado')
def step_sistema_almacena_transcripciones(context):
    """Confirma que las transcripciones .txt están habilitadas."""
    context.transcripciones_habilitadas = True
    context.formato_transcripcion = ".txt"


@given(r'el agente de IA para análisis de entrevistas está habilitado')
def step_agente_ia_habilitado(context):
    """Configura el agente de IA."""
    context.agente_ia_habilitado = True


@given(r'la generación de documentos de recomendaciones está disponible')
def step_generacion_documentos_disponible(context):
    """Confirma que la generación de documentos está habilitada."""
    context.generacion_documentos_habilitada = True
    context.formatos_exportacion = [FormatoDocumento.PDF, FormatoDocumento.HTML]


# =============================================================================
# ESCENARIO 1: GENERACIÓN DEL DOCUMENTO DE RECOMENDACIONES
# =============================================================================

@given(r'que el migrante completó el simulacro "([^"]*)" con transcripción disponible')
def step_migrante_completo_simulacro_transcripcion(context, id_simulacro):
    """Registra un simulacro completado con transcripción disponible."""
    if not hasattr(context, 'simulacros'):
        context.simulacros = {}
    
    simulacro = SimulacroParaRecomendaciones(
        id=id_simulacro,
        migrante_id="migrante-001",
        migrante_nombre="Oscar",
    )
    
    # Transcripción en formato .txt
    transcripcion = TranscripcionSimulacro(
        simulacro_id=id_simulacro,
        contenido="""
        Entrevistador: ¿Cuál es el motivo de su viaje?
        Migrante: Quiero estudiar una maestría en ciencias de datos.
        Entrevistador: ¿Cómo financiará sus estudios?
        Migrante: Tengo una beca completa y apoyo familiar documentado.
        """,
        fecha_simulacro=datetime.now()
    )
    simulacro.transcripcion = transcripcion
    
    context.simulacros[id_simulacro] = simulacro
    context.simulacro_actual = simulacro


@given(r'la IA analizó la transcripción del simulacro "([^"]*)" con los siguientes resultados:')
def step_ia_analizo_transcripcion(context, id_simulacro):
    """La IA analizó la transcripción con indicadores de desempeño."""
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
    context.simulacro_actual = simulacro


@when(r'se genera el documento de recomendaciones para el simulacro "([^"]*)"')
def step_genera_documento_para_simulacro(context, id_simulacro):
    """Se genera el documento de recomendaciones con validaciones."""
    simulacro = context.simulacros.get(id_simulacro)
    
    # Validar transcripción disponible
    if not simulacro or not simulacro.transcripcion:
        context.errores.append(
            f"No es posible generar recomendaciones: la transcripción del simulacro {id_simulacro} no está disponible"
        )
        context.documento_generado = False
        return
    
    # Validar análisis completado
    if not simulacro.analisis or not simulacro.analisis.completado:
        context.errores.append(
            f"No es posible generar recomendaciones: el análisis de IA del simulacro {id_simulacro} no se ha completado"
        )
        context.documento_generado = False
        return
    
    # Generar documento
    documento = simulacro.generar_documento_recomendaciones()
    
    if not hasattr(context, 'documentos'):
        context.documentos = {}
    
    context.documentos[id_simulacro] = documento
    context.documento_actual = documento
    context.documento_generado = True


@then(r'el documento tiene estado "([^"]*)"')
def step_documento_tiene_estado(context, estado_esperado):
    """Verifica el estado del documento."""
    documento = context.documento_actual
    assert documento is not None, "No se generó el documento"
    
    # Comparar con el valor del enum o el string del estado
    estado_actual = documento.estado.value if hasattr(documento.estado, 'value') else str(documento.estado)
    # Normalizar para comparación
    estado_esperado_normalizado = estado_esperado.lower().replace(" ", "_")
    estado_actual_normalizado = estado_actual.lower().replace(" ", "_")
    
    assert estado_esperado_normalizado == estado_actual_normalizado, \
        f"Estado esperado: '{estado_esperado}', actual: '{estado_actual}'"


@then(r'el nivel de preparación calculado es "([^"]*)"')
def step_nivel_preparacion_calculado(context, nivel_esperado):
    """Verifica el nivel de preparación calculado."""
    documento = context.documento_actual
    nivel_map = {
        "Alto": NivelPreparacion.ALTO,
        "Medio": NivelPreparacion.MEDIO,
        "Bajo": NivelPreparacion.BAJO,
    }
    nivel_esperado_enum = nivel_map.get(nivel_esperado)
    assert documento.nivel_preparacion == nivel_esperado_enum, \
        f"Nivel esperado: {nivel_esperado}, actual: {documento.nivel_preparacion.value}"


@then(r'el documento contiene las siguientes secciones:')
def step_documento_contiene_secciones(context):
    """Verifica que el documento contiene las secciones requeridas."""
    documento = context.documento_actual
    
    for row in context.table:
        seccion = row['seccion']
        assert documento.tiene_seccion(seccion), \
            f"Sección '{seccion}' no encontrada en el documento"


# =============================================================================
# ESCENARIO 2: RECOMENDACIONES ACCIONABLES POR CATEGORÍA
# =============================================================================

@given(r'que el migrante completó el simulacro "([^"]*)" con transcripción procesada')
def step_migrante_completo_con_transcripcion(context, id_simulacro):
    """El migrante completó simulacro con transcripción procesada."""
    if not hasattr(context, 'simulacros'):
        context.simulacros = {}
    
    simulacro = SimulacroParaRecomendaciones(id=id_simulacro)
    simulacro.transcripcion = TranscripcionSimulacro(
        simulacro_id=id_simulacro,
        contenido="Transcripción del simulacro procesada."
    )
    context.simulacros[id_simulacro] = simulacro
    context.simulacro_actual = simulacro


@given(r'la IA identificó los siguientes puntos de mejora en el simulacro "([^"]*)":')
def step_ia_identifico_puntos_mejora(context, id_simulacro):
    """Configura los puntos de mejora identificados por la IA."""
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
# ESCENARIO 3: NIVEL DE PREPARACIÓN
# =============================================================================

@given(r'el análisis del simulacro "([^"]*)" tiene los siguientes resultados:')
def step_analisis_simulacro_resultados(context, id_simulacro):
    """Configura los resultados del análisis."""
    if not hasattr(context, 'simulacros'):
        context.simulacros = {}
    
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
# ESCENARIO 4: TRAZABILIDAD
# =============================================================================

@given(r'que el simulacro "([^"]*)" tiene las siguientes preguntas y respuestas:')
def step_simulacro_tiene_preguntas(context, id_simulacro):
    """Configura las preguntas del simulacro."""
    if not hasattr(context, 'simulacros'):
        context.simulacros = {}
    
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
    if not hasattr(context, 'documentos'):
        context.documentos = {}
    
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
    
    # Mapeo de nombres amigables a nombres técnicos
    mapeo_atributos = {
        "Número de pregunta": "numero_pregunta_origen",
        "Tipo de pregunta": "tipo_pregunta_origen",
    }
    
    for atributo in atributos_esperados:
        atributo_tecnico = mapeo_atributos.get(atributo, atributo)
        assert atributo_tecnico in atributos_disponibles, \
            f"Atributo '{atributo}' no disponible en el documento"


# =============================================================================
# ESCENARIO 5: CLASIFICACIÓN POR IMPACTO
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
# ESCENARIO 6: ACCIÓN SUGERIDA
# =============================================================================

@given(r'que el documento de recomendaciones del simulacro "([^"]*)" tiene nivel de preparación "([^"]*)"')
def step_documento_tiene_nivel(context, id_simulacro, nivel_str):
    """El documento tiene un nivel de preparación."""
    if not hasattr(context, 'documentos'):
        context.documentos = {}
    
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
# ESCENARIO 7: CONSULTA Y DESCARGA
# =============================================================================

@given(r'que existe un documento de recomendaciones publicado para el simulacro "([^"]*)"')
def step_documento_publicado(context, id_simulacro):
    """Existe un documento publicado."""
    if not hasattr(context, 'documentos'):
        context.documentos = {}
    
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
    
    # Verificar que se puede exportar
    try:
        documento.exportar_formato(formato)
    except Exception as e:
        assert False, f"Error al exportar: {e}"


# =============================================================================
# ESCENARIOS 8 y 9: MANEJO DE ERRORES
# =============================================================================

@given(r'que el migrante completó el simulacro "([^"]*)" sin transcripción generada')
def step_simulacro_sin_transcripcion(context, id_simulacro):
    """El simulacro no tiene transcripción."""
    if not hasattr(context, 'simulacros'):
        context.simulacros = {}
    
    simulacro = SimulacroParaRecomendaciones(id=id_simulacro)
    # No asignar transcripción
    simulacro.transcripcion = None
    context.simulacros[id_simulacro] = simulacro


@when(r'se intenta generar el documento de recomendaciones para el simulacro "([^"]*)"')
def step_intenta_generar_documento(context, id_simulacro):
    """Se intenta generar el documento (puede fallar)."""
    simulacro = context.simulacros.get(id_simulacro)
    
    # Validar transcripción disponible
    if not simulacro or not simulacro.transcripcion:
        context.errores.append(
            f"No es posible generar recomendaciones: la transcripción del simulacro {id_simulacro} no está disponible"
        )
        context.documento_generado = False
        return
    
    # Validar análisis completado
    if not simulacro.analisis or not simulacro.analisis.completado:
        context.errores.append(
            f"No es posible generar recomendaciones: el análisis de IA del simulacro {id_simulacro} no se ha completado"
        )
        context.documento_generado = False
        return
    
    # Si pasó validaciones, generar
    documento = simulacro.generar_documento_recomendaciones()
    if not hasattr(context, 'documentos'):
        context.documentos = {}
    context.documentos[id_simulacro] = documento
    context.documento_actual = documento
    context.documento_generado = True


@given(r'el análisis de IA del simulacro "([^"]*)" está incompleto')
def step_analisis_incompleto(context, id_simulacro):
    """El análisis de IA está incompleto."""
    simulacro = context.simulacros.get(id_simulacro)
    if simulacro:
        # Crear análisis pero NO marcarlo como completado
        simulacro.analisis = AnalisisIA(simulacro_id=id_simulacro)
        # No llamar a marcar_completado()


@then(r'el sistema debe mostrar el mensaje de error "([^"]*)"')
def step_sistema_muestra_error(context, mensaje_esperado):
    """Verifica que se muestre el mensaje de error."""
    assert len(context.errores) > 0, "No se registró ningún error"
    assert mensaje_esperado in context.errores, \
        f"Mensaje esperado: '{mensaje_esperado}', errores: {context.errores}"


@then(r'el documento no debe ser generado')
def step_documento_no_generado(context):
    """Verifica que el documento no fue generado."""
    assert context.documento_generado == False, "El documento fue generado cuando no debía"
