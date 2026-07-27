from cliente import Cliente
from servicio import Servicio
from reserva import Reserva, EstadoReserva
from excepciones import SoftwareFJError, ClienteNoEncontradoError
from logger import logger


class SistemaSoftwareFJ:
    def __init__(self):
        self.__clientes = []   # list[Cliente]
        self.__servicios = []  # list[Servicio]
        self.__reservas = []   # list[Reserva]

    # ---------------- clientes ----------------
    def registrar_cliente(self, nombre, documento, email, telefono) -> Cliente:
        try:
            if any(c.documento == str(documento).strip() for c in self.__clientes):
                raise SoftwareFJError(
                    f"Ya existe un cliente registrado con el documento '{documento}'."
                )
            cliente = Cliente(nombre, documento, email, telefono)
        except SoftwareFJError as exc:
            logger.error(f"Fallo al registrar cliente ({nombre!r}): {exc.mensaje}")
            raise
        else:
            self.__clientes.append(cliente)
            logger.info(f"Cliente registrado exitosamente: {cliente.descripcion()}")
            return cliente

    def buscar_cliente(self, documento: str) -> Cliente:
        for c in self.__clientes:
            if c.documento == str(documento).strip():
                return c
        raise ClienteNoEncontradoError(f"No existe un cliente con documento '{documento}'.")

    @property
    def clientes(self):
        return list(self.__clientes)  # copia defensiva

    # ---------------- servicios ----------------
    def registrar_servicio(self, servicio_cls, *args, **kwargs) -> Servicio:
        try:
            servicio = servicio_cls(*args, **kwargs)
        except SoftwareFJError as exc:
            logger.error(f"Fallo al registrar servicio ({servicio_cls.__name__}): {exc.mensaje}")
            raise
        else:
            self.__servicios.append(servicio)
            logger.info(f"Servicio registrado exitosamente: {servicio.descripcion()}")
            return servicio

    @property
    def servicios(self):
        return list(self.__servicios)

    # ---------------- reservas ----------------
    def crear_reserva(self, cliente: Cliente, servicio: Servicio, cantidad) -> Reserva:
        try:
            reserva = Reserva(cliente, servicio, cantidad)
        except SoftwareFJError as exc:
            logger.error(
                f"Fallo al crear reserva (cliente={getattr(cliente, 'nombre', '???')!r}, "
                f"servicio={getattr(servicio, 'nombre', '???')!r}): {exc.mensaje}"
            )
            raise
        else:
            self.__reservas.append(reserva)
            logger.info(f"Reserva creada exitosamente: {reserva.descripcion()}")
            return reserva

    @property
    def reservas(self):
        return list(self.__reservas)

    # ---------------- reportes ----------------
    def resumen(self) -> str:
        lineas = ["=" * 70, "RESUMEN DEL SISTEMA SOFTWARE FJ", "=" * 70]
        lineas.append(f"\nClientes registrados ({len(self.__clientes)}):")
        for c in self.__clientes:
            lineas.append(f"  - {c.descripcion()}")

        lineas.append(f"\nServicios registrados ({len(self.__servicios)}):")
        for s in self.__servicios:
            lineas.append(f"  - {s.descripcion()}")

        lineas.append(f"\nReservas registradas ({len(self.__reservas)}):")
        for r in self.__reservas:
            lineas.append(f"  - {r.descripcion()}")

        procesadas = [r for r in self.__reservas if r.estado == EstadoReserva.PROCESADA]
        ingresos = sum(r.costo_final for r in procesadas)
        lineas.append(f"\nIngresos totales por reservas procesadas: ${ingresos:,.2f}")
        lineas.append("=" * 70)
        return "\n".join(lineas)
