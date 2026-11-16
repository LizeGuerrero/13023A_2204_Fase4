# -*- coding: utf-8 -*-
"""
test_servicios_reservas.py

Pruebas rápidas de los servicios, la sobrecarga de costos y la clase Reserva.
Se ejecuta con:

    python test_servicios_reservas.py

Cada prueba usa assert: si algo no se cumple, el programa se detiene y muestra
cuál fue. Si todo está bien, al final se imprime un mensaje de éxito.

Estas pruebas NO reemplazan las 10 simulaciones completas del enunciado; solo
comprueban que cada pieza funciona por separado.
"""

# Excepciones del proyecto que se esperan en las pruebas
from excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    RecursoNoDisponibleError,
    SoftwareFJError,
    ValidacionError,
)

# Clases que se van a probar
from gestor_reservas import GestorReservas
from gestor_servicios import GestorServicios
from modelos import Cliente
from reservas import EstadoReserva, Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, SalaReuniones, Servicio


def esperar_error(tipo_error, funcion, *args, **kwargs):
    """Ejecuta la función y comprueba que lance el error indicado.

    Args:
        tipo_error: clase de excepción que se espera.
        funcion: función que se va a ejecutar.
        *args: argumentos posicionales de la función.
        **kwargs: argumentos con nombre de la función.

    Returns:
        La excepción capturada, por si la prueba quiere revisarla.
    """
    try:
        funcion(*args, **kwargs)
    except tipo_error as error:
        # Era el error esperado
        return error
    # Si llegó aquí, la función no lanzó nada: la prueba falla
    raise AssertionError(f"Se esperaba {tipo_error.__name__} y no se lanzó")


class ServicioDefectuoso(Servicio):
    """Servicio de prueba cuyo cálculo falla a propósito.

    Sirve para comprobar que calcular_costo() convierte los errores de cálculo
    en CalculoInconsistenteError y conserva la causa original.
    """

    # Modo de falla: "division" lanza ZeroDivisionError, "negativo" devuelve -5
    def __init__(self, modo):
        # Se construye como cualquier servicio, con datos válidos
        super().__init__("D-01", "Servicio defectuoso", 1000)
        # Se guarda el modo de falla que se quiere simular
        self.modo = modo

    def describir(self):
        # Descripción mínima, solo para cumplir con el método abstracto
        return "Servicio defectuoso de prueba"

    def validar_parametros(self, duracion, **opciones):
        # Solo se valida la duración con las reglas comunes
        self._validar_duracion(duracion)

    def calcular_costo_base(self, duracion, **opciones):
        # Simula una división por cero
        if self.modo == "division":
            return 1 / 0
        # Simula un costo negativo
        return -5.0


