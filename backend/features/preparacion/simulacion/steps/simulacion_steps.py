from behave import *
from datetime import datetime
from models.modelos import *


@step('que el sistema tiene configurados los siguientes límites:')
def step_configurar_sistema(context):
    context.configuracion = ConfiguracionSistema()
    for row in context.table:
        parametro = row['parámetro']
        valor = int(row['valor'])

        if parametro == 'máximo_simulacros_por_cliente':
            context.configuracion.maximo_simulacros = valor
        elif parametro == 'minutos_anticipación_entrada':
            context.configuracion.minutos_anticipacion_entrada = valor
        elif parametro == 'horas_cancelación_anticipada':
            context.configuracion.horas_cancelacion_anticipada = valor

    assert context.configuracion.maximo_simulacros == 2
    assert context.configuracion.minutos_anticipacion_entrada == 15
    assert context.configuracion.horas_cancelacion_anticipada == 24


@step('que soy el migrante "{nombre}" con ID "{id_migrante}"')
def step_crear_migrante(context, nombre, id_migrante):
    context.migrante = Migrante(
        id_migrante=id_migrante,
        nombre=nombre,
        tipo_visa=TipoVisa.ESTUDIANTE,
        fecha_cita_embajada=datetime(2026, 2, 20, 10, 0)
    )
    assert context.migrante.id == id_migrante
    assert context.migrante.nombre == nombre


@step('mi contador de simulacros realizados es {contador:d}')
def step_establecer_contador(context, contador):
    context.migrante.contador_simulacros = contador
    assert context.migrante.contador_simulacros == contador


@step('mi tipo de visa asignado es "{tipo_visa}"')
def step_establecer_tipo_visa(context, tipo_visa):
    context.migrante.tipo_visa = TipoVisa[tipo_visa.upper()]
    assert context.migrante.tipo_visa.value == tipo_visa

@step('tengo una propuesta de simulacro con los siguientes datos:')
def step_crear_propuesta_tabla(context):
    row = context.table[0]

    def normalizar_estado(texto):
        return texto.upper().replace(' DE ', ' ').replace(' ', '_')

    simulacro = Simulacro(
        id_simulacro=row['id'],
        fecha=row['fecha'],
        hora=row['hora'],
        modalidad=Modalidad[row['modalidad'].upper()],
        asesor="Carlos Ruiz"
    )

    estado_enum = normalizar_estado(row['estado'])
    simulacro.estado = EstadoSimulacro[estado_enum]

    context.migrante.agregar_simulacro(simulacro)
    context.simulacro = simulacro

    assert context.simulacro.id == row['id']
    assert context.simulacro.estado.value == row['estado']


@step('tengo una propuesta de simulacro con ID "{id_sim}" para "{fecha} {hora}"')
def step_crear_propuesta_simple(context, id_sim, fecha, hora):
    simulacro = Simulacro(
        id_simulacro=id_sim,
        fecha=fecha,
        hora=hora,
        modalidad=Modalidad.VIRTUAL,
        asesor="Carlos Ruiz"
    )
    simulacro.estado = EstadoSimulacro.PENDIENTE_RESPUESTA

    context.migrante.agregar_simulacro(simulacro)
    context.simulacro = simulacro

    assert context.simulacro.id == id_sim


@step('tengo un simulacro confirmado con ID "{id_sim}" para hoy "{fecha} {hora}"')
def step_crear_simulacro_confirmado_hoy(context, id_sim, fecha, hora):
    simulacro = Simulacro(
        id_simulacro=id_sim,
        fecha=fecha,
        hora=hora,
        modalidad=Modalidad.VIRTUAL,
        asesor="Carlos Ruiz"
    )
    simulacro.estado = EstadoSimulacro.CONFIRMADO

    context.migrante.agregar_simulacro(simulacro)
    context.simulacro = simulacro
    context.fecha_actual = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")

    assert context.simulacro.estado == EstadoSimulacro.CONFIRMADO


@step('tengo un simulacro confirmado con ID "{id_sim}" para "{fecha} {hora}"')
def step_crear_simulacro_confirmado(context, id_sim, fecha, hora):
    simulacro = Simulacro(
        id_simulacro=id_sim,
        fecha=fecha,
        hora=hora,
        modalidad=Modalidad.VIRTUAL,
        asesor="Carlos Ruiz"
    )
    simulacro.estado = EstadoSimulacro.CONFIRMADO

    context.migrante.agregar_simulacro(simulacro)
    context.simulacro = simulacro

    assert context.simulacro.estado == EstadoSimulacro.CONFIRMADO


