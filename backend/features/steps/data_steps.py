"""
Steps para crear y gestionar datos de prueba.
"""
from behave import given
from datetime import datetime, timedelta


@given('que existen datos de prueba en la base de datos')
def step_datos_prueba(context):
    """Crea datos de prueba básicos."""
    # Aquí se crearán datos de prueba cuando se implementen los modelos
    pass


@given('que la fecha actual es "{fecha}"')
def step_fecha_actual(context, fecha):
    """Establece una fecha específica para el contexto de prueba."""
    context.fecha_actual = datetime.strptime(fecha, '%Y-%m-%d')
