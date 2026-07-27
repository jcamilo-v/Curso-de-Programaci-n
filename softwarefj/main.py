from sistema import SistemaSoftwareFJ
from servicio import SalaReunion, AlquilerEquipo, AsesoriaEspecializada
from excepciones import SoftwareFJError
from logger import logger, get_log_path


def operacion(numero: int, titulo: str, funcion):
    """
    Envoltorio genérico que ejecuta una operación del sistema y garantiza
    que un fallo en una operación NUNCA detenga la ejecución del programa.
    """
    print(f"\n--- Operación {numero}: {titulo} ---")
    try:
        resultado = funcion()
    except SoftwareFJError as exc:
        # Errores de negocio esperados: se informan y quedan en el log.
        print(f"  [ERROR CONTROLADO] {exc.mensaje}")
        logger.warning(f"Operación {numero} ({titulo}) finalizó con error controlado: {exc.mensaje}")
    except Exception as exc:  # noqa: BLE001 - resguardo final ante errores no previstos
        print(f"  [ERROR INESPERADO] {type(exc).__name__}: {exc}")
        logger.exception(f"Operación {numero} ({titulo}) falló con un error NO controlado.")
    else:
        print(f"  [OK] {resultado}")
        return resultado


def main():
    sistema = SistemaSoftwareFJ()
    logger.info("===== INICIO DE SIMULACIÓN SOFTWARE FJ =====")

    # 1) Registro de cliente válido
    cliente1 = operacion(
        1, "Registrar cliente válido",
        lambda: sistema.registrar_cliente("Paola Cadena", "1130612345", "paola@softwarefj.com", "3001234567"),
    )

    # 2) Registro de cliente inválido (email mal formado)
    operacion(
        2, "Registrar cliente con email inválido",
        lambda: sistema.registrar_cliente("Carlos Ruiz", "1130699999", "carlos_at_correo", "3007654321"),
    )

    # 3) Registro de cliente inválido (documento no numérico / parámetro faltante)
    operacion(
        3, "Registrar cliente con documento vacío",
        lambda: sistema.registrar_cliente("Ana Torres", "", "ana@correo.com", "3009876543"),
    )

    # 4) Segundo cliente válido, necesario para más reservas
    cliente2 = operacion(
        4, "Registrar segundo cliente válido",
        lambda: sistema.registrar_cliente("Julián Gómez", "1130698888", "julian@softwarefj.com", "3011122233"),
    )

    # 5) Creación correcta de servicio: Sala de reuniones
    sala = operacion(
        5, "Crear servicio Sala de Reuniones (correcto)",
        lambda: sistema.registrar_servicio(SalaReunion, "Sala Ejecutiva A", 50000, 10),
    )

    # 6) Creación incorrecta de servicio: tarifa negativa
    operacion(
        6, "Crear servicio de Alquiler de Equipo con tarifa negativa (incorrecto)",
        lambda: sistema.registrar_servicio(AlquilerEquipo, "Videobeam Epson", -20000, "Proyector"),
    )

    # 7) Creación correcta de servicio: Alquiler de equipo
    equipo = operacion(
        7, "Crear servicio Alquiler de Equipo (correcto)",
        lambda: sistema.registrar_servicio(AlquilerEquipo, "Portátil Dell i7", 45000, "Computador"),
    )

    # 8) Creación correcta de servicio: Asesoría especializada
    asesoria = operacion(
        8, "Crear servicio Asesoría Especializada (correcto)",
        lambda: sistema.registrar_servicio(AsesoriaEspecializada, "Consultoría en Analítica", 120000, "Business Analytics"),
    )

    # 9) Reserva exitosa: sala de reuniones, con impuesto
    reserva1 = operacion(
        9, "Crear y procesar reserva de sala (exitosa)",
        lambda: _flujo_reserva_completo(sistema, cliente1, sala, cantidad=3, impuesto=True, descuento=0.0),
    )

    # 10) Reserva fallida: servicio no disponible
    if equipo:
        equipo.marcar_no_disponible()
    operacion(
        10, "Intentar reservar equipo marcado como no disponible (fallida)",
        lambda: sistema.crear_reserva(cliente2, equipo, 2),
    )

    # 11) Reserva fallida: cantidad inválida (negativa)
    operacion(
        11, "Crear reserva con cantidad negativa (fallida)",
        lambda: sistema.crear_reserva(cliente2, asesoria, -5),
    )

    # 12) Reserva exitosa: asesoría especializada con descuento, sin impuesto
    operacion(
        12, "Crear y procesar reserva de asesoría con descuento (exitosa)",
        lambda: _flujo_reserva_completo(sistema, cliente2, asesoria, cantidad=2, impuesto=False, descuento=0.10),
    )

    # 13) Intento de procesar una reserva sin confirmarla primero (operación no permitida)
    operacion(
        13, "Procesar reserva sin confirmar (operación no permitida)",
        lambda: _reserva_sin_confirmar(sistema, cliente1, sala),
    )

    # 14) Cancelar una reserva ya procesada (operación no permitida)
    operacion(
        14, "Cancelar una reserva ya procesada (fallida)",
        lambda: reserva1.cancelar("Cliente se arrepintió") if reserva1 else _fallar("No hay reserva1"),
    )

    # 15) Búsqueda de cliente inexistente
    operacion(
        15, "Buscar cliente con documento inexistente",
        lambda: sistema.buscar_cliente("0000000000"),
    )

    print("\n" + sistema.resumen())
    print(f"\nArchivo de logs generado en: {get_log_path()}")
    logger.info("===== FIN DE SIMULACIÓN SOFTWARE FJ =====")


def _flujo_reserva_completo(sistema, cliente, servicio, cantidad, impuesto, descuento):
    """Crea, confirma y procesa una reserva en un solo flujo, para simular un caso de uso real."""
    reserva = sistema.crear_reserva(cliente, servicio, cantidad)
    reserva.confirmar()
    reserva.procesar(aplicar_impuesto=impuesto, descuento=descuento)
    return reserva


def _reserva_sin_confirmar(sistema, cliente, servicio):
    """Crea una reserva y trata de procesarla sin pasar por confirmar() -> debe fallar controladamente."""
    reserva = sistema.crear_reserva(cliente, servicio, 1)
    reserva.procesar()  # Debe lanzar OperacionNoPermitidaError
    return reserva.descripcion()


def _fallar(mensaje):
    raise RuntimeError(mensaje)


if __name__ == "__main__":
    main()
