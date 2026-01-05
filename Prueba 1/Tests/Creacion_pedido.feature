#language: es
Característica: Armar pizzas de diferentes tamaños y con varios ingredientes diferentes
  Como cliente de la pizzería
  Quiero crear mi pedido de pizzas personalizadas
  Para disfrutar pizzas con los ingredientes que más me gustan


  Escenario: Crear una pizza con al menos dos ingredientes
    Dado el cliente "Alexis Guerrero" inicia un nuevo pedido
    Cuando el cliente arma una pizza de tamaño "Familiar" con los ingredientes:
      | ingrediente     |
      | jamon           |
      | champinones     |
    Entonces la pizza se agrega correctamente al pedido
    Y el sistema calcula el precio según el tamaño y los ingredientes

  Escenario: Intentar crear una pizza con menos de dos ingredientes
    Dado el cliente "Juan Naranjo" inicia un nuevo pedido
    Cuando el cliente intenta armar una pizza de tamaño "Normal" con los ingredientes
      | ingrediente |
      | pepperoni   |
    Entonces el sistema no permite agregar la pizza al pedido
    Y se muestra el mensaje "Cada pizza debe tener al menos 2 ingredientes"
