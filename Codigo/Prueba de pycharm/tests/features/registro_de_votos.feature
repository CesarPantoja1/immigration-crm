# language: es

Característica: Emisión del voto
  Como votante,
  quiero registrar mi voto de manera segura y única,
  para asegurar que mi elección sea válida y contabilizada.

#  Escenario: Registro exitoso de un voto único
#   Escenario 2.0 despues de que surgiera un DEPENDE porque no esta definido bien las reglas del negocio
  Esquema del escenario: Registro exitoso de un voto único para elecciones de opción única
  #Flujo  normal - Happy path
    # Cada texto entre las Y, son metodos que se van a implementar por separado
#    Dado que existe
#    Y la votación está abierta
#    Y el votante está autenticado
#    Y no ha votado

  # Ojo --> Para el caso de personas mayores o con discapacidad se podria a llegar a considerar
#    que se debe tomar en cuenta otra regla de negocio u otro criterio a tomar en cuenta
#    pero en este caso esto seria mas desde el punto de vista del front ya que el front se adapta
#    pero la funcionalidad al final es la misma por lo que el back no cambia

#    Dado que el proceso de elección de "Decano de la fis" de la FIS está "activo"
#    Y el votante esta autorizado para votar
#    Cuando el votante confirma su elección
#    Entonces la opción seleccionada incrementa en un voto su total
#    Y  el votante ya no esta autorizado para votar de nuevo
#    Y el sistema envía la confirmación de voto al correo de voto al correo electrónico del votante


    #No colocar cosas que no sirvan para validar el escenario "fecha creacion partido, fecha creacion candidato, etc"
    Dado que existen los siguientes candidatos
      | Partido     | Candidato |
      | Iluminación | Jose L.   |
      | Por siempre | Jenny T.  |
    Y  que existen los siguientes votantes
      | cedula     | nombre       | correo             |
      | 1123423423 | Juan Naranjo | jnaranjo@gmail.com |
      | 1111111111 | Carlos Gómez | carlos@gmail.com   |
    Y que el proceso de elección de Decano de la FIS está activo desde "2025-11-19T10:00:00" hasta "2025-11-19T17:00:00"
    Y el votante con la <cedula> esta autorizado para votar
    Cuando el votante confirma su elección por el candidato <candidato>
    Entonces la contabilización de votos será
      | Candidato | Votos    |
      | Jose L.   | <votos_jose> |
      | Jenny T.  | <votos_jenny>|
    Y  el votante con la <cedula> ya no esta autorizado para votar de nuevo
    Y  la confirmación de voto del <correo> se agregó a la cola de envío

    Ejemplos:
      | cedula      | correo             | candidato | votos_jose | votos_jenny |
      | 1123423423  | jnaranjo@gmail.com | Jenny T.  | 0          | 1           |
      | 1111111111  | carlos@gmail.com   | Jose L.   | 1          | 0           |





# Mi Característica: Emisión del voto
#  Scenario: Registrar sufragio cuando el elector no ha votado
#  	Given que el elector no ha votado
#	When confirma su voto
#	Then el sistema registra el sufragio


