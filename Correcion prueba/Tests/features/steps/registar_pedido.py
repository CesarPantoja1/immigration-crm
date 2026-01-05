from behave import *
from src.models.modelos import *


@step("que se tiene el siguiente listado de precios")
def step_impl(context):
    context.listado_de_precios = []
    for item in context.table:
        context.listado_de_precios.append(ListadoPrecios(item["nombre"], item["precio"]))
    assert len(context.listado_de_precios) == 4


@step('que el cliente hace el pedido a nombre de {nombre_cliente}')
def step_impl(context, nombre_cliente):
    context.pedido = Pedido(nombre_cliente, context.listado_de_precios)
    assert context.pedido.contar_items() == 0


@step("que el cliente agrega una pizza normal de {cantidad_ingredientes:d} ingredientes")
def step_impl(context, cantidad_ingredientes):
    #NO mandamos el tamaño de la pizza como parametro por el principio de responsabilidad unica
    #La prueba no seria fragil a cambios ya que aceptaria de todof y por lo tanto no podriamos identificar cuando
    # ocurran errores
    context.pedido.agregar_pizza_normal(cantidad_ingredientes)
    assert context.pedido.contar_items() == 1

@step("que el cliente agrega una pizza familiar de {cantidad_ingredientes:d} ingredientes")
def step_impl(context, cantidad_ingredientes):
    context.pedido.agregar_pizza_familiar(cantidad_ingredientes)
    assert context.pedido.contar_items() == 2

@step("que el cliente agrega una segunda pizza normal de {cantidad_ingredientes:d} ingredientes")
def step_impl(context, cantidad_ingredientes):
    context.pedido.agregar_pizza_normal(cantidad_ingredientes)
    assert context.pedido.contar_items() == 3

@step("el pedido vale {valor:f}")
def step_impl(context, valor):
    assert context.pedido.obtener_valor_a_pagar() == valor


