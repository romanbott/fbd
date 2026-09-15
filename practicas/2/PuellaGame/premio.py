"""Entidad Premio.

Catálogo de premios que el centro puede entregar a cambio de puntos. De cada
premio se guarda su nombre, su categoría, el rango de edad al que está
dirigido, su valor aproximado y los puntos necesarios para canjearlo. La
cantidad disponible no vive aquí sino en inventario.csv, porque depende de
la sucursal. Archivo asociado: premio.csv.
"""

from __future__ import annotations

from campos import Campo
from entidad import Entidad

CATEGORIAS = ("Bajo", "Medio", "Grande")
RANGOS_DE_EDAD = ("Infantil", "Juvenil", "Adulto")


class Premio(Entidad):
    """Premio del catálogo de PuellaGame."""

    CLAVE = "premios"
    ETIQUETA = "Premio"
    ETIQUETA_PLURAL = "Premios"
    ARCHIVO = "premio.csv"
    LLAVE = "idPremio"
    DESCRIPCION = "Catálogo de premios con su categoría, valor y puntos."

    CAMPOS = [
        Campo("idPremio", "Id de premio", "entero", automatico=True),
        Campo("nombre", "Nombre"),
        Campo(
            "categoria",
            "Categoría",
            "opcion",
            opciones=CATEGORIAS,
            ayuda="Bajo: 20 a 1,000 puntos - Medio: 1,001 a 3,999 - Grande: 4,000 o más.",
        ),
        Campo(
            "rangoEdad",
            "Rango de edad",
            "opcion",
            opciones=RANGOS_DE_EDAD,
            ayuda="Infantil: 3 a 12 años · Juvenil: 13 a 17 · Adulto: 18 o más.",
        ),
        Campo("valorAprox", "Valor aproximado (MXN)", "decimal", minimo=0),
        Campo("puntosNecesarios", "Puntos necesarios", "entero", minimo=0),
    ]

    @classmethod
    def describir(cls, registro: dict) -> str:
        """Muestra el premio como <nombre — categoría>."""
        return f"{registro['nombre']} — {registro['categoria']}"

    @classmethod
    def relacionados(cls, registro: dict) -> list[dict]:
        """Devuelve las sucursales que tienen existencias de este premio."""
        from inventario import Inventario
        from sucursal import Sucursal

        existencias = Inventario.almacen().buscar(idPremio=registro[cls.LLAVE])
        sucursales = {s[Sucursal.LLAVE]: s for s in Sucursal.listar()}
        filas = []
        for existencia in existencias:
            sucursal = sucursales.get(existencia["idSucursal"], {})
            filas.append(
                [
                    str(existencia["idInventario"]),
                    sucursal.get("nombre", "—"),
                    sucursal.get("colonia", "—"),
                    sucursal.get("estado", "—"),
                    str(existencia["cantidadDisponible"]),
                ]
            )
        return [
            {
                "titulo": "Disponibilidad por sucursal",
                "encabezados": [
                    "Id de inventario",
                    "Sucursal",
                    "Colonia",
                    "Estado",
                    "Cantidad disponible",
                ],
                "filas": filas,
            }
        ]
