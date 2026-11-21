# -*- coding: utf-8 -*-
"""
simulacion_integral_fase4.py
Modulo de validacion integral y 12 simulaciones (validas e invalidas) para Software FJ.
Integra el modulo excepciones.py del equipo e implementa encadenamiento de excepciones,
bloques try/except/else y try/finally segun los criterios de la Fase 4.
"""

from abc import ABC, abstractmethod
from excepciones import (
    SoftwareFJError,
    ValidacionError,
    OperacionNoPermitidaError,
    RecursoNoDisponibleError,
    registrar_error,
    ejecutar_seguro,
    RUTA_LOG,
)


class EntidadBaseFJ(ABC):
    """Clase abstracta base para entidades auditables en Software FJ."""

    def __init__(self, codigo: str):
        if not codigo or not str(codigo).strip():
            raise ValidacionError("El codigo de identificacion es obligatorio.", contexto="EntidadBaseFJ")
        self._codigo = str(codigo).strip()

    @property
    def codigo(self) -> str:
        return self._codigo

    @abstractmethod
    def resumen(self) -> str:
        pass


class ClienteSimulado(EntidadBaseFJ):
    """Representa un cliente con encapsulacion y validaciones estrictas."""

    def __init__(self, codigo: str, nombre: str, correo: str):
        super().__init__(codigo)
        self.nombre = nombre
        self.correo = correo

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or len(valor.strip()) < 3:
            raise ValidacionError(f"Nombre de cliente invalido: '{valor}'.", contexto="Cliente")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not valor or "@" not in valor or "." not in valor.split("@")[-1]:
            raise ValidacionError(f"Formato de correo invalido: '{valor}'.", contexto="Cliente")
        self._correo = valor.strip().lower()

    def resumen(self) -> str:
        return f"Cliente [{self.codigo}] {self.nombre} ({self.correo})"


class ServicioBaseFJ(EntidadBaseFJ, ABC):
    """Clase abstracta para los distintos servicios de Software FJ."""

    def __init__(self, codigo: str, nombre: str, tarifa_hora: float, disponible: bool = True):
        super().__init__(codigo)
        if tarifa_hora <= 0:
            raise ValidacionError(f"La tarifa ({tarifa_hora}) debe ser mayor a 0.", contexto="Servicio")
        self._nombre = nombre
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def disponible(self) -> bool:
        return self._disponible

    @abstractmethod
    def calcular_subtotal(self, horas: int) -> float:
        pass

    def calcular_total(self, horas: int, descuento: float = 0.0, iva: float = 0.19, recargo: float = 0.0) -> float:
        if not isinstance(horas, int) or horas <= 0:
            raise ValidacionError("La cantidad de horas debe ser un entero positivo.", contexto="CalculoTarifa")
        if not (0 <= descuento <= 100):
            raise ValidacionError("El descuento debe estar entre 0% y 100%.", contexto="CalculoTarifa")

        subtotal = self.calcular_subtotal(horas)
        base = (subtotal * (1 - descuento / 100.0)) + recargo
        return round(base * (1 + iva), 2)

    def resumen(self) -> str:
        estado = "Activo" if self.disponible else "Inactivo"
        return f"Servicio [{self.codigo}] {self.nombre} - ${self._tarifa_hora:,.0f}/h ({estado})"


class SalaReuniones(ServicioBaseFJ):
    def calcular_subtotal(self, horas: int) -> float:
        total = self._tarifa_hora * horas
        return total * 0.90 if horas > 4 else total


class EquipoTecnologico(ServicioBaseFJ):
    def __init__(self, codigo: str, nombre: str, tarifa_hora: float, seguro: float = 20000.0, disponible: bool = True):
        super().__init__(codigo, nombre, tarifa_hora, disponible)
        self._seguro = seguro

    def calcular_subtotal(self, horas: int) -> float:
        if horas < 2:
            raise ValidacionError("El alquiler de equipos exige minimo 2 horas.", contexto="EquipoTecnologico")
        return (self._tarifa_hora * horas) + self._seguro