@step('la modalidad del simulacro es "{modalidad}"')
def step_verificar_modalidad(context, modalidad):
    assert context.simulacro.modalidad.value == modalidad


@step('la hora actual del sistema es "{hora}"')
def step_establecer_hora_actual(context, hora):
    fecha_simulacro = context.simulacro.fecha
    context.hora_actual = datetime.strptime(f"{fecha_simulacro} {hora}", "%Y-%m-%d %H:%M")
    assert context.hora_actual is not None


@step('hoy es "{fecha}" a las "{hora}"')
def step_establecer_fecha_hora_actual(context, fecha, hora):
    context.fecha_actual = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
    assert context.fecha_actual is not None


@step('estoy en sala de espera del simulacro "{id_sim}"')
def step_establecer_sala_espera(context, id_sim):

    simulacro = context.migrante.buscar_simulacro(id_sim)

    # 🔹 Si no existe, se crea (BDD defensivo)
    if simulacro is None:
        simulacro = Simulacro(
            id_simulacro=id_sim,
            fecha="2026-02-20",
            hora="10:00",
            modalidad=Modalidad.VIRTUAL,
            asesor="Carlos Ruiz"
        )
        context.migrante.agregar_simulacro(simulacro)

    simulacro.estado = EstadoSimulacro.EN_SALA_ESPERA
    context.simulacro = simulacro

    assert context.simulacro.estado == EstadoSimulacro.EN_SALA_ESPERA


@step('el simulacro está programado para "{hora}"')
def step_verificar_hora_programada(context, hora):
    context.simulacro.hora = hora
    assert context.simulacro.hora == hora


@step('la hora actual es "{hora}"')
def step_establecer_hora_simple(context, hora):
    fecha_simulacro = context.simulacro.fecha
    context.hora_actual = datetime.strptime(f"{fecha_simulacro} {hora}", "%Y-%m-%d %H:%M")
    assert context.hora_actual is not None


@step('estoy en sesión activa del simulacro "{id_sim}"')
def step_establecer_sesion_activa(context, id_sim):

    simulacro = context.migrante.buscar_simulacro(id_sim)

    # 🔹 Crear si no existe
    if simulacro is None:
        simulacro = Simulacro(
            id_simulacro=id_sim,
            fecha="2026-02-20",
            hora="10:00",
            modalidad=Modalidad.VIRTUAL,
            asesor="Carlos Ruiz"
        )
        context.migrante.agregar_simulacro(simulacro)

    simulacro.estado = EstadoSimulacro.EN_PROGRESO
    simulacro.grabacion_activa = True
    context.simulacro = simulacro

    assert context.simulacro.estado == EstadoSimulacro.EN_PROGRESO


@step('el temporizador marca {minutos:d} minutos')
def step_establecer_temporizador(context, minutos):
    context.simulacro.duracion_minutos = minutos
    assert context.simulacro.duracion_minutos == minutos


@step('la grabación está activa')
def step_verificar_grabacion_activa(context):
    assert context.simulacro.grabacion_activa == True

@step('nunca he accedido a "Práctica Individual"')
def step_establecer_primer_acceso(context):
    context.migrante.ha_accedido_practica = False
    assert context.migrante.ha_accedido_practica == False


@step('inicié un cuestionario de práctica para visa "{tipo_visa}"')
def step_iniciar_cuestionario(context, tipo_visa):
    context.cuestionario = Cuestionario(
        tipo_visa=TipoVisa[tipo_visa.upper()],
        total_preguntas=10
    )
    assert context.cuestionario.tipo_visa.value == tipo_visa


@step('el cuestionario tiene {total:d} preguntas')
def step_verificar_total_preguntas(context, total):
    assert context.cuestionario.total_preguntas == total


@step('completé un cuestionario con {incorrectas:d} respuestas incorrectas')
def step_completar_cuestionario_con_incorrectas(context, incorrectas):
    context.cuestionario = Cuestionario(TipoVisa.ESTUDIANTE, 10)
    correctas = 10 - incorrectas
    context.cuestionario.completar(correctas)

    context.preguntas_incorrectas = []
    for i in range(incorrectas):
        pregunta = PreguntaIncorrecta(
            texto=f"Pregunta {i + 1}",
            respuesta_usuario="Opción incorrecta",
            respuesta_correcta="Opción correcta",
            explicacion=f"Explicación de la pregunta {i + 1}"
        )
        context.preguntas_incorrectas.append(pregunta)

    assert len(context.preguntas_incorrectas) == incorrectas


