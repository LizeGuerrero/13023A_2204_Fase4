# -*- coding: utf-8 -*-
"""
consola_servicios.py

Submenú de consola para gestionar servicios y reservas de Software FJ.

Se conecta con la opción 6 del menú de main.py mediante opcion_servicios().
Desde este submenú se puede:
    1. Registrar un servicio (sala, equipo o asesoría).
    2. Listar los servicios.
    3. Cambiar la disponibilidad de un servicio.
    4. Crear una reserva (para un cliente ya registrado en main.py).
    5. Listar las reservas.
    6. Confirmar una reserva.
    7. Cancelar una reserva.
    8. Procesar una reserva (calcula el costo final).
    9. Volver al menú principal.

Esta pantalla no tiene reglas de negocio: solo pide datos, llama a las clases
del proyecto y muestra el resultado. Las validaciones están en las clases.

Los servicios y las reservas se guardan en memoria mientras el programa está
abierto, y se pierden al cerrarlo.
"""

# Excepciones y función de log del proyecto
from excepciones import (
    OperacionNoPermitidaError,
    SoftwareFJError,
    ValidacionError,
    registrar_error,
)

# Gestores de servicios y de reservas
from gestor_reservas import GestorReservas
from gestor_servicios import GestorServicios

# Clase de reserva
from reservas import Reserva

# Clases de servicio y tasa de IVA
from servicios import (
    IVA_GENERAL,
    AlquilerEquipo,
    AsesoriaEspecializada,
    SalaReuniones,
)

# Estos dos gestores se crean una sola vez, al importar el módulo. Así los
# servicios y reservas se conservan cada vez que se vuelve a entrar al
# submenú durante la misma ejecución del programa.
_gestor_servicios = GestorServicios()
_gestor_reservas = GestorReservas()


# Funciones para pedir datos al usuario

def solicitar_texto(mensaje):
    """Pide un texto por consola y lo devuelve sin espacios laterales.

    Args:
        mensaje: texto que se muestra al usuario.

    Returns:
        Lo que escribió el usuario, sin espacios al inicio ni al final.
    """
    return input(mensaje).strip()


def convertir_numero(texto, nombre):
    """Convierte un texto a número (con o sin decimales).

    Args:
        texto: texto que escribió el usuario.
        nombre: nombre del dato, para el mensaje de error.

    Returns:
        El número como float.

    Raises:
        ValidacionError: si el texto no es un número.
    """
    # Se acepta la coma decimal cambiándola por punto
    limpio = texto.strip().replace(",", ".")

    try:
        return float(limpio)
    except ValueError as error:
        # float() falla con textos como "abc"; se convierte en un error del
        # sistema conservando el original como causa
        raise ValidacionError(
            f"El dato '{nombre}' debe ser un número (se recibió '{texto}')",
            contexto="Consola",
        ) from error


def solicitar_numero(mensaje, nombre):
    """Pide un número por consola y lo convierte a float.

    Args:
        mensaje: texto que se muestra al usuario.
        nombre: nombre del dato, para el mensaje de error.

    Returns:
        El número como float.

    Raises:
        ValidacionError: si lo escrito no es un número.
    """
    return convertir_numero(solicitar_texto(mensaje), nombre)


def solicitar_entero(mensaje, nombre):
    """Pide un número entero y lo convierte a int.

    Args:
        mensaje: texto que se muestra al usuario.
        nombre: nombre del dato, para el mensaje de error.

    Returns:
        El número como int.

    Raises:
        ValidacionError: si lo escrito no es un número entero.
    """
    texto = solicitar_texto(mensaje)

    try:
        return int(texto)
    except ValueError as error:
        # int() falla con textos como "2.5" o "abc"
        raise ValidacionError(
            f"El dato '{nombre}' debe ser un número entero (se recibió '{texto}')",
            contexto="Consola",
        ) from error


def solicitar_si_no(mensaje):
    """Pide una respuesta de sí o no.

    Args:
        mensaje: pregunta que se muestra al usuario.

    Returns:
        True si respondió sí, False si respondió no.

    Raises:
        ValidacionError: si responde otra cosa.
    """
    # Se pasa a minúsculas para aceptar "S", "Si", "NO", etc.
    respuesta = solicitar_texto(mensaje + " (s/n): ").lower()

    if respuesta in ("s", "si", "sí"):
        return True
    if respuesta in ("n", "no"):
        return False

    # Cualquier otra respuesta no se puede interpretar
    raise ValidacionError(
        f"Responda 's' o 'n' (se recibió '{respuesta}')", contexto="Consola"
    )


