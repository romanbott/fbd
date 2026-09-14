"""Atributo multivaluado: correos electrónicos de un cliente.

Un cliente puede tener varios correos, así que no caben en una sola columna de
cliente.csv. Se guardan en correo_cliente.csv, donde cada renglón es un correo
que apunta a su cliente mediante idCliente.
"""

from __future__ import annotations

from campos import Campo
from entidad import Entidad


class CorreoCliente(Entidad):
    """Correo electrónico perteneciente a un cliente."""

    CLAVE = "correos"
    ETIQUETA = "Correo de cliente"
    ETIQUETA_PLURAL = "Correos de clientes"
    ARCHIVO = "correo_cliente.csv"
    LLAVE = "idCorreo"
    DESCRIPCION = "Correos electrónicos de cada cliente (multivaluado)."

    CAMPOS = [
        Campo("idCorreo", "Id de correo", "entero", automatico=True),
        Campo("idCliente", "Cliente", "llave", referencia="clientes"),
        Campo("correo", "Correo electrónico", "correo"),
    ]

    @classmethod
    def describir(cls, registro: dict) -> str:
        """Muestra el correo tal cual."""
        return registro["correo"]

    @classmethod
    def relacionados(cls, registro: dict) -> list[dict]:
        """Devuelve los datos del cliente dueño del correo."""
        from cliente import Cliente

        return [
            cls.bloque(
                "Cliente al que pertenece",
                Cliente,
                [Cliente.obtener(registro["idCliente"])],
            )
        ]
