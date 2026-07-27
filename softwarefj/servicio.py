from abc import ABC, abstractmethod
from entidad import EntidadSistema
from excepciones import (
    DatoInvalidoError,
    ParametroFaltanteError,
    CalculoInconsistenteError,
)

IVA_COLOMBIA = 0.19


class Servicio(EntidadSistema, ABC):
    """
    Clase abstracta que define el contrato de cualquier servicio ofrecido
    por Software FJ: reservas de salas, alquiler de equipos, asesorías, etc.
    """

    def __init__(self, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__()
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.__disponible = disponible

    # ---------------- nombre ----------------
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        self.__nombre = str(valor).strip()

    # ---------------- tarifa_base ----------------
    @property
    def tarifa_base(self) -> float:
        return self.__tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor):
        try:
            valor_num = float(valor)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError(
                f"La tarifa base '{valor}' no es un número válido."
            ) from exc
        if valor_num <= 0:
            raise DatoInvalidoError("La tarifa base debe ser mayor que cero.")
        self.__tarifa_base = valor_num

    # ---------------- disponibilidad ----------------
    @property
    def disponible(self) -> bool:
        return self.__disponible

    def marcar_no_disponible(self):
        self.__disponible = False

    def marcar_disponible(self):
        self.__disponible = True

    # ---------------- contrato abstracto que cada hijo debe sobrescribir ----------------
    @abstractmethod
    def calcular_costo_base(self, cantidad: float) -> float:
        """Calcula el costo puro según la unidad de medida propia del servicio
        (horas, días, sesiones, etc.). Cada subclase decide su fórmula."""
        raise NotImplementedError

    @abstractmethod
    def validar_parametros(self, **kwargs) -> bool:
        """Valida que los parámetros específicos del servicio sean coherentes."""
        raise NotImplementedError

    # ---------------- "sobrecarga" de calcular_costo ----------------
    def calcular_costo(self, *args, **kwargs) -> float:
        """
        Método sobrecargado (simulado) para calcular el costo final:

        - calcular_costo(cantidad)
        - calcular_costo(cantidad, impuesto=True)
        - calcular_costo(cantidad, impuesto=True, descuento=0.10)
        - calcular_costo(cantidad=2, impuesto=False, descuento=0.05)

        Cualquier combinación válida de argumentos posicionales/nombrados
        es aceptada; los que falten toman valores por defecto.
        """
        if len(args) >= 1:
            cantidad = args[0]
        else:
            cantidad = kwargs.get("cantidad")

        impuesto = kwargs.get("impuesto", args[1] if len(args) >= 2 else False)
        descuento = kwargs.get("descuento", args[2] if len(args) >= 3 else 0.0)

        if cantidad is None:
            raise ParametroFaltanteError(
                "Debe indicarse la cantidad (horas/días/sesiones) para calcular el costo."
            )
        try:
            cantidad = float(cantidad)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError(f"La cantidad '{cantidad}' no es numérica.") from exc
        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad debe ser mayor que cero.")

        if not (0 <= float(descuento) <= 0.9):
            raise DatoInvalidoError("El descuento debe estar entre 0 y 0.9 (0% a 90%).")

        costo = self.calcular_costo_base(cantidad)

        if descuento:
            costo -= costo * float(descuento)

        if impuesto:
            costo += costo * IVA_COLOMBIA

        costo = round(costo, 2)

        if costo <= 0 or costo != costo:  # costo != costo detecta NaN
            raise CalculoInconsistenteError(
                f"El cálculo de costo produjo un valor inconsistente: {costo}"
            )
        return costo

    # ---------------- contrato EntidadSistema ----------------
    def validar(self) -> bool:
        return bool(self.__nombre) and self.__tarifa_base > 0

    def __str__(self) -> str:
        return self.descripcion()


class SalaReunion(Servicio):
    """Servicio de reserva de salas de reuniones, tarifado por hora."""

    def __init__(self, nombre: str, tarifa_base: float, capacidad: int, disponible: bool = True):
        super().__init__(nombre, tarifa_base, disponible)
        self.capacidad = capacidad

    @property
    def capacidad(self) -> int:
        return self.__capacidad

    @capacidad.setter
    def capacidad(self, valor):
        try:
            valor_int = int(valor)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError(f"La capacidad '{valor}' no es un entero válido.") from exc
        if valor_int <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser mayor que cero.")
        self.__capacidad = valor_int

    def calcular_costo_base(self, horas: float) -> float:
        return self.tarifa_base * horas

    def validar_parametros(self, **kwargs) -> bool:
        personas = kwargs.get("personas")
        if personas is not None and personas > self.__capacidad:
            raise DatoInvalidoError(
                f"La sala '{self.nombre}' tiene capacidad para {self.__capacidad} personas, "
                f"se solicitaron {personas}."
            )
        return True

    def descripcion(self) -> str:
        return (
            f"[Sala] #{self.id} {self.nombre} | Capacidad: {self.__capacidad} | "
            f"Tarifa/hora: ${self.tarifa_base:,.2f} | "
            f"{'Disponible' if self.disponible else 'No disponible'}"
        )


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos, tarifado por día."""

    def __init__(self, nombre: str, tarifa_base: float, tipo_equipo: str, disponible: bool = True):
        super().__init__(nombre, tarifa_base, disponible)
        self.tipo_equipo = tipo_equipo

    @property
    def tipo_equipo(self) -> str:
        return self.__tipo_equipo

    @tipo_equipo.setter
    def tipo_equipo(self, valor: str):
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El tipo de equipo es obligatorio.")
        self.__tipo_equipo = str(valor).strip()

    def calcular_costo_base(self, dias: float) -> float:
        # Recargo simple por alquileres prolongados (más de 7 días)
        if dias > 7:
            return self.tarifa_base * dias * 0.9  # 10% de descuento por volumen
        return self.tarifa_base * dias

    def validar_parametros(self, **kwargs) -> bool:
        dias = kwargs.get("dias")
        if dias is not None and dias > 90:
            raise DatoInvalidoError("No se permiten alquileres de equipo mayores a 90 días.")
        return True

    def descripcion(self) -> str:
        return (
            f"[Equipo] #{self.id} {self.nombre} ({self.__tipo_equipo}) | "
            f"Tarifa/día: ${self.tarifa_base:,.2f} | "
            f"{'Disponible' if self.disponible else 'No disponible'}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría especializada, tarifado por sesión de una hora."""

    def __init__(self, nombre: str, tarifa_base: float, area_experticia: str, disponible: bool = True):
        super().__init__(nombre, tarifa_base, disponible)
        self.area_experticia = area_experticia

    @property
    def area_experticia(self) -> str:
        return self.__area_experticia

    @area_experticia.setter
    def area_experticia(self, valor: str):
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El área de experticia es obligatoria.")
        self.__area_experticia = str(valor).strip()

    def calcular_costo_base(self, sesiones: float) -> float:
        return self.tarifa_base * sesiones

    def validar_parametros(self, **kwargs) -> bool:
        sesiones = kwargs.get("sesiones")
        if sesiones is not None and sesiones <= 0:
            raise DatoInvalidoError("El número de sesiones debe ser mayor que cero.")
        return True

    def descripcion(self) -> str:
        return (
            f"[Asesoría] #{self.id} {self.nombre} ({self.__area_experticia}) | "
            f"Tarifa/sesión: ${self.tarifa_base:,.2f} | "
            f"{'Disponible' if self.disponible else 'No disponible'}"
        )
