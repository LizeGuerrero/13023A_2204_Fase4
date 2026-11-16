# -*- coding: utf-8 -*-
"""
main.py
=======

Módulo principal (interfaz de consola) del sistema integral **Software FJ**.

Proyecto académico - UNAD

Ofrece un menú interactivo en bucle que permite:
    1. Registrar un nuevo cliente.
    2. Listar todos los clientes registrados.
    3. Buscar un cliente por su identificador.
    4. Guardar los clientes en el archivo de texto (``clientes.txt``).
    5. Cargar los clientes desde el archivo de texto.
    6. Salir del programa.

Estabilidad
-----------
Cada opción se ejecuta dentro de un bloque ``try-except``:

* ``SoftwareFJError`` (y sus subclases) se capturan y se muestra su mensaje
  amigable; el error ya quedó registrado en ``log_errores.txt``.
* Cualquier otro error inesperado también se captura y se registra, de modo que
  el programa nunca se cierra por una falla durante su uso normal.

Dependencias
------------
Requiere ``excepciones.py``, ``modelos.py`` y ``gestor.py`` en la misma carpeta.

Ejecución
---------
    python main.py
"""

# ---------------------------------------------------------------------------
# Importaciones de los módulos del proyecto
# ---------------------------------------------------------------------------
from excepciones import SoftwareFJError, registrar_error
from gestor import GestorClientes
from modelos import Cliente
from consola_servicios import opcion_servicios

# ---------------------------------------------------------------------------
# Funciones de apoyo de la interfaz
# ---------------------------------------------------------------------------
def mostrar_menu() -> None:
    """Imprime en consola las opciones disponibles del menú principal."""
    print("\n" + "=" * 40)
    print("        SOFTWARE FJ - GESTIÓN DE CLIENTES")
    print("=" * 40)
    print("1. Registrar un nuevo cliente")
    print("2. Listar todos los clientes")
    print("3. Buscar un cliente por identificador")
    print("4. Guardar clientes en archivo")
    print("5. Cargar clientes desde archivo")
    print("6. Ver servicios y reservas")
    print("7. Salir")
    
    print("-" * 40)


def solicitar_texto(mensaje: str) -> str:
    """Pide un dato al usuario por consola y lo devuelve sin espacios laterales.

    Args:
        mensaje: Texto que se muestra al usuario para solicitar el dato.

    Returns:
        El texto digitado por el usuario, sin espacios al inicio ni al final.
    """
    return input(mensaje).strip()


# ---------------------------------------------------------------------------
# Acciones del menú (una función por opción)
# ---------------------------------------------------------------------------
def opcion_registrar(gestor: GestorClientes) -> None:
    """Solicita los datos de un cliente y lo registra en el gestor.

    La validación de los datos (identificador, nombre y correo) ocurre al crear
    el objeto ``Cliente``; la validación de duplicados ocurre en el gestor.
    Cualquier ``SoftwareFJError`` se propaga hacia el bucle principal, que lo
    muestra al usuario.

    Args:
        gestor: Gestor de clientes donde se registrará el nuevo cliente.

    Raises:
        SoftwareFJError: Si algún dato es inválido o el identificador ya existe.
    """
    print("\n--- Registrar nuevo cliente ---")
    identificador = solicitar_texto("Identificador: ")
    nombre = solicitar_texto("Nombre completo: ")
    correo = solicitar_texto("Correo electrónico: ")

    # El constructor valida los tres datos; el gestor valida que no se repita.
    cliente = Cliente(identificador, nombre, correo)
    gestor.agregar_cliente(cliente)
    print(f"✔ Cliente '{cliente.nombre}' registrado correctamente.")


def opcion_listar(gestor: GestorClientes) -> None:
    """Muestra en consola el detalle de todos los clientes registrados.

    Args:
        gestor: Gestor de clientes del cual se obtiene el listado.
    """
    print("\n--- Clientes registrados ---")
    print(gestor.mostrar_clientes())
    print(f"Total: {len(gestor)}")


