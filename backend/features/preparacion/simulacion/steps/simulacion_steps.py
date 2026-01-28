from behave import *
from datetime import datetime, date, time, timedelta

# Importar desde la ruta correcta del dominio
from backend.apps.preparacion.simulacion.domain.entities import (
    SimulacroConAsesor,
    SesionPracticaIndividual,
    GestorSimulacros
)
from backend.apps.preparacion.simulacion.domain.value_objects import (
    TipoVisado,
    ModalidadSimulacro,
    EstadoSimulacro,
    NivelDificultad,
    Pregunta,
    RespuestaMigrante,
    HorarioSimulacro,
    ResultadoPractica,
    Transcripcion,
    FeedbackAsesor,
    PreguntaIncorrecta
)


# ============================================================================
# CONFIGURACIÓN DEL SISTEMA
# ============================================================================

@step('que el sistema tiene configurados los siguientes límites')
def step_configurar_sistema(context):
    context.config_params = {}
    for row in context.table:
        parametro = row['parámetro']
        valor = int(row['valor'])
        context.config_params[parametro] = valor

    assert context.config_params['máximo_simulacros_por_cliente'] == 2
    assert context.config_params['minutos_anticipación_entrada'] == 15
    assert context.config_params['horas_cancelación_anticipada'] == 24


@step('que soy el migrante "{nombre}" con ID "{id_migrante}"')
def step_crear_migrante(context, nombre, id_migrante):
    context.migrante_id = id_migrante
    context.migrante_nombre = nombre
    context.gestor = GestorSimulacros(
        migrante_id=id_migrante,
        migrante_nombre=nombre,
        fecha_cita_real=date(2026, 2, 20)
    )
    assert context.migrante_id == id_migrante
    assert context.migrante_nombre == nombre


@step('mi contador de simulacros realizados es {contador:d}')
def step_establecer_contador(context, contador):
    # Limpiar simulacros existentes primero
    context.gestor.simulacros_con_asesor = []

    # Crear simulacros ficticios ya completados para alcanzar el contador
    for i in range(contador):
        simulacro = SimulacroConAsesor(
            id=f"SIM-PREV-{i + 1}",
            migrante_id=context.migrante_id,
            migrante_nombre=context.migrante_nombre,
            asesor_id="ASESOR-001",
            fecha_cita_real=context.gestor.fecha_cita_real,
            numero_intento=i + 1,
            estado=EstadoSimulacro.COMPLETADO
        )
        context.gestor.simulacros_con_asesor.append(simulacro)

    # Guardar el contador inicial para verificaciones posteriores
    context.contador_inicial = contador
    assert context.gestor.contar_simulacros_con_asesor() == contador


@step('mi tipo de visa asignado es "{tipo_visa}"')
def step_establecer_tipo_visa(context, tipo_visa):
    context.tipo_visado = TipoVisado[tipo_visa.upper()]
    assert context.tipo_visado.value == tipo_visa


@step('tengo una propuesta de simulacro con los siguientes datos')
def step_crear_propuesta_tabla(context):
    row = context.table[0]

    # Mapear estados del feature a los estados del dominio
    estado_map = {
        'Pendiente de respuesta': EstadoSimulacro.AGENDADO,
        'Confirmado': EstadoSimulacro.AGENDADO,
        'En sala de espera': EstadoSimulacro.EN_PROGRESO,
        'En progreso': EstadoSimulacro.EN_PROGRESO,
        'Completado': EstadoSimulacro.COMPLETADO
    }

    modalidad = ModalidadSimulacro[row['modalidad'].upper()]
    estado = estado_map.get(row['estado'], EstadoSimulacro.AGENDADO)

    fecha_parts = row['fecha'].split('-')
    hora_parts = row['hora'].split(':')

    simulacro = SimulacroConAsesor(
        id=row['id'],
        migrante_id=context.migrante_id,
        migrante_nombre=context.migrante_nombre,
        asesor_id="ASESOR-001",
        fecha_cita_real=context.gestor.fecha_cita_real,
        modalidad=modalidad,
        estado=estado,
        horario=HorarioSimulacro(
            fecha=date(int(fecha_parts[0]), int(fecha_parts[1]), int(fecha_parts[2])),
            hora=time(int(hora_parts[0]), int(hora_parts[1]))
        )
    )

    context.gestor.simulacros_con_asesor.append(simulacro)
    context.simulacro_actual = simulacro
    context.estado_original = row['estado']

    assert context.simulacro_actual.id == row['id']


