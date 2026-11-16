# -*- coding: utf-8 -*-
"""
estado.py

Estados por los que puede pasar una reserva y las transiciones permitidas.

Flujo permitido:

    PENDIENTE  ->  CONFIRMADA  ->  PROCESADA
        |              |
        +--> CANCELADA <--+

Una reserva CANCELADA o PROCESADA ya no puede cambiar de estado.
"""

# Enum permite definir un conjunto fijo de valores con nombre
from enum import Enum


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""

    # Recién creada, todavía sin confirmar
    PENDIENTE = "Pendiente"

    # Confirmada por la empresa, lista para procesar
    CONFIRMADA = "Confirmada"

    # Cancelada antes de procesarse
    CANCELADA = "Cancelada"

    # Procesada: ya se calculó el costo final
    PROCESADA = "Procesada"

    def puede_pasar_a(self, destino):
        """Indica si desde este estado se puede pasar al estado destino.

        Args:
            destino: estado al que se quiere llegar.

        Returns:
            True si la transición está permitida, False si no.
        """
        # Se consulta la tabla de transiciones definida más abajo
        return destino in TRANSICIONES_PERMITIDAS[self]


# Tabla de transiciones: para cada estado, a cuáles se puede pasar.
# Se define después de la clase porque necesita que los estados ya existan.
TRANSICIONES_PERMITIDAS = {
    EstadoReserva.PENDIENTE: {EstadoReserva.CONFIRMADA, EstadoReserva.CANCELADA},
    EstadoReserva.CONFIRMADA: {EstadoReserva.PROCESADA, EstadoReserva.CANCELADA},
    EstadoReserva.CANCELADA: set(),
    EstadoReserva.PROCESADA: set(),
}