if __name__ == "__main__":
    print("Pruebas de servicios y reservas")

    # Datos de apoyo que se usan en varias pruebas
    cliente = Cliente("1001", "Ana Pérez", "ana@correo.com")
    sala = SalaReuniones("S-01", "Sala Andes", 50000, capacidad=10)
    equipo = AlquilerEquipo("E-01", "Portátil Dell", 8000, unidades_disponibles=3)
    asesoria = AsesoriaEspecializada("A-01", "Asesoría Python", 40000, "Python", "senior")

    # 1. La clase abstracta no se puede instanciar
    esperar_error(TypeError, Servicio, "X-01", "Servicio genérico", 1000)
    print("1. Servicio abstracto no se puede instanciar: correcto")

    # 2. Cada servicio se describe a su manera (polimorfismo)
    for servicio in (sala, equipo, asesoria):
        print("   ", servicio.describir())
    print("2. describir() de los tres servicios: correcto")

    # 3. Costo base de cada servicio
    assert sala.calcular_costo(2, asistentes=6, con_audiovisual=True) == 120000
    assert equipo.calcular_costo(5, unidades=2) == 80000
    assert asesoria.calcular_costo(2, modalidad="virtual") == 120000
    print("3. Costo base de los tres servicios: correcto")

    # 4. Sobrecarga: impuesto, descuento y ambos
    assert sala.calcular_costo(2, impuesto=0.19, asistentes=6, con_audiovisual=True) == 142800
    assert sala.calcular_costo(2, descuento=0.10, asistentes=6, con_audiovisual=True) == 108000
    assert sala.calcular_costo(2, 0.19, 0.10, asistentes=6, con_audiovisual=True) == 128520
    assert sala.calcular_costo_con_impuesto(2, asistentes=6, con_audiovisual=True) == 142800
    assert sala.calcular_costo_con_descuento(2, 0.10, asistentes=6, con_audiovisual=True) == 108000
    print("4. Sobrecarga de calcular_costo: correcto")

    # 5. Recargos propios de cada servicio
    assert equipo.calcular_costo(5, unidades=2, con_seguro=True) == 84000
    assert asesoria.calcular_costo(2, modalidad="presencial") == 150000
    print("5. Seguro y recargo presencial: correcto")

    # 6. Errores de validación en los servicios
    esperar_error(ValidacionError, sala.calcular_costo, 20, asistentes=5)
    esperar_error(ValidacionError, sala.calcular_costo, 2)
    esperar_error(RecursoNoDisponibleError, sala.calcular_costo, 2, asistentes=50)
    esperar_error(ValidacionError, sala.calcular_costo, 2, asistente=5)
    esperar_error(RecursoNoDisponibleError, equipo.calcular_costo, 2, unidades=9)
    esperar_error(ValidacionError, asesoria.calcular_costo, 2, modalidad="telepatía")
    esperar_error(ValidacionError, sala.calcular_costo, 2, impuesto=1.5, asistentes=5)
    esperar_error(ValidacionError, sala.calcular_costo, "dos", asistentes=5)
    esperar_error(ValidacionError, SalaReuniones, "S-02", "Sala X", -100, 5)
    esperar_error(ValidacionError, AsesoriaEspecializada, "A-02", "Ase", 100, "Java", "maestro")
    print("6. Validaciones de los servicios: correcto")

    # 7. Flujo completo de una reserva: crear, confirmar y procesar
    reserva = Reserva("R-001", cliente, sala, 2, impuesto=0.19, asistentes=6)
    assert reserva.estado == EstadoReserva.PENDIENTE
    reserva.confirmar()
    assert reserva.estado == EstadoReserva.CONFIRMADA
    total = reserva.procesar()
    assert total == 119000 and reserva.costo_total == 119000
    assert reserva.estado == EstadoReserva.PROCESADA
    print("   ", reserva.mostrar_detalle())
    print("7. Reserva confirmada y procesada: correcto")

    # 8. Operaciones no permitidas según el estado
    esperar_error(OperacionNoPermitidaError, reserva.cancelar)
    esperar_error(OperacionNoPermitidaError, reserva.confirmar)
    pendiente = Reserva("R-002", cliente, equipo, 3, unidades=1)
    esperar_error(OperacionNoPermitidaError, pendiente.procesar)
    pendiente.cancelar("El cliente ya no lo necesita")
    assert pendiente.estado == EstadoReserva.CANCELADA
    esperar_error(OperacionNoPermitidaError, pendiente.confirmar)
    print("8. Transiciones de estado: correcto")

    # 9. Datos incorrectos al crear una reserva
    esperar_error(ValidacionError, Reserva, "R-003", "no soy cliente", sala, 2, asistentes=5)
    esperar_error(ValidacionError, Reserva, "R-004", cliente, "no soy servicio", 2)
    esperar_error(ValidacionError, Reserva, "R-005", cliente, sala, 2)
    esperar_error(RecursoNoDisponibleError, Reserva, "R-006", cliente, sala, 2, asistentes=99)
    print("9. Validación al crear reservas: correcto")

    # 10. Servicio que deja de estar disponible antes de confirmar
    asesoria.disponible = False
    inactiva = Reserva("R-007", cliente, asesoria, 2, modalidad="virtual")
    esperar_error(RecursoNoDisponibleError, inactiva.confirmar)
    assert inactiva.estado == EstadoReserva.PENDIENTE
    asesoria.disponible = True
    print("10. Servicio no disponible: correcto")

    # 11. Encadenamiento de excepciones en procesar()
    # Se reserva 3 equipos y luego el inventario baja a 1: al procesar falla el cálculo
    encadenada = Reserva("R-008", cliente, equipo, 2, unidades=3)
    encadenada.confirmar()
    equipo.unidades_disponibles = 1
    error = esperar_error(OperacionNoPermitidaError, encadenada.procesar)
    assert isinstance(error.__cause__, RecursoNoDisponibleError)
    assert encadenada.estado == EstadoReserva.CONFIRMADA
    assert encadenada.costo_total is None
    print("11. Encadenamiento de excepciones: correcto")

    # 12. Cálculos inconsistentes: se lanza CalculoInconsistenteError
    error = esperar_error(CalculoInconsistenteError, ServicioDefectuoso("division").calcular_costo, 2)
    assert isinstance(error.__cause__, ZeroDivisionError)
    esperar_error(CalculoInconsistenteError, ServicioDefectuoso("negativo").calcular_costo, 2)
    print("12. Cálculos inconsistentes: correcto")

    # 13. El programa sigue funcionando después de todos los errores
    assert isinstance(SoftwareFJError("prueba final"), Exception)
    print("13. El sistema sigue activo: correcto")

    # 14. Gestor de servicios: agregar, buscar, duplicados y tipo incorrecto
    gestor_s = GestorServicios()
    gestor_s.agregar_servicio(sala)
    gestor_s.agregar_servicio(equipo)
    assert len(gestor_s) == 2
    assert gestor_s.buscar_servicio("S-01") is sala
    assert gestor_s.existe_servicio("E-01") and not gestor_s.existe_servicio("Z-99")
    esperar_error(OperacionNoPermitidaError, gestor_s.agregar_servicio, sala)
    esperar_error(ValidacionError, gestor_s.agregar_servicio, "no soy servicio")
    esperar_error(RecursoNoDisponibleError, gestor_s.buscar_servicio, "Z-99")
    # La lista que devuelve es una copia: modificarla no afecta al gestor
    gestor_s.listar_servicios().clear()
    assert len(gestor_s) == 2
    print("14. Gestor de servicios: correcto")

    # 15. Gestor de reservas: agregar, buscar, duplicados y tipo incorrecto
    gestor_r = GestorReservas()
    gestor_r.agregar_reserva(reserva)
    assert len(gestor_r) == 1
    assert gestor_r.buscar_reserva("R-001") is reserva
    esperar_error(OperacionNoPermitidaError, gestor_r.agregar_reserva, reserva)
    esperar_error(ValidacionError, gestor_r.agregar_reserva, "no soy reserva")
    esperar_error(RecursoNoDisponibleError, gestor_r.buscar_reserva, "R-999")
    print("15. Gestor de reservas: correcto")

    print("Todas las pruebas pasaron. Revisa log_errores.txt para ver los eventos.")
