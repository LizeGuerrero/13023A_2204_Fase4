# -*- coding: utf-8 -*-
"""
gestor.py
=========

Módulo de gestión de clientes del sistema integral **Software FJ**.

Proyecto académico - UNAD
Restricciones del proyecto: sin bases de datos; solo objetos en memoria,
archivos de texto plano y manejo de excepciones.

Contenido del módulo
--------------------
``GestorClientes`` : mantiene una lista de objetos ``Cliente`` en memoria y
                     ofrece operaciones para agregar (sin duplicar
                     identificadores), buscar, listar, guardar en un archivo de
                     texto y cargar desde él.

Formato del archivo de persistencia (``clientes.txt``)
------------------------------------------------------
Una línea por cliente, con los campos separados por el carácter ``|``::

    identificador|nombre|correo

Dependencias
------------
Requiere ``excepciones.py`` y ``modelos.py`` en la misma carpeta.
"""

# ---------------------------------------------------------------------------
# Importaciones
# ---------------------------------------------------------------------------
import os
from pathlib import Path
from typing import List, Optional, Tuple

from excepciones import (
    OperacionNoPermitidaError,
    RecursoNoDisponibleError,
    SoftwareFJError,
)
from modelos import Cliente


# ---------------------------------------------------------------------------
# Constantes del módulo
# ---------------------------------------------------------------------------

#: Carácter que separa los campos de cada línea en el archivo de texto.
SEPARADOR: str = "|"

#: Ruta por defecto del archivo de datos (junto a este módulo).
RUTA_DATOS_POR_DEFECTO: Path = Path(__file__).resolve().parent / "clientes.txt"