def solicitar_opciones_del_servicio(servicio):
    """Pide los parámetros propios del tipo de servicio que se va a reservar.

    Args:
        servicio: servicio elegido para la reserva.

    Returns:
        Diccionario con los parámetros, listo para pasarlo a Reserva.
    """
    # Cada tipo de servicio necesita datos distintos
    if isinstance(servicio, SalaReuniones):
        return {
            "asistentes": solicitar_entero("Cantidad de asistentes: ", "asistentes"),
            "con_audiovisual": solicitar_si_no("¿Usará equipo audiovisual?"),
        }

    if isinstance(servicio, AlquilerEquipo):
        return {
            "unidades": solicitar_entero("Cantidad de unidades: ", "unidades"),
            "con_seguro": solicitar_si_no("¿Con seguro?"),
        }

    if isinstance(servicio, AsesoriaEspecializada):
        return {"modalidad": solicitar_texto("Modalidad (virtual/presencial): ")}

    # Un servicio de otro tipo no necesita parámetros extra
    return {}


# Opciones del submenú

def mostrar_menu():
    """Imprime las opciones del submenú de servicios y reservas."""
    print("\n" + "=" * 40)
    print("        SERVICIOS Y RESERVAS")
    print("=" * 40)
    print("1. Registrar un servicio")
    print("2. Listar servicios")
    print("3. Cambiar disponibilidad de un servicio")
    print("4. Crear una reserva")
    print("5. Listar reservas")
    print("6. Confirmar una reserva")
    print("7. Cancelar una reserva")
    print("8. Procesar una reserva")
    print("9. Volver al menú principal")
    print("-" * 40)


def registrar_servicio(gestor_clientes):
    """Pide los datos de un servicio, lo crea y lo registra.

    Args:
        gestor_clientes: gestor de clientes de main.py. No se usa aquí.

    Raises:
        SoftwareFJError: si algún dato es inválido o el identificador existe.
    """
    print("\n--- Registrar servicio ---")
    print("1. Sala de reuniones")
    print("2. Alquiler de equipo")
    print("3. Asesoría especializada")
    tipo = solicitar_texto("Tipo de servicio (1-3): ")

    # Si el tipo no es válido se corta antes de pedir más datos
    if tipo not in ("1", "2", "3"):
        raise ValidacionError(
            f"Tipo de servicio '{tipo}' no válido. Use 1, 2 o 3", contexto="Consola"
        )

    # Datos comunes a los tres tipos
    identificador = solicitar_texto("Identificador del servicio: ")
    nombre = solicitar_texto("Nombre: ")
    tarifa = solicitar_numero(
        "Tarifa por hora en pesos (solo números, sin puntos de miles): ", "tarifa"
    )

    # Datos propios de cada tipo; el constructor de cada clase los valida
    if tipo == "1":
        capacidad = solicitar_entero("Capacidad (personas): ", "capacidad")
        servicio = SalaReuniones(identificador, nombre, tarifa, capacidad)
    elif tipo == "2":
        unidades = solicitar_entero("Unidades disponibles: ", "unidades")
        servicio = AlquilerEquipo(identificador, nombre, tarifa, unidades)
    else:
        especialidad = solicitar_texto("Especialidad: ")
        nivel = solicitar_texto("Nivel (junior/senior/experto): ")
        servicio = AsesoriaEspecializada(identificador, nombre, tarifa, especialidad, nivel)

    # El gestor comprueba que el identificador no esté repetido
    _gestor_servicios.agregar_servicio(servicio)
    print(f"Servicio '{servicio.nombre}' registrado correctamente.")


def listar_servicios(gestor_clientes):
    """Muestra todos los servicios registrados.

    Args:
        gestor_clientes: gestor de clientes de main.py. No se usa aquí.
    """
    print("\n--- Servicios registrados ---")
    print(_gestor_servicios.mostrar_servicios())
    print(f"Total: {len(_gestor_servicios)}")


def cambiar_disponibilidad(gestor_clientes):
    """Activa o desactiva un servicio.

    Args:
        gestor_clientes: gestor de clientes de main.py. No se usa aquí.

    Raises:
        SoftwareFJError: si el servicio no existe.
    """
    print("\n--- Cambiar disponibilidad ---")
    identificador = solicitar_texto("Identificador del servicio: ")

    # Si no existe, buscar_servicio lanza RecursoNoDisponibleError
    servicio = _gestor_servicios.buscar_servicio(identificador)

    # Se invierte el valor actual: disponible pasa a no disponible y viceversa
    servicio.disponible = not servicio.disponible
    estado = "disponible" if servicio.disponible else "no disponible"
    print(f"El servicio '{servicio.nombre}' ahora está {estado}.")


