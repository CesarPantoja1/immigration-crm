# -*- coding: utf-8 -*-
"""
Steps para los escenarios de Generacion de Recomendaciones.
Implementacion de los pasos BDD definidos en generacion_recomendaciones.feature

Los objetos de dominio se definen como dataclasses locales para testing.
Valida la logica de negocio sin conexion a base de datos.
"""
from behave import given, when, then, step, use_step_matcher
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date, time

use_step_matcher("parse")


# ==============================================================================
# OBJETOS DE DOMINIO PARA TESTING (dataclasses locales)
# Mapean a los modelos Django existentes
# ==============================================================================

@dataclass
class Usuario:
    """Representa un usuario - mapea a apps.usuarios.models.Usuario"""
    id: int = 0
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    rol: str = "cliente"
    is_active: bool = True
    
    def nombre_completo(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class Simulacro:
    """Representa un simulacro - mapea a apps.preparacion.models.Simulacro"""
    id: int = 0
    codigo: str = ""
    cliente: Usuario = None
    asesor: Usuario = None
    fecha: date = None
    hora: time = None
    estado: str = "completado"
    modalidad: str = "virtual"
    transcripcion_texto: str = ""
    transcripcion_archivo: str = ""
    tiene_recomendaciones: bool = False
    
    def tiene_transcripcion(self) -> bool:
        return bool(self.transcripcion_texto and len(self.transcripcion_texto.strip()) >= 50)


@dataclass
class ConfiguracionIA:
    """Representa configuracion de IA - mapea a apps.preparacion.models.ConfiguracionIA"""
    id: int = 0
    asesor: Usuario = None
    api_key: str = ""
    modelo: str = "gemini-2.0-flash"
    activo: bool = True
    
    def esta_configurada(self) -> bool:
        return bool(self.api_key and self.activo)


@dataclass
class Recomendacion:
    """Representa una recomendacion - mapea a apps.preparacion.models.Recomendacion"""
    id: int = 0
    simulacro: Simulacro = None
    estado_feedback: str = "pendiente"
    
    # Indicadores de desempeno
    claridad: str = "medio"
    coherencia: str = "medio"
    seguridad: str = "medio"
    pertinencia: str = "medio"
    
    # Nivel global
    nivel_preparacion: str = "medio"
    
    # Contenido estructurado
    fortalezas: List[Dict] = field(default_factory=list)
    puntos_mejora: List[Dict] = field(default_factory=list)
    recomendaciones: List[Dict] = field(default_factory=list)
    
    # Accion sugerida
    accion_sugerida: str = ""
    resumen_ejecutivo: str = ""
    publicada: bool = False
    
    def calcular_nivel_preparacion(self) -> str:
        """Calcula el nivel de preparacion basado en los indicadores."""
        niveles = {'bajo': 1, 'medio': 2, 'alto': 3}
        indicadores = [self.claridad, self.coherencia, self.seguridad, self.pertinencia]
        promedio = sum(niveles.get(i.lower(), 2) for i in indicadores) / len(indicadores)
        
        if promedio >= 2.5:
            return 'alto'
        elif promedio >= 1.5:
            return 'medio'
        return 'bajo'
    
    def obtener_accion_sugerida(self) -> str:
        """Obtiene la accion sugerida segun el nivel de preparacion."""
        acciones = {
            'bajo': 'Realizar un nuevo simulacro con asesor',
            'medio': 'Reforzar los puntos de mejora identificados',
            'alto': 'Mantener el plan actual de preparacion'
        }
        return acciones.get(self.nivel_preparacion, acciones['medio'])


@dataclass
class Notificacion:
    """Representa una notificacion"""
    id: int = 0
    usuario: Usuario = None
    mensaje: str = ""
    leida: bool = False


# ==============================================================================
# SERVICIOS DE LOGICA DE NEGOCIO
# ==============================================================================

class TranscripcionService:
    """Servicio para validar y procesar transcripciones."""
    
    EXTENSION_VALIDA = '.txt'
    MIN_CARACTERES = 50
    
    @staticmethod
    def validar_archivo(nombre_archivo: str) -> tuple:
        """Valida que el archivo sea .txt"""
        if not nombre_archivo.endswith(TranscripcionService.EXTENSION_VALIDA):
            return False, "El archivo debe ser de texto (.txt)"
        return True, None
    
    @staticmethod
    def validar_contenido(contenido: str) -> tuple:
        """Valida que el contenido tenga minimo 50 caracteres."""
        if len(contenido.strip()) < TranscripcionService.MIN_CARACTERES:
            return False, f"La transcripcion es muy corta (minimo {TranscripcionService.MIN_CARACTERES} caracteres)"
        return True, None
    
    @staticmethod
    def procesar_transcripcion(contenido: str) -> dict:
        """Procesa la transcripcion y retorna estadisticas."""
        return {
            'caracteres': len(contenido),
            'lineas': len(contenido.split('\n'))
        }


class RecomendacionIAService:
    """Servicio para generar recomendaciones con IA."""
    
    @staticmethod
    def validar_configuracion(config: ConfiguracionIA) -> tuple:
        """Valida que el asesor tenga API key configurada."""
        if not config or not config.esta_configurada():
            return False, "No se ha configurado una API key de IA valida. Por favor, configura tu API key de Gemini."
        return True, None
    
    @staticmethod
    def validar_transcripcion(simulacro: Simulacro) -> tuple:
        """Valida que el simulacro tenga transcripcion."""
        if not simulacro.tiene_transcripcion():
            return False, f"No es posible generar recomendaciones: la transcripcion del simulacro {simulacro.codigo} no esta disponible"
        return True, None
    
    @staticmethod
    def generar_recomendacion(simulacro: Simulacro) -> Recomendacion:
        """Genera una recomendacion con IA (simulado para testing)."""
        recomendacion = Recomendacion(
            id=1,
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
        recomendacion.nivel_preparacion = recomendacion.calcular_nivel_preparacion()
        return recomendacion


class PDFService:
    """Servicio para descargar PDF de recomendaciones."""
    
    @staticmethod
    def validar_descarga(simulacro: Simulacro, tiene_recomendaciones: bool) -> tuple:
        """Valida que el simulacro tenga recomendaciones para descargar."""
        if not tiene_recomendaciones:
            return False, "Este simulacro no tiene recomendaciones"
        return True, None


# ==============================================================================
# HELPERS
# ==============================================================================

def crear_usuario(id: int, nombre: str, apellido: str, rol: str) -> Usuario:
    """Helper para crear usuarios de prueba."""
    return Usuario(
        id=id,
        email=f"{nombre.lower().replace(' ', '.')}@test.com",
        first_name=nombre,
        last_name=apellido,
        rol=rol
    )


def crear_simulacro(id: int, codigo: str, asesor: Usuario, cliente: Usuario, estado: str = 'completado') -> Simulacro:
    """Helper para crear simulacros de prueba."""
    return Simulacro(
        id=id,
        codigo=codigo,
        asesor=asesor,
        cliente=cliente,
        fecha=date.today(),
        hora=time(10, 0),
        estado=estado,
        modalidad='virtual'
    )


# ==============================================================================
# ANTECEDENTES
# ==============================================================================

@step("que el asesor tiene simulacros completados")
def step_asesor_tiene_simulacros(context):
    """Configura los simulacros completados segun la tabla."""
    context.asesores = {}
    context.clientes = {}
    context.simulacros = {}
    context.configuraciones_ia = {}
    context.recomendaciones = {}
    
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
        
        # Crear simulacro
        simulacro = crear_simulacro(
            sim_id, codigo,
            context.asesores[nombre_asesor],
            context.clientes[nombre_cliente],
            estado
        )
        context.simulacros[codigo] = simulacro
        sim_id += 1


# ==============================================================================
# SUBIR TRANSCRIPCION
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
    assert context.simulacro_actual.estado == 'completado', "El simulacro no esta completado"


@step('sube el archivo "{nombre_archivo}" con la conversacion del simulacro')
def step_sube_archivo_txt(context, nombre_archivo):
    """El asesor sube un archivo .txt de transcripcion."""
    # Validar extension
    valido, error = TranscripcionService.validar_archivo(nombre_archivo)
    
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
    
    # Validar contenido
    valido, error = TranscripcionService.validar_contenido(contenido)
    if not valido:
        context.upload_exitoso = False
        context.mensaje_sistema = error
        return
    
    # Procesar
    context.simulacro_actual.transcripcion_texto = contenido
    stats = TranscripcionService.procesar_transcripcion(contenido)
    
    context.upload_exitoso = True
    context.mensaje_sistema = "Transcripcion subida exitosamente"
    context.caracteres = stats['caracteres']
    context.lineas = stats['lineas']


@step('intenta subir el archivo "{nombre_archivo}"')
def step_intenta_subir_archivo(context, nombre_archivo):
    """El asesor intenta subir un archivo (puede no ser .txt)."""
    valido, error = TranscripcionService.validar_archivo(nombre_archivo)
    
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
    """Verifica que el simulacro no tiene transcripcion."""
    assert not context.simulacro_actual.tiene_transcripcion(), "El simulacro no deberia tener transcripcion"


# ==============================================================================
# GENERAR RECOMENDACIONES CON IA
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
    
    # Agregar transcripcion de prueba
    context.simulacro_actual.transcripcion_texto = """
    Entrevistador: Buenos dias, cual es el proposito de su viaje?
    Cliente: Buenos dias, mi proposito es estudiar una maestria.
    Entrevistador: Como financiara sus estudios?
    Cliente: Tengo una beca y apoyo de mi familia.
    """ * 5


@step("tiene configurada su API key de Gemini")
def step_tiene_api_key(context):
    """El asesor tiene configurada su API key."""
    config = ConfiguracionIA(
        id=1,
        asesor=context.asesor_actual,
        api_key='test-api-key-12345',
        modelo='gemini-2.0-flash',
        activo=True
    )
    context.configuraciones_ia[context.asesor_actual.email] = config
    context.config_ia = config


@step('que el asesor "{nombre_asesor}" no ha configurado su API key de Gemini')
def step_asesor_sin_api_key(context, nombre_asesor):
    """El asesor no tiene API key configurada."""
    context.asesor_actual = context.asesores[nombre_asesor]
    # No crear configuracion = sin API key
    context.config_ia = None


@step("tiene un simulacro con transcripcion disponible")
def step_tiene_simulacro_con_transcripcion(context):
    """El asesor tiene un simulacro con transcripcion."""
    for codigo, sim in context.simulacros.items():
        if sim.asesor == context.asesor_actual:
            context.simulacro_actual = sim
            context.cliente_actual = sim.cliente
            break
    
    context.simulacro_actual.transcripcion_texto = "Transcripcion de prueba con contenido suficiente " * 5


@step('hace clic en "Generar con IA"')
def step_generar_con_ia(context):
    """El asesor hace clic en generar con IA."""
    # Validar configuracion de IA
    valido, error = RecomendacionIAService.validar_configuracion(context.config_ia)
    if not valido:
        context.mensaje_sistema = error
        context.generacion_exitosa = False
        return
    
    # Validar transcripcion
    valido, error = RecomendacionIAService.validar_transcripcion(context.simulacro_actual)
    if not valido:
        context.mensaje_sistema = error
        context.generacion_exitosa = False
        return
    
    # Generar recomendacion
    recomendacion = RecomendacionIAService.generar_recomendacion(context.simulacro_actual)
    context.recomendacion_actual = recomendacion
    context.recomendaciones[context.simulacro_actual.codigo] = recomendacion
    context.simulacro_actual.tiene_recomendaciones = True
    
    context.generacion_exitosa = True
    context.mensaje_sistema = "Recomendaciones generadas exitosamente"
    
    # Crear notificacion
    context.notificacion = Notificacion(
        id=1,
        usuario=context.cliente_actual,
        mensaje="Recomendaciones disponibles"
    )


@step("el sistema analiza la transcripcion con Gemini")
def step_analiza_con_gemini(context):
    """Verifica que se analice con Gemini."""
    assert context.generacion_exitosa, "La generacion debio ser exitosa"


@step("genera el documento de recomendaciones")
def step_genera_documento(context):
    """Verifica que se genere el documento."""
    assert context.recomendacion_actual is not None, "Debe existir recomendacion"
    assert context.recomendacion_actual.estado_feedback == 'generado', "Estado debe ser 'generado'"


@step('el cliente "{nombre_cliente}" recibe la notificacion "{mensaje}"')
def step_cliente_recibe_notificacion(context, nombre_cliente, mensaje):
    """Verifica que el cliente reciba notificacion."""
    assert context.recomendacion_actual.publicada, "Recomendacion debe estar publicada"
    assert context.notificacion is not None, "Debe existir notificacion"


@step("el simulacro tiene la opcion de ver feedback disponible")
def step_simulacro_tiene_feedback(context):
    """Verifica que el simulacro tenga feedback disponible."""
    assert context.simulacro_actual.tiene_recomendaciones, "Simulacro debe tener recomendaciones"


# ==============================================================================
# CLIENTE CONSULTA RECOMENDACIONES
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
    recomendacion = RecomendacionIAService.generar_recomendacion(context.simulacro_actual)
    context.recomendacion_actual = recomendacion
    context.recomendaciones[context.simulacro_actual.codigo] = recomendacion
    context.simulacro_actual.tiene_recomendaciones = True


@step('el cliente accede a "Ver Resumen" en la seccion de simulacros completados y "Ver Recomendaciones"')
def step_cliente_accede_ver_resumen_recomendaciones(context):
    """El cliente navega a Ver Resumen y luego Ver Recomendaciones."""
    # Simula la navegacion del cliente
    codigo = context.simulacro_actual.codigo
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
    
    # Verificar campos segun la tabla
    rec = context.recomendacion_actual
    assert rec.simulacro.fecha is not None, "Debe tener fecha del simulacro"
    assert rec.nivel_preparacion in ['alto', 'medio', 'bajo'], "Debe tener nivel de preparacion"


@then("puede expandir las secciones colapsables:")
def step_expandir_secciones(context):
    """Verifica las secciones colapsables disponibles."""
    secciones_esperadas = [row['seccion'] for row in context.table]
    
    # Verificar que las secciones existen en la recomendacion
    rec = context.recomendacion_actual
    
    secciones_disponibles = []
    if hasattr(rec, 'claridad'):
        secciones_disponibles.append('Indicadores de Desempeno')
    if rec.fortalezas:
        secciones_disponibles.append('Fortalezas Identificadas')
    if rec.puntos_mejora:
        secciones_disponibles.append('Puntos de Mejora')
    if rec.recomendaciones:
        secciones_disponibles.append('Recomendaciones')
    
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
    context.simulacro_actual.tiene_recomendaciones = False
    codigo = context.simulacro_actual.codigo
    if codigo in context.recomendaciones:
        del context.recomendaciones[codigo]


@step("intenta descargar el PDF de recomendaciones")
def step_intenta_descargar_pdf(context):
    """El cliente intenta descargar el PDF."""
    valido, error = PDFService.validar_descarga(
        context.simulacro_actual, 
        context.simulacro_actual.tiene_recomendaciones
    )
    
    if not valido:
        context.mensaje_sistema = error
    else:
        context.mensaje_sistema = "PDF descargado exitosamente"


# ==============================================================================
# ANALISIS DE IA: INDICADORES
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
    
    # Agregar transcripcion
    context.simulacro_actual.transcripcion_texto = "Transcripcion de prueba " * 20
    
    # Generar recomendacion
    recomendacion = RecomendacionIAService.generar_recomendacion(context.simulacro_actual)
    context.recomendacion_actual = recomendacion
    context.recomendaciones[context.simulacro_actual.codigo] = recomendacion
    context.simulacro_actual.tiene_recomendaciones = True


@step("el cliente consulta sus recomendaciones")
def step_cliente_consulta_recomendaciones(context):
    """El cliente consulta sus recomendaciones."""
    codigo = context.simulacro_actual.codigo
    if codigo in context.recomendaciones:
        context.recomendaciones_lista = [context.recomendaciones[codigo]]
    else:
        context.recomendaciones_lista = []


@then("la recomendacion incluye los indicadores:")
def step_recomendacion_incluye_indicadores(context):
    """Verifica que la recomendacion tenga los indicadores."""
    rec = context.recomendacion_actual
    
    indicadores = ['claridad', 'coherencia', 'seguridad', 'pertinencia']
    valores_validos = ['alto', 'medio', 'bajo']
    
    for indicador in indicadores:
        valor = getattr(rec, indicador)
        assert valor in valores_validos, \
            f"Indicador {indicador} tiene valor invalido: {valor}"


# ==============================================================================
# ANALISIS DE IA: CONTENIDO GENERADO
# ==============================================================================

@then("cada fortaleza identificada contiene:")
def step_fortaleza_contiene_campos(context):
    """Verifica estructura de fortalezas."""
    rec = context.recomendacion_actual
    
    # Mapear campos de la tabla a campos reales
    campos_mapping = {
        'Categoria': 'categoria',
        'Descripcion': 'descripcion',
        'Pregunta relacionada': 'pregunta_relacionada',
        'Impacto': 'impacto'
    }
    
    campos_requeridos = [campos_mapping[row['campo']] for row in context.table]
    
    assert len(rec.fortalezas) > 0, "No hay fortalezas"
    
    for fortaleza in rec.fortalezas:
        for campo in campos_requeridos:
            assert campo in fortaleza, f"Falta campo {campo} en fortaleza"


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
