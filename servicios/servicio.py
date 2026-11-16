# -*- coding: utf-8 -*-
"""
servicio.py

Clase abstracta Servicio del sistema Software FJ.

Servicio hereda de EntidadBase (modelos.py), por lo que ya trae el
identificador y la obligación de implementar mostrar_detalle(). Aquí se define
lo que tienen en común todos los servicios y lo que cada uno debe resolver a
su manera:

    Métodos abstractos (cada servicio los sobrescribe):
        describir()                         texto que describe el servicio.
        validar_parametros(duracion, ...)   revisa los datos de una solicitud.
        calcular_costo_base(duracion, ...)  costo sin impuestos ni descuentos.

    Métodos ya implementados (iguales para todos):
        calcular_costo(...)                 costo final, con sobrecarga.
        calcular_costo_con_impuesto(...)    variante con impuesto.
        calcular_costo_con_descuento(...)   variante con descuento.

Sobre la sobrecarga: Python no permite dos métodos con el mismo nombre y
distinta firma, así que se simula con parámetros opcionales. Un mismo
calcular_costo() sirve de tres formas:

    servicio.calcular_costo(2)                       solo el costo base
    servicio.calcular_costo(2, impuesto=0.19)        costo base más impuesto
    servicio.calcular_costo(2, 0.19, 0.10)           impuesto y descuento
"""

# math se usa para comprobar que el resultado de un cálculo sea un número real
import math

# abstractmethod marca los métodos que las clases hijas están obligadas a escribir
from abc import abstractmethod

# Se importan las excepciones del proyecto que usa esta clase
from excepciones import (
    CalculoInconsistenteError,
    RecursoNoDisponibleError,
    ValidacionError,
)

# Clase de la que hereda Servicio
from modelos import EntidadBase

# Funciones de validación compartidas
from validaciones import (
    validar_numero_positivo,
    validar_proporcion,
    validar_texto,
)

# Tasa de IVA general en Colombia, expresada como fracción (19 %)
IVA_GENERAL = 0.19


