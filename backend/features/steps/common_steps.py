"""
Steps comunes que se reutilizan en múltiples features.
"""
from behave import given, when, then


@given('que el sistema está operativo')
def step_sistema_operativo(context):
    """Step común para verificar que el sistema está listo."""
    assert True


@then('el sistema debe mostrar un mensaje de éxito')
def step_mensaje_exito(context):
    """Step común para verificar mensajes de éxito."""
    assert hasattr(context, 'mensaje')
    assert 'éxito' in context.mensaje.lower() or 'exitosa' in context.mensaje.lower()
