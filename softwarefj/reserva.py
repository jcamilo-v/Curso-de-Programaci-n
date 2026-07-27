from enum import Enum
from entidad import EntidadSistema
from cliente import Cliente
from servicio import Servicio
from excepciones import (
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    DatoInvalidoError,
)
from logger import logger


class EstadoReserva(Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"


class Reserva(EntidadSistema):
    """
    Representa la reserva de un servicio por parte de un cliente, con una
    duración/cantidad determinada (horas, días o sesiones según el servicio).
    """

    def __init__(self, cliente: Cliente, servicio: Servicio, cantidad: float):
        super().__init__()

        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere una instancia válida de Servicio.")
        if not cliente.activo:
            raise ReservaInvalidaError(
                f"El cliente '{cliente.nombre}' está inactivo y no puede generar reservas."
            )
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible actualmente."
            )
        if cantidad is None:
            raise ParametroFaltanteError("Debe indicarse la cantidad/duración de la reserva.")
        try:
            cantidad = float(cantidad)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError(f"La cantidad '{cantidad}' no es numérica.") from exc
        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad/duración de la reserva debe ser mayor que cero.")

        self.__cliente = cliente
        self.__servicio = servicio
        self.__cantidad = cantidad
        self.__estado = EstadoReserva.PENDIENTE
        self.__costo_final = None

    # ---------------- accesores de solo lectura ----------------
    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def cantidad(self) -> float:
        return self.__cantidad

    @property
    def estado(self) -> EstadoReserva:
        return self.__estado

    @property
    def costo_final(self):
        return self.__costo_final

    # ---------------- ciclo de vida ----------------
    def confirmar(self):
        """Pasa la reserva de PENDIENTE a CONFIRMADA."""
        if self.__estado != EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva #{self.id}: estado actual '{self.__estado.value}'."
            )
        if not self.__servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.__servicio.nombre}' dejó de estar disponible."
            )
        self.__estado = EstadoReserva.CONFIRMADA
        logger.info(f"Reserva #{self.id} confirmada para cliente '{self.__cliente.nombre}'.")

    def cancelar(self, motivo: str = "No especificado"):
        """Cancela la reserva, sin importar su estado previo, salvo que ya esté procesada."""
        if self.__estado == EstadoReserva.PROCESADA:
            raise OperacionNoPermitidaError(
                f"La reserva #{self.id} ya fue procesada y no puede cancelarse."
            )
        if self.__estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaError(f"La reserva #{self.id} ya estaba cancelada.")
        self.__estado = EstadoReserva.CANCELADA
        logger.info(f"Reserva #{self.id} cancelada. Motivo: {motivo}.")

    def procesar(self, aplicar_impuesto: bool = True, descuento: float = 0.0):
        """
        Calcula el costo final y marca la reserva como PROCESADA.
        Encadena excepciones (raise ... from exc) si el cálculo de costo falla.
        """
        if self.__estado != EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"La reserva #{self.id} debe estar CONFIRMADA antes de procesarse "
                f"(estado actual: '{self.__estado.value}')."
            )
        try:
            costo = self.__servicio.calcular_costo(
                self.__cantidad, impuesto=aplicar_impuesto, descuento=descuento
            )
        except Exception as exc:
            # Encadenamiento de excepciones: se preserva la causa original.
            raise OperacionNoPermitidaError(
                f"No fue posible procesar la reserva #{self.id} por un error en el cálculo de costo."
            ) from exc
        else:
            self.__costo_final = costo
            self.__estado = EstadoReserva.PROCESADA
            logger.info(
                f"Reserva #{self.id} procesada. Cliente: '{self.__cliente.nombre}', "
                f"Servicio: '{self.__servicio.nombre}', Costo final: ${costo:,.2f}."
            )
        finally:
            logger.debug(f"Intento de procesamiento finalizado para reserva #{self.id}.")

    # ---------------- contrato EntidadSistema ----------------
    def descripcion(self) -> str:
        costo_txt = f"${self.__costo_final:,.2f}" if self.__costo_final is not None else "N/A"
        return (
            f"Reserva #{self.id} | Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} | Cantidad: {self.__cantidad} | "
            f"Estado: {self.__estado.value} | Costo: {costo_txt}"
        )

    def validar(self) -> bool:
        return (
            isinstance(self.__cliente, Cliente)
            and isinstance(self.__servicio, Servicio)
            and self.__cantidad > 0
        )