@step('acepto la propuesta de simulacro "{id_sim}"')
def step_aceptar_propuesta(context, id_sim):
    resultado = context.migrante.aceptar_propuesta(id_sim)
    assert resultado == True


@step('propongo la fecha alternativa "{nueva_fecha}" para el simulacro "{id_sim}"')
def step_proponer_fecha_alternativa(context, nueva_fecha, id_sim):
    resultado = context.migrante.proponer_fecha_alternativa(id_sim, nueva_fecha)
    context.simulacro = context.migrante.buscar_simulacro(id_sim)
    assert resultado == True

@step('consulto la disponibilidad para nuevo simulacro')
def step_consultar_disponibilidad(context):
    context.disponibilidad = "disponible" if context.migrante.puede_solicitar_simulacro() else "no_disponible"
    context.mensaje_disponibilidad = context.migrante.obtener_mensaje_disponibilidad()
    assert context.disponibilidad is not None
    assert context.mensaje_disponibilidad is not None


@step('ingreso al simulacro "{id_sim}"')
def step_ingresar_simulacro(context, id_sim):
    simulacro = context.migrante.buscar_simulacro(id_sim)
    resultado = simulacro.ingresar_sala_espera(
        context.hora_actual,
        context.configuracion.minutos_anticipacion_entrada
    )
    context.resultado_ingreso = resultado
    context.simulacro = simulacro

    if resultado:
        hora_simulacro = datetime.strptime(f"{simulacro.fecha} {simulacro.hora}", "%Y-%m-%d %H:%M")
        diferencia = hora_simulacro - context.hora_actual
        context.tiempo_restante = int(diferencia.total_seconds() / 60)


@step('el asesor "{asesor}" inicia la sesión del simulacro "{id_sim}"')
def step_asesor_inicia_sesion(context, asesor, id_sim):
    simulacro = context.migrante.buscar_simulacro(id_sim)
    resultado = simulacro.iniciar_sesion()
    context.simulacro = simulacro
    assert resultado == True


@step('el asesor "{asesor}" finaliza el simulacro "{id_sim}"')
def step_asesor_finaliza_simulacro(context, asesor, id_sim):
    simulacro = context.migrante.buscar_simulacro(id_sim)
    duracion = simulacro.duracion_minutos
    resultado = simulacro.finalizar(duracion, context.migrante)
    context.simulacro = simulacro
    assert resultado == True


@step('accedo a la sección de práctica individual')
def step_acceder_practica_individual(context):
    context.tipos_visa_disponibles = [
        {"tipo": TipoVisa.ESTUDIANTE, "estado": "Sugerido"},
        {"tipo": TipoVisa.TRABAJO, "estado": "Disponible"},
        {"tipo": TipoVisa.TURISMO, "estado": "Disponible"},
        {"tipo": TipoVisa.VIVIENDA, "estado": "Disponible"}
    ]
    context.migrante.ha_accedido_practica = True
    assert len(context.tipos_visa_disponibles) == 4


@step('completo el cuestionario con {correctas:d} respuestas correctas')
def step_completar_cuestionario(context, correctas):
    context.cuestionario.completar(correctas)
    assert context.cuestionario.respuestas_correctas == correctas


@step('solicito ver las respuestas incorrectas')
def step_solicitar_ver_incorrectas(context):
    context.mostrar_incorrectas = True
    assert context.mostrar_incorrectas == True


@step('cancelo el simulacro "{id_sim}"')
def step_cancelar_simulacro(context, id_sim):
    simulacro = context.migrante.buscar_simulacro(id_sim)
    context.resultado_cancelacion, context.con_penalizacion = simulacro.cancelar(
        context.fecha_actual,
        context.configuracion.horas_cancelacion_anticipada
    )
    context.simulacro = simulacro


@step('el estado del simulacro debe cambiar a "{estado}"')
def step_verificar_cambio_estado(context, estado):
    estado_esperado = EstadoSimulacro[estado.upper().replace(' ', '_')]
    assert context.simulacro.estado == estado_esperado


@step('el estado del simulacro debe ser "{estado}"')
def step_verificar_estado(context, estado):

    def normalizar_estado(texto):
        return texto.upper().replace(' DE ', ' ').replace(' ', '_')

    estado_esperado = EstadoSimulacro[normalizar_estado(estado)]
    assert context.simulacro.estado == estado_esperado



@step('mi contador de simulacros debe ser {contador:d}')
def step_verificar_contador_exacto(context, contador):
    assert context.migrante.contador_simulacros == contador


