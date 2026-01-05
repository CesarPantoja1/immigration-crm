Sistema de Pedidos para Pizzería

Una pizzería local desea entrar en la era digital, iniciando por su proceso de pedidos mediante un sistema que permita a los clientes armar pizzas personalizadas y recibir el precio automáticamente.

La pizzería ofrece dos tamaños de pizza: Pizza Normal y Pizza Familiar

Reglas del negocio

Ingredientes

Se pueden agregar muchos ingredientes en cada pizza.
Cada pizza debe tener al menos 2 ingredientes obligatorios.
Cada ingrediente tiene un precio que depende del tamaño de la pizza.
El precio de los ingredientes depende del tamaño de la pizza.

Promoción

2da pizza al 50% Si el cliente pide dos pizzas en un solo pedido:  La pizza de menor precio se vende con un 50% de descuento. Si son más de dos pizzas, el descuento se aplica únicamente a la más barata del pedido.

Ejemplo

Un cliente pide 1 pizza Familiar con: jamón, champiñones y extra queso y 1 pizza Normal con pepperoni y aceitunas. Si la pizza normal es la más barata, entonces: La pizza normal se cobra al 50% de su precio y la pizza familiar se cobra al 100%

Tips

Puede usar arreglos y la función sort para esta actividad por ejemplo:
```python
planes = [
  Plan("Básico", 1, 10.0),
  Plan("Premium", 6, 45.0),
  Plan("Estándar", 3, 25.0)
]```

# Ordenar los planes de mayor a menor precio
planes.sort(key=lambda plan: plan.precio, reverse=False)
Se puede acceder a los elementos con el indice, por ejemplo: planes[-1] o usar la función len(planes) para saber la dimensión. 

**Instrucciones

1. En un proyecto en Python escriba un documento .md (markdown) en la que defina la visión, objetivos y capacidades y características del sistema y su trazabilidad
2. Desarrolle las características utilizando el proceso BDD como se ha realizado en clases
3. Debe subir su proyecto (solamente src y tests) comprimido con su apellido tomando en cuenta que la evaluación se cierra automáticamente a la hora señalada. No se receptará trabajos fuera de tiempo.
4. Vuelva a leer las instrucciones una vez más!!!!!!!!!

**B. DESARROLLO**
Vision
Que la pizeria ingrese al mundo digital
Observaciones:
- Como se ve el resultado final


Objetivos del negocio 
Procesa de forma digital el pedido de pizzas y sus promociones
Observaciones
-- Cuales son los pasos para lograr el resultado final   (vision)

Capacidades
- Procesamiento de pedidos

Caracteristicas
- Registrar pedidos
(Maximo eran dos, en este caso seria crear pedido y pagarlo -> se puede agrupar en registar pedido)



B.2

