# -*- coding: utf-8 -*-
"""
Paquete reservas

Reúne la clase Reserva y el enum con sus estados:

    from reservas import Reserva, EstadoReserva
"""

# Estados de la reserva
from reservas.estado import EstadoReserva

# Clase principal
from reservas.reserva import Reserva

# Nombres que se exportan al hacer "from reservas import *"
__all__ = ["EstadoReserva", "Reserva"]