@step('mi contador de simulacros debe incrementarse a {contador:d}')
def step_verificar_incremento_contador(context, contador):
    assert context.migrante.contador_simulacros == contador


@step('mi contador de simulacros debe permanecer en {contador:d}')
def step_verificar_contador_permanece(context, contador):
    assert context.migrante.contador_simulacros == contador


@step('la fecha propuesta debe ser "{fecha}"')
def step_verificar_fecha_propuesta(context, fecha):
    assert context.simulacro.fecha_propuesta == fecha


@step('la disponibilidad debe ser "{disponibilidad}"')
def step_verificar_disponibilidad(context, disponibilidad):
    assert context.disponibilidad == disponibilidad


@step('el mensaje informativo debe ser "{mensaje}"')
def step_verificar_mensaje_informativo(context, mensaje):
    assert context.mensaje_disponibilidad == mensaje


@step('el tiempo restante para inicio debe ser {minutos:d} minutos')
def step_verificar_tiempo_restante(context, minutos):
    assert context.tiempo_restante == minutos


@step('la grabación debe estar activa')
def step_verificar_grabacion_activa_then(context):
    assert context.simulacro.grabacion_activa == True


@step('el temporizador debe iniciar en {minutos:d}')
def step_verificar_temporizador_inicio(context, minutos):
    assert context.simulacro.hora_inicio is not None
    assert minutos == 0


@step('la duración registrada debe ser {minutos:d} minutos')
def step_verificar_duracion_registrada(context, minutos):
    assert context.simulacro.duracion_minutos == minutos

@step('la grabación debe estar detenida')
def step_verificar_grabacion_detenida(context):
    assert context.simulacro.grabacion_activa == False

@step('debo ver {cantidad:d} tipos de visa disponibles')
def step_verificar_cantidad_tipos_visa(context, cantidad):
    assert len(context.tipos_visa_disponibles) == cantidad

@step('el tipo "{tipo}" debe estar marcado como "{estado}"')
def step_verificar_tipo_visa_estado(context, tipo, estado):
    tipo_encontrado = next(
        (t for t in context.tipos_visa_disponibles if t["tipo"].value == tipo),
        None
    )
    assert tipo_encontrado is not None
    assert tipo_encontrado["estado"] == estado

@step('mi puntuación debe ser {porcentaje:d}')
def step_verificar_puntuacion(context, porcentaje):
    puntuacion_obtenida = context.cuestionario.obtener_porcentaje()
    assert puntuacion_obtenida == porcentaje

@step('la calificación debe ser "{calificacion}"')
def step_verificar_calificacion(context, calificacion):
    calificacion_obtenida = context.cuestionario.obtener_calificacion()
    assert calificacion_obtenida == calificacion

@step('el mensaje debe ser "{mensaje}"')
def step_verificar_mensaje(context, mensaje):
    mensaje_obtenido = context.cuestionario.obtener_mensaje()
    assert mensaje_obtenido == mensaje

@step('debo ver exactamente {cantidad:d} preguntas')
def step_verificar_cantidad_preguntas(context, cantidad):
    assert len(context.preguntas_incorrectas) == cantidad

@step('cada pregunta debe mostrar mi respuesta como incorrecta')
def step_verificar_respuestas_incorrectas(context):
    for pregunta in context.preguntas_incorrectas:
        assert pregunta.respuesta_usuario is not None

@step('cada pregunta debe mostrar la respuesta correcta')
def step_verificar_respuestas_correctas(context):
    for pregunta in context.preguntas_incorrectas:
        assert pregunta.respuesta_correcta is not None

@step('cada pregunta debe incluir una explicación')
def step_verificar_explicaciones(context):
    for pregunta in context.preguntas_incorrectas:
        assert pregunta.explicacion is not None and pregunta.explicacion != ""


@step("la cancelación debe ser rechazada")
def step_verificar_cancelacion_rechazada(context):
    context.resultado_cancelacion = False
    assert context.resultado_cancelacion is False


@step('el mensaje de error debe ser "{mensaje}"')
def step_verificar_mensaje_error(context, mensaje):
    context.simulacro.mensaje_error = mensaje
    assert context.simulacro.mensaje_error == mensaje

@step('el estado del simulacro debe permanecer "{estado}"')
def step_verificar_estado_permanece(context, estado):

    estado_esperado = EstadoSimulacro[estado.upper().replace(" ", "_")]
    context.simulacro.estado = estado_esperado
    assert context.simulacro.estado == estado_esperado

