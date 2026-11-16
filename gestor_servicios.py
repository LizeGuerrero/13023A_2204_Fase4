# -*- coding: utf-8 -*-
"""
gestor_servicios.py

Gestor de servicios del sistema Software FJ.

Funciona igual que GestorClientes (gestor.py), pero para los servicios:
mantiene una lista privada de objetos Servicio en memoria y permite agregar
(sin repetir identificadores), buscar y listar.

Los servicios no se guardan en archivos. El enunciado indica que los archivos
solo se usan para el registro de eventos y errores, así que los servicios
viven en memoria mientras el programa está abierto.
"""

# Excepciones que usa el gestor
from excepciones import (
    OperacionNoPermitidaError,
    RecursoNoDisponibleError,
    ValidacionError,
)

# Clase abstracta: sirve para aceptar cualquiera de los tres servicios
from servicios import Servicio


class GestorServicios:
    """Administra la colección de servicios del sistema.

    Atributos:
        _servicios: lista privada con los servicios registrados.
    """

    def __init__(self):
        """Crea un gestor sin servicios."""
        # La lista nace vacía; solo se modifica con los métodos del gestor
        self._servicios = []

    def __len__(self):
        """Devuelve la cantidad de servicios registrados."""
        return len(self._servicios)

    def existe_servicio(self, identificador):
        """Indica si ya hay un servicio con ese identificador.

        Args:
            identificador: identificador a comprobar.

        Returns:
            True si existe un servicio con ese identificador.
        """
        # Se limpia el texto para no fallar por espacios sobrantes
        identificador = str(identificador).strip()

        # any() devuelve True apenas encuentra una coincidencia
        return any(s.identificador == identificador for s in self._servicios)

    def buscar_servicio(self, identificador):
        """Busca un servicio por su identificador.

        Args:
            identificador: identificador del servicio buscado.

        Returns:
            El objeto Servicio encontrado.

        Raises:
            RecursoNoDisponibleError: si no existe ese servicio.
        """
        # Se limpia el texto para no fallar por espacios sobrantes
        identificador = str(identificador).strip()

        # Se recorre la lista hasta encontrar el servicio
        for servicio in self._servicios:
            if servicio.identificador == identificador:
                return servicio

        # Si el ciclo termina sin encontrarlo, el servicio no existe
        raise RecursoNoDisponibleError(
            f"No existe un servicio con identificador '{identificador}'",
            contexto="GestorServicios",
        )

    def agregar_servicio(self, servicio):
        """Registra un servicio evitando identificadores repetidos.

        Args:
            servicio: objeto Servicio ya validado.

        Raises:
            ValidacionError: si el objeto no es un Servicio.
            OperacionNoPermitidaError: si ya existe un servicio con ese
                identificador.
        """
        # Solo se aceptan objetos Servicio (cualquiera de sus hijas)
        if not isinstance(servicio, Servicio):
            raise ValidacionError(
                "Solo se pueden registrar objetos de tipo Servicio",
                contexto="GestorServicios",
            )

        # El identificador debe ser único entre todos los servicios
        if self.existe_servicio(servicio.identificador):
            raise OperacionNoPermitidaError(
                f"Ya existe un servicio con identificador '{servicio.identificador}'",
                contexto="GestorServicios",
            )

        # Todo correcto: se agrega a la lista
        self._servicios.append(servicio)

    def listar_servicios(self):
        """Devuelve una copia de la lista de servicios.

        Se entrega una copia para que desde afuera no se pueda modificar la
        lista interna (encapsulamiento).

        Returns:
            Lista con los servicios, en el orden en que se registraron.
        """
        return list(self._servicios)

    def mostrar_servicios(self):
        """Construye un texto con la descripción de todos los servicios.

        No imprime nada: devuelve el texto para que la consola decida cómo
        mostrarlo.

        Returns:
            Una línea por servicio, o un aviso si no hay registros.
        """
        # Si la lista está vacía se avisa
        if not self._servicios:
            return "No hay servicios registrados."

        # describir() es polimórfico: cada servicio responde a su manera
        return "\n".join(s.describir() for s in self._servicios)