class AsesoriaTecnica(ServicioBaseFJ):
    def calcular_subtotal(self, horas: int) -> float:
        return (self._tarifa_hora * horas) + 30000.0


class ReservaFJ(EntidadBaseFJ):
    """Gestiona la reserva aplicando encadenamiento de excepciones."""

    def __init__(self, codigo: str, cliente: ClienteSimulado, servicio: ServicioBaseFJ, horas: int):
        super().__init__(codigo)
        if not servicio.disponible:
            raise RecursoNoDisponibleError(
                f"El servicio '{servicio.nombre}' no se encuentra disponible.",
                contexto="ReservaFJ",
            )
        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "PENDIENTE"
        self.total = 0.0

    def confirmar(self, descuento: float = 0.0, recargo: float = 0.0) -> None:
        if self.estado == "CANCELADA":
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva {self.codigo} porque esta cancelada.",
                contexto="ReservaFJ",
            )
        try:
            self.total = self.servicio.calcular_total(self.horas, descuento=descuento, recargo=recargo)
            self.estado = "CONFIRMADA"
            registrar_error(
                f"Reserva {self.codigo} confirmada para {self.cliente.nombre} por ${self.total:,.2f}",
                nivel="INFO",
                contexto="ReservaFJ",
            )
        except ValidacionError as error_origen:
            raise OperacionNoPermitidaError(
                f"No fue posible procesar la reserva {self.codigo} debido a parametros invalidos.",
                contexto="ReservaFJ",
            ) from error_origen

    def cancelar(self) -> None:
        if self.estado == "CANCELADA":
            raise OperacionNoPermitidaError(
                f"La reserva {self.codigo} ya fue cancelada previamente.",
                contexto="ReservaFJ",
            )
        self.estado = "CANCELADA"
        registrar_error(f"Reserva {self.codigo} cancelada por el usuario.", nivel="ADVERTENCIA", contexto="ReservaFJ")

    def resumen(self) -> str:
        return f"Reserva [{self.codigo}] {self.estado} | {self.cliente.nombre} -> {self.servicio.nombre} (${self.total:,.2f})"


