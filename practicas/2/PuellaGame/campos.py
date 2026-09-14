"""Definición de campos y validación de tipos de dato.

Este módulo concentra la parte de "verificar que en los campos donde deban
almacenar números solo se puedan almacenar este tipo de dato". Cada entidad
declara una lista de objetos Campo y toda conversión entre el texto
que escribe el usuario (o el texto guardado en el archivo .csv) y el valor
de Python correspondiente pasa por aquí.

Tipos soportados:

texto - Cadena de caracteres no vacía (salvo que el campo sea opcional).
entero - Número entero, opcionalmente acotado por minimo y maximo.
decimal - Número con punto decimal, opcionalmente acotado.
fecha - Fecha en formato ISO AAAA-MM-DD (el que produce <input type="date">).
opcion - Cadena que debe pertenecer al conjunto opciones.
correo - Cadena con formato de correo electrónico.
telefono - Cadena de exactamente 10 dígitos.
llave - Entero que referencia la llave primaria de otra entidad (llave foránea).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime

# expresiones regulares para campos complejos
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
PATRON_TELEFONO = re.compile(r"^\d{10}$")


class ErrorDeValidacion(Exception):
    """Se lanza cuando un valor capturado no respeta el tipo de dato del campo.

    mensaje: descripción del problema, redactada para el usuario final.
    campo: nombre del campo que provocó el error, si se conoce.
    """
    def __init__(self, mensaje: str, campo: str = ""):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campo = campo


@dataclass(frozen=True)
class Campo:
    """Descripción de un atributo de una entidad.

    nombre: nombre de la columna en el archivo .csv.
    etiqueta: texto que se muestra en el formulario.
    tipo: uno de los tipos soportados por el módulo.
    obligatorio: si False se acepta la cadena vacía.
    opciones: valores permitidos cuando el tipo es opcion.
    minimo: cota inferior para entero y decimal.
    maximo: cota superior para entero y decimal.
    referencia: clave de la entidad referenciada cuando el tipo es llave.
    automatico: si True el valor lo genera el almacén y no se pide al usuario.
    ayuda: texto breve que se muestra debajo del control del formulario.
    """

    nombre: str
    etiqueta: str
    tipo: str = "texto"
    obligatorio: bool = True
    opciones: tuple[str, ...] = ()
    minimo: float | None = None
    maximo: float | None = None
    referencia: str = ""
    automatico: bool = False
    ayuda: str = ""


    # texto a valor
    def convertir(self, crudo: str | None):
        """Convierte el texto crudo al tipo de dato del campo.

        crudo: texto capturado en el formulario o leído del .csv.
        Devuleve el valor ya convertido, o None si el campo es opcional y el
        texto viene vacío.

        ErrorDeValidacion: si el texto no corresponde al tipo del campo.
        """
        texto = (crudo or "").strip()

        if not texto:
            if self.obligatorio:
                raise ErrorDeValidacion(
                    f"El campo <{self.etiqueta}> es obligatorio.", self.nombre
                )
            return None

        if self.tipo in ("entero", "llave"):
            return self._convertir_entero(texto)
        if self.tipo == "decimal":
            return self._convertir_decimal(texto)
        if self.tipo == "fecha":
            return self._convertir_fecha(texto)
        if self.tipo == "opcion":
            if texto not in self.opciones:
                permitidas = ", ".join(self.opciones)
                raise ErrorDeValidacion(
                    f"<{self.etiqueta}> solo acepta: {permitidas}.", self.nombre
                )
            return texto
        if self.tipo == "correo":
            if not PATRON_CORREO.match(texto):
                raise ErrorDeValidacion(
                    f"<{self.etiqueta}> debe tener el formato usuario@dominio.com.",
                    self.nombre,
                )
            return texto
        if self.tipo == "telefono":
            compacto = re.sub(r"[\s\-()]", "", texto)
            if not PATRON_TELEFONO.match(compacto):
                raise ErrorDeValidacion(
                    f"<{self.etiqueta}> debe contener exactamente 10 dígitos.",
                    self.nombre,
                )
            return compacto
        return texto

    def _convertir_entero(self, texto: str) -> int:
        """Convierte a int verificando que no haya caracteres no numéricos."""
        try:
            valor = int(texto)
        except ValueError:
            raise ErrorDeValidacion(
                f"<{self.etiqueta}> debe ser un número entero; se recibió <{texto}>.",
                self.nombre,
            ) from None
        self._verificar_rango(valor)
        return valor

    def _convertir_decimal(self, texto: str) -> float:
        """Convierte a float aceptando coma o punto decimal."""
        try:
            valor = float(texto.replace(",", "."))
        except ValueError:
            raise ErrorDeValidacion(
                f"<{self.etiqueta}> debe ser un número; se recibió <{texto}>.",
                self.nombre,
            ) from None
        self._verificar_rango(valor)
        return valor

    def _convertir_fecha(self, texto: str) -> date:
        """Convierte una cadena AAAA-MM-DD en datetime.date."""
        try:
            return datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            raise ErrorDeValidacion(
                f"<{self.etiqueta}> debe tener el formato AAAA-MM-DD.", self.nombre
            ) from None

    def _verificar_rango(self, valor: float) -> None:
        """Verifica las cotas minimo y maximo del campo numérico."""
        if self.minimo is not None and valor < self.minimo:
            raise ErrorDeValidacion(
                f"<{self.etiqueta}> no puede ser menor que {self.minimo:g}.",
                self.nombre,
            )
        if self.maximo is not None and valor > self.maximo:
            raise ErrorDeValidacion(
                f"<{self.etiqueta}> no puede ser mayor que {self.maximo:g}.",
                self.nombre,
            )

    # valor a texto
    def a_texto(self, valor) -> str:
        """Representa valor como se guarda en el archivo .csv."""
        if valor is None:
            return ""
        if self.tipo == "fecha":
            return valor.isoformat()
        if self.tipo == "decimal":
            return f"{float(valor):.2f}"
        return str(valor)

    def a_visual(self, valor) -> str:
        """Representa valor como se muestra en la interfaz web."""
        if valor is None or valor == "":
            return "—"
        if self.tipo == "fecha":
            return valor.strftime("%d/%m/%Y")
        if self.tipo == "decimal":
            return f"${float(valor):,.2f}"
        return str(valor)

    def valor_para_formulario(self, valor) -> str:
        """Representa valor como debe aparecer dentro de un control HTML."""
        return self.a_texto(valor)

    @property
    def control_html(self) -> str:
        """Tipo de control HTML que corresponde al campo."""
        if self.tipo in ("opcion", "llave"):
            return "select"
        if self.tipo == "fecha":
            return "date"
        if self.tipo in ("entero", "decimal"):
            return "number"
        if self.tipo == "correo":
            return "email"
        return "text"

    @property
    def paso_html(self) -> str:
        """Atributo step para los controles numéricos."""
        return "0.01" if self.tipo == "decimal" else "1"