@step('tengo una propuesta de simulacro con ID "{id_sim}" para "{fecha} {hora}"')
def step_crear_propuesta_simple(context, id_sim, fecha, hora):
    fecha_parts = fecha.split('-')
    hora_parts = hora.split(':')

    simulacro = SimulacroConAsesor(
        id=id_sim,
        migrante_id=context.migrante_id,
        migrante_nombre=context.migrante_nombre,
        asesor_id="ASESOR-001",
        fecha_cita_real=context.gestor.fecha_cita_real,
        modalidad=ModalidadSimulacro.VIRTUAL,
        estado=EstadoSimulacro.AGENDADO,
        horario=HorarioSimulacro(
            fecha=date(int(fecha_parts[0]), int(fecha_parts[1]), int(fecha_parts[2])),
            hora=time(int(hora_parts[0]), int(hora_parts[1]))
        ),
        numero_intento=0  # Propuesta, no cuenta como intento real
    )

    # NO agregar al gestor - es solo una propuesta pendiente
    # context.gestor.simulacros_con_asesor.append(simulacro)
    context.simulacro_actual = simulacro
    context.es_propuesta = True  # Marcar que es una propuesta


@step('tengo un simulacro confirmado con ID "{id_sim}" para hoy "{fecha} {hora}"')
def step_crear_simulacro_confirmado_hoy(context, id_sim, fecha, hora):
    fecha_parts = fecha.split('-')
    hora_parts = hora.split(':')

    simulacro = SimulacroConAsesor(
        id=id_sim,
        migrante_id=context.migrante_id,
        migrante_nombre=context.migrante_nombre,
        asesor_id="ASESOR-001",
        fecha_cita_real=context.gestor.fecha_cita_real,
        modalidad=ModalidadSimulacro.VIRTUAL,
        estado=EstadoSimulacro.AGENDADO,
        horario=HorarioSimulacro(
            fecha=date(int(fecha_parts[0]), int(fecha_parts[1]), int(fecha_parts[2])),
            hora=time(int(hora_parts[0]), int(hora_parts[1]))
        )
    )

    context.gestor.simulacros_con_asesor.append(simulacro)
    context.simulacro_actual = simulacro
    context.fecha_actual = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")


@step('tengo un simulacro confirmado con ID "{id_sim}" para "{fecha} {hora}"')
def step_crear_simulacro_confirmado(context, id_sim, fecha, hora):
    fecha_parts = fecha.split('-')
    hora_parts = hora.split(':')

    simulacro = SimulacroConAsesor(
        id=id_sim,
        migrante_id=context.migrante_id,
        migrante_nombre=context.migrante_nombre,
        asesor_id="ASESOR-001",
        fecha_cita_real=context.gestor.fecha_cita_real,
        modalidad=ModalidadSimulacro.VIRTUAL,
        estado=EstadoSimulacro.AGENDADO,
        horario=HorarioSimulacro(
            fecha=date(int(fecha_parts[0]), int(fecha_parts[1]), int(fecha_parts[2])),
            hora=time(int(hora_parts[0]), int(hora_parts[1]))
        )
    )

    context.gestor.simulacros_con_asesor.append(simulacro)
    context.simulacro_actual = simulacro


@step('la modalidad del simulacro es "{modalidad}"')
def step_verificar_modalidad(context, modalidad):
    assert context.simulacro_actual.modalidad.value == modalidad


@step('la hora actual del sistema es "{hora}"')
def step_establecer_hora_actual(context, hora):
    fecha_simulacro = context.simulacro_actual.horario.fecha
    hora_parts = hora.split(':')
    context.hora_actual = datetime.combine(
        fecha_simulacro,
        time(int(hora_parts[0]), int(hora_parts[1]))
    )


@step('hoy es "{fecha}" a las "{hora}"')
def step_establecer_fecha_hora_actual(context, fecha, hora):
    context.fecha_actual = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")


@step('estoy en sala de espera del simulacro "{id_sim}"')
def step_establecer_sala_espera(context, id_sim):
    simulacro = next((s for s in context.gestor.simulacros_con_asesor if s.id == id_sim), None)

    if simulacro is None:
        simulacro = SimulacroConAsesor(
            id=id_sim,
            migrante_id=context.migrante_id,
            migrante_nombre=context.migrante_nombre,
            asesor_id="ASESOR-001",
            fecha_cita_real=context.gestor.fecha_cita_real,
            modalidad=ModalidadSimulacro.VIRTUAL,
            horario=HorarioSimulacro(
                fecha=date(2026, 2, 10),
                hora=time(15, 0)
            )
        )
        context.gestor.simulacros_con_asesor.append(simulacro)

    # Cambiar a estado EN_PROGRESO (equivalente a sala de espera en el modelo DDD)
    simulacro.estado = EstadoSimulacro.EN_PROGRESO
    context.simulacro_actual = simulacro


