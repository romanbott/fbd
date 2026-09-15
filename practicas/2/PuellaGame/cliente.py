"""Entidad Cliente.

Cliente registrado del centro. Su nombre es un atributo compuesto (nombres,
apellido paterno y apellido materno) y tanto sus correos como sus teléfonos son
atributos multivaluados, por lo que viven en archivos aparte
(``correo_cliente.csv`` y ``telefono_cliente.csv``), igual que ocurriría en la
base de datos. Archivo asociado: ``cliente.csv``.
"""

from __future__ import annotations

from datetime import date

from campos import Campo, ErrorDeValidacion
from entidad import Entidad

#: Valores de sexo contemplados en el caso de uso.
SEXOS = ("Masculino", "Femenino", "No binario")


class Cliente(Entidad):
    """Cliente (jugador) de PuellaGame."""

    CLAVE = "clientes"
    ETIQUETA = "Cliente"
    ETIQUETA_PLURAL = "Clientes"
    ARCHIVO = "cliente.csv"
    LLAVE = "idCliente"
    DESCRIPCION = "Datos personales de los jugadores registrados."

    #: Campo de presentación: no se guarda, se calcula desde fechaNacimiento.
    EDAD = Campo("edad", "Edad", "entero")

    #: Campos de los atributos multivaluados que se capturan en el alta.
    CORREO = Campo("correo", "Correo electrónico", "correo")
    TELEFONO = Campo("telefono", "Teléfono", "telefono")
    TIPO_TELEFONO = Campo(
        "tipo", "Tipo", "opcion", opciones=("Celular", "Casa", "Trabajo")
    )

    CAMPOS = [
        Campo("idCliente", "Id de cliente", "entero", automatico=True),
        Campo("nombres", "Nombre(s)"),
        Campo("apellidoPaterno", "Apellido paterno"),
        Campo("apellidoMaterno", "Apellido materno", obligatorio=False),
        Campo("fechaNacimiento", "Fecha de nacimiento", "fecha"),
        Campo("sexo", "Sexo", "opcion", opciones=SEXOS),
        Campo(
            "esVIP",
            "Categoría VIP",
            "opcion",
            opciones=("Sí", "No"),
            ayuda="Se obtiene con 10 visitas en un mismo mes.",
        ),
    ]

    @classmethod
    def edad(cls, registro: dict) -> int | None:
        """Calcula los años cumplidos a partir de fechaNacimiento."""
        nacimiento = registro.get("fechaNacimiento")
        if nacimiento is None:
            return None
        hoy = date.today()
        return hoy.year - nacimiento.year - (
            (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day)
        )

    @classmethod
    def campos_visor(cls) -> list[Campo]:
        """Muestra la edad calculada justo después de la fecha de nacimiento."""
        campos: list[Campo] = []
        for campo in cls.CAMPOS:
            campos.append(campo)
            if campo.nombre == "fechaNacimiento":
                campos.append(cls.EDAD)
        return campos

    @classmethod
    def valor_visor(cls, campo: Campo, registro: dict):
        """Devuelve la edad calculada para el campo Edad."""
        if campo is cls.EDAD:
            return cls.edad(registro)
        return registro.get(campo.nombre)

    @classmethod
    def grupos_formulario(cls) -> list[dict]:
        """Correos y teléfonos que se capturan al dar de alta un cliente."""
        return [
            {
                "etiqueta": "Correos electrónicos",
                "ayuda": "Se requiere al menos uno.",
                "campos": [cls.CORREO],
            },
            {
                "etiqueta": "Teléfonos",
                "ayuda": "Se requiere al menos uno.",
                "campos": [cls.TELEFONO, cls.TIPO_TELEFONO],
            },
        ]

    @classmethod
    def _multivaluados(cls, formulario) -> tuple[list[str], list[tuple[str, str]]]:
        """Valida los correos y teléfonos capturados en el formulario.

        Devuelve los correos y los pares (teléfono, tipo) ya convertidos. No
        escribe nada: sirve para comprobar que la operación completa sea
        posible antes de tocar los ``.csv``.

        ErrorDeValidacion: si falta un correo o un teléfono, o si alguno no
        respeta su formato.
        """
        correos = [
            cls.CORREO.convertir(texto)
            for texto in formulario.getlist("correo")
            if texto.strip()
        ]
        numeros = formulario.getlist("telefono")
        tipos = formulario.getlist("tipo")
        telefonos = []
        for indice, numero in enumerate(numeros):
            if not numero.strip():
                continue
            tipo = tipos[indice] if indice < len(tipos) else ""
            telefonos.append(
                (cls.TELEFONO.convertir(numero), cls.TIPO_TELEFONO.convertir(tipo))
            )
        if not correos:
            raise ErrorDeValidacion("Debes indicar al menos un correo.", "correo")
        if not telefonos:
            raise ErrorDeValidacion(
                "Debes indicar al menos un teléfono.", "telefono"
            )
        return correos, telefonos

    @classmethod
    def agregar(cls, formulario) -> dict:
        """Da de alta un cliente junto con sus correos y teléfonos.

        Primero valida todo, incluidos los atributos multivaluados; solo si
        todo es válido escribe el cliente y sus registros relacionados. Así un
        correo mal formado no deja un cliente a medias.
        """
        from correo_cliente import CorreoCliente
        from telefono_cliente import TelefonoCliente

        datos = cls.convertir(formulario)
        correos, telefonos = cls._multivaluados(formulario)
        registro = cls.almacen().agregar(datos)
        llave = registro[cls.LLAVE]
        for correo in correos:
            CorreoCliente.almacen().agregar({"idCliente": llave, "correo": correo})
        for telefono, tipo in telefonos:
            TelefonoCliente.almacen().agregar(
                {"idCliente": llave, "telefono": telefono, "tipo": tipo}
            )
        return registro

    @classmethod
    def describir(cls, registro: dict) -> str:
        """Muestra al cliente con su nombre completo y su id."""
        return f"{cls.nombre_completo(registro)} (#{registro[cls.LLAVE]})"

    @classmethod
    def nombre_completo(cls, registro: dict) -> str:
        """Une nombres y apellidos en una sola cadena."""
        partes = [
            registro.get("nombres", ""),
            registro.get("apellidoPaterno", ""),
            registro.get("apellidoMaterno") or "",
        ]
        return " ".join(parte for parte in partes if parte).strip()

    @classmethod
    def relacionados(cls, registro: dict) -> list[dict]:
        """Devuelve los correos y los teléfonos del cliente."""
        from correo_cliente import CorreoCliente
        from telefono_cliente import TelefonoCliente

        llave = registro[cls.LLAVE]
        return [
            cls.bloque(
                "Correos electrónicos",
                CorreoCliente,
                CorreoCliente.almacen().buscar(idCliente=llave),
                omitir=("idCliente",),
            ),
            cls.bloque(
                "Teléfonos",
                TelefonoCliente,
                TelefonoCliente.almacen().buscar(idCliente=llave),
                omitir=("idCliente",),
            ),
        ]
