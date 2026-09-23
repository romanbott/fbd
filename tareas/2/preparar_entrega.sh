#!/usr/bin/env bash
#
# Empaqueta los entregables de la Tarea 02 sin modificar el repositorio.
# Todo el armado se hace en un directorio temporal (/tmp) y al final se
# genera Tarea02_DoblesComillas.zip en el directorio actual.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_ZIP="$PWD/Tarea02_DoblesComillas.zip"

DOC_PDF="$SCRIPT_DIR/tarea02.pdf"
README_PDF="$SCRIPT_DIR/../../README_DoblesComillas.pdf"

TMP="$(mktemp -d /tmp/preparar_entrega.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

echo "Preparando entregables en $TMP ..."
mkdir -p "$TMP/SRC" "$TMP/Docs" "$TMP/Diagramas"

cp Diagramas/3b.drawio "$TMP/Diagramas/3b.drawio"
cp Diagramas/3b.png "$TMP/Diagramas/3b.png"
cp Diagramas/3c.drawio "$TMP/Diagramas/3c.drawio"
cp Diagramas/3c.png "$TMP/Diagramas/3c.png"

# Documento compilado
cp "$DOC_PDF" "$TMP/Docs/Tarea02.pdf"

# PDF del README (misma ruta relativa que usaba el script original)
if [ -f "$README_PDF" ]; then
    cp "$README_PDF" "$TMP/README_DoblesComillas.pdf"
else
    echo "Advertencia: no se encontro '$README_PDF' (se omitira del zip)." >&2
fi

# Empaquetar desde el temp para no arrastrar prefijos de ruta
ZIP_ITEMS=(Docs Diagramas)
[ -f "$TMP/README_DoblesComillas.pdf" ] && ZIP_ITEMS+=(README_DoblesComillas.pdf)

rm -f "$OUTPUT_ZIP"
( cd "$TMP" && zip -rq "$OUTPUT_ZIP" "${ZIP_ITEMS[@]}" )

echo "Contenido de $OUTPUT_ZIP:"
unzip -l "$OUTPUT_ZIP"

echo "Listo: $OUTPUT_ZIP"
