# -*- coding: utf-8 -*-
"""
asesoria.py

Servicio de asesorías especializadas.

Hereda de Servicio y sobrescribe describir(), validar_parametros() y
calcular_costo_base().

El nivel del asesor multiplica la tarifa por hora:
    junior   x 1.0
    senior   x 1.5
    experto  x 2.0

Parámetros que acepta al solicitar el servicio:
    modalidad  (obligatorio) "virtual" o "presencial". La presencial agrega un
               recargo fijo por desplazamiento.

Costo base = horas * tarifa por hora * factor del nivel + recargo (si es
presencial).
"""

# Excepciones que puede lanzar este servicio
from excepciones import ValidacionError

# Clase de la que hereda
from servicios.servicio import Servicio

# Función de validación compartida
from validaciones import validar_texto


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría especializada en un tema.

    Atributos propios:
        _especialidad: tema en el que el asesor da la asesoría.
        _nivel: nivel del asesor ("junior", "senior" o "experto").
    """

    # Datos propios de este servicio
    TIPO = "AsesoriaEspecializada"
    DURACION_MINIMA = 1
    DURACION_MAXIMA = 8

    # Factor que multiplica la tarifa según el nivel del asesor
    FACTORES_NIVEL = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    # Modalidades permitidas para una asesoría
    MODALIDADES = ("virtual", "presencial")

    # Recargo fijo, en pesos, por desplazamiento en la modalidad presencial
    RECARGO_PRESENCIAL = 30000

    def __init__(self, identificador, nombre, tarifa_hora, especialidad, nivel, disponible=True):
        """Crea un servicio de asesoría especializada.

        Args:
            identificador: código único del servicio.
            nombre: nombre comercial de la asesoría.
            tarifa_hora: tarifa base por hora, en pesos (antes del nivel).
            especialidad: tema de la asesoría (por ejemplo, "Python").
            nivel: "junior", "senior" o "experto".
            disponible: si el servicio nace disponible. Por defecto True.

        Raises:
            ValidacionError: si algún dato no es válido.
        """
        # Primero se construye la parte común (identificador, nombre, tarifa)
        super().__init__(identificador, nombre, tarifa_hora, disponible)

        # Se declaran los atributos y luego se asignan con las propiedades
        self._especialidad = ""
        self._nivel = "junior"
        self.especialidad = especialidad
        self.nivel = nivel

    @property
    def especialidad(self):
        """str: tema en el que se da la asesoría."""
        return self._especialidad

    @especialidad.setter
    def especialidad(self, valor):
        """Valida y guarda la especialidad."""
        # Debe ser un texto con contenido
        self._especialidad = validar_texto(valor, "especialidad", self.TIPO)

    @property
    def nivel(self):
        """str: nivel del asesor."""
        return self._nivel

    @nivel.setter
    def nivel(self, valor):
        """Valida y guarda el nivel del asesor."""
        # Primero debe ser texto; se pasa a minúsculas para aceptar "Senior"
        texto = validar_texto(valor, "nivel", self.TIPO).lower()

        # Debe ser uno de los niveles que tienen factor definido
        if texto not in self.FACTORES_NIVEL:
            raise ValidacionError(
                f"Nivel '{valor}' no válido. Use: {', '.join(self.FACTORES_NIVEL)}",
                contexto=self.TIPO,
            )
        self._nivel = texto

    def describir(self):
        """Describe la asesoría con su especialidad, nivel, tarifa y estado.

        Returns:
            Texto de una línea con los datos del servicio.
        """
        # Se arma el texto del estado a partir del booleano
        estado = "disponible" if self.disponible else "no disponible"

        # Se devuelve la descripción completa en una sola línea
        return (
            f"Asesoría especializada [ID: {self.identificador}] {self.nombre} | "
            f"Especialidad: {self.especialidad} | Nivel: {self.nivel} | "
            f"Tarifa base: ${self.tarifa_hora:,.0f} por hora | Estado: {estado}"
        )

    def validar_parametros(self, duracion, **opciones):
        """Revisa duración y modalidad de una solicitud.

        Args:
            duracion: horas de asesoría.
            **opciones: modalidad (obligatorio).

        Raises:
            ValidacionError: si falta la modalidad o alguno de los datos es
                inválido.
        """
        # Solo se acepta el parámetro que usa este servicio
        self._rechazar_opciones_desconocidas(opciones, ("modalidad",))

        # La duración se valida con el rango propio de la asesoría (1 a 8 horas)
        self._validar_duracion(duracion)

        # La modalidad es obligatoria
        if "modalidad" not in opciones:
            raise ValidacionError(
                "Falta el parámetro obligatorio 'modalidad'", contexto=self.TIPO
            )

        # Debe ser un texto; se pasa a minúsculas para comparar
        modalidad = validar_texto(opciones["modalidad"], "modalidad", self.TIPO).lower()

        # Y debe ser una de las modalidades permitidas
        if modalidad not in self.MODALIDADES:
            raise ValidacionError(
                f"Modalidad '{opciones['modalidad']}' no válida. "
                f"Use: {', '.join(self.MODALIDADES)}",
                contexto=self.TIPO,
            )

    def calcular_costo_base(self, duracion, **opciones):
        """Calcula el costo de la asesoría sin impuestos ni descuentos.

        Args:
            duracion: horas de asesoría.
            **opciones: modalidad.

        Returns:
            Horas por tarifa por factor del nivel, más el recargo si la
            modalidad es presencial.
        """
        # Factor según el nivel del asesor (1.0, 1.5 o 2.0)
        factor = self.FACTORES_NIVEL[self.nivel]

        # Costo del tiempo de asesoría
        costo = float(duracion) * self.tarifa_hora * factor

        # La modalidad presencial suma el recargo por desplazamiento
        if str(opciones.get("modalidad", "")).strip().lower() == "presencial":
            costo += self.RECARGO_PRESENCIAL

        return costo
