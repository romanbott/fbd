"""Aplicación web del prototipo de PuellaGame.

Interfaz sencilla basada en FastAPI para manejo de una "base de datos csv".

==========================================  ===================================
Ruta                                        Operación
==========================================  ===================================
GET  /                                  Menú principal
GET  /{entidad}                         Listar registros
GET  /{entidad}/nuevo                   Formulario de alta
POST /{entidad}/nuevo                   Agregar registro
GET  /{entidad}/consultar?llave=...     Consultar por llave primaria
GET  /{entidad}/{llave}                 Ver un registro
GET  /{entidad}/{llave}/editar          Formulario de edición
POST /{entidad}/{llave}/editar          Guardar cambios
POST /{entidad}/{llave}/eliminar        Eliminar registro
==========================================  ===================================
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from almacen import ErrorDeAlmacen, ErrorDeDependencia, RegistroNoEncontrado
from campos import Campo, ErrorDeValidacion
from catalogo import ENTIDADES, EntidadDesconocida, entidad_por_clave
from entidad import Entidad, preparar_almacen

DIRECTORIO = Path(__file__).resolve().parent


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    """Prepara el directorio de datos antes de atender peticiones."""
    preparar_almacen()
    yield


app = FastAPI(
    title="PuellaGame · prototipo sobre archivos CSV",
    description="Alta, consulta, edición y baja de sucursales, premios y clientes.",
    version="1.0",
    lifespan=ciclo_de_vida,
)
app.mount(
    "/static", StaticFiles(directory=DIRECTORIO / "static"), name="static"
)
templates = Jinja2Templates(directory=str(DIRECTORIO / "templates"))


def _controles(entidad: type[Entidad], valores: dict) -> list[dict]:
    """Prepara los datos que la plantilla necesita para dibujar un formulario.

    entidad: entidad cuyo formulario se va a dibujar.
    valores: valores actuales del formulario, como texto.
    Devuelve una lista de diccionarios con el campo, su valor y cuando
    corresponde, las opciones del <select>.
    """
    controles = []
    for campo in entidad.campos_editables():
        opciones: list[tuple[str, str]] = []
        if campo.tipo == "opcion":
            opciones = [(opcion, opcion) for opcion in campo.opciones]
        elif campo.tipo == "llave":
            opciones = entidad_por_clave(campo.referencia).opciones_llave()
        controles.append(
            {
                "campo": campo,
                "valor": valores.get(campo.nombre, ""),
                "opciones": opciones,
            }
        )
    return controles


def _valores_texto(entidad: type[Entidad], registro: dict) -> dict:
    """Convierte un registro a los textos que se colocan en el formulario."""
    return {
        campo.nombre: campo.valor_para_formulario(registro.get(campo.nombre))
        for campo in entidad.CAMPOS
    }


def _pagina(request: Request, plantilla: str, **contexto) -> HTMLResponse:
    """Renderiza una plantilla agregando el contexto común a todas las páginas."""
    contexto.setdefault("entidades", ENTIDADES)
    contexto.setdefault("aviso", request.query_params.get("aviso"))
    return templates.TemplateResponse(request, plantilla, contexto)


def _formulario(
    request: Request,
    entidad: type[Entidad],
    valores: dict,
    accion: str,
    titulo: str,
    error: str = "",
    campo_con_error: str = "",
    codigo: int = 200,
) -> HTMLResponse:
    """Dibuja el formulario de alta o de edición de una entidad."""
    respuesta = _pagina(
        request,
        "formulario.html",
        entidad=entidad,
        controles=_controles(entidad, valores),
        accion=accion,
        titulo=titulo,
        error=error,
        campo_con_error=campo_con_error,
    )
    respuesta.status_code = codigo
    return respuesta


def _error(request: Request, mensaje: str, codigo: int = 400) -> HTMLResponse:
    """Dibuja la página de error con un mensaje para el usuario."""
    respuesta = _pagina(request, "error.html", mensaje=mensaje, codigo=codigo)
    respuesta.status_code = codigo
    return respuesta


# Excepciones
@app.exception_handler(EntidadDesconocida)
async def _entidad_desconocida(request: Request, error: EntidadDesconocida):
    """Responde con una página de error cuando la URL nombra algo inexistente."""
    return _error(request, str(error), 404)


@app.exception_handler(RegistroNoEncontrado)
async def _registro_no_encontrado(request: Request, error: RegistroNoEncontrado):
    """Responde con una página de error cuando la llave consultada no existe."""
    return _error(request, str(error), 404)


@app.exception_handler(ErrorDeDependencia)
async def _error_de_dependencia(request: Request, error: ErrorDeDependencia):
    """Responde cuando se intenta borrar un registro al que otros apuntan."""
    return _error(request, str(error), 409)


@app.exception_handler(ErrorDeAlmacen)
async def _error_de_almacen(request: Request, error: ErrorDeAlmacen):
    """Responde con una página de error ante fallas de lectura o escritura."""
    return _error(request, str(error), 500)


@app.exception_handler(Exception)
async def _error_inesperado(request: Request, error: Exception):
    """Última red de seguridad: informa al usuario sin exponer el traceback.

    El servidor vuelve a lanzar la excepción después de enviar esta respuesta,
    de modo que el detalle técnico queda en la bitácora de uvicorn.
    """
    return _error(
        request,
        "Ocurrió un error inesperado durante la operación. Revisa la consola "
        "del servidor para ver el detalle técnico.",
        500,
    )


# Rutas
@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    """Menú principal con una tarjeta por entidad."""
    resumen = []
    for entidad in ENTIDADES:
        resumen.append({"entidad": entidad, "total": len(entidad.listar())})
    return _pagina(request, "inicio.html", resumen=resumen)


@app.get("/{clave}", response_class=HTMLResponse)
async def listar(request: Request, clave: str):
    """Muestra todos los registros de una entidad."""
    entidad = entidad_por_clave(clave)
    campos = entidad.campos_visor()
    return _pagina(
        request,
        "lista.html",
        entidad=entidad,
        campos=campos,
        registros=[
            {
                "llave": registro[entidad.LLAVE],
                "celdas": [
                    campo.a_visual(entidad.valor_visor(campo, registro))
                    for campo in campos
                ],
            }
            for registro in entidad.listar()
        ],
    )


@app.get("/{clave}/nuevo", response_class=HTMLResponse)
async def formulario_de_alta(request: Request, clave: str):
    """Muestra el formulario vacío para agregar un registro."""
    entidad = entidad_por_clave(clave)
    return _formulario(
        request,
        entidad,
        {},
        accion=f"/{clave}/nuevo",
        titulo=f"Agregar {entidad.ETIQUETA.lower()}",
    )


@app.post("/{clave}/nuevo", response_class=HTMLResponse)
async def agregar(request: Request, clave: str):
    """Da de alta un registro con los datos del formulario."""
    entidad = entidad_por_clave(clave)
    formulario = dict(await request.form())
    try:
        registro = entidad.agregar(formulario)
    except ErrorDeValidacion as error:
        return _formulario(
            request,
            entidad,
            formulario,
            accion=f"/{clave}/nuevo",
            titulo=f"Agregar {entidad.ETIQUETA.lower()}",
            error=error.mensaje,
            campo_con_error=error.campo,
            codigo=422,
        )
    aviso = (
        f"Se agregó {entidad.ETIQUETA.lower()} con "
        f"{entidad.LLAVE} = {registro[entidad.LLAVE]}."
    )
    return RedirectResponse(f"/{clave}?aviso={quote(aviso)}", status_code=303)


@app.get("/{clave}/consultar", response_class=HTMLResponse)
async def consultar(request: Request, clave: str, llave: str = ""):
    """Recibe la llave de la entidad y devuelve todos sus datos.

    Si llave viene vacía solo se muestra el formulario de búsqueda; si la
    llave no es un número o no existe, el mensaje se muestra en ese mismo
    formulario.
    """
    entidad = entidad_por_clave(clave)
    contexto = {"entidad": entidad, "llave": llave, "error": "", "registro": None}

    if llave.strip():
        try:
            numero = entidad.campo_llave().convertir(llave)
            registro = entidad.obtener(numero)
        except (ErrorDeValidacion, RegistroNoEncontrado) as error:
            contexto["error"] = getattr(error, "mensaje", str(error))
        else:
            return RedirectResponse(f"/{clave}/{numero}", status_code=303)

    return _pagina(request, "consultar.html", **contexto)


@app.get("/{clave}/{llave}", response_class=HTMLResponse)
async def ver(request: Request, clave: str, llave: int):
    """Muestra un registro con todos sus datos relacionados."""
    entidad = entidad_por_clave(clave)
    registro = entidad.obtener(llave)
    return _pagina(
        request,
        "detalle.html",
        entidad=entidad,
        llave=llave,
        titulo=entidad.describir(registro),
        datos=[
            (campo.etiqueta, campo.a_visual(entidad.valor_visor(campo, registro)))
            for campo in entidad.campos_visor()
        ],
        bloques=entidad.relacionados(registro),
    )


@app.get("/{clave}/{llave}/editar", response_class=HTMLResponse)
async def formulario_de_edicion(request: Request, clave: str, llave: int):
    """Muestra el formulario con los datos actuales del registro."""
    entidad = entidad_por_clave(clave)
    registro = entidad.obtener(llave)
    return _formulario(
        request,
        entidad,
        _valores_texto(entidad, registro),
        accion=f"/{clave}/{llave}/editar",
        titulo=f"Editar {entidad.ETIQUETA.lower()} #{llave}",
    )


@app.post("/{clave}/{llave}/editar", response_class=HTMLResponse)
async def editar(request: Request, clave: str, llave: int):
    """Guarda los cambios hechos sobre un registro."""
    entidad = entidad_por_clave(clave)
    formulario = dict(await request.form())
    try:
        entidad.editar(llave, formulario)
    except ErrorDeValidacion as error:
        return _formulario(
            request,
            entidad,
            formulario,
            accion=f"/{clave}/{llave}/editar",
            titulo=f"Editar {entidad.ETIQUETA.lower()} #{llave}",
            error=error.mensaje,
            campo_con_error=error.campo,
            codigo=422,
        )
    return RedirectResponse(
        f"/{clave}/{llave}?aviso={quote('Se guardaron los cambios.')}",
        status_code=303,
    )


@app.post("/{clave}/{llave}/eliminar", response_class=HTMLResponse)
async def eliminar(request: Request, clave: str, llave: int):
    """Elimina un registro y regresa a la lista de la entidad."""
    entidad = entidad_por_clave(clave)
    entidad.eliminar(llave)
    aviso = f"Se eliminó {entidad.ETIQUETA.lower()} #{llave}."
    return RedirectResponse(f"/{clave}?aviso={quote(aviso)}", status_code=303)