class Servicio(EntidadBase):
    """Clase abstracta que representa cualquier servicio que ofrece Software FJ.

    No se puede crear un objeto de esta clase directamente; hay que usar una de
    sus hijas (SalaReuniones, AlquilerEquipo, AsesoriaEspecializada).

    Atributos de clase (cada hija puede cambiarlos):
        TIPO: nombre corto del tipo de servicio, se usa en el log.
        DURACION_MINIMA: menor cantidad de horas que se puede solicitar.
        DURACION_MAXIMA: mayor cantidad de horas que se puede solicitar.

    Atributos de instancia (todos privados):
        _nombre: nombre comercial del servicio.
        _tarifa_hora: valor de una hora del servicio, en pesos.
        _disponible: indica si el servicio se puede reservar ahora.
    """

    # Valores por defecto; las clases hijas los reemplazan con los suyos
    TIPO = "Servicio"
    DURACION_MINIMA = 0.5
    DURACION_MAXIMA = 24

    def __init__(self, identificador, nombre, tarifa_hora, disponible=True):
        """Crea un servicio validando sus datos.

        Args:
            identificador: código único del servicio.
            nombre: nombre comercial del servicio.
            tarifa_hora: valor de una hora, en pesos. Debe ser mayor que cero.
            disponible: si el servicio nace disponible. Por defecto True.

        Raises:
            SoftwareFJError: si el identificador no es válido.
            ValidacionError: si el nombre, la tarifa o la disponibilidad no
                son válidos.
        """
        # El constructor de EntidadBase valida y guarda el identificador
        super().__init__(identificador)

        # Se declaran los atributos privados antes de pasar por las propiedades
        self._nombre = ""
        self._tarifa_hora = 0.0
        self._disponible = True

        # Se asigna mediante las propiedades para que se ejecute la validación
        self.nombre = nombre
        self.tarifa_hora = tarifa_hora
        self.disponible = disponible

    # Propiedades (encapsulamiento)

    @property
    def nombre(self):
        """str: nombre comercial del servicio."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        """Valida y guarda el nombre del servicio."""
        # validar_texto devuelve el texto limpio o lanza ValidacionError
        self._nombre = validar_texto(valor, "nombre", self.TIPO)

    @property
    def tarifa_hora(self):
        """float: valor de una hora del servicio, en pesos."""
        return self._tarifa_hora

    @tarifa_hora.setter
    def tarifa_hora(self, valor):
        """Valida y guarda la tarifa por hora."""
        # La tarifa debe ser un número mayor que cero
        self._tarifa_hora = validar_numero_positivo(valor, "tarifa por hora", self.TIPO)

    @property
    def disponible(self):
        """bool: True si el servicio se puede reservar en este momento."""
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        """Valida y guarda la disponibilidad del servicio."""
        # Solo se acepta un booleano real, no 0, 1 ni textos
        if not isinstance(valor, bool):
            raise ValidacionError(
                "La disponibilidad debe ser True o False", contexto=self.TIPO
            )
        self._disponible = valor

    # Métodos abstractos: cada servicio los sobrescribe

    @abstractmethod
    def describir(self):
        """Devuelve un texto que describe el servicio.

        Returns:
            Descripción del servicio con sus datos propios.
        """

    @abstractmethod
    def validar_parametros(self, duracion, **opciones):
        """Revisa que los datos de una solicitud sean válidos para este servicio.

        Args:
            duracion: horas que se quieren contratar.
            **opciones: parámetros propios de cada servicio.

        Raises:
            ValidacionError: si falta un parámetro o alguno no es válido.
            RecursoNoDisponibleError: si lo pedido supera lo que hay disponible.
        """

    @abstractmethod
    def calcular_costo_base(self, duracion, **opciones):
        """Calcula el costo del servicio sin impuestos ni descuentos.

        Método de uso interno: se espera que los datos ya hayan pasado por
        validar_parametros(). Lo normal es llamar a calcular_costo().

        Args:
            duracion: horas que se quieren contratar.
            **opciones: parámetros propios de cada servicio.

        Returns:
            Costo base en pesos.
        """

    # Métodos ya implementados, iguales para todos los servicios

    def mostrar_detalle(self):
        """Implementa el método abstracto de EntidadBase usando describir().

        Returns:
            La misma descripción que devuelve describir().
        """
        return self.describir()

    def calcular_costo(self, duracion, impuesto=None, descuento=None, **opciones):
        """Calcula el costo final del servicio (método sobrecargado).

        El descuento se aplica primero sobre el costo base y el impuesto se
        calcula sobre el valor ya descontado.

        Formas de llamarlo:
            calcular_costo(2)                     costo base.
            calcular_costo(2, impuesto=0.19)      costo base con impuesto.
            calcular_costo(2, descuento=0.10)     costo base con descuento.
            calcular_costo(2, 0.19, 0.10)         con descuento e impuesto.

        Args:
            duracion: horas que se quieren contratar.
            impuesto: fracción de impuesto entre 0 y 1 (0.19 es el 19 %).
                Si es None no se aplica impuesto.
            descuento: fracción de descuento entre 0 y 1 (0.10 es el 10 %).
                Si es None no se aplica descuento.
            **opciones: parámetros propios de cada servicio.

        Returns:
            Costo final en pesos, redondeado a dos decimales.

        Raises:
            ValidacionError: si algún dato no es válido.
            RecursoNoDisponibleError: si lo pedido supera lo disponible.
            CalculoInconsistenteError: si el cálculo falla o el total no tiene
                sentido (por ejemplo, es negativo).
        """
        # Primero se revisan los datos propios de cada servicio
        self.validar_parametros(duracion, **opciones)

        # Si no se indica impuesto o descuento, la tasa es cero
        tasa_impuesto = 0.0
        tasa_descuento = 0.0

        # Cuando sí se indican, se validan como fracciones entre 0 y 1
        if impuesto is not None:
            tasa_impuesto = validar_proporcion(impuesto, "impuesto", self.TIPO)
        if descuento is not None:
            tasa_descuento = validar_proporcion(descuento, "descuento", self.TIPO)

        try:
            # Costo base: lo calcula cada servicio a su manera (polimorfismo)
            subtotal = self.calcular_costo_base(duracion, **opciones)

            # El descuento se resta del subtotal
            neto = subtotal - (subtotal * tasa_descuento)

            # El impuesto se calcula sobre el valor ya descontado
            total = neto + (neto * tasa_impuesto)

        except (ArithmeticError, TypeError, ValueError) as error:
            # Se encadena la excepción original con "from" para no perder la causa
            raise CalculoInconsistenteError(
                f"No fue posible calcular el costo de '{self.nombre}': {error}",
                contexto=self.TIPO,
            ) from error

        else:
            # Este bloque solo corre si el cálculo no lanzó ninguna excepción.
            # Aquí se revisa que el resultado tenga sentido.
            if not isinstance(total, (int, float)) or not math.isfinite(total) or total < 0:
                raise CalculoInconsistenteError(
                    f"El costo calculado para '{self.nombre}' no es válido: {total}",
                    contexto=self.TIPO,
                )

        # Se redondea a dos decimales para evitar números como 12000.000000001
        return round(total, 2)

    def calcular_costo_con_impuesto(self, duracion, impuesto=IVA_GENERAL, **opciones):
        """Variante de calcular_costo() que solo aplica impuesto.

        Args:
            duracion: horas que se quieren contratar.
            impuesto: fracción de impuesto. Por defecto el IVA general (19 %).
            **opciones: parámetros propios de cada servicio.

        Returns:
            Costo final con impuesto, en pesos.
        """
        # Se delega en el método principal, sin descuento
        return self.calcular_costo(duracion, impuesto=impuesto, **opciones)

    def calcular_costo_con_descuento(self, duracion, descuento, **opciones):
        """Variante de calcular_costo() que solo aplica descuento.

        Args:
            duracion: horas que se quieren contratar.
            descuento: fracción de descuento entre 0 y 1.
            **opciones: parámetros propios de cada servicio.

        Returns:
            Costo final con descuento, en pesos.
        """
        # Se delega en el método principal, sin impuesto
        return self.calcular_costo(duracion, descuento=descuento, **opciones)

    # Métodos auxiliares para las clases hijas

    def verificar_disponible(self):
        """Comprueba que el servicio se pueda reservar.

        Raises:
            RecursoNoDisponibleError: si el servicio está marcado como no
                disponible.
        """
        # Si está inactivo no se puede reservar
        if not self._disponible:
            raise RecursoNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible", contexto=self.TIPO
            )

    def _validar_duracion(self, duracion):
        """Valida las horas solicitadas contra el mínimo y el máximo del servicio.

        Args:
            duracion: horas que se quieren contratar.

        Returns:
            La duración como float.

        Raises:
            ValidacionError: si no es un número positivo o si está fuera del
                rango permitido por el servicio.
        """
        # Primero debe ser un número positivo
        horas = validar_numero_positivo(duracion, "duración (horas)", self.TIPO)

        # Luego se compara con los límites propios de cada servicio
        if horas < self.DURACION_MINIMA or horas > self.DURACION_MAXIMA:
            raise ValidacionError(
                f"La duración debe estar entre {self.DURACION_MINIMA} y "
                f"{self.DURACION_MAXIMA} horas (se recibió {horas})",
                contexto=self.TIPO,
            )
        return horas

    def _rechazar_opciones_desconocidas(self, opciones, permitidas):
        """Lanza un error si se recibe un parámetro que el servicio no usa.

        Sirve para detectar errores de digitación, por ejemplo 'asistente'
        en lugar de 'asistentes'.

        Args:
            opciones: diccionario con los parámetros recibidos.
            permitidas: nombres de los parámetros que el servicio acepta.

        Raises:
            ValidacionError: si hay algún parámetro que no está permitido.
        """
        # Se buscan los nombres recibidos que no están en la lista permitida
        desconocidas = [clave for clave in opciones if clave not in permitidas]

        # Si hay alguno, se informa cuáles son y cuáles se aceptan
        if desconocidas:
            raise ValidacionError(
                f"Parámetros no reconocidos: {', '.join(desconocidas)}. "
                f"Se aceptan: {', '.join(permitidas)}",
                contexto=self.TIPO,
            )
