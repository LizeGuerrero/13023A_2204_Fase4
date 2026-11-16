
    
    
    # -*- coding: utf-8 -*-
"""
modelos.py (Parte 1)
====================

Modelos de dominio del sistema integral **Software FJ**.

Proyecto académico - UNAD
Paradigma: Programación Orientada a Objetos (POO).

Contenido de esta primera parte
-------------------------------
1. ``EntidadBase`` : clase abstracta que define el contrato común de todas las
                     entidades del sistema (abstracción y polimorfismo).
2. ``Cliente``     : entidad concreta con atributos encapsulados y validación
                     estricta del correo electrónico.

Dependencias
------------
Requiere el módulo ``excepciones.py`` (``SoftwareFJError``), que debe estar en
la misma carpeta que este archivo.
"""

# ---------------------------------------------------------------------------
# Importaciones
# ---------------------------------------------------------------------------
from abc import ABC, abstractmethod

from excepciones import SoftwareFJError


# ---------------------------------------------------------------------------
# Clase abstracta base
# ---------------------------------------------------------------------------
class EntidadBase(ABC):
    """Clase abstracta que representa cualquier entidad del sistema Software FJ.

    No se puede instanciar directamente. Obliga a las clases hijas a
    implementar ``mostrar_detalle()``, garantizando que todas las entidades
    (clientes, servicios, reservas...) puedan describirse de forma uniforme
    (polimorfismo).

    Attributes:
        _identificador (str): Código único de la entidad (encapsulado).
    """

    def __init__(self, identificador: str) -> None:
        """Inicializa la entidad con su identificador único.

        Args:
            identificador: Código único de la entidad. No puede estar vacío.

        Raises:
            SoftwareFJError: Si el identificador está vacío o no es texto.
        """
        # Se asigna mediante la propiedad para reutilizar su validación.
        self._identificador: str = ""
        self.identificador = identificador

    @property
    def identificador(self) -> str:
        """str: Identificador único de la entidad."""
        return self._identificador

    @identificador.setter
    def identificador(self, valor: str) -> None:
        """Valida y asigna el identificador.

        Args:
            valor: Nuevo identificador.

        Raises:
            SoftwareFJError: Si el valor no es texto o está vacío.
        """
        if not isinstance(valor, str) or not valor.strip():
            raise SoftwareFJError(
                "El identificador es obligatorio y debe ser texto no vacío",
                contexto="EntidadBase",
            )
        self._identificador = valor.strip()

    @abstractmethod
    def mostrar_detalle(self) -> str:
        """Devuelve una descripción legible de la entidad.

        Método abstracto: cada clase hija debe implementarlo a su manera.

        Returns:
            Texto con el detalle de la entidad.
        """

    def __str__(self) -> str:
        """Representación en texto: delega en ``mostrar_detalle()``."""
        return self.mostrar_detalle()


# ---------------------------------------------------------------------------
# Entidad concreta: Cliente
# ---------------------------------------------------------------------------
class Cliente(EntidadBase):
    """Representa a un cliente de Software FJ.

    Todos sus atributos son privados (encapsulamiento) y se acceden mediante
    propiedades que validan los datos antes de guardarlos.

    Attributes:
        _nombre (str): Nombre completo del cliente.
        _correo (str): Correo electrónico validado del cliente.
    """

    def __init__(self, identificador: str, nombre: str, correo: str) -> None:
        """Crea un cliente validando todos sus datos.

        Args:
            identificador: Código único del cliente (ej. documento de identidad).
            nombre: Nombre completo del cliente.
            correo: Correo electrónico con formato válido.

        Raises:
            SoftwareFJError: Si el identificador, el nombre o el correo no
                cumplen las reglas de validación.
        """
        super().__init__(identificador)
        self._nombre: str = ""
        self._correo: str = ""
        # Se usan las propiedades (no los atributos) para forzar la validación.
        self.nombre = nombre
        self.correo = correo

    # ----- Nombre ----------------------------------------------------------
    @property
    def nombre(self) -> str:
        """str: Nombre completo del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida y asigna el nombre.

        Args:
            valor: Nuevo nombre del cliente.

        Raises:
            SoftwareFJError: Si el nombre no es texto o está vacío.
        """
        if not isinstance(valor, str) or not valor.strip():
            raise SoftwareFJError(
                "El nombre del cliente es obligatorio y no puede estar vacío",
                contexto="Cliente",
            )
        self._nombre = valor.strip()

    # ----- Correo ----------------------------------------------------------
    @property
    def correo(self) -> str:
        """str: Correo electrónico validado del cliente."""
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        """Valida el formato del correo y lo asigna.

        Reglas aplicadas:
            * Debe ser texto sin espacios.
            * Debe contener exactamente un '@'.
            * Debe haber texto antes del '@' (usuario).
            * Después del '@' debe haber un dominio con al menos un '.', que
              no esté al inicio ni al final del dominio (ej. ``ejemplo.com``).

        Args:
            valor: Correo electrónico a validar.

        Raises:
            SoftwareFJError: Si el correo no cumple el formato esperado.
        """
        # 1) Debe ser texto; se eliminan espacios laterales accidentales.
        if not isinstance(valor, str):
            raise SoftwareFJError(
                "El correo debe ser una cadena de texto", contexto="Cliente"
            )
        correo = valor.strip()

        # 2) No puede contener espacios internos ni estar vacío.
        if not correo or " " in correo:
            raise SoftwareFJError(
                f"Correo inválido '{valor}': no puede estar vacío ni tener espacios",
                contexto="Cliente",
            )

        # 3) Debe tener exactamente un '@'.
        if correo.count("@") != 1:
            raise SoftwareFJError(
                f"Correo inválido '{valor}': debe contener un único '@'",
                contexto="Cliente",
            )

        usuario, dominio = correo.split("@")

        # 4) Debe existir un usuario antes del '@'.
        if not usuario:
            raise SoftwareFJError(
                f"Correo inválido '{valor}': falta el usuario antes del '@'",
                contexto="Cliente",
            )

        # 5) El dominio debe tener un '.' que no esté en los extremos.
        if "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
            raise SoftwareFJError(
                f"Correo inválido '{valor}': el dominio debe tener un '.' "
                "válido (ej. ejemplo.com)",
                contexto="Cliente",
            )

        # Todas las validaciones pasaron: se guarda el correo.
        self._correo = correo

    # ----- Implementación del método abstracto -----------------------------
    def mostrar_detalle(self) -> str:
        """Devuelve el detalle del cliente en una línea.

        Returns:
            Texto con identificador, nombre y correo del cliente.
        """
        return (
            f"Cliente [ID: {self.identificador}] "
            f"Nombre: {self.nombre} | Correo: {self.correo}"
        )
