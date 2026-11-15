# -*- coding: utf-8 -*-
"""
excepciones.py
==============

Módulo de excepciones personalizadas y registro de errores (logs) del sistema
integral **Software FJ**.

Proyecto académico - UNAD
Paradigma: Programación Orientada a Objetos (POO)
Restricciones del proyecto: sin bases de datos; solo objetos, archivos de texto
y manejo de excepciones.

Contenido del módulo
--------------------
1. ``registrar_error``      : función de logging que escribe en ``log_errores.txt``
                              con fecha y hora exactas. Nunca lanza excepciones.
2. ``SoftwareFJError``      : excepción base del sistema (errores de negocio).
3. Excepciones derivadas    : ``ValidacionError``, ``OperacionNoPermitidaError``
                              y ``RecursoNoDisponibleError``.
4. ``ejecutar_seguro``      : utilidad que ejecuta una función capturando
                              cualquier error para que la aplicación NO se caiga.

Ejemplo de uso rápido
---------------------
>>> from excepciones import SoftwareFJError, ValidacionError, ejecutar_seguro
>>> try:
...     raise ValidacionError("El correo del cliente no es válido")
... except SoftwareFJError as error:
...     print("Error controlado:", error)   # ya quedó registrado en el log
"""

# ---------------------------------------------------------------------------
# Importaciones (solo librería estándar, sin dependencias externas)
# ---------------------------------------------------------------------------
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional


# ---------------------------------------------------------------------------
# Configuración global del módulo
# ---------------------------------------------------------------------------

#: Ruta del archivo de registro. Se ubica junto a este módulo para que funcione
#: igual sin importar desde qué carpeta se ejecute el programa en VS Code.
RUTA_LOG: Path = Path(__file__).resolve().parent / "log_errores.txt"

#: Formato de fecha y hora de cada línea del log (año-mes-día hora:min:seg).
FORMATO_FECHA: str = "%Y-%m-%d %H:%M:%S"

#: Candado para evitar que dos hilos escriban al mismo tiempo en el archivo y
#: mezclen o corrompan las líneas del registro.
_CANDADO_LOG = threading.Lock()


# ---------------------------------------------------------------------------
# Mecanismo de registro (logs)
# ---------------------------------------------------------------------------
def registrar_error(
    mensaje: str,
    nivel: str = "ERROR",
    excepcion: Optional[BaseException] = None,
    contexto: Optional[str] = None,
) -> bool:
    """Escribe un evento en el archivo ``log_errores.txt`` con timestamp.

    Cada registro ocupa una sola línea con el formato::

        [AAAA-MM-DD HH:MM:SS] [NIVEL] [Contexto] Mensaje | Tipo: X | Origen: archivo:línea

    Esta función está diseñada para ser **a prueba de fallos**: si el archivo
    no se puede escribir (permisos, disco lleno, ruta inválida, etc.), el error
    de escritura se captura, se informa por la salida de error estándar y la
    función devuelve ``False``. Jamás propaga una excepción, por lo que el
    programa principal sigue activo y estable.

    Args:
        mensaje: Descripción legible del error o evento.
        nivel: Severidad del evento (``"ERROR"``, ``"ADVERTENCIA"``, ``"INFO"``,
            ``"CRITICO"``...). Por defecto ``"ERROR"``.
        excepcion: Excepción asociada (opcional). Si se entrega, se registra su
            tipo y el punto del código donde se originó.
        contexto: Nombre del módulo, clase o proceso donde ocurrió (opcional).

    Returns:
        ``True`` si el registro se escribió correctamente; ``False`` en caso
        contrario.
    """
    try:
        # 1) Marca de tiempo exacta del momento en que se detecta el error.
        marca_tiempo = datetime.now().strftime(FORMATO_FECHA)

        # 2) Construcción de la línea base: fecha, nivel y (si existe) contexto.
        partes = [f"[{marca_tiempo}]", f"[{str(nivel).upper()}]"]
        if contexto:
            partes.append(f"[{contexto}]")

        # 3) Se aplana el mensaje a una sola línea para mantener el log legible.
        mensaje_plano = " ".join(str(mensaje).split())
        linea = " ".join(partes) + f" {mensaje_plano}"

        # 4) Si hay excepción asociada, se agrega su tipo y su origen.
        if excepcion is not None:
            linea += f" | Tipo: {type(excepcion).__name__}"
            rastro = traceback.extract_tb(excepcion.__traceback__)
            if rastro:
                ultimo = rastro[-1]  # Último marco = donde realmente se originó.
                linea += f" | Origen: {Path(ultimo.filename).name}:{ultimo.lineno}"

        # 5) Escritura en modo "append" (a) para conservar el historial previo.
        #    El candado garantiza escrituras ordenadas aunque haya varios hilos.
        with _CANDADO_LOG:
            with open(RUTA_LOG, "a", encoding="utf-8") as archivo:
                archivo.write(linea + "\n")
        return True

    except Exception as fallo_log:  # noqa: BLE001 - se captura todo a propósito
        # El sistema de logs NUNCA debe tumbar la aplicación. Se avisa por
        # stderr y se continúa con normalidad.
        print(
            f"[Software FJ] No fue posible escribir en el log: {fallo_log}",
            file=sys.stderr,
        )
        return False


