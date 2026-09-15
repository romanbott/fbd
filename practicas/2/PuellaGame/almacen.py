"""Manejo de archivos csv (persistencia de datos)

Cada entidad del prototipo tiene un archivo .csv propio que hace las veces de
tabla: la primera línea contiene los encabezados y cada línea siguiente es un
registro. La clase Almacen ofrece sobre ese archivo las cuatro operaciones que
pide la práctica agregar, consultar, editar y eliminar junto con la generación
de la llave primaria.
"""

from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path

from campos import Campo, ErrorDeValidacion


class ErrorDeAlmacen(Exception):
    """Error al leer o escribir el archivo ``.csv`` de una entidad."""


class RegistroNoEncontrado(ErrorDeAlmacen):
    """No existe un registro con la llave solicitada."""


class ErrorDeDependencia(ErrorDeAlmacen):
    """Otro registro hace referencia al que se intenta eliminar."""


class Almacen:
    """Lee y escribe los registros de una entidad en un archivo .csv.

    archivo: ruta del archivo .csv que respalda a la entidad.
    campos: lista de campos.Campo que describe las columnas.
    llave: nombre del campo que funciona como llave primaria.
    """

    def __init__(self, archivo: Path, campos: list[Campo], llave: str):
        self.archivo = Path(archivo)
        self.campos = list(campos)
        self.llave = llave
        self._por_nombre = {campo.nombre: campo for campo in self.campos}

    @property
    def encabezados(self) -> list[str]:
        """Nombres de las columnas, en el orden en que se escriben."""
        return [campo.nombre for campo in self.campos]

    def campo(self, nombre: str) -> Campo:
        """Devuelve el campos.Campo llamado nombre.

        ErrorDeAlmacen: si la entidad no declara ese campo.
        """
        try:
            return self._por_nombre[nombre]
        except KeyError:
            raise ErrorDeAlmacen(
                f"El campo <{nombre}> no pertenece a {self.archivo.name}."
            ) from None

    def _asegurar_archivo(self) -> None:
        """Crea el archivo con sus encabezados si todavía no existe."""
        if self.archivo.exists():
            return
        try:
            self.archivo.parent.mkdir(parents=True, exist_ok=True)
            with self.archivo.open("w", newline="", encoding="utf-8") as destino:
                csv.writer(destino).writerow(self.encabezados)
        except OSError as error:
            raise ErrorDeAlmacen(
                f"No se pudo crear el archivo {self.archivo.name}: {error}"
            ) from error

    def _escribir(self, registros: list[dict]) -> None:
        """Reescribe el archivo completo con registros.

        La escritura se hace primero en un archivo temporal y después se
        reemplaza el original, de modo que una interrupción a media escritura
        no deje el .csv truncado.
        """
        self._asegurar_archivo()
        try:
            descriptor, ruta_temporal = tempfile.mkstemp(
                dir=str(self.archivo.parent), suffix=".tmp"
            )
            with os.fdopen(descriptor, "w", newline="", encoding="utf-8") as destino:
                escritor = csv.DictWriter(destino, fieldnames=self.encabezados)
                escritor.writeheader()
                for registro in registros:
                    escritor.writerow(
                        {
                            campo.nombre: campo.a_texto(registro.get(campo.nombre))
                            for campo in self.campos
                        }
                    )
            os.replace(ruta_temporal, self.archivo)
        except OSError as error:
            raise ErrorDeAlmacen(
                f"No se pudo guardar en {self.archivo.name}: {error}"
            ) from error

    def _convertir_fila(self, fila: dict, numero: int) -> dict:
        """Convierte una fila de texto del .csv a valores de Python.

        fila: diccionario tal como lo entrega csv.DictReader.
        numero: número de línea, usado en el mensaje de error.

        ErrorDeAlmacen: si el archivo contiene un dato con tipo inválido.
        """
        registro = {}
        for campo in self.campos:
            try:
                registro[campo.nombre] = campo.convertir(fila.get(campo.nombre))
            except ErrorDeValidacion as error:
                raise ErrorDeAlmacen(
                    f"{self.archivo.name}, línea {numero}: {error.mensaje}"
                ) from error
        return registro

    def listar(self) -> list[dict]:
        """Devuelve todos los registros del archivo, ordenados por llave.

        ErrorDeAlmacen: si el archivo no se puede leer o está corrupto.
        """
        self._asegurar_archivo()
        try:
            with self.archivo.open(newline="", encoding="utf-8") as origen:
                lector = csv.DictReader(origen)
                if lector.fieldnames is None:
                    return []
                faltantes = set(self.encabezados) - set(lector.fieldnames)
                if faltantes:
                    raise ErrorDeAlmacen(
                        f"A {self.archivo.name} le faltan las columnas: "
                        + ", ".join(sorted(faltantes))
                    )
                registros = [
                    self._convertir_fila(fila, numero)
                    for numero, fila in enumerate(lector, start=2)
                ]
        except OSError as error:
            raise ErrorDeAlmacen(
                f"No se pudo leer {self.archivo.name}: {error}"
            ) from error
        registros.sort(key=lambda registro: registro[self.llave])
        return registros

    def obtener(self, llave: int) -> dict:
        """Devuelve el registro cuya llave primaria es llave.

        RegistroNoEncontrado: si ningún registro tiene esa llave.
        """
        for registro in self.listar():
            if registro[self.llave] == llave:
                return registro
        raise RegistroNoEncontrado(
            f"No existe un registro con {self.llave} = {llave} en "
            f"{self.archivo.name}."
        )

    def existe(self, llave: int) -> bool:
        """Indica si hay un registro con la llave primaria llave."""
        try:
            self.obtener(llave)
        except RegistroNoEncontrado:
            return False
        return True

    def buscar(self, **criterios) -> list[dict]:
        """Devuelve los registros que coinciden con todos los criterios.

        Se usa para recuperar los datos relacionados de una entidad, por
        ejemplo los teléfonos de un cliente::

            almacen.buscar(idCliente=3)
        """
        return [
            registro
            for registro in self.listar()
            if all(registro.get(nombre) == valor for nombre, valor in criterios.items())
        ]

    def siguiente_llave(self) -> int:
        """Calcula la siguiente llave primaria disponible."""
        registros = self.listar()
        if not registros:
            return 1
        return max(registro[self.llave] for registro in registros) + 1

    def agregar(self, datos: dict) -> dict:
        """Agrega un registro nuevo y le asigna su llave primaria.

        datos: valores ya convertidos, sin la llave primaria.
        Devuelve el registro guardado, incluyendo la llave generada.
        """
        registros = self.listar()
        registro = dict(datos)
        registro[self.llave] = self.siguiente_llave()
        registros.append(registro)
        self._escribir(registros)
        return registro

    def actualizar(self, llave: int, datos: dict) -> dict:
        """Reemplaza los datos del registro identificado por llave.

        RegistroNoEncontrado: si ningún registro tiene esa llave.
        """
        registros = self.listar()
        for indice, registro in enumerate(registros):
            if registro[self.llave] == llave:
                actualizado = dict(datos)
                actualizado[self.llave] = llave
                registros[indice] = actualizado
                self._escribir(registros)
                return actualizado
        raise RegistroNoEncontrado(
            f"No se puede editar: no existe {self.llave} = {llave} en "
            f"{self.archivo.name}."
        )

    def eliminar(self, llave: int) -> dict:
        """Elimina el registro identificado por llave y lo devuelve.

        RegistroNoEncontrado: si ningún registro tiene esa llave.
        """
        registros = self.listar()
        for indice, registro in enumerate(registros):
            if registro[self.llave] == llave:
                eliminado = registros.pop(indice)
                self._escribir(registros)
                return eliminado
        raise RegistroNoEncontrado(
            f"No se puede eliminar: no existe {self.llave} = {llave} en "
            f"{self.archivo.name}."
        )
