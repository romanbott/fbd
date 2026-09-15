# PuellaGame — prototipo sobre archivos CSV

Aplicación web (Python + FastAPI) que captura y consulta la información de
**sucursales, premios y clientes** del caso de uso, guardándola en archivos
`.csv`. Es una implementación parcial: se omite todo lo que no cuelga de esas
tres entidades (tarjetas, recargas, partidas, canjes, juegos, máquinas y
empleados).

## Cómo ejecutarlo

```bash
docker build -t puella .
docker run -p 8000:8000 -v "$PWD/store:/store:Z" puella
```

Y abrir <http://127.0.0.1:8000>.

## Dónde viven los `.csv`

Los datos se guardan en un directorio separado del código:

- **`store/`** — datos en tiempo de ejecución. Es donde el prototipo lee y
  escribe. Al arrancar, si un `.csv` no existe aquí, se copia desde el
  directorio de defecto; los archivos que ya existan **nunca** se sobreescriben.
- **`default_store/`** — los `.csv` de ejemplo que sirven de semilla.

Las rutas se configuran con las variables de entorno `STORE_DIR` y
`DEFAULT_STORE_DIR`. En el contenedor son `/store` y `/default_store`; sin
Docker se usan `store/` y `default_store/` dentro del repositorio.

Esto permite persistir los datos montando `store/`:

```bash
# Con un directorio del host (si está vacío se siembra desde default_store)
docker run -p 8000:8000 -v "$PWD/mis_datos:/store" puella

# Con un volumen con nombre
docker run -p 8000:8000 -v puella_datos:/store puella
```

El contenedor corre como `root` para que los bind mounts funcionen sin ajustar
permisos. Con Podman rootless, un usuario no-root necesitaría `--userns=keep-id`.

## Estructura

Un módulo por clase, cada uno con su archivo `.csv` del mismo nombre (los de
ejemplo están en `default_store/`, los de trabajo en `store/`):

| Módulo                 | Archivo                  | Contenido                                        |
| ---------------------- | ------------------------ | ------------------------------------------------ |
| `sucursal.py`          | `sucursal.csv`           | Sucursal con su dirección desglosada             |
| `premio.py`            | `premio.csv`             | Catálogo de premios                              |
| `cliente.py`           | `cliente.csv`            | Datos personales del jugador                     |
| `correo_cliente.py`    | `correo_cliente.csv`     | Correos del cliente (atributo multivaluado)      |
| `telefono_cliente.py`  | `telefono_cliente.csv`   | Teléfonos del cliente (atributo multivaluado)    |
| `inventario.py`        | `inventario.csv`         | Existencias de un premio en una sucursal         |

Módulos de apoyo:

- `campos.py` — define el tipo de dato de cada columna y valida lo que captura
  el usuario (`ErrorDeValidacion`).
- `almacen.py` — lee y escribe los `.csv`: listar, obtener, buscar, agregar,
  actualizar, eliminar y generar la llave primaria.
- `entidad.py` — clase base con el comportamiento común a todas las entidades.
- `catalogo.py` — registro de entidades; la aplicación las resuelve por la
  clave que viene en la URL.
- `app.py` — rutas de FastAPI y manejo de excepciones.
- `templates/`, `static/` — formularios HTML y hoja de estilo.

## Decisiones sobre los `.csv`

- Cada entidad tiene su propio archivo, con encabezados en la primera línea y
  una llave primaria entera (`idSucursal`, `idPremio`, …) que genera el
  almacén. Así el contenido se puede volcar tal cual a las tablas de la base de
  datos más adelante.
- Los atributos **multivaluados** del cliente (correos y teléfonos) no caben en
  una columna, así que viven en su propio archivo con una llave foránea
  `idCliente`, que es como quedarán en el modelo relacional. El alta de un
  cliente pide al menos un correo y un teléfono (con un botón para agregar más
  y, en el caso del teléfono, su tipo); el formulario valida **todo** antes de
  escribir y luego reparte cada valor en su archivo correspondiente.
- El atributo **compuesto** `Direccion` de la sucursal se guarda desglosado en
  columnas (`calle`, `numExterior`, `numInterior`, `colonia`, `estado`).
- `Inventario` es la relación entre sucursal y premio: la cantidad disponible
  depende de las dos, por eso no es columna de `premio.csv`.
- La escritura se hace sobre un archivo temporal que después reemplaza al
  original, para que una interrupción no deje el `.csv` a medias.

## Validación y errores

- Toda captura pasa por `Campo.convertir`, que revisa el tipo: enteros y
  decimales rechazan cualquier carácter no numérico, las fechas exigen formato
  `AAAA-MM-DD`, los teléfonos diez dígitos, los correos `usuario@dominio`, y
  los campos de opción solo aceptan los valores del caso de uso.
- Las llaves foráneas se capturan en un `<select>` y además se verifica que el
  registro referido exista.
- No se puede eliminar un registro al que otro apunta; la aplicación lo avisa
  en vez de dejar referencias rotas.
- Los errores de validación se muestran dentro del mismo formulario, sin perder
  lo ya capturado; los de lectura o escritura y cualquier falla inesperada caen
  en una página de error con su mensaje.