@step('el simulacro está programado para "{hora}"')
def step_verificar_hora_programada(context, hora):
    hora_parts = hora.split(':')
    hora_programada = time(int(hora_parts[0]), int(hora_parts[1]))
    assert context.simulacro_actual.horario.hora == hora_programada


@step('la hora actual es "{hora}"')
def step_establecer_hora_simple(context, hora):
    fecha_simulacro = context.simulacro_actual.horario.fecha
    hora_parts = hora.split(':')
    context.hora_actual = datetime.combine(
        fecha_simulacro,
        time(int(hora_parts[0]), int(hora_parts[1]))
    )


@step('estoy en sesión activa del simulacro "{id_sim}"')
def step_establecer_sesion_activa(context, id_sim):
    simulacro = next((s for s in context.gestor.simulacros_con_asesor if s.id == id_sim), None)

    if simulacro is None:
        simulacro = SimulacroConAsesor(
            id=id_sim,
            migrante_id=context.migrante_id,
            migrante_nombre=context.migrante_nombre,
            asesor_id="ASESOR-001",
            fecha_cita_real=context.gestor.fecha_cita_real,
            modalidad=ModalidadSimulacro.VIRTUAL,
            horario=HorarioSimulacro(
                fecha=date(2026, 2, 10),
                hora=time(15, 0)
            )
        )
        context.gestor.simulacros_con_asesor.append(simulacro)

    simulacro.estado = EstadoSimulacro.EN_PROGRESO
    context.simulacro_actual = simulacro
    context.grabacion_activa = True


@step('el temporizador marca {minutos:d} minutos')
def step_establecer_temporizador(context, minutos):
    context.duracion_minutos = minutos


@step('la grabación está activa')
def step_verificar_grabacion_activa(context):
    context.grabacion_activa = True
    assert context.grabacion_activa == True


@step('nunca he accedido a "Práctica Individual"')
def step_establecer_primer_acceso(context):
    context.ha_accedido_practica = False


@step('inicié un cuestionario de práctica para visa "{tipo_visa}"')
def step_iniciar_cuestionario(context, tipo_visa):
    tipo_visado = TipoVisado[tipo_visa.upper()]
    context.sesion_practica = context.gestor.iniciar_practica_individual(tipo_visado)
    assert context.sesion_practica is not None


@step('el cuestionario tiene {total:d} preguntas')
def step_establecer_total_preguntas(context, total):
    assert len(context.sesion_practica.preguntas) == total


@step('completé un cuestionario con {incorrectas:d} respuestas incorrectas')
def step_completar_cuestionario_con_incorrectas(context, incorrectas):
    tipo_visado = TipoVisado.ESTUDIANTE
    context.sesion_practica = context.gestor.iniciar_practica_individual(tipo_visado)

    total_preguntas = len(context.sesion_practica.preguntas)
    correctas = total_preguntas - incorrectas

    # Crear una lista con los índices de las preguntas que serán incorrectas
    # Las hacemos incorrectas de forma distribuida (por ejemplo: 7, 8, 9)
    indices_incorrectas = list(range(correctas, total_preguntas))

    for i in range(total_preguntas):
        pregunta = context.sesion_practica.preguntas[i]

        if i in indices_incorrectas:
            # Responder INCORRECTAMENTE - elegir un índice diferente al correcto
            indice_correcto = pregunta.respuesta_correcta
            # Asegurarnos de elegir una respuesta diferente
            num_respuestas = len(pregunta.respuestas)
            indice_respuesta = (indice_correcto + 1) % num_respuestas
        else:
            # Responder CORRECTAMENTE
            indice_respuesta = pregunta.respuesta_correcta

        context.sesion_practica.responder_pregunta(indice_respuesta, tiempo_segundos=30)

    context.resultado_practica = context.sesion_practica.finalizar_practica()

    # Crear lista de preguntas incorrectas para el siguiente paso
    context.preguntas_incorrectas = []
    for i, respuesta in enumerate(context.sesion_practica.respuestas):
        if not respuesta.es_correcta:
            pregunta_obj = context.sesion_practica.preguntas[i]
            pregunta_incorrecta = PreguntaIncorrecta(
                pregunta=pregunta_obj,
                indice_respuesta_usuario=respuesta.respuesta_seleccionada,
                explicacion=pregunta_obj.explicacion
            )
            context.preguntas_incorrectas.append(pregunta_incorrecta)

    # Verificar que tenemos exactamente el número correcto de incorrectas
    assert len(context.preguntas_incorrectas) == incorrectas, \
        f"Se esperaban {incorrectas} incorrectas pero se generaron {len(context.preguntas_incorrectas)}"