# ---------------------------------------------------------------------------
# Clase gestora
# ---------------------------------------------------------------------------
class GestorClientes:
    """Administra la colección de clientes del sistema.

    Los clientes se mantienen en una lista privada en memoria. Todos los fallos
    de negocio (duplicados, clientes inexistentes, problemas con el archivo)
    se reportan lanzando ``SoftwareFJError`` o una de sus subclases, por lo que
    quedan registrados automáticamente en ``log_errores.txt``.

    Attributes:
        _clientes (List[Cliente]): Lista privada de clientes registrados.
        _ruta_archivo (Path): Ruta del archivo de texto de persistencia.
    """

    def __init__(self, ruta_archivo: Optional[Path] = None) -> None:
        """Crea un gestor vacío.

        Args:
            ruta_archivo: Ruta del archivo de persistencia. Si no se indica,
                se usa ``clientes.txt`` junto a este módulo.
        """
        self._clientes: List[Cliente] = []
        self._ruta_archivo: Path = Path(ruta_archivo) if ruta_archivo else RUTA_DATOS_POR_DEFECTO

    # ----- Consultas básicas ------------------------------------------------
    def __len__(self) -> int:
        """Devuelve la cantidad de clientes registrados."""
        return len(self._clientes)

    @property
    def ruta_archivo(self) -> Path:
        """Path: Ruta del archivo de persistencia (solo lectura)."""
        return self._ruta_archivo

    def existe_cliente(self, identificador: str) -> bool:
        """Indica si ya hay un cliente con ese identificador.

        Args:
            identificador: Identificador a comprobar.

        Returns:
            ``True`` si existe un cliente con ese identificador.
        """
        identificador = str(identificador).strip()
        return any(c.identificador == identificador for c in self._clientes)

    def buscar_cliente(self, identificador: str) -> Cliente:
        """Busca un cliente por su identificador.

        Args:
            identificador: Identificador del cliente buscado.

        Returns:
            El objeto ``Cliente`` encontrado.

        Raises:
            RecursoNoDisponibleError: Si no existe un cliente con ese
                identificador.
        """
        identificador = str(identificador).strip()
        for cliente in self._clientes:
            if cliente.identificador == identificador:
                return cliente
        raise RecursoNoDisponibleError(
            f"No existe un cliente con identificador '{identificador}'",
            contexto="GestorClientes",
        )

    # ----- Alta de clientes -------------------------------------------------
    def agregar_cliente(self, cliente: Cliente) -> None:
        """Registra un nuevo cliente evitando identificadores repetidos.

        Args:
            cliente: Objeto ``Cliente`` ya validado.

        Raises:
            SoftwareFJError: Si el objeto no es un ``Cliente`` o si algún campo
                contiene el separador ``|`` o saltos de línea (no podría
                guardarse correctamente en el archivo).
            OperacionNoPermitidaError: Si ya existe un cliente con el mismo
                identificador.
        """
        # 1) Solo se aceptan objetos Cliente (evita datos basura en la lista).
        if not isinstance(cliente, Cliente):
            raise SoftwareFJError(
                "Solo se pueden registrar objetos de tipo Cliente",
                contexto="GestorClientes",
            )

        # 2) Los campos no pueden romper el formato del archivo de texto.
        self._validar_campos_persistibles(cliente)

        # 3) El identificador debe ser único.
        if self.existe_cliente(cliente.identificador):
            raise OperacionNoPermitidaError(
                f"Ya existe un cliente con identificador '{cliente.identificador}'",
                contexto="GestorClientes",
            )

        # 4) Todo correcto: se agrega a la lista en memoria.
        self._clientes.append(cliente)

    # ----- Listado ----------------------------------------------------------
    def listar_clientes(self) -> List[Cliente]:
        """Devuelve una copia de la lista de clientes registrados.

        Se entrega una copia para que el código externo no pueda modificar la
        lista interna directamente (encapsulamiento).

        Returns:
            Lista con los clientes, en el orden en que fueron registrados.
        """
        return list(self._clientes)

    def mostrar_clientes(self) -> str:
        """Construye un texto con el detalle de todos los clientes.

        No imprime nada: devuelve el texto para que la interfaz (módulo
        posterior) decida cómo mostrarlo.

        Returns:
            Texto con una línea por cliente, o un aviso si no hay registros.
        """
        if not self._clientes:
            return "No hay clientes registrados."
        return "\n".join(c.mostrar_detalle() for c in self._clientes)

    # ----- Persistencia en archivo de texto --------------------------------
    def guardar_clientes(self) -> int:
        """Guarda todos los clientes en el archivo de texto plano.

        Escribe primero en un archivo temporal y luego lo reemplaza, de modo
        que si ocurre un fallo a mitad de la escritura el archivo anterior no
        queda dañado.

        Returns:
            Cantidad de clientes guardados.

        Raises:
            SoftwareFJError: Si no se puede escribir el archivo.
        """
        temporal = self._ruta_archivo.with_name(self._ruta_archivo.name + ".tmp")
        try:
            with open(temporal, "w", encoding="utf-8") as archivo:
                for c in self._clientes:
                    archivo.write(
                        SEPARADOR.join([c.identificador, c.nombre, c.correo]) + "\n"
                    )
            # Reemplazo atómico: el archivo final solo cambia si todo salió bien.
            os.replace(temporal, self._ruta_archivo)
        except OSError as error:
            raise SoftwareFJError(
                f"No se pudo guardar el archivo '{self._ruta_archivo.name}': {error}",
                contexto="GestorClientes",
            ) from error
        return len(self._clientes)

    def cargar_clientes(self) -> Tuple[int, int]:
        """Carga los clientes desde el archivo, reemplazando los actuales.

        Cada línea se valida creando un ``Cliente``. Las líneas inválidas
        (formato incorrecto, correo mal escrito, identificador repetido) se
        omiten y quedan registradas en el log, sin detener la carga.

        Los datos en memoria solo se reemplazan si la lectura del archivo
        termina sin errores de acceso.

        Returns:
            Tupla ``(cargados, omitidos)`` con la cantidad de clientes
            cargados y de líneas descartadas.

        Raises:
            RecursoNoDisponibleError: Si el archivo de datos no existe.
            SoftwareFJError: Si el archivo no se puede leer.
        """
        if not self._ruta_archivo.exists():
            raise RecursoNoDisponibleError(
                f"El archivo '{self._ruta_archivo.name}' no existe",
                contexto="GestorClientes",
            )

        nuevos: List[Cliente] = []
        ids_vistos = set()
        omitidos = 0

        try:
            with open(self._ruta_archivo, "r", encoding="utf-8") as archivo:
                for numero, linea in enumerate(archivo, start=1):
                    linea = linea.strip()
                    if not linea:
                        continue  # Se ignoran las líneas en blanco.

                    try:
                        partes = linea.split(SEPARADOR)
                        if len(partes) != 3:
                            raise SoftwareFJError(
                                f"Línea {numero} con formato inválido en el archivo",
                                contexto="GestorClientes",
                            )
                        # El constructor de Cliente valida id, nombre y correo.
                        cliente = Cliente(*partes)
                        if cliente.identificador in ids_vistos:
                            raise OperacionNoPermitidaError(
                                f"Línea {numero}: identificador repetido "
                                f"'{cliente.identificador}'",
                                contexto="GestorClientes",
                            )
                        nuevos.append(cliente)
                        ids_vistos.add(cliente.identificador)

                    except SoftwareFJError:
                        # Ya quedó registrado en el log; se omite y se continúa.
                        omitidos += 1

        except (OSError, UnicodeDecodeError) as error:
            raise SoftwareFJError(
                f"No se pudo leer el archivo '{self._ruta_archivo.name}': {error}",
                contexto="GestorClientes",
            ) from error

        # Solo si la lectura fue exitosa se reemplazan los datos en memoria.
        self._clientes = nuevos
        return len(nuevos), omitidos

    # ----- Métodos auxiliares privados -------------------------------------
    @staticmethod
    def _validar_campos_persistibles(cliente: Cliente) -> None:
        """Verifica que los campos del cliente puedan guardarse en el archivo.

        Args:
            cliente: Cliente a verificar.

        Raises:
            SoftwareFJError: Si algún campo contiene el separador ``|`` o un
                salto de línea.
        """
        for campo in (cliente.identificador, cliente.nombre, cliente.correo):
            if SEPARADOR in campo or "\n" in campo or "\r" in campo:
                raise SoftwareFJError(
                    f"Los datos del cliente no pueden contener '{SEPARADOR}' "
                    "ni saltos de línea",
                    contexto="GestorClientes",
                )


