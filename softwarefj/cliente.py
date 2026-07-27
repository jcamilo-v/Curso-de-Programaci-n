import re
from entidad import EntidadSistema
from excepciones import DatoInvalidoError, ParametroFaltanteError


class Cliente(EntidadSistema):
    """
    Representa a un cliente de Software FJ.

    Todos los atributos son privados
    y se exponen únicamente mediante propiedades con validación estricta,
    garantizando la encapsulación real de los datos personales.
    """

    _PATRON_EMAIL = re.compile(r"^[\w\.\-+]+@[\w\-]+\.[a-zA-Z]{2,}$")
    _PATRON_TELEFONO = re.compile(r"^\+?\d{7,15}$")
    _PATRON_DOCUMENTO = re.compile(r"^\d{6,10}$")

    def __init__(self, nombre: str, documento: str, email: str, telefono: str):
        super().__init__()
        # Se usan los setters (propiedades) para reutilizar las validaciones
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.telefono = telefono
        self.__activo = True

    # ---------------- nombre ----------------
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        if valor is None or not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")
        if len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre debe tener al menos 3 caracteres.")
        if not all(c.isalpha() or c.isspace() for c in valor.strip()):
            raise DatoInvalidoError("El nombre solo puede contener letras y espacios.")
        self.__nombre = valor.strip().title()

    # ---------------- documento ----------------
    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor: str):
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError("El documento del cliente es obligatorio.")
        valor = str(valor).strip()
        if not self._PATRON_DOCUMENTO.match(valor):
            raise DatoInvalidoError(
                f"Documento '{valor}' inválido: debe tener entre 6 y 10 dígitos numéricos."
            )
        self.__documento = valor

    # ---------------- email ----------------
    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str):
        if valor is None or not valor.strip():
            raise ParametroFaltanteError("El email del cliente es obligatorio.")
        valor = valor.strip()
        if not self._PATRON_EMAIL.match(valor):
            raise DatoInvalidoError(f"El email '{valor}' no tiene un formato válido.")
        self.__email = valor.lower()

    # ---------------- telefono ----------------
    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError("El teléfono del cliente es obligatorio.")
        valor = str(valor).strip().replace(" ", "")
        if not self._PATRON_TELEFONO.match(valor):
            raise DatoInvalidoError(
                f"El teléfono '{valor}' no es válido (7 a 15 dígitos, opcionalmente con '+')."
            )
        self.__telefono = valor

    # ---------------- estado ----------------
    @property
    def activo(self) -> bool:
        return self.__activo

    def desactivar(self):
        self.__activo = False

    def activar(self):
        self.__activo = True

    # ---------------- contrato EntidadSistema ----------------
    def descripcion(self) -> str:
        estado = "activo" if self.__activo else "inactivo"
        return (
            f"Cliente #{self.id} | {self.__nombre} | Doc: {self.__documento} | "
            f"{self.__email} | Tel: {self.__telefono} | Estado: {estado}"
        )

    def validar(self) -> bool:
        # Si el objeto existe, ya pasó por los setters; se revalida por defensividad.
        return bool(self.__nombre and self.__documento and self.__email and self.__telefono)