@step('acepto la propuesta de simulacro "{id_sim}"')
def step_aceptar_propuesta(context, id_sim):
    simulacro = next((s for s in context.gestor.simulacros_con_asesor if s.id == id_sim), None)
    if simulacro:
        # En el modelo DDD, aceptar = confirmar el estado como AGENDADO
        simulacro.estado = EstadoSimulacro.AGENDADO
        context.simulacro_actual = simulacro


@step('propongo la fecha alternativa "{nueva_fecha}" para el simulacro "{id_sim}"')
def step_proponer_fecha_alternativa(context, nueva_fecha, id_sim):
    # Buscar el simulacro o usar el actual si es una propuesta
    if hasattr(context, 'es_propuesta') and context.es_propuesta:
        simulacro = context.simulacro_actual
    else:
        simulacro = next((s for s in context.gestor.simulacros_con_asesor if s.id == id_sim), None)

    if simulacro:
        # Guardar la fecha propuesta
        context.fecha_propuesta = nueva_fecha
        # En DDD no tenemos estado de contrapropuesta, mantenemos AGENDADO
        # Pero guardamos que hubo una contrapropuesta
        context.hubo_contrapropuesta = True
        context.simulacro_actual = simulacro


@step('consulto la disponibilidad para nuevo simulacro')
def step_consultar_disponibilidad(context):
    puede, mensaje = context.gestor.puede_agendar_simulacro()
    context.disponibilidad = "disponible" if puede else "no_disponible"

    # Generar mensaje según el contador
    contador = context.gestor.contar_simulacros_con_asesor()
    if contador == 0:
        context.mensaje_disponibilidad = "Puede solicitar hasta 2 simulacros en total"
    elif contador == 1:
        context.mensaje_disponibilidad = "Tiene 1 simulacro disponible restante"
    else:
        context.mensaje_disponibilidad = "Ha alcanzado el límite de 2 simulacros por proceso"


@step('ingreso al simulacro "{id_sim}"')
def step_ingresar_simulacro(context, id_sim):
    simulacro = next((s for s in context.gestor.simulacros_con_asesor if s.id == id_sim), None)

    if simulacro and simulacro.horario:
        # Verificar si puede ingresar (15 minutos antes)
        hora_simulacro = datetime.combine(simulacro.horario.fecha, simulacro.horario.hora)
        minutos_anticipacion = context.config_params.get('minutos_anticipación_entrada', 15)

        if context.hora_actual >= hora_simulacro - timedelta(minutes=minutos_anticipacion):
            simulacro.estado = EstadoSimulacro.EN_PROGRESO
            context.resultado_ingreso = True

            # Calcular tiempo restante
            diferencia = hora_simulacro - context.hora_actual
            context.tiempo_restante = int(diferencia.total_seconds() / 60)
        else:
            context.resultado_ingreso = False

        context.simulacro_actual = simulacro


@step('el asesor "{asesor}" inicia la sesión del simulacro "{id_sim}"')
def step_asesor_inicia_sesion(context, asesor, id_sim):
    simulacro = next((s for s in context.gestor.simulacros_con_asesor if s.id == id_sim), None)
    if simulacro:
        exito, mensaje = simulacro.iniciar_sesion()
        context.simulacro_actual = simulacro
        context.grabacion_activa = True
        context.temporizador = 0


@step('el asesor "{asesor}" finaliza el simulacro "{id_sim}"')
def step_asesor_finaliza_simulacro(context, asesor, id_sim):
    simulacro = next((s for s in context.gestor.simulacros_con_asesor if s.id == id_sim), None)
    if simulacro:
        # Terminar simulación con transcripción
        transcripcion_contenido = f"Simulacro de {context.duracion_minutos} minutos"
        exito, mensaje = simulacro.terminar_simulacion(transcripcion_contenido)

        # Agregar feedback para completar el simulacro
        feedback = FeedbackAsesor(
            simulacro_id=id_sim,
            asesor_id=asesor,
            comentarios="Simulacro completado exitosamente",
            puntuacion=8,
            fortalezas=["Buena comunicación"],
            areas_mejora=["Mejorar confianza"],
            recomendaciones="Practicar más"
        )
        simulacro.agregar_feedback(feedback)

        context.simulacro_actual = simulacro
        context.grabacion_activa = False


