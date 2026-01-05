from behave import *
from Sources.Cliente import Cliente

@step('el cliente "{nombre_cliente}" inicia un nuevo pedido')
def step_impl(context, nombre_cliente:str):
    context.cliente = Cliente(nombre_cliente)


@step('el cliente arma una pizza de tamaño "Familiar" con los ingredientes:')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando el cliente arma una pizza de tamaño "Familiar" con los ingredientes:
                              | ingrediente |
                              | jamon |
                              | champinones | ')