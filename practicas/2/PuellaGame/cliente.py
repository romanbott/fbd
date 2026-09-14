"""Entidad Cliente.

Cliente registrado del centro. Su nombre es un atributo compuesto (nombres,
apellido paterno y apellido materno) y tanto sus correos como sus teléfonos son
atributos multivaluados, por lo que viven en archivos aparte
(``correo_cliente.csv`` y ``telefono_cliente.csv``), igual que ocurriría en la
base de datos. Archivo asociado: ``cliente.csv``.
"""

from __future__ import annotations

from campos import Campo
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

    CAMPOS = [
        Campo("idCliente", "Id de cliente", "entero", automatico=True),
        Campo("nombres", "Nombre(s)"),
        Campo("apellidoPaterno", "Apellido paterno"),
        Campo("apellidoMaterno", "Apellido materno", obligatorio=False),
        Campo("fechaNacimiento", "Fecha de nacimiento", "fecha"),
        Campo("edad", "Edad", "entero", minimo=0, maximo=120),
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
