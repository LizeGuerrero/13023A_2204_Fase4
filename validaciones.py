# -*- coding: utf-8 -*-
"""
validaciones.py

Funciones pequeñas de validación que se reutilizan en los servicios y en las
reservas del sistema Software FJ.

Cada función revisa un solo tipo de dato. Si el dato es correcto lo devuelve
ya limpio (por ejemplo, un texto sin espacios sobrantes); si no lo es, lanza
una ValidacionError, que además queda escrita en el archivo de log.

Funciones del módulo:
    validar_texto           : texto obligatorio, no vacío.
    validar_entero          : número entero con un mínimo opcional.
    validar_numero_positivo : número real mayor que cero.
    validar_proporcion      : número entre 0 y 1 (para impuestos y descuentos).
"""

# math sirve para comprobar que un número no sea infinito ni NaN
import math

# Solo se necesita la excepción de validación del proyecto
from excepciones import ValidacionError


def validar_texto(valor, nombre, contexto):
    """Comprueba que el valor sea un texto con contenido.

    Args:
        valor: dato que se quiere validar.
        nombre: nombre del campo, se usa para armar el mensaje de error.
        contexto: clase o módulo que está validando, se escribe en el log.

    Returns:
        El texto sin espacios al inicio ni al final.

    Raises:
        ValidacionError: si no es texto o si está vacío.
    """
    # Si no es una cadena de texto no se puede aceptar
    if not isinstance(valor, str):
        raise ValidacionError(f"El campo '{nombre}' debe ser texto", contexto=contexto)

    # Se quitan los espacios laterales para comparar con el texto limpio
    limpio = valor.strip()

    # Un texto vacío (o solo con espacios) tampoco es válido
    if not limpio:
        raise ValidacionError(
            f"El campo '{nombre}' es obligatorio y no puede estar vacío",
            contexto=contexto,
        )

    # Todo bien, se devuelve el texto limpio
    return limpio


def validar_entero(valor, nombre, contexto, minimo=1):
    """Comprueba que el valor sea un número entero mayor o igual al mínimo.

    Args:
        valor: dato que se quiere validar.
        nombre: nombre del campo, se usa para armar el mensaje de error.
        contexto: clase o módulo que está validando, se escribe en el log.
        minimo: menor valor permitido. Por defecto 1.

    Returns:
        El mismo número entero.

    Raises:
        ValidacionError: si no es entero o si es menor que el mínimo.
    """
    # En Python True y False son enteros, pero aquí no tienen sentido
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValidacionError(
            f"El campo '{nombre}' debe ser un número entero", contexto=contexto
        )

    # Se verifica que no esté por debajo del mínimo permitido
    if valor < minimo:
        raise ValidacionError(
            f"El campo '{nombre}' debe ser mayor o igual a {minimo}", contexto=contexto
        )

    # Dato correcto
    return valor


def validar_numero_positivo(valor, nombre, contexto):
    """Comprueba que el valor sea un número real mayor que cero.

    Args:
        valor: dato que se quiere validar.
        nombre: nombre del campo, se usa para armar el mensaje de error.
        contexto: clase o módulo que está validando, se escribe en el log.

    Returns:
        El número convertido a float.

    Raises:
        ValidacionError: si no es número, no es finito o no es mayor que cero.
    """
    # Se descartan los booleanos y todo lo que no sea int o float
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidacionError(
            f"El campo '{nombre}' debe ser un número", contexto=contexto
        )

    # NaN e infinito pasarían como float, pero rompen cualquier cálculo
    if not math.isfinite(valor):
        raise ValidacionError(
            f"El campo '{nombre}' debe ser un número finito", contexto=contexto
        )

    # Debe ser estrictamente mayor que cero
    if valor <= 0:
        raise ValidacionError(
            f"El campo '{nombre}' debe ser mayor que cero", contexto=contexto
        )

    # Se devuelve como float para trabajar siempre con el mismo tipo
    return float(valor)


def validar_proporcion(valor, nombre, contexto):
    """Comprueba que el valor sea un número entre 0 y 1 (ambos incluidos).

    Se usa para impuestos y descuentos expresados como fracción:
    0.19 equivale al 19 %.

    Args:
        valor: dato que se quiere validar.
        nombre: nombre del campo, se usa para armar el mensaje de error.
        contexto: clase o módulo que está validando, se escribe en el log.

    Returns:
        El número convertido a float.

    Raises:
        ValidacionError: si no es número o está fuera del rango 0 a 1.
    """
    # Mismo filtro de tipo que en los demás números
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidacionError(
            f"El campo '{nombre}' debe ser un número", contexto=contexto
        )

    # Se exige que sea finito y esté dentro del rango; NaN falla la comparación
    if not math.isfinite(valor) or not 0 <= valor <= 1:
        raise ValidacionError(
            f"El campo '{nombre}' debe estar entre 0 y 1 (por ejemplo 0.19 para 19 %)",
            contexto=contexto,
        )

    # Dato correcto
    return float(valor)
