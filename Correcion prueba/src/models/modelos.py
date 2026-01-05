class ListadoPrecios:
    def __init__(self, nombre, precio):
        self.nombre = nombre
        self.precio = float(precio)

class Pizza:
    def __init__(self, tamaño, cantidad_ingredientes, precio_base_pizza, precio_ingredientes):
        self.tamaño = tamaño
        self.cantidad_ingredientes = cantidad_ingredientes
        self.precio = precio_base_pizza + precio_ingredientes * self.cantidad_ingredientes

    def obtener_valor(self) -> float:
        return self.precio


class Pedido:
    def __init__(self, nombre, listado_de_precios):
        self.nombre = nombre
        self.listado_de_precios = listado_de_precios
        self.carrito = []

    def contar_items(self):
        return len(self.carrito)

    def agregar_pizza_normal(self, cantidad_ingredientes):
        self.validar_minimo_ingredientes(cantidad_ingredientes)
        self.carrito.append(Pizza("Normal", cantidad_ingredientes, self.listado_de_precios[0].precio, self.listado_de_precios[1].precio))

    def agregar_pizza_familiar(self, cantidad_ingredientes):
        self.validar_minimo_ingredientes(cantidad_ingredientes)
        self.carrito.append(Pizza("Grande", cantidad_ingredientes, self.listado_de_precios[2].precio, self.listado_de_precios[3].precio))

    def validar_minimo_ingredientes(self, cantidad_ingredientes: int):
        if cantidad_ingredientes < 2:
            raise ValueError("Cada pizza debe tener al menos 2 ingredientes")

    def obtener_valor_a_pagar(self):
        valor_a_pagar = 0.0
        descuento_promocion = self.calcular_descuento()
        for pizza in self.carrito:
            valor_a_pagar += pizza.obtener_valor()
        return valor_a_pagar - descuento_promocion

    def calcular_descuento(self) -> float:
        valor_descuento = 0.0
        if len(self.carrito) < 2:
            return valor_descuento
        else:
            pizza_de_menor_precio = min((pizza.obtener_valor() for pizza in self.carrito), default=0.0)
            valor_descuento = pizza_de_menor_precio / 2
            return valor_descuento
