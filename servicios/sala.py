# -*- coding: utf-8 -*-
"""
sala.py

Servicio de reserva de salas de reuniones.

Hereda de Servicio y sobrescribe describir(), validar_parametros() y
calcular_costo_base().

Parámetros que acepta al solicitar el servicio:
    asistentes       (obligatorio) cantidad de personas; no puede superar la
                     capacidad de la sala.
    con_audiovisual  (opcional, False por defecto) agrega un recargo fijo por
                     el uso de proyector y sonido.

Costo base = horas * tarifa por hora + recargo audiovisual (si se pidió).
"""

# Excepciones que puede lanzar este servicio
from excepciones import RecursoNoDisponibleError, ValidacionError

# Clase de la que hereda
from servicios.servicio import Servicio

# Función de validación compartida
from validaciones import validar_entero


class SalaReuniones(Servicio):
    """Servicio de reserva de salas de reuniones.

    Atributos propios:
        _capacidad: cantidad máxima de personas que caben en la sala.
    """

    # Datos propios de este servicio
    TIPO = "SalaReuniones"
    DURACION_MINIMA = 1
    DURACION_MAXIMA = 12

    # Recargo fijo, en pesos, por usar el equipo audiovisual de la sala
    RECARGO_AUDIOVISUAL = 20000

    def __init__(self, identificador, nombre, tarifa_hora, capacidad, disponible=True):
        """Crea una sala de reuniones.

        Args:
            identificador: código único del servicio.
            nombre: nombre de la sala.
            tarifa_hora: valor de una hora de uso, en pesos.
            capacidad: cantidad máxima de personas.
            disponible: si la sala nace disponible. Por defecto True.

        Raises:
            ValidacionError: si algún dato no es válido.
        """
        # Primero se construye la parte común (identificador, nombre, tarifa)
        super().__init__(identificador, nombre, tarifa_hora, disponible)

        # Se declara el atributo y luego se asigna con la propiedad para validar
        self._capacidad = 1
        self.capacidad = capacidad

    @property
    def capacidad(self):
        """int: cantidad máxima de personas que caben en la sala."""
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor):
        """Valida y guarda la capacidad de la sala."""
        # La capacidad debe ser un entero de al menos 1
        self._capacidad = validar_entero(valor, "capacidad", self.TIPO, minimo=1)

    def describir(self):
        """Describe la sala con su capacidad, tarifa y estado.

        Returns:
            Texto de una línea con los datos de la sala.
        """
        # Se arma el texto del estado a partir del booleano
        estado = "disponible" if self.disponible else "no disponible"

        # Se devuelve la descripción completa en una sola línea
        return (
            f"Sala de reuniones [ID: {self.identificador}] {self.nombre} | "
            f"Capacidad: {self.capacidad} personas | "
            f"Tarifa: ${self.tarifa_hora:,.0f} por hora | Estado: {estado}"
        )

    def validar_parametros(self, duracion, **opciones):
        """Revisa duración, asistentes y recargo audiovisual de una solicitud.

        Args:
            duracion: horas que se quieren usar la sala.
            **opciones: asistentes (obligatorio) y con_audiovisual (opcional).

        Raises:
            ValidacionError: si falta algún parámetro obligatorio o alguno
                es inválido.
            RecursoNoDisponibleError: si los asistentes superan la capacidad.
        """
        # Solo se aceptan los dos parámetros que usa este servicio
        self._rechazar_opciones_desconocidas(opciones, ("asistentes", "con_audiovisual"))

        # La duración se valida con el rango propio de la sala (1 a 12 horas)
        self._validar_duracion(duracion)

        # Los asistentes son obligatorios: si no vienen, es un parámetro faltante
        if "asistentes" not in opciones:
            raise ValidacionError(
                "Falta el parámetro obligatorio 'asistentes'", contexto=self.TIPO
            )

        # Deben ser un entero de al menos 1
        asistentes = validar_entero(opciones["asistentes"], "asistentes", self.TIPO, minimo=1)

        # No pueden ser más que la capacidad de la sala
        if asistentes > self.capacidad:
            raise RecursoNoDisponibleError(
                f"La sala '{self.nombre}' tiene capacidad para {self.capacidad} "
                f"personas y se pidieron {asistentes}",
                contexto=self.TIPO,
            )

        # El recargo audiovisual es opcional, pero si viene debe ser True o False
        if "con_audiovisual" in opciones and not isinstance(opciones["con_audiovisual"], bool):
            raise ValidacionError(
                "El parámetro 'con_audiovisual' debe ser True o False",
                contexto=self.TIPO,
            )

    def calcular_costo_base(self, duracion, **opciones):
        """Calcula el costo de la sala sin impuestos ni descuentos.

        Args:
            duracion: horas de uso.
            **opciones: con_audiovisual (opcional).

        Returns:
            Horas por tarifa, más el recargo audiovisual si se pidió.
        """
        # Costo del tiempo de uso
        costo = float(duracion) * self.tarifa_hora

        # Si se pidió equipo audiovisual se suma el recargo fijo
        if opciones.get("con_audiovisual", False):
            costo += self.RECARGO_AUDIOVISUAL

        return costo
