#!/usr/bin/env bash
#
# Empaqueta los entregables de la Práctica 05 sin modificar el repositorio.
# Todo el armado se hace en un directorio temporal (/tmp) y al final se genera
# Practica05_DoblesComillas.zip en el directorio actual.
#
# Estructura (lineamientos de entrega):
#   Practica05_DoblesComillas.zip
#     Diagramas/
#       ERDoblesComillas.png
#       ERDoblesComillas.drawio
#       RelacionalDoblesComillas.png
#       RelacionalDoblesComillas.drawio
#     SQL/
#       DDL.sql
#     Docs/
#       Practica05.pdf
#     README_DoblesComillas.pdf

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_ZIP="$PWD/Practica05_DoblesComillas.zip"

DOC_PDF="$SCRIPT_DIR/practica05.pdf"
README_PDF="$SCRIPT_DIR/../../README_DoblesComillas.pdf"
DDL_SQL="$SCRIPT_DIR/SQL/DDL.sql"

TMP="$(mktemp -d /tmp/preparar_entrega.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

echo "Preparando entregables en $TMP ..."
mkdir -p "$TMP/Diagramas" "$TMP/SQL" "$TMP/Docs"

# Diagramas: solo las fuentes .drawio y sus renders .png
for f in ERDoblesComillas.drawio ERDoblesComillas.png \
         RelacionalDoblesComillas.drawio RelacionalDoblesComillas.png; do
    cp "$SCRIPT_DIR/Diagramas/$f" "$TMP/Diagramas/"
done

# Guion SQL
cp "$DDL_SQL" "$TMP/SQL/DDL.sql"

# Documento compilado
cp "$DOC_PDF" "$TMP/Docs/Practica05.pdf"

# README del equipo
if [ -f "$README_PDF" ]; then
    cp "$README_PDF" "$TMP/README_DoblesComillas.pdf"
else
    echo "Advertencia: no se encontro '$README_PDF' (se omitira del zip)." >&2
fi

# Empaquetar desde el temporal para no arrastrar prefijos de ruta
ZIP_ITEMS=(Docs Diagramas SQL)
[ -f "$TMP/README_DoblesComillas.pdf" ] && ZIP_ITEMS+=(README_DoblesComillas.pdf)

rm -f "$OUTPUT_ZIP"
( cd "$TMP" && zip -rq "$OUTPUT_ZIP" "${ZIP_ITEMS[@]}" )

echo "Contenido de $OUTPUT_ZIP:"
unzip -l "$OUTPUT_ZIP"

echo "Listo: $OUTPUT_ZIP"
