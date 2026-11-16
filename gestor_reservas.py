# -*- coding: utf-8 -*-
"""
gestor_reservas.py

Gestor de reservas del sistema Software FJ.

Funciona igual que GestorClientes (gestor.py), pero para las reservas:
mantiene una lista privada de objetos Reserva en memoria y permite agregar
(sin repetir identificadores), buscar y listar.

Las operaciones de cada reserva (confirmar, cancelar y procesar) las hace la
propia clase Reserva; el gestor solo la entrega con buscar_reserva():

    gestor.buscar_reserva("R-001").confirmar()

Las reservas no se guardan en archivos: el enunciado indica que los archivos
solo se usan para el registro de eventos y errores.
"""

# Excepciones que usa el gestor
from excepciones import (
    OperacionNoPermitidaError,
    RecursoNoDisponibleError,
    ValidacionError,
)

# Clase de las reservas
from reservas import Reserva


class GestorReservas:
    """Administra la colección de reservas del sistema.

    Atributos:
        _reservas: lista privada con las reservas registradas.
    """

    def __init__(self):
        """Crea un gestor sin reservas."""
        # La lista nace vacía; solo se modifica con los métodos del gestor
        self._reservas = []

    def __len__(self):
        """Devuelve la cantidad de reservas registradas."""
        return len(self._reservas)

    def existe_reserva(self, identificador):
        """Indica si ya hay una reserva con ese identificador.

        Args:
            identificador: identificador a comprobar.

        Returns:
            True si existe una reserva con ese identificador.
        """
        # Se limpia el texto para no fallar por espacios sobrantes
        identificador = str(identificador).strip()

        # any() devuelve True apenas encuentra una coincidencia
        return any(r.identificador == identificador for r in self._reservas)

    def buscar_reserva(self, identificador):
        """Busca una reserva por su identificador.

        Args:
            identificador: identificador de la reserva buscada.

        Returns:
            El objeto Reserva encontrado.

        Raises:
            RecursoNoDisponibleError: si no existe esa reserva.
        """
        # Se limpia el texto para no fallar por espacios sobrantes
        identificador = str(identificador).strip()

        # Se recorre la lista hasta encontrar la reserva
        for reserva in self._reservas:
            if reserva.identificador == identificador:
                return reserva

        # Si el ciclo termina sin encontrarla, la reserva no existe
        raise RecursoNoDisponibleError(
            f"No existe una reserva con identificador '{identificador}'",
            contexto="GestorReservas",
        )

    def agregar_reserva(self, reserva):
        """Registra una reserva evitando identificadores repetidos.

        Args:
            reserva: objeto Reserva ya validado.

        Raises:
            ValidacionError: si el objeto no es una Reserva.
            OperacionNoPermitidaError: si ya existe una reserva con ese
                identificador.
        """
        # Solo se aceptan objetos Reserva
        if not isinstance(reserva, Reserva):
            raise ValidacionError(
                "Solo se pueden registrar objetos de tipo Reserva",
                contexto="GestorReservas",
            )

        # El identificador debe ser único entre todas las reservas
        if self.existe_reserva(reserva.identificador):
            raise OperacionNoPermitidaError(
                f"Ya existe una reserva con identificador '{reserva.identificador}'",
                contexto="GestorReservas",
            )

        # Todo correcto: se agrega a la lista
        self._reservas.append(reserva)

    def listar_reservas(self):
        """Devuelve una copia de la lista de reservas.

        Se entrega una copia para que desde afuera no se pueda modificar la
        lista interna (encapsulamiento).

        Returns:
            Lista con las reservas, en el orden en que se registraron.
        """
        return list(self._reservas)

    def mostrar_reservas(self):
        """Construye un texto con el detalle de todas las reservas.

        No imprime nada: devuelve el texto para que la consola decida cómo
        mostrarlo.

        Returns:
            Una línea por reserva, o un aviso si no hay registros.
        """
        # Si la lista está vacía se avisa
        if not self._reservas:
            return "No hay reservas registradas."

        # mostrar_detalle() viene de EntidadBase y cada clase lo implementa
        return "\n".join(r.mostrar_detalle() for r in self._reservas)
