#!/usr/bin/env bash
#
# Empaqueta los entregables de la Practica 02 sin modificar el repositorio.
# Todo el armado se hace en un directorio temporal (/tmp) y al final se
# genera Practica02_DoblesComillas.zip en el directorio actual.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_ZIP="$PWD/Practica02_DoblesComillas.zip"

APP_DIR="$SCRIPT_DIR/PuellaGame"
DOC_PDF="$SCRIPT_DIR/practica02.pdf"
README_PDF="$SCRIPT_DIR/../../README_DoblesComillas.pdf"

TMP="$(mktemp -d /tmp/preparar_entrega.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

echo "Preparando entregables en $TMP ..."
mkdir -p "$TMP/SRC" "$TMP/Doc"

# Codigo fuente de la aplicacion (se excluyen artefactos y datos de runtime)
rsync -a \
    --exclude '__pycache__' \
    --exclude '.venv' \
    --exclude 'store' \
    "$APP_DIR/." "$TMP/SRC/"


# Documento compilado
cp "$DOC_PDF" "$TMP/Doc/Practica02.pdf"

# PDF del README (misma ruta relativa que usaba el script original)
if [ -f "$README_PDF" ]; then
    cp "$README_PDF" "$TMP/README_DoblesComillas.pdf"
else
    echo "Advertencia: no se encontro '$README_PDF' (se omitira del zip)." >&2
fi

# Empaquetar desde el temp para no arrastrar prefijos de ruta
ZIP_ITEMS=(SRC Doc)
[ -f "$TMP/README_DoblesComillas.pdf" ] && ZIP_ITEMS+=(README_DoblesComillas.pdf)

rm -f "$OUTPUT_ZIP"
( cd "$TMP" && zip -rq "$OUTPUT_ZIP" "${ZIP_ITEMS[@]}" )

echo "Contenido de $OUTPUT_ZIP:"
unzip -l "$OUTPUT_ZIP"

echo "Listo: $OUTPUT_ZIP"
