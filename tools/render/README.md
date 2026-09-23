# drawio-render

Herramienta genérica para renderizar archivos `.drawio` a **PNG** o **SVG**
usando [Puppeteer](https://pptr.dev/) contra el modo *embed* de draw.io
(`https://embed.diagrams.net`). No depende de la estructura de ningún
proyecto: funciona sobre cualquier carpeta y puede usarse como CLI o como
módulo de Node.

## Requisitos

- Node.js >= 18.
- Conexión a Internet (para `embed.diagrams.net` y, la primera vez, para
  descargar Chromium durante `npm install`).

## Instalación

```bash
npm install
```

## Uso (CLI)

```bash
drawio-render [inputDir] [opciones]
```

`inputDir` puede ser un archivo `.drawio` o una carpeta que los contenga (por
defecto `.`). Los PNG/SVG se escriben con el mismo nombre junto al `.drawio`,
salvo que indiques `--out`.

```bash
# Un solo archivo
node drawio-render.js ./Figuras/3b.drawio

# Todos los .drawio de ./Figuras
node drawio-render.js ./Figuras

# Recursivo, en SVG, dentro de ./build
node drawio-render.js ./diagramas -r -f svg -o ./build

# Más resolución y fondo transparente
node drawio-render.js ./Figuras --scale 4 --background transparent

# Ver qué haría sin escribir nada
node drawio-render.js ./Figuras --dry-run
```

### Opciones

| Opción | Por defecto | Descripción |
| --- | --- | --- |
| `inputDir` | `.` | Archivo `.drawio` o carpeta que los contenga. |
| `-o, --out <dir>` | `inputDir` | Carpeta de salida. |
| `-s, --scale <n>` | `3` | Escala de exportación. |
| `-b, --border <n>` | `10` | Borde en píxeles. |
| `--background <c>` | `#ffffff` | Fondo (`#ffffff`, `transparent`, etc.). |
| `-f, --format <png\|svg>` | `png` | Formato de salida. |
| `-r, --recursive` | apagado | Recorre subcarpetas (replica el árbol en la salida). |
| `--backup-dir <dir>` | `<out>/original` | Dónde respaldar las salidas existentes. |
| `--no-backup` | apagado | Sobrescribe sin respaldar. |
| `--embed-url <url>` | `$DRAWIO_EMBED_URL` o `https://embed.diagrams.net` | Endpoint *embed* de draw.io. |
| `--timeout <ms>` | `45000` | Tiempo máximo por diagrama. |
| `--dry-run` | apagado | Muestra lo que haría sin escribir nada. |
| `-h, --help` | | Muestra la ayuda. |
| `-V, --version` | | Muestra la versión. |

Antes de sobrescribir una salida, el archivo existente se mueve a
`<out>/original/` (una sola vez). Usa `--no-backup` para evitarlo.

## Uso como módulo

```js
const { renderDirectory, renderDrawio } = require('drawio-render');

await renderDirectory({ input: './Figuras', format: 'png', scale: 3, border: 10 });
```

`renderDirectory(opts)` acepta las mismas claves que el CLI (`input`, `out`,
`format`, `scale`, `border`, `background`, `recursive`, `backup`, `backupDir`,
`embedUrl`, `timeout`, `dryRun`) y devuelve `{ ok, total, failed }`.
`renderDrawio(browser, xml, outPath, opts)` renderiza un único diagrama.

## Notas

- El render usa un `<iframe>` y una escucha en línea (`window.__msgs`) para la
  secuencia `init → load → export` del embed de draw.io.
- `npm run render` (definido en `package.json`) equivale a
  `node drawio-render.js ../../Figuras`, pensado para este repositorio.
