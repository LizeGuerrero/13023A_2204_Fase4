# -*- coding: utf-8 -*-
"""
reserva.py

Clase Reserva del sistema Software FJ.

Une un cliente, un servicio, una duración y un estado, e implementa las tres
operaciones del enunciado: confirmar, cancelar y procesar. Cada operación
revisa que el cambio de estado esté permitido (ver estado.py) y deja registro
en el archivo de log.

Los parámetros propios de cada servicio (asistentes, unidades, modalidad...)
se pasan como argumentos con nombre al crear la reserva:

    Reserva("R-001", cliente, sala, 2, asistentes=6)
    Reserva("R-002", cliente, equipo, 5, impuesto=0.19, unidades=2)
"""

# datetime se usa para poner fecha y hora en el historial de la reserva
from datetime import datetime

# Excepciones y función de log del proyecto
from excepciones import (
    OperacionNoPermitidaError,
    RecursoNoDisponibleError,
    SoftwareFJError,
    ValidacionError,
    registrar_error,
)

# Clases de las que depende la reserva
from modelos import Cliente, EntidadBase
from reservas.estado import EstadoReserva
from servicios.servicio import Servicio

# Función de validación compartida
from validaciones import validar_proporcion


class Reserva(EntidadBase):
    """Reserva de un servicio hecha por un cliente.

    Atributos (todos privados):
        _cliente: cliente que hace la reserva.
        _servicio: servicio reservado.
        _duracion: horas reservadas.
        _impuesto: fracción de impuesto a aplicar, o None.
        _descuento: fracción de descuento a aplicar, o None.
        _opciones: parámetros propios del servicio (asistentes, unidades...).
        _estado: estado actual de la reserva.
        _costo_total: costo final; es None hasta que la reserva se procesa.
        _historial: lista con los cambios de estado y su fecha.
    """

    def __init__(self, identificador, cliente, servicio, duracion,
                 impuesto=None, descuento=None, **opciones):
        """Crea una reserva en estado PENDIENTE validando todos sus datos.

        Args:
            identificador: código único de la reserva.
            cliente: objeto Cliente que reserva.
            servicio: objeto Servicio que se reserva.
            duracion: horas que se reservan.
            impuesto: fracción de impuesto entre 0 y 1, o None.
            descuento: fracción de descuento entre 0 y 1, o None.
            **opciones: parámetros propios del servicio.

        Raises:
            SoftwareFJError: si el identificador no es válido.
            ValidacionError: si el cliente o el servicio no son del tipo
                correcto, o si la duración o las opciones no son válidas.
            RecursoNoDisponibleError: si lo pedido supera lo disponible.
        """
        # El constructor de EntidadBase valida y guarda el identificador
        super().__init__(identificador)

        # Solo se acepta un objeto Cliente
        if not isinstance(cliente, Cliente):
            raise ValidacionError(
                "La reserva necesita un objeto de tipo Cliente", contexto="Reserva"
            )

        # Solo se acepta un objeto Servicio (cualquiera de sus clases hijas)
        if not isinstance(servicio, Servicio):
            raise ValidacionError(
                "La reserva necesita un objeto de tipo Servicio", contexto="Reserva"
            )

        # Se revisan los datos de la solicitud con las reglas propias del servicio
        servicio.validar_parametros(duracion, **opciones)

        # Impuesto y descuento son opcionales; si vienen se validan
        if impuesto is not None:
            validar_proporcion(impuesto, "impuesto", "Reserva")
        if descuento is not None:
            validar_proporcion(descuento, "descuento", "Reserva")

        # Se guardan los datos ya validados
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = float(duracion)
        self._impuesto = impuesto
        self._descuento = descuento
        self._opciones = dict(opciones)

        # Toda reserva nace pendiente y sin costo final
        self._estado = EstadoReserva.PENDIENTE
        self._costo_total = None

        # La lista del historial guarda cada cambio de estado
        self._historial = []
        self._anotar_historial("Reserva creada en estado Pendiente")

    # Propiedades de solo lectura (encapsulamiento)

    @property
    def cliente(self):
        """Cliente que hizo la reserva."""
        return self._cliente

    @property
    def servicio(self):
        """Servicio reservado."""
        return self._servicio

    @property
    def duracion(self):
        """float: horas reservadas."""
        return self._duracion

    @property
    def estado(self):
        """EstadoReserva: estado actual de la reserva."""
        return self._estado

    @property
    def costo_total(self):
        """float o None: costo final; solo existe después de procesar."""
        return self._costo_total

    @property
    def historial(self):
        """list: copia del historial de cambios de la reserva."""
        # Se devuelve una copia para que nadie modifique la lista interna
        return list(self._historial)

    # Operaciones de la reserva

    def confirmar(self):
        """Confirma la reserva (PENDIENTE a CONFIRMADA).

        Raises:
            OperacionNoPermitidaError: si la reserva no está pendiente.
            RecursoNoDisponibleError: si el servicio ya no está disponible.
        """
        # Primero se revisa que el cambio de estado esté permitido
        self._verificar_transicion(EstadoReserva.CONFIRMADA, "confirmar")

        # Luego se comprueba que el servicio todavía se pueda reservar
        self._servicio.verificar_disponible()

        # Todo correcto: se cambia el estado
        self._cambiar_estado(EstadoReserva.CONFIRMADA)

    def cancelar(self, motivo=""):
        """Cancela la reserva (desde PENDIENTE o CONFIRMADA).

        Args:
            motivo: razón de la cancelación. Es opcional.

        Raises:
            ValidacionError: si el motivo no es texto.
            OperacionNoPermitidaError: si la reserva ya está cancelada o
                procesada.
        """
        # El motivo debe ser texto aunque venga vacío
        if not isinstance(motivo, str):
            raise ValidacionError(
                "El motivo de la cancelación debe ser texto", contexto="Reserva"
            )

        # Se revisa que la cancelación esté permitida desde el estado actual
        self._verificar_transicion(EstadoReserva.CANCELADA, "cancelar")

        # Si hay motivo se agrega a la nota del historial
        nota = f"Cancelada. Motivo: {motivo.strip()}" if motivo.strip() else "Cancelada"
        self._cambiar_estado(EstadoReserva.CANCELADA, nota)

    def procesar(self):
        """Procesa la reserva: calcula el costo final y la marca PROCESADA.

        Usa try/except/else/finally. El error original se conserva con
        'raise ... from' para que la causa quede en el encadenamiento.

        Returns:
            Costo final de la reserva, en pesos.

        Raises:
            OperacionNoPermitidaError: si la reserva no está confirmada o si
                el cálculo del costo falló.
        """
        # Solo se procesa una reserva confirmada
        self._verificar_transicion(EstadoReserva.PROCESADA, "procesar")

        # Se inicia en cero por si el cálculo falla antes de asignar el valor
        total = 0.0

        try:
            # El servicio calcula el costo con su propia lógica (polimorfismo)
            total = self._servicio.calcular_costo(
                self._duracion, self._impuesto, self._descuento, **self._opciones
            )

        except SoftwareFJError as error:
            # Error propio del sistema: se envuelve en uno de operación,
            # conservando el original como causa
            raise OperacionNoPermitidaError(
                f"No se pudo procesar la reserva '{self.identificador}': {error}",
                contexto="Reserva",
            ) from error

        except Exception as error:
            # Error que no se esperaba: se registra como crítico y se encadena
            registrar_error(
                mensaje=str(error) or "Error inesperado al procesar la reserva",
                nivel="CRITICO",
                excepcion=error,
                contexto="Reserva",
            )
            raise OperacionNoPermitidaError(
                f"Error inesperado al procesar la reserva '{self.identificador}'",
                contexto="Reserva",
            ) from error

        else:
            # Solo si el cálculo salió bien se guarda el costo y se cambia el estado
            self._costo_total = total
            self._cambiar_estado(EstadoReserva.PROCESADA, f"Procesada. Total: ${total:,.2f}")

        finally:
            # Este bloque corre siempre, haya salido bien o mal el intento
            registrar_error(
                f"Fin del intento de procesar la reserva '{self.identificador}'",
                nivel="INFO",
                contexto="Reserva",
            )

        return total

    def mostrar_detalle(self):
        """Implementa el método abstracto de EntidadBase.

        Returns:
            Texto de una línea con los datos principales de la reserva.
        """
        # Si todavía no se procesa, el costo se muestra como pendiente
        if self._costo_total is None:
            costo = "por calcular"
        else:
            costo = f"${self._costo_total:,.2f}"

        # Se devuelve el resumen completo en una sola línea
        return (
            f"Reserva [ID: {self.identificador}] Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | Duración: {self._duracion:g} h | "
            f"Estado: {self._estado.value} | Costo: {costo}"
        )

    # Métodos auxiliares privados

    def _verificar_transicion(self, destino, accion):
        """Comprueba que se pueda pasar del estado actual al estado destino.

        Args:
            destino: estado al que se quiere llegar.
            accion: nombre de la operación, para armar el mensaje de error.

        Raises:
            OperacionNoPermitidaError: si la transición no está permitida.
        """
        # La tabla de transiciones decide si el cambio es válido
        if not self._estado.puede_pasar_a(destino):
            raise OperacionNoPermitidaError(
                f"No se puede {accion} la reserva '{self.identificador}' "
                f"porque está en estado {self._estado.value}",
                contexto="Reserva",
            )

    def _cambiar_estado(self, nuevo_estado, nota=None):
        """Cambia el estado, lo anota en el historial y lo registra en el log.

        Args:
            nuevo_estado: estado al que pasa la reserva.
            nota: texto para el historial. Si no se da, se genera uno.
        """
        # Se guarda el estado anterior para poder escribir el cambio completo
        anterior = self._estado.value

        # Se aplica el cambio
        self._estado = nuevo_estado

        # Si no se pasó nota, se arma una con los dos estados
        texto = nota or f"{anterior} a {nuevo_estado.value}"
        self._anotar_historial(texto)

        # El cambio de estado es un evento relevante: va al archivo de log
        registrar_error(
            f"Reserva '{self.identificador}': {anterior} a {nuevo_estado.value}",
            nivel="INFO",
            contexto="Reserva",
        )

    def _anotar_historial(self, texto):
        """Agrega una línea con fecha y hora a la lista del historial.

        Args:
            texto: descripción del evento.
        """
        # Marca de tiempo del momento exacto del evento
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._historial.append(f"[{marca}] {texto}")