def opcion_buscar(gestor: GestorClientes) -> None:
    """Busca un cliente por su identificador y muestra su detalle.

    Args:
        gestor: Gestor de clientes donde se realiza la búsqueda.

    Raises:
        SoftwareFJError: Si no existe un cliente con ese identificador.
    """
    print("\n--- Buscar cliente ---")
    identificador = solicitar_texto("Identificador a buscar: ")
    cliente = gestor.buscar_cliente(identificador)
    print("✔ Cliente encontrado:")
    print(cliente.mostrar_detalle())


def opcion_guardar(gestor: GestorClientes) -> None:
    """Guarda los clientes actuales en el archivo de texto.

    Args:
        gestor: Gestor de clientes cuyos datos se guardarán.

    Raises:
        SoftwareFJError: Si no se puede escribir el archivo.
    """
    cantidad = gestor.guardar_clientes()
    print(f"✔ {cantidad} cliente(s) guardado(s) en '{gestor.ruta_archivo.name}'.")


def opcion_cargar(gestor: GestorClientes) -> None:
    """Carga los clientes desde el archivo de texto, reemplazando los actuales.

    Args:
        gestor: Gestor de clientes que recibirá los datos cargados.

    Raises:
        SoftwareFJError: Si el archivo no existe o no se puede leer.
    """
    cargados, omitidos = gestor.cargar_clientes()
    print(f"✔ {cargados} cliente(s) cargado(s) desde '{gestor.ruta_archivo.name}'.")
    if omitidos:
        print(
            f"⚠ Se omitieron {omitidos} línea(s) inválida(s). "
            "Consulta 'log_errores.txt' para ver el detalle."
        )


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main() -> None:
    """Ejecuta el bucle principal del menú interactivo.

    El bucle continúa hasta que el usuario elige la opción "Salir" (o cierra la
    entrada con Ctrl+C / Ctrl+D). Los errores de cada opción se capturan para
    que el programa se mantenga siempre activo y estable.
    """
    gestor = GestorClientes()  # Usa 'clientes.txt' junto a los módulos.

    # Tabla que asocia cada opción del menú con la función que la ejecuta.
    acciones = {
        "1": opcion_registrar,
        "2": opcion_listar,
        "3": opcion_buscar,
        "4": opcion_guardar,
        "5": opcion_cargar,
        "6": opcion_servicios,
    }

    print("Bienvenido a Software FJ")

    while True:
        mostrar_menu()

        try:
            opcion = input("Seleccione una opción (1-7): ").strip()

            # Opción de salida: rompe el bucle y termina el programa.
            if opcion == "7":
                print("\nGracias por usar Software FJ. ¡Hasta pronto!")
                break

            accion = acciones.get(opcion)
            if accion is None:
                # Opción fuera del menú: se avisa y se vuelve a mostrar el menú.
                print("⚠ Opción no válida. Digite un número del 1 al 6.")
                continue

            # Se ejecuta la acción elegida.
            accion(gestor)

        except SoftwareFJError as error:
            # Error de negocio esperado (validación, duplicado, archivo...).
            # Ya quedó registrado en el log al crearse la excepción.
            print(f"✖ Error: {error}")

        except (KeyboardInterrupt, EOFError):
            # El usuario cerró la entrada (Ctrl+C / Ctrl+D): salida ordenada.
            print("\n\nEntrada cancelada. Cerrando Software FJ. ¡Hasta pronto!")
            break

        except Exception as error:  # noqa: BLE001 - red de seguridad final
            # Error inesperado: se registra en el log y el programa continúa.
            registrar_error(
                mensaje=str(error) or "Error inesperado sin descripción",
                nivel="CRITICO",
                excepcion=error,
                contexto="main",
            )
            print("✖ Ocurrió un error inesperado. Fue registrado en el log; "
                  "puede continuar usando el programa.")


# ---------------------------------------------------------------------------
# Punto de entrada del programa
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
    
    