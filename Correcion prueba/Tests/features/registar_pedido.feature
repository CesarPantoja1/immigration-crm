#language: es

  Característica: Registrar los pedidos de pizza
    Como cliente
    quiero ordenar pizzas personalizadas
    #En el para se debe evidenciar como esto genera mas valor para el cliente
    #que hacerlo sin el sistema, ejemplo si dijera para satisfacer mi hambre, eso se puede hacer sin el sistema
    para calcular el valor a pagar incluyendo descuentos por compra


    Antecedentes:
    Dado que se tiene el siguiente listado de precios
      | nombre               | precio  |
      | normal               | 5.00    |
      | ingrediente normal   | 1.00    |
      | familiar             | 7.00    |
      | ingrediente familiar | 1.50    |

    Escenario: Cliente compra una pizza y no tiene descuento
      #Aqui entra una regla de negocio que es sobre el numero de ingredientes
      Y que el cliente hace el pedido a nombre de "Juan"
      Y que el cliente agrega una pizza normal de 3 ingredientes
      #Cuando se le cobra 5.00
      Entonces el pedido vale 8.00

      #Pizzas info
      #Nomal: $5
      #Ingrenientes normal a $1
      #Familiar: $7
      #Ingrenientes familiar a $1.5

  # Otros escenarios ha implementar
  Escenario: Cliente ordena dos pizzas y tiene descuento
    Y que el cliente hace el pedido a nombre de "Juan"
    Y que el cliente agrega una pizza normal de 6 ingredientes
    Y que el cliente agrega una pizza familiar de 2 ingredientes
    Entonces el pedido vale 16.00


  Escenario: Cliente ordena tres pizzas y tiene descuento
    Y que el cliente hace el pedido a nombre de "Juan"
    Y que el cliente agrega una pizza normal de 6 ingredientes
    Y que el cliente agrega una pizza familiar de 2 ingredientes
    Y que el cliente agrega una segunda pizza normal de 2 ingredientes
    Entonces el pedido vale 24.50