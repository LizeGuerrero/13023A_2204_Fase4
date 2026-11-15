# -*- coding: utf-8 -*-
from excepciones import SoftwareFJError
from modelos import Cliente

if __name__ == "__main__":
    print("=== Iniciando prueba de modelos y excepciones ===")

    # 1. Caso exitoso (Happy Path)
    try:
        c = Cliente("1001", "Ana Pérez", "ana@correo.com")
        print(c)  # Debe imprimir el detalle correctamente
    except SoftwareFJError as e:
        print(f"Error inesperado: {e}")

    # 2. Caso con error de validación (Sad Path - correo sin punto en el dominio)
    try:
        print("Intentando crear cliente con correo inválido...")
        Cliente("1002", "Luis", "luis@correo")
    except SoftwareFJError as e:
        print(f"¡Excepción controlada con éxito!: {e}")

    print("=== Prueba finalizada. Revisa si se generó el archivo log_errores.txt ===")
    