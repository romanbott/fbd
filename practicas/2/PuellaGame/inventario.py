"""Entidad Inventario: relación entre Sucursal y Premio.

Cada sucursal tiene un inventario de premios y lo único que distingue a una
sucursal de otra respecto de un mismo premio es la cantidad disponible. Por eso
el inventario se guarda aparte, con una llave foránea a la sucursal y otra al
premio. Archivo asociado: ``inventario.csv``.
"""

from __future__ import annotations

from campos import Campo
from entidad import Entidad


class Inventario(Entidad):
    """Existencias de un premio en una sucursal."""

    CLAVE = "inventarios"
    ETIQUETA = "Inventario"
    ETIQUETA_PLURAL = "Inventarios"
    ARCHIVO = "inventario.csv"
    LLAVE = "idInventario"
    DESCRIPCION = "Cuántas piezas de cada premio hay en cada sucursal."

    CAMPOS = [
        Campo("idInventario", "Id de inventario", "entero", automatico=True),
        Campo("idSucursal", "Sucursal", "llave", referencia="sucursales"),
        Campo("idPremio", "Premio", "llave", referencia="premios"),
        Campo("cantidadDisponible", "Cantidad disponible", "entero", minimo=0),
    ]

    @classmethod
    def describir(cls, registro: dict) -> str:
        """Muestra el inventario como <premio en sucursal>."""
        from premio import Premio
        from sucursal import Sucursal

        try:
            premio = Premio.obtener(registro["idPremio"])["nombre"]
            sucursal = Sucursal.obtener(registro["idSucursal"])["nombre"]
        except Exception:  # el registro referido pudo borrarse a mano del .csv
            return f"Inventario #{registro[cls.LLAVE]}"
        return f"{premio} en {sucursal}"

    @classmethod
    def relacionados(cls, registro: dict) -> list[dict]:
        """Devuelve los datos completos de la sucursal y del premio."""
        from premio import Premio
        from sucursal import Sucursal

        return [
            cls.bloque(
                "Sucursal", Sucursal, [Sucursal.obtener(registro["idSucursal"])]
            ),
            cls.bloque("Premio", Premio, [Premio.obtener(registro["idPremio"])]),
        ]
