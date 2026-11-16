# -*- coding: utf-8 -*-
"""
equipo.py

Servicio de alquiler de equipos (portátiles, proyectores, cámaras, etc.).

Hereda de Servicio y sobrescribe describir(), validar_parametros() y
calcular_costo_base().

Parámetros que acepta al solicitar el servicio:
    unidades    (opcional, 1 por defecto) cantidad de equipos que se alquilan;
                no puede superar las unidades disponibles.
    con_seguro  (opcional, False por defecto) agrega un seguro del 5 % sobre
                el costo del alquiler.

Costo base = horas * tarifa por hora * unidades (+ 5 % si lleva seguro).
"""

# Excepciones que puede lanzar este servicio
from excepciones import RecursoNoDisponibleError, ValidacionError

# Clase de la que hereda
from servicios.servicio import Servicio

# Función de validación compartida
from validaciones import validar_entero


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos por horas.

    Atributos propios:
        _unidades_disponibles: cuántos equipos de este tipo hay para alquilar.
    """

    # Datos propios de este servicio
    TIPO = "AlquilerEquipo"
    DURACION_MINIMA = 1
    DURACION_MAXIMA = 72

    # Porcentaje del seguro opcional, como fracción (5 %)
    TASA_SEGURO = 0.05

    def __init__(self, identificador, nombre, tarifa_hora, unidades_disponibles, disponible=True):
        """Crea un servicio de alquiler de equipos.

        Args:
            identificador: código único del servicio.
            nombre: nombre del equipo que se alquila.
            tarifa_hora: valor de una hora de alquiler por unidad, en pesos.
            unidades_disponibles: cantidad de equipos en inventario.
            disponible: si el servicio nace disponible. Por defecto True.

        Raises:
            ValidacionError: si algún dato no es válido.
        """
        # Primero se construye la parte común (identificador, nombre, tarifa)
        super().__init__(identificador, nombre, tarifa_hora, disponible)

        # Se declara el atributo y luego se asigna con la propiedad para validar
        self._unidades_disponibles = 0
        self.unidades_disponibles = unidades_disponibles

    @property
    def unidades_disponibles(self):
        """int: cantidad de equipos que hay para alquilar."""
        return self._unidades_disponibles

    @unidades_disponibles.setter
    def unidades_disponibles(self, valor):
        """Valida y guarda las unidades en inventario."""
        # Se permite cero (sin existencias), pero no negativos
        self._unidades_disponibles = validar_entero(
            valor, "unidades disponibles", self.TIPO, minimo=0
        )

    def describir(self):
        """Describe el equipo con su inventario, tarifa y estado.

        Returns:
            Texto de una línea con los datos del servicio.
        """
        # Se arma el texto del estado a partir del booleano
        estado = "disponible" if self.disponible else "no disponible"

        # Se devuelve la descripción completa en una sola línea
        return (
            f"Alquiler de equipo [ID: {self.identificador}] {self.nombre} | "
            f"Unidades: {self.unidades_disponibles} | "
            f"Tarifa: ${self.tarifa_hora:,.0f} por hora y unidad | Estado: {estado}"
        )

    def validar_parametros(self, duracion, **opciones):
        """Revisa duración, unidades y seguro de una solicitud.

        Args:
            duracion: horas de alquiler.
            **opciones: unidades y con_seguro, ambos opcionales.

        Raises:
            ValidacionError: si algún parámetro es inválido.
            RecursoNoDisponibleError: si se piden más unidades de las que hay.
        """
        # Solo se aceptan los dos parámetros que usa este servicio
        self._rechazar_opciones_desconocidas(opciones, ("unidades", "con_seguro"))

        # La duración se valida con el rango propio del alquiler (1 a 72 horas)
        self._validar_duracion(duracion)

        # Si no se indican unidades se asume una sola
        unidades = validar_entero(opciones.get("unidades", 1), "unidades", self.TIPO, minimo=1)

        # No se pueden alquilar más equipos de los que hay
        if unidades > self.unidades_disponibles:
            raise RecursoNoDisponibleError(
                f"Solo hay {self.unidades_disponibles} unidad(es) de '{self.nombre}' "
                f"y se pidieron {unidades}",
                contexto=self.TIPO,
            )

        # El seguro es opcional, pero si viene debe ser True o False
        if "con_seguro" in opciones and not isinstance(opciones["con_seguro"], bool):
            raise ValidacionError(
                "El parámetro 'con_seguro' debe ser True o False", contexto=self.TIPO
            )

    def calcular_costo_base(self, duracion, **opciones):
        """Calcula el costo del alquiler sin impuestos ni descuentos.

        Args:
            duracion: horas de alquiler.
            **opciones: unidades y con_seguro, ambos opcionales.

        Returns:
            Horas por tarifa por unidades, más el seguro si se pidió.
        """
        # Si no se indican unidades se asume una
        unidades = opciones.get("unidades", 1)

        # Costo del alquiler: horas por tarifa por cantidad de equipos
        costo = float(duracion) * self.tarifa_hora * unidades

        # El seguro es un porcentaje del costo del alquiler
        if opciones.get("con_seguro", False):
            costo += costo * self.TASA_SEGURO

        return costo
