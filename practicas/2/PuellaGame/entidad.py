"""Clase base de la que heredan todas las entidades del prototipo.

Una entidad se describe con cuatro cosas: el archivo .csv donde vive, la
lista de campos que la componen, cuál de esos campos es su llave primaria y
cómo se muestra un registro suyo en una lista. Todo lo demás: altas, bajas,
cambios, consultas y validación lo hereda de aquí.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from almacen import Almacen, ErrorDeDependencia
from campos import Campo, ErrorDeValidacion

RAIZ = Path(__file__).resolve().parent

#: Directorio donde el prototipo guarda y lee los .csv en tiempo de ejecución.
DIRECTORIO_ALMACEN = Path(os.environ.get("STORE_DIR") or RAIZ / "store")

#: Directorio con los .csv de ejemplo que sirven de semilla.
DIRECTORIO_DEFECTO = Path(
    os.environ.get("DEFAULT_STORE_DIR") or RAIZ / "default_store"
)


def preparar_almacen() -> None:
    """Deja listo el directorio de datos, sembrándolo si hace falta.

    Crea el directorio del almacén y, para cada ``.csv`` del directorio de
    defecto, copia los que todavía no existan. Nunca sobreescribe archivos: si
    el usuario monta un directorio con sus propios datos, esos se respetan.
    """
    DIRECTORIO_ALMACEN.mkdir(parents=True, exist_ok=True)
    if not DIRECTORIO_DEFECTO.is_dir():
        return
    for origen in DIRECTORIO_DEFECTO.glob("*.csv"):
        destino = DIRECTORIO_ALMACEN / origen.name
        if not destino.exists():
            shutil.copy2(origen, destino)


class Entidad:
    """Comportamiento común a Sucursal, Premio, Cliente y sus relaciones."""

    CLAVE: str = ""
    ETIQUETA: str = ""
    ETIQUETA_PLURAL: str = ""
    ARCHIVO: str = ""
    LLAVE: str = ""
    CAMPOS: list[Campo] = []
    DESCRIPCION: str = ""

    _almacen: Almacen | None = None

    # acceso
    @classmethod
    def almacen(cls) -> Almacen:
        """Devuelve (creándolo la primera vez) el almacén de la entidad."""
        if cls.__dict__.get("_almacen") is None:
            cls._almacen = Almacen(
                DIRECTORIO_ALMACEN / cls.ARCHIVO, cls.CAMPOS, cls.LLAVE
            )
        return cls._almacen

    @classmethod
    def campos_editables(cls) -> list[Campo]:
        """Campos que se capturan en el formulario (todos menos la llave)."""
        return [campo for campo in cls.CAMPOS if not campo.automatico]

    @classmethod
    def campo_llave(cls) -> Campo:
        """Campo que corresponde a la llave primaria."""
        return cls.almacen().campo(cls.LLAVE)

    # operaciones
    @classmethod
    def convertir(cls, formulario: dict) -> dict:
        """Convierte y valida los datos crudos de un formulario.

        formulario: diccionario nombre_del_campo -> texto.
        Devuelve un diccionario con los valores ya convertidos a su tipo.

        ErrorDeValidacion: ante el primer campo con tipo inválido.
        """
        datos = {
            campo.nombre: campo.convertir(formulario.get(campo.nombre))
            for campo in cls.campos_editables()
        }
        cls.validar(datos)
        return datos

    @classmethod
    def validar(cls, datos: dict) -> None:
        """Verifica las referencias a otras entidades (llaves foráneas).

        ErrorDeValidacion: si la llave foránea capturada no existe.
        """
        from catalogo import entidad_por_clave  # importación tardía: evita ciclos

        for campo in cls.campos_editables():
            if campo.tipo != "llave" or datos.get(campo.nombre) is None:
                continue
            referida = entidad_por_clave(campo.referencia)
            if not referida.almacen().existe(datos[campo.nombre]):
                raise ErrorDeValidacion(
                    f"No existe {referida.ETIQUETA.lower()} con "
                    f"{referida.LLAVE} = {datos[campo.nombre]}.",
                    campo.nombre,
                )

    @classmethod
    def listar(cls) -> list[dict]:
        """Devuelve todos los registros de la entidad."""
        return cls.almacen().listar()

    @classmethod
    def obtener(cls, llave: int) -> dict:
        """Devuelve el registro con la llave primaria llave."""
        return cls.almacen().obtener(llave)

    @classmethod
    def agregar(cls, formulario: dict) -> dict:
        """Da de alta un registro a partir de los datos de un formulario."""
        return cls.almacen().agregar(cls.convertir(formulario))

    @classmethod
    def editar(cls, llave: int, formulario: dict) -> dict:
        """Actualiza el registro llave con los datos de un formulario."""
        return cls.almacen().actualizar(llave, cls.convertir(formulario))

    @classmethod
    def eliminar(cls, llave: int) -> dict:
        """Elimina el registro llave.

        Antes de borrar se revisa que ninguna otra entidad lo referencie, para
        no dejar llaves foráneas apuntando a un registro inexistente.
        """
        cls.verificar_sin_dependencias(llave)
        return cls.almacen().eliminar(llave)

    @classmethod
    def verificar_sin_dependencias(cls, llave: int) -> None:
        """Revisa que ninguna entidad apunte al registro llave.

        ErrorDeDependencia: si alguna otra entidad lo referencia.
        """
        from catalogo import ENTIDADES

        for otra in ENTIDADES:
            for campo in otra.campos_editables():
                if campo.tipo == "llave" and campo.referencia == cls.CLAVE:
                    dependientes = otra.almacen().buscar(**{campo.nombre: llave})
                    if dependientes:
                        raise ErrorDeDependencia(
                            f"No se puede eliminar: {len(dependientes)} registro(s) "
                            f"de {otra.ETIQUETA_PLURAL.lower()} hacen referencia a "
                            f"este registro. Elimínalos primero."
                        )

    # presentación
    @classmethod
    def describir(cls, registro: dict) -> str:
        """Texto corto que identifica a un registro en listas y menús."""
        return f"{registro[cls.LLAVE]}"

    @classmethod
    def campos_visor(cls) -> list[Campo]:
        """Campos que se muestran en listas y fichas.

        Por defecto son los mismos que se almacenan. Las entidades que además
        quieran mostrar valores derivados (no guardados) pueden sobrescribirlo.
        """
        return list(cls.CAMPOS)

    @classmethod
    def valor_visor(cls, campo: Campo, registro: dict):
        """Valor que se muestra para un campo de ``campos_visor``.

        Por defecto es el valor guardado. Las entidades con valores derivados
        sobrescriben esto para calcularlos a partir del registro.
        """
        return registro.get(campo.nombre)

    @classmethod
    def grupos_formulario(cls) -> list[dict]:
        """Grupos de campos repetibles que se capturan junto con la entidad.

        Cada grupo es un diccionario con ``etiqueta``, ``ayuda`` opcional y
        ``campos`` (lista de :class:`campos.Campo`). La implementación
        predeterminada no captura nada y las entidades con atributos
        multivaluados la sobrescriben.
        """
        return []

    @classmethod
    def opciones_llave(cls) -> list[tuple[str, str]]:
        """Pares (llave, descripción) para llenar un <select>."""
        return [
            (str(registro[cls.LLAVE]), cls.describir(registro))
            for registro in cls.listar()
        ]

    @classmethod
    def relacionados(cls, registro: dict) -> list[dict]:
        """Bloques de datos relacionados que acompañan a la consulta.

        Cada bloque es un diccionario con las llaves titulo,
        encabezados y filas. La implementación predeterminada no
        devuelve nada, las entidades que sí tienen relaciones la sobrescriben.
        """
        return []

    @classmethod
    def bloque(cls, titulo: str, entidad: type["Entidad"], registros: list[dict],
               omitir: tuple[str, ...] = ()) -> dict:
        """Arma un bloque de datos relacionados a partir de registros.

        titulo: encabezado del bloque.
        entidad: entidad a la que pertenecen los registros.
        registros: registros que se van a mostrar.
        omitir: campos que no se muestran (normalmente la llave foránea que ya
        se conoce por el contexto).
        """
        campos = [campo for campo in entidad.CAMPOS if campo.nombre not in omitir]
        return {
            "titulo": titulo,
            "encabezados": [campo.etiqueta for campo in campos],
            "filas": [
                [campo.a_visual(registro.get(campo.nombre)) for campo in campos]
                for registro in registros
            ],
        }