def ejecutar_bateria_simulaciones() -> None:
    print("\n=================================================================")
    print(" EJECUTANDO BATERIA DE 12 SIMULACIONES - SISTEMA SOFTWARE FJ")
    print("=================================================================\n")

    clientes = []
    servicios = []
    reservas = []

    # --- SIMULACION 1: Registro valido de cliente ---
    try:
        c1 = ClienteSimulado("CLI-01", "Laura Gomez", "laura.gomez@unad.edu.co")
    except SoftwareFJError as e:
        print(f"[Sim 1] Fallo: {e}")
    else:
        clientes.append(c1)
        registrar_error(f"Registro exitoso: {c1.resumen()}", nivel="INFO", contexto="Simulacion")
        print(f"[Sim 1] OK -> {c1.resumen()}")
    finally:
        print("[Sim 1] -> Bloque finally ejecutado (auditoria de intento cerrada).")

    # --- SIMULACION 2: Registro valido de segundo cliente ---
    c2 = ClienteSimulado("CLI-02", "Andres Martinez", "amartinez@empresa.co")
    clientes.append(c2)
    registrar_error(f"Registro exitoso: {c2.resumen()}", nivel="INFO", contexto="Simulacion")
    print(f"[Sim 2] OK -> {c2.resumen()}")

    # --- SIMULACION 3: Registro INVALIDO de cliente (correo sin dominio) ---
    try:
        ClienteSimulado("CLI-03", "Carlos Ruiz", "carlos.ruiz_sin_arroba.com")
    except ValidacionError as e:
        print(f"[Sim 3] Error controlado (correo invalido): {e}")

    # --- SIMULACION 4: Registro INVALIDO de cliente (nombre vacio) ---
    try:
        ClienteSimulado("CLI-04", " ", "valido@correo.com")
    except ValidacionError as e:
        print(f"[Sim 4] Error controlado (nombre vacio): {e}")

    # --- SIMULACION 5: Creacion valida de 3 tipos de servicio (polimorfismo) ---
    s_sala = SalaReuniones("SRV-01", "Sala Ejecutiva Norte", 90000, disponible=True)
    s_equipo = EquipoTecnologico("SRV-02", "Servidor Portatil Workstation", 45000, seguro=25000, disponible=True)
    s_asesoria = AsesoriaTecnica("SRV-03", "Consultoria Ciberseguridad", 130000, disponible=True)
    s_inactivo = SalaReuniones("SRV-04", "Sala Mantenimiento", 70000, disponible=False)
    servicios.extend([s_sala, s_equipo, s_asesoria, s_inactivo])
    print(f"[Sim 5] OK -> 4 servicios cargados en memoria ({len(servicios)} activos/inactivos).")

    # --- SIMULACION 6: Creacion INVALIDA de servicio (tarifa negativa) ---
    try:
        AsesoriaTecnica("SRV-05", "Auditoria Express", -50000)
    except ValidacionError as e:
        print(f"[Sim 6] Error controlado (tarifa negativa): {e}")

    # --- SIMULACION 7: Reserva EXITOSA de Sala ---
    try:
        r1 = ReservaFJ("RES-01", c1, s_sala, horas=6)
        r1.confirmar(descuento=5.0)
    except SoftwareFJError as e:
        print(f"[Sim 7] Error: {e}")
    else:
        reservas.append(r1)
        print(f"[Sim 7] OK -> {r1.resumen()}")

    # --- SIMULACION 8: Reserva EXITOSA de Equipo con recargo logistico ---
    r2 = ReservaFJ("RES-02", c2, s_equipo, horas=4)
    r2.confirmar(recargo=15000.0)
    reservas.append(r2)
    print(f"[Sim 8] OK -> {r2.resumen()}")

    # --- SIMULACION 9: Reserva EXITOSA de Asesoria Tecnica ---
    r3 = ReservaFJ("RES-03", c1, s_asesoria, horas=2)
    r3.confirmar()
    reservas.append(r3)
    print(f"[Sim 9] OK -> {r3.resumen()}")

    # --- SIMULACION 10: Reserva FALLIDA por servicio no disponible ---
    try:
        ReservaFJ("RES-04", c2, s_inactivo, horas=3)
    except RecursoNoDisponibleError as e:
        print(f"[Sim 10] Recurso no disponible controlado: {e}")

    # --- SIMULACION 11: Reserva FALLIDA con ENCADENAMIENTO DE EXCEPCIONES ---
    try:
        r_bad = ReservaFJ("RES-05", c1, s_equipo, horas=1)
        r_bad.confirmar()
    except OperacionNoPermitidaError as e:
        print(f"[Sim 11] Encadenamiento capturado: {e}")
        print(f"          -> Causa raiz (__cause__): {type(e.__cause__).__name__} -> {e.__cause__}")

    # --- SIMULACION 12: Cancelacion y doble cancelacion controlada + ejecucion segura ---
    try:
        r2.cancelar()
        print(f"[Sim 12a] Advertencia -> {r2.resumen()}")
        r2.cancelar()
    except OperacionNoPermitidaError as e:
        print(f"[Sim 12b] Doble cancelacion bloqueada: {e}")
    finally:
        res_seguro = ejecutar_seguro(lambda: 100 / 0, valor_por_defecto=0.0, contexto="Simulacion12")
        print(f"[Sim 12c] ejecutar_seguro mantuvo el sistema activo (retorno={res_seguro}).")

    print("\n=================================================================")
    print(f" FIN DE SIMULACION | Clientes: {len(clientes)} | Servicios: {len(servicios)} | Reservas: {len(reservas)}")
    print(f" Todos los eventos quedaron registrados en: {RUTA_LOG}")
    print("=================================================================\n")


if __name__ == "__main__":
    ejecutar_bateria_simulaciones()