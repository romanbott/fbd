"""Registro de las entidades que maneja el prototipo.

La aplicación web no conoce a las entidades una por una: las busca en este
catálogo a partir de la clave que viene en la URL. Para agregar una entidad
nueva basta con crear su módulo y añadirla a :data:`ENTIDADES`.
"""

from __future__ import annotations

from cliente import Cliente
from correo_cliente import CorreoCliente
from entidad import Entidad
from inventario import Inventario
from premio import Premio
from sucursal import Sucursal
from telefono_cliente import TelefonoCliente

# Entidades del prototipo
ENTIDADES: list[type[Entidad]] = [
    Sucursal,
    Premio,
    Cliente,
    CorreoCliente,
    TelefonoCliente,
    Inventario,
]

_POR_CLAVE = {entidad.CLAVE: entidad for entidad in ENTIDADES}


class EntidadDesconocida(Exception):
    """La clave solicitada no corresponde a ninguna entidad registrada."""


def entidad_por_clave(clave: str) -> type[Entidad]:
    """Devuelve la entidad registrada bajo ``clave``.

    EntidadDesconocida: si la clave no existe en el catálogo.
    """
    try:
        return _POR_CLAVE[clave]
    except KeyError:
        raise EntidadDesconocida(
            f"<{clave}> no corresponde a ninguna entidad del prototipo."
        ) from None
