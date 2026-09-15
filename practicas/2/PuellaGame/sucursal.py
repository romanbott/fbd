"""Entidad Sucursal.

Un centro *PuellaGame* está formado por varias sucursales. De cada una se
guarda su nombre, su dirección completa (atributo compuesto: calle, número
interior, número exterior, colonia y estado), su teléfono y su horario de
atención. Archivo asociado: sucursal.csv.
"""

from __future__ import annotations

from campos import Campo
from entidad import Entidad


class Sucursal(Entidad):
    """Sucursal del centro de entretenimiento familiar PuellaGame."""

    CLAVE = "sucursales"
    ETIQUETA = "Sucursal"
    ETIQUETA_PLURAL = "Sucursales"
    ARCHIVO = "sucursal.csv"
    LLAVE = "idSucursal"
    DESCRIPCION = "Nombre, dirección, teléfono y horario de cada sucursal."

    CAMPOS = [
        Campo("idSucursal", "Id de sucursal", "entero", automatico=True),
        Campo("nombre", "Nombre"),
        Campo("calle", "Calle"),
        Campo("numExterior", "Número exterior", "entero", minimo=0),
        Campo(
            "numInterior",
            "Número interior",
            "texto",
            obligatorio=False,
            ayuda="Déjalo vacío si la sucursal no tiene número interior.",
        ),
        Campo("colonia", "Colonia"),
        Campo("estado", "Estado"),
        Campo("telefono", "Teléfono", "telefono", ayuda="10 dígitos, sin espacios."),
        Campo(
            "horario",
            "Horario",
            "texto",
            ayuda="Por ejemplo: Lunes a domingo de 11:00 a 21:00.",
        ),
    ]

    @classmethod
    def describir(cls, registro: dict) -> str:
        """Muestra la sucursal como <nombre (colonia)>."""
        return f"{registro['nombre']} ({registro['colonia']})"

    @classmethod
    def direccion(cls, registro: dict) -> str:
        """Arma la dirección completa en una sola línea."""
        interior = registro.get("numInterior")
        interior = f", int. {interior}" if interior else ""
        return (
            f"{registro['calle']} {registro['numExterior']}{interior}, "
            f"{registro['colonia']}, {registro['estado']}"
        )

    @classmethod
    def relacionados(cls, registro: dict) -> list[dict]:
        """Devuelve el inventario de premios que tiene la sucursal."""
        from inventario import Inventario
        from premio import Premio

        existencias = Inventario.almacen().buscar(idSucursal=registro[cls.LLAVE])
        premios = {p[Premio.LLAVE]: p for p in Premio.listar()}
        filas = []
        for existencia in existencias:
            premio = premios.get(existencia["idPremio"], {})
            filas.append(
                [
                    str(existencia["idInventario"]),
                    premio.get("nombre", "—"),
                    premio.get("categoria", "—"),
                    premio.get("rangoEdad", "—"),
                    str(premio.get("puntosNecesarios", "—")),
                    str(existencia["cantidadDisponible"]),
                ]
            )
        return [
            {
                "titulo": "Inventario de premios en esta sucursal",
                "encabezados": [
                    "Id de inventario",
                    "Premio",
                    "Categoría",
                    "Rango de edad",
                    "Puntos necesarios",
                    "Cantidad disponible",
                ],
                "filas": filas,
            }
        ]