# ---------------------------------------------------------------------------
# Jerarquía de excepciones personalizadas
# ---------------------------------------------------------------------------
class SoftwareFJError(Exception):
    """Excepción base para todos los errores de negocio de Software FJ.

    Al capturar ``SoftwareFJError`` en un ``except`` se atrapan también todas
    sus subclases, lo que permite separar los errores propios del sistema de
    los errores inesperados de Python (``ValueError``, ``TypeError``, etc.).

    Por defecto, **cada vez que se crea una instancia el error se registra
    automáticamente** en ``log_errores.txt`` (ver parámetro ``registrar``).

    Attributes:
        mensaje (str): Descripción del error.
        contexto (Optional[str]): Módulo o proceso donde se originó.
        registrado (bool): ``True`` si el error se escribió en el log.
    """

    #: Nivel de severidad con el que se escribe en el log (las subclases
    #: pueden sobrescribirlo).
    NIVEL_LOG: str = "ERROR"

    def __init__(
        self,
        mensaje: str = "Error en Software FJ",
        contexto: Optional[str] = None,
        registrar: bool = True,
    ) -> None:
        """Inicializa la excepción y, opcionalmente, la registra en el log.

        Args:
            mensaje: Texto descriptivo del error de negocio.
            contexto: Nombre del módulo, clase o proceso donde ocurrió.
            registrar: Si es ``True`` (valor por defecto) se escribe el error en
                el archivo de log automáticamente.
        """
        # Se llama al constructor de Exception para conservar el comportamiento
        # estándar (str(error), error.args, etc.).
        super().__init__(mensaje)
        self.mensaje: str = mensaje
        self.contexto: Optional[str] = contexto
        self.registrado: bool = False

        if registrar:
            # Aún no se ha lanzado la excepción, por lo que no hay traceback;
            # se registra el mensaje con el nombre de la clase concreta.
            self.registrado = registrar_error(
                mensaje=f"{mensaje} | Tipo: {type(self).__name__}",
                nivel=self.NIVEL_LOG,
                contexto=contexto,
            )

    def __str__(self) -> str:
        """Devuelve el mensaje legible, anteponiendo el contexto si existe."""
        if self.contexto:
            return f"[{self.contexto}] {self.mensaje}"
        return self.mensaje


class ValidacionError(SoftwareFJError):
    """Se lanza cuando un dato de entrada no cumple las reglas de validación.

    Ejemplos: correo con formato inválido, campo obligatorio vacío, número
    fuera del rango permitido.
    """

    NIVEL_LOG = "ADVERTENCIA"


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una operación que las reglas de negocio
    prohíben en el estado actual del sistema.

    Ejemplos: cancelar una reserva ya finalizada, procesar un servicio inactivo.
    """


class RecursoNoDisponibleError(SoftwareFJError):
    """Se lanza cuando un recurso requerido no existe o no está disponible.

    Ejemplos: cliente no encontrado, servicio sin cupo, archivo inexistente.
    """


# ---------------------------------------------------------------------------
# Utilidad para mantener la aplicación estable
# ---------------------------------------------------------------------------
def ejecutar_seguro(
    funcion: Callable[..., Any],
    *args: Any,
    valor_por_defecto: Any = None,
    contexto: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """Ejecuta ``funcion`` capturando cualquier error para no cerrar el programa.

    Comportamiento:

    * Si la función termina bien, devuelve su resultado.
    * Si lanza un ``SoftwareFJError``, este ya se registró al crearse; solo se
      captura y se devuelve ``valor_por_defecto``.
    * Si lanza cualquier otra excepción inesperada, se registra con nivel
      ``CRITICO`` (incluyendo su tipo y origen) y se devuelve
      ``valor_por_defecto``.

    En ningún caso la excepción se propaga, de modo que el flujo principal de la
    aplicación continúa activo.

    Args:
        funcion: Función o método que se desea ejecutar de forma segura.
        *args: Argumentos posicionales que se pasan a ``funcion``.
        valor_por_defecto: Valor devuelto si ocurre un error. Por defecto ``None``.
        contexto: Nombre del proceso, útil para identificar la línea en el log.
        **kwargs: Argumentos con nombre que se pasan a ``funcion``.

    Returns:
        El resultado de ``funcion`` o ``valor_por_defecto`` si hubo un error.

    Example:
        >>> resultado = ejecutar_seguro(int, "abc", valor_por_defecto=0)
        >>> resultado
        0
    """
    try:
        return funcion(*args, **kwargs)

    except SoftwareFJError:
        # Error de negocio esperado: ya fue registrado en su constructor.
        return valor_por_defecto

    except Exception as error:  # noqa: BLE001 - se captura todo a propósito
        # Error inesperado (bug, dato corrupto, etc.): se registra con detalle.
        registrar_error(
            mensaje=str(error) or "Error inesperado sin descripción",
            nivel="CRITICO",
            excepcion=error,
            contexto=contexto or getattr(funcion, "__name__", "desconocido"),
        )
        return valor_por_defecto


# ---------------------------------------------------------------------------
# Prueba rápida del módulo (solo se ejecuta con: python excepciones.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Prueba del módulo excepciones.py ===")

    # 1) Error de negocio lanzado y capturado manualmente.
    try:
        raise ValidacionError("El documento del cliente está vacío", contexto="Cliente")
    except SoftwareFJError as e:
        print(f"Error de negocio capturado: {e}")

    # 2) Error inesperado de Python controlado con ejecutar_seguro.
    resultado = ejecutar_seguro(lambda: 10 / 0, valor_por_defecto=-1, contexto="Calculo")
    print(f"Resultado tras error inesperado: {resultado}")

    # 3) La aplicación sigue activa después de los errores.
    print(f"La aplicación continúa estable. Revisa el log en: {RUTA_LOG}")