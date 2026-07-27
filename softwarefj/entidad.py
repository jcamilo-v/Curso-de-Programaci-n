from abc import ABC, abstractmethod
from datetime import datetime
import itertools


class EntidadSistema(ABC):
    """
    Clase abstracta que define el contrato común para toda entidad
    persistida en memoria dentro del sistema Software FJ.
    """

    _contador_global = itertools.count(1)

    def __init__(self):
        self._id = next(EntidadSistema._contador_global)
        self._fecha_creacion = datetime.now()

    @property
    def id(self) -> int:
        return self._id

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @abstractmethod
    def descripcion(self) -> str:
        """Cada entidad concreta debe describirse a sí misma en texto legible."""
        raise NotImplementedError

    @abstractmethod
    def validar(self) -> bool:
        """Cada entidad concreta debe poder validar su propio estado interno."""
        raise NotImplementedError

    def __str__(self) -> str:
        return self.descripcion()