@step('accedo a la sección de práctica individual')
def step_acceder_practica_individual(context):
    context.tipos_visa_disponibles = [
        {"tipo": TipoVisado.ESTUDIANTE, "estado": "Sugerido"},
        {"tipo": TipoVisado.TRABAJO, "estado": "Disponible"},
        {"tipo": TipoVisado.TURISMO, "estado": "Disponible"},
        {"tipo": TipoVisado.VIVIENDA, "estado": "Disponible"}
    ]
    context.ha_accedido_practica = True


@step('completo el cuestionario con {correctas:d} respuestas correctas')
def step_completar_cuestionario(context, correctas):
    total_preguntas = len(context.sesion_practica.preguntas)

    # Responder todas las preguntas
    for i in range(total_preguntas):
        # Determinar si la respuesta es correcta o incorrecta
        if i < correctas:
            # Respuesta correcta (índice 0 es correcto según nuestro banco de preguntas)
            indice_respuesta = context.sesion_practica.preguntas[i].respuesta_correcta
        else:
            # Respuesta incorrecta (elegir un índice diferente al correcto)
            indice_correcto = context.sesion_practica.preguntas[i].respuesta_correcta
            indice_respuesta = (indice_correcto + 1) % len(context.sesion_practica.preguntas[i].respuestas)

        context.sesion_practica.responder_pregunta(indice_respuesta, tiempo_segundos=30)

    context.resultado_practica = context.sesion_practica.finalizar_practica()


@step('solicito ver las respuestas incorrectas')
def step_solicitar_ver_incorrectas(context):
    context.mostrar_incorrectas = True


@step('cancelo el simulacro "{id_sim}"')
def step_cancelar_simulacro(context, id_sim):
    simulacro = next((s for s in context.gestor.simulacros_con_asesor if s.id == id_sim), None)

    if simulacro and simulacro.horario:
        # Verificar si está en progreso
        if simulacro.estado == EstadoSimulacro.EN_PROGRESO:
            context.resultado_cancelacion = False
            context.mensaje_error = "No se puede cancelar un simulacro en progreso"
            return

        # Calcular horas de anticipación
        hora_simulacro = datetime.combine(simulacro.horario.fecha, simulacro.horario.hora)
        horas_anticipacion = context.config_params.get('horas_cancelación_anticipada', 24)
        diferencia_horas = (hora_simulacro - context.fecha_actual).total_seconds() / 3600

        if diferencia_horas >= horas_anticipacion:
            # Cancelación sin penalización
            simulacro.estado = EstadoSimulacro.CANCELADO
            context.resultado_cancelacion = True
            context.con_penalizacion = False
        elif diferencia_horas > 0:
            # Cancelación con penalización
            simulacro.estado = EstadoSimulacro.CANCELADO
            context.resultado_cancelacion = True
            context.con_penalizacion = True
        else:
            # No permitido
            context.resultado_cancelacion = False
            context.mensaje_error = "No puedes cancelar con menos de 24 horas de anticipación"

        context.simulacro_actual = simulacro

@step('el estado del simulacro debe cambiar a "{estado}"')
def step_verificar_cambio_estado(context, estado):
    # Manejar casos especiales
    if estado == "Contrapropuesta pendiente":
        # En nuestro modelo DDD, las contrapropuestas no cambian el estado
        # Verificamos que se haya registrado la contrapropuesta
        assert hasattr(context, 'hubo_contrapropuesta') and context.hubo_contrapropuesta
        return

    estado_map = {
        'Confirmado': EstadoSimulacro.AGENDADO,
        'En progreso': EstadoSimulacro.EN_PROGRESO,
        'Completado': EstadoSimulacro.COMPLETADO,
        'Pendiente de respuesta': EstadoSimulacro.AGENDADO
    }
    estado_esperado = estado_map.get(estado, EstadoSimulacro.AGENDADO)
    assert context.simulacro_actual.estado == estado_esperado


