# -*- coding: utf-8 -*-
"""
consola_servicios.py

Salida por consola para ver los servicios y las reservas en funcionamiento.

Se conecta al menú de main.py con la función opcion_servicios(). Muestra:
    1. Los tres servicios y su descripción.
    2. Los cálculos de costo con la sobrecarga (base, impuesto, descuento).
    3. Una reserva que pasa por confirmar y procesar.
    4. Un error controlado: una reserva que no se puede crear.

No guarda nada ni modifica la lista de clientes; solo muestra resultados.
Esto no reemplaza las 10 simulaciones del enunciado.
"""

# Excepción base del proyecto, para capturar los errores esperados
from excepciones import SoftwareFJError

# Clase de cliente que usa la reserva
from modelos import Cliente

# Clase de reserva
from reservas import Reserva

# Los tres servicios especializados
from servicios import AlquilerEquipo, AsesoriaEspecializada, SalaReuniones


def opcion_servicios(gestor=None):
    """Muestra en consola los servicios y las reservas en funcionamiento.

    Recibe el parámetro gestor solo para que tenga la misma forma que las
    demás opciones del menú de main.py; aquí no se usa.

    Args:
        gestor: gestor de clientes de main.py. No se utiliza.
    """
    # Título de la salida
    print("\n--- Servicios y reservas ---")

    # Se crea un cliente de ejemplo (no se agrega al gestor de clientes)
    cliente = Cliente("9001", "Cliente de ejemplo", "ejemplo@correo.com")

    # Se crea un servicio de cada tipo
    sala = SalaReuniones("S-01", "Sala Andes", 50000, capacidad=10)
    equipo = AlquilerEquipo("E-01", "Portátil Dell", 8000, unidades_disponibles=3)
    asesoria = AsesoriaEspecializada("A-01", "Asesoría Python", 40000, "Python", "senior")

    # Primera parte: cada servicio se describe a su manera (polimorfismo)
    print("\n1. Servicios disponibles:")
    for servicio in (sala, equipo, asesoria):
        print("   " + servicio.describir())

    # Segunda parte: el mismo método con distintos parámetros (sobrecarga)
    print("\n2. Costo de la sala por 2 horas, 6 asistentes, con audiovisual:")
    print(f"   Solo costo base:               ${sala.calcular_costo(2, asistentes=6, con_audiovisual=True):,.2f}")
    print(f"   Con IVA 19 %:                  ${sala.calcular_costo(2, impuesto=0.19, asistentes=6, con_audiovisual=True):,.2f}")
    print(f"   Con descuento 10 %:            ${sala.calcular_costo(2, descuento=0.10, asistentes=6, con_audiovisual=True):,.2f}")
    print(f"   Con descuento 10 % e IVA 19 %: ${sala.calcular_costo(2, 0.19, 0.10, asistentes=6, con_audiovisual=True):,.2f}")

    # Tercera parte: una reserva completa, de pendiente a procesada
    print("\n3. Reserva de 5 horas de 2 portátiles, con IVA:")
    reserva = Reserva("R-EJEMPLO", cliente, equipo, 5, impuesto=0.19, unidades=2)
    print("   " + reserva.mostrar_detalle())

    # Se confirma y se muestra el cambio de estado
    reserva.confirmar()
    print("   " + reserva.mostrar_detalle())

    # Se procesa y se muestra el costo final
    reserva.procesar()
    print("   " + reserva.mostrar_detalle())

    # Cuarta parte: un error controlado, para ver cómo responde el sistema
    print("\n4. Intento de reserva incorrecto (12 asistentes en una sala de 10):")
    try:
        Reserva("R-ERROR", cliente, sala, 2, asistentes=12)
    except SoftwareFJError as error:
        # El error ya quedó escrito en log_errores.txt al crearse
        print(f"   Error controlado: {error}")

    # Cierre
    print("\nRevisa log_errores.txt para ver los eventos registrados.")
