from sources.sistema_electoral import SistemaElectoral
from sources.votante import Votante

def main():
    print("=== SIMULACIÓN DEL SISTEMA DE VOTO ELECTRÓNICO ===\n")

    sistema = SistemaElectoral("Elección de Decano de la FIS")
    print(f"🔧 Sistema creado para: {sistema.nombre}")
    sistema.activar_proceso_eleccion()

    votante1 = Votante("12345", "Juan Naranjo", "juan.naranjo01@epn.edu.ec")
    sistema.registrar_votante(votante1)
    sistema.esta_autorizado(votante1, True)
    print(f"🧑‍💼 Votante registrado y autorizado: {votante1.nombre}")

    votante2 = Votante("67890", "Ana Pérez", "ana.perez@epn.edu.ec")
    sistema.registrar_votante(votante2)
    sistema.esta_autorizado(votante2, True)
    print(f"🧑‍💼 Votante registrado y autorizado: {votante2.nombre}\n")

    sistema.registrar_voto(votante1, "Candidato A")
    print(f"🗳️ {votante1.nombre} votó por Candidato A")

    sistema.registrar_voto(votante2, "Candidato B")
    print(f"🗳️ {votante2.nombre} votó por Candidato B")


    print("\n🔁 Intento de voto doble por Juan Naranjo:")
    sistema.registrar_voto(votante1, "Candidato A")


    print("\n=== RESULTADOS PARCIALES ===")
    for candidato, total in sistema.conteo.items():
        print(f"🗳️ {candidato}: {total} voto(s)")

    # 6️⃣ Mostrar confirmaciones enviadas
    print("\n=== CONFIRMACIONES DE VOTO ENVIADAS ===")
    for correo in sistema.notificaciones_enviadas:
        print(f"📧 Confirmación enviada a: {correo}")

    # 7️⃣ Mostrar estado final de los votantes
    print("\n=== ESTADO FINAL DE LOS VOTANTES ===")
    for v in [votante1, votante2]:
        estado = "autorizado" if v.autorizado else "no autorizado"
        print(f"👤 {v.nombre}: {estado}")


if __name__ == "__main__":
    main()
