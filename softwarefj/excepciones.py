"""
Todas las excepciones propias del dominio heredan de SoftwareFJError,
lo que permite capturarlas de forma genérica o específica según el caso.
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class DatoInvalidoError(SoftwareFJError):
    """Se lanza cuando un dato no cumple las reglas de validación (formato, tipo, rango)."""
    pass


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando falta un parámetro obligatorio para completar una operación."""
    pass


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una operación que el estado actual del objeto no permite."""
    pass


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza ante intentos de reserva incorrectos (duración, fechas, cliente/servicio inválido)."""
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando el servicio solicitado no está disponible para reservar."""
    pass


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos produce un resultado inconsistente (negativo, NaN, etc.)."""
    pass


class ClienteNoEncontradoError(SoftwareFJError):
    """Se lanza cuando se busca un cliente que no existe en el sistema."""
    pass
