from datetime import datetime
from behave import *

from sources.sistema_electoral import SistemaElectoral
from sources.votante import Votante
from sources.candidato import Candidato


@step("que existen los siguientes candidatos")
def step_impl(context):
    context.candidatos = {}

    for row in context.table:
        nombre_partido = row["Partido"].strip()
        nombre_candidato = row["Candidato"].strip()

        # Crear el Candidato con votos iniciales en 0
        candidato = Candidato(nombre_candidato, nombre_partido, votos=0)

        # Guardar el candidato por partido, ya que será unico
        context.candidatos[nombre_candidato] = candidato


@step("que existen los siguientes votantes")
def step_impl(context):
    context.votantes = {}

    for row in context.table:
        cedula = row["cedula"].strip()
        nombre = row["nombre"].strip()
        correo = row["correo"].strip()

        votante = Votante(cedula, nombre, correo)
        context.votantes[cedula] = votante

@step('que el proceso de elección de Decano de la FIS está activo desde "{fecha_inicio}" hasta "{fecha_fin}"')
def step_impl(context, fecha_inicio, fecha_fin):
    fecha_inicio_votacion = datetime.fromisoformat(fecha_inicio.strip())
    fecha_fin_votacion = datetime.fromisoformat(fecha_fin.strip())

    context.eleccion_decano_FIS = SistemaElectoral(context.candidatos, context.votantes, fecha_inicio_votacion, fecha_fin_votacion)
    context.eleccion_decano_FIS.activar_proceso_electoral()

    assert context.eleccion_decano_FIS.esta_activo() is True


@step("el votante con la {cedula} esta autorizado para votar")
def step_impl(context, cedula):
    context.cedula_votante_actual = cedula.strip()
    assert context.eleccion_decano_FIS.esta_votante_autorizado(context.cedula_votante_actual) is True


@step("el votante confirma su elección por el candidato {candidato}")
def step_impl(context, candidato: str):
    context.eleccion_decano_FIS.emitir_voto(context.cedula_votante_actual, candidato.strip())


@step("la contabilización de votos será")
def step_impl(context):
    for row in context.table:
        candidato = row["Candidato"].strip()
        votos_obtenidos = int(row["Votos"].strip())

        # Validar que los votos obtenidos por el candidato son iguales a los esperados
        assert votos_obtenidos == context.eleccion_decano_FIS.contar_votos_candidato(candidato)


@step("el votante con la {cedula} ya no esta autorizado para votar de nuevo")
def step_impl(context, cedula):
    cedula_votante = cedula.strip()
    assert context.eleccion_decano_FIS.esta_votante_autorizado(cedula_votante) is False


@step("la confirmación de voto del {correo} se agregó a la cola de envío")
def step_impl(context, correo: str):
    correo_votante = correo.strip()
    assert context.eleccion_decano_FIS.esta_confirmacion_voto_en_cola(correo_votante) is True
