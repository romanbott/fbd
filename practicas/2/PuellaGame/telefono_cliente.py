"""Atributo multivaluado: teléfonos de un cliente.

Mismo caso que los correos: un cliente puede tener varios teléfonos, así que
cada uno ocupa un renglón de telefono_cliente.csv y apunta a su cliente
mediante idCliente.
"""

from __future__ import annotations

from campos import Campo
from entidad import Entidad


class TelefonoCliente(Entidad):
    """Teléfono perteneciente a un cliente."""

    CLAVE = "telefonos"
    ETIQUETA = "Teléfono de cliente"
    ETIQUETA_PLURAL = "Teléfonos de clientes"
    ARCHIVO = "telefono_cliente.csv"
    LLAVE = "idTelefono"
    DESCRIPCION = "Teléfonos de cada cliente (atributo multivaluado)."

    CAMPOS = [
        Campo("idTelefono", "Id de teléfono", "entero", automatico=True),
        Campo("idCliente", "Cliente", "llave", referencia="clientes"),
        Campo("telefono", "Teléfono", "telefono", ayuda="10 dígitos, sin espacios."),
        Campo(
            "tipo",
            "Tipo",
            "opcion",
            opciones=("Celular", "Casa", "Trabajo"),
        ),
    ]

    @classmethod
    def describir(cls, registro: dict) -> str:
        """Muestra el teléfono con su tipo."""
        return f"{registro['telefono']} ({registro['tipo'].lower()})"

    @classmethod
    def relacionados(cls, registro: dict) -> list[dict]:
        """Devuelve los datos del cliente dueño del teléfono."""
        from cliente import Cliente

        return [
            cls.bloque(
                "Cliente al que pertenece",
                Cliente,
                [Cliente.obtener(registro["idCliente"])],
            )
        ]