# ---------------------------------------------------------------------------
# Prueba rápida del módulo (solo se ejecuta con: python gestor.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import tempfile

    print("=== Prueba del módulo gestor.py ===")

    # Se usa una carpeta temporal para no dejar archivos de prueba en el proyecto.
    with tempfile.TemporaryDirectory() as carpeta:
        gestor = GestorClientes(Path(carpeta) / "clientes_prueba.txt")

        # 1) Altas correctas.
        gestor.agregar_cliente(Cliente("1001", "Ana Pérez", "ana@correo.com"))
        gestor.agregar_cliente(Cliente("1002", "Luis Gómez", "luis@correo.com"))

        # 2) Intento de duplicado.
        try:
            gestor.agregar_cliente(Cliente("1001", "Otra Ana", "otra@correo.com"))
        except SoftwareFJError as e:
            print(f"Duplicado detectado: {e}")

        # 3) Búsqueda de un cliente inexistente.
        try:
            gestor.buscar_cliente("9999")
        except SoftwareFJError as e:
            print(f"Búsqueda fallida: {e}")

        # 4) Listado, guardado y recarga desde archivo.
        print(gestor.mostrar_clientes())
        print(f"Guardados: {gestor.guardar_clientes()}")

        otro = GestorClientes(gestor.ruta_archivo)
        cargados, omitidos = otro.cargar_clientes()
        print(f"Cargados: {cargados} | Omitidos: {omitidos}")
        print(otro.mostrar_clientes())
        
        