def crear_reserva(gestor_clientes):
    """Pide los datos de una reserva, la crea y la registra.

    El cliente debe estar registrado en el gestor de clientes de main.py.

    Args:
        gestor_clientes: gestor de clientes de main.py.

    Raises:
        SoftwareFJError: si algún dato es inválido, el cliente o el servicio
            no existen, o el identificador de la reserva ya existe.
    """
    print("\n--- Crear reserva ---")

    # Se muestran los clientes y servicios para que el usuario vea los códigos
    print("Clientes:")
    print(gestor_clientes.mostrar_clientes())
    print("\nServicios:")
    print(_gestor_servicios.mostrar_servicios())
    print()

    identificador = solicitar_texto("Identificador de la reserva: ")

    # Se revisa el identificador antes de pedir el resto de datos
    if _gestor_reservas.existe_reserva(identificador):
        raise OperacionNoPermitidaError(
            f"Ya existe una reserva con identificador '{identificador}'",
            contexto="Consola",
        )

    # Se buscan el cliente y el servicio; si no existen, se lanza el error
    cliente = gestor_clientes.buscar_cliente(solicitar_texto("Identificador del cliente: "))
    servicio = _gestor_servicios.buscar_servicio(solicitar_texto("Identificador del servicio: "))

    duracion = solicitar_numero("Duración en horas: ", "duración")

    # Parámetros propios del tipo de servicio elegido
    opciones = solicitar_opciones_del_servicio(servicio)

    # Impuesto opcional: si responde sí se usa el IVA general
    impuesto = IVA_GENERAL if solicitar_si_no("¿Aplicar IVA del 19 %?") else None

    # Descuento opcional: se escribe en porcentaje y se pasa a fracción
    texto_descuento = solicitar_texto("Descuento en % (Enter si no hay): ")
    descuento = None
    if texto_descuento:
        # Por ejemplo, 10 se convierte en 0.10
        descuento = convertir_numero(texto_descuento, "descuento") / 100

    # El constructor de Reserva valida todos los datos
    reserva = Reserva(identificador, cliente, servicio, duracion,
                      impuesto=impuesto, descuento=descuento, **opciones)

    # El gestor comprueba que el identificador no esté repetido
    _gestor_reservas.agregar_reserva(reserva)
    print("Reserva creada en estado Pendiente.")


def listar_reservas(gestor_clientes):
    """Muestra todas las reservas registradas.

    Args:
        gestor_clientes: gestor de clientes de main.py. No se usa aquí.
    """
    print("\n--- Reservas registradas ---")
    print(_gestor_reservas.mostrar_reservas())
    print(f"Total: {len(_gestor_reservas)}")


def confirmar_reserva(gestor_clientes):
    """Confirma una reserva pendiente.

    Args:
        gestor_clientes: gestor de clientes de main.py. No se usa aquí.

    Raises:
        SoftwareFJError: si la reserva no existe o no se puede confirmar.
    """
    print("\n--- Confirmar reserva ---")
    reserva = _gestor_reservas.buscar_reserva(solicitar_texto("Identificador de la reserva: "))
    reserva.confirmar()
    print("Reserva confirmada.")


def cancelar_reserva(gestor_clientes):
    """Cancela una reserva pendiente o confirmada.

    Args:
        gestor_clientes: gestor de clientes de main.py. No se usa aquí.

    Raises:
        SoftwareFJError: si la reserva no existe o no se puede cancelar.
    """
    print("\n--- Cancelar reserva ---")
    reserva = _gestor_reservas.buscar_reserva(solicitar_texto("Identificador de la reserva: "))
    motivo = solicitar_texto("Motivo (opcional): ")
    reserva.cancelar(motivo)
    print("Reserva cancelada.")


def procesar_reserva(gestor_clientes):
    """Procesa una reserva confirmada y muestra su costo final.

    Args:
        gestor_clientes: gestor de clientes de main.py. No se usa aquí.

    Raises:
        SoftwareFJError: si la reserva no existe o no se puede procesar.
    """
    print("\n--- Procesar reserva ---")
    reserva = _gestor_reservas.buscar_reserva(solicitar_texto("Identificador de la reserva: "))
    total = reserva.procesar()
    print(f"Reserva procesada. Costo final: ${total:,.2f}")


# Función que conecta este módulo con main.py

def opcion_servicios(gestor_clientes):
    """Ejecuta el submenú de servicios y reservas hasta que el usuario vuelve.

    Es la función que main.py llama desde su opción 6. Recibe el gestor de
    clientes para poder buscar clientes al crear reservas.

    Args:
        gestor_clientes: gestor de clientes de main.py.
    """
    # Tabla que asocia cada opción del submenú con la función que la ejecuta
    acciones = {
        "1": registrar_servicio,
        "2": listar_servicios,
        "3": cambiar_disponibilidad,
        "4": crear_reserva,
        "5": listar_reservas,
        "6": confirmar_reserva,
        "7": cancelar_reserva,
        "8": procesar_reserva,
    }

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-9): ").strip()

        # La opción 9 rompe el ciclo y devuelve el control a main.py
        if opcion == "9":
            break

        accion = acciones.get(opcion)
        if accion is None:
            print("Opción no válida. Digite un número del 1 al 9.")
            continue

        try:
            accion(gestor_clientes)

        except SoftwareFJError as error:
            # Error esperado: ya quedó escrito en el log al crearse
            print(f"Error: {error}")

        except Exception as error:
            # Error inesperado: se registra y el submenú sigue activo
            registrar_error(
                mensaje=str(error) or "Error inesperado sin descripción",
                nivel="CRITICO",
                excepcion=error,
                contexto="consola_servicios",
            )
            print("Ocurrió un error inesperado. Quedó registrado en el log; "
                  "puede continuar.")
