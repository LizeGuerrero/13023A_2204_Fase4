# -*- coding: utf-8 -*-
"""
Paquete servicios

Reúne la clase abstracta Servicio y los tres servicios especializados de
Software FJ. Con este archivo se pueden importar todos desde un solo lugar:

    from servicios import SalaReuniones, AlquilerEquipo, AsesoriaEspecializada
"""

# Clase abstracta y constante de impuesto
from servicios.servicio import IVA_GENERAL, Servicio

# Servicios especializados
from servicios.sala import SalaReuniones
from servicios.equipo import AlquilerEquipo
from servicios.asesoria import AsesoriaEspecializada

# Nombres que se exportan al hacer "from servicios import *"
__all__ = [
    "IVA_GENERAL",
    "Servicio",
    "SalaReuniones",
    "AlquilerEquipo",
    "AsesoriaEspecializada",
]