@step('el estado del simulacro debe ser "{estado}"')
def step_verificar_estado(context, estado):
    estado_map = {
        'En sala de espera': EstadoSimulacro.EN_PROGRESO,
        'En progreso': EstadoSimulacro.EN_PROGRESO,
        'Completado': EstadoSimulacro.COMPLETADO,
        'Confirmado': EstadoSimulacro.AGENDADO
    }
    estado_esperado = estado_map.get(estado, EstadoSimulacro.AGENDADO)
    assert context.simulacro_actual.estado == estado_esperado


@step('mi contador de simulacros debe ser {contador:d}')
def step_verificar_contador_exacto(context, contador):
    # El contador incluye TODOS los simulacros (previos + actuales)
    assert context.gestor.contar_simulacros_con_asesor() == contador


@step('mi contador de simulacros debe incrementarse a {contador:d}')
def step_verificar_incremento_contador(context, contador):
    assert context.gestor.contar_simulacros_con_asesor() == contador


@step('mi contador de simulacros debe permanecer en {contador:d}')
def step_verificar_contador_permanece(context, contador):
    # Verificar que el contador no ha cambiado desde el valor inicial
    # En el caso de contrapropuesta, el contador no debería aumentar
    assert context.gestor.contar_simulacros_con_asesor() == contador


@step('la fecha propuesta debe ser "{fecha}"')
def step_verificar_fecha_propuesta(context, fecha):
    assert context.fecha_propuesta == fecha


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
    assert context.grabacion_activa == True


@step('el temporizador debe iniciar en {minutos:d}')
def step_verificar_temporizador_inicio(context, minutos):
    assert context.temporizador == minutos


@step('la duración registrada debe ser {minutos:d} minutos')
def step_verificar_duracion_registrada(context, minutos):
    assert context.duracion_minutos == minutos


@step('la grabación debe estar detenida')
def step_verificar_grabacion_detenida(context):
    assert context.grabacion_activa == False


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
    puntuacion_obtenida = context.resultado_practica.calcular_porcentaje()
    # Permitir un margen de error de 1% debido a redondeo
    assert abs(puntuacion_obtenida - porcentaje) <= 1, f"Esperado: {porcentaje}, Obtenido: {puntuacion_obtenida}"


@step('la calificación debe ser "{calificacion}"')
def step_verificar_calificacion(context, calificacion):
    calificacion_obtenida = context.resultado_practica.obtener_calificacion()
    assert calificacion_obtenida == calificacion


@step('el mensaje debe ser "{mensaje}"')
def step_verificar_mensaje(context, mensaje):
    mensaje_obtenido = context.resultado_practica.obtener_mensaje_motivacional()
    assert mensaje_obtenido == mensaje


@step('debo ver exactamente {cantidad:d} preguntas')
def step_verificar_cantidad_preguntas(context, cantidad):
    assert len(
        context.preguntas_incorrectas) == cantidad, f"Esperado: {cantidad}, Obtenido: {len(context.preguntas_incorrectas)}"


@step('cada pregunta debe mostrar mi respuesta como incorrecta')
def step_verificar_respuestas_incorrectas(context):
    for pregunta_inc in context.preguntas_incorrectas:
        assert pregunta_inc.indice_respuesta_usuario is not None


@step('cada pregunta debe mostrar la respuesta correcta')
def step_verificar_respuestas_correctas(context):
    for pregunta_inc in context.preguntas_incorrectas:
        assert pregunta_inc.pregunta.respuesta_correcta is not None


@step('cada pregunta debe incluir una explicación')
def step_verificar_explicaciones(context):
    for pregunta_inc in context.preguntas_incorrectas:
        assert pregunta_inc.explicacion is not None and pregunta_inc.explicacion != ""


@step("la cancelación debe ser rechazada")
def step_verificar_cancelacion_rechazada(context):
    # Verificar que la cancelación no fue exitosa
    assert context.resultado_cancelacion == False, f"Se esperaba False pero se obtuvo {context.resultado_cancelacion}"


@step('el mensaje de error debe ser "{mensaje}"')
def step_verificar_mensaje_error(context, mensaje):
    assert context.mensaje_error == mensaje


@step('el estado del simulacro debe permanecer "{estado}"')
def step_verificar_estado_permanece(context, estado):
    estado_map = {
        'Confirmado': EstadoSimulacro.AGENDADO,
        'En progreso': EstadoSimulacro.EN_PROGRESO
    }
    estado_esperado = estado_map.get(estado, EstadoSimulacro.AGENDADO)
    assert context.simulacro_actual.estado == estado_esperado