#!/usr/bin/env bash
#
# Empaqueta los entregables de la Tarea 03 (Modelo Relacional) sin modificar el
# repositorio: arma todo en un directorio temporal y genera
# Tarea03_DoblesComillas.zip en el directorio donde se invoca.
#
# Contenido del zip:
#   README_DoblesComillas.pdf
#   Docs/Tarea03.pdf
#   Diagramas/EJERCICIO 2.a.drawio  (+ .png)
#   Diagramas/EJERCICIO 2.b.drawio  (+ .png)
#
# Solo se incluyen los diagramas RELACIONALES de los incisos 2a y 2b (no los E-R).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ==========================================
# CONFIGURACIÓN (EDITAR AQUÍ)
# ==========================================
EQUIPO="Dobles Comillas"
CAP="Tarea"
NUM2="03"

DOC_PDF="$SCRIPT_DIR/tarea03.pdf"
README_SRC="$SCRIPT_DIR/../../README_DoblesComillas.pdf"

# Diagramas a incluir: "<ruta relativa a este script>|<nombre dentro del zip>"
DIAGRAMAS=(
  "Diagramas/2_a.drawio|EJERCICIO 2.a.drawio"
  "Figuras/2_a.png|EJERCICIO 2.a.png"
  "Diagramas/RelacionalT2E3c.drawio|EJERCICIO 2.b.drawio"
  "Figuras/RelacionalT2E3c.png|EJERCICIO 2.b.png"
)
# ==========================================

EQUIPO_ZIP=${EQUIPO// /}
OUTPUT_ZIP="$PWD/${CAP}${NUM2}_${EQUIPO_ZIP}.zip"

confirm() {  # confirm "mensaje"  -> 0 solo con una respuesta afirmativa
  local ans=""
  if ! read -rp "$1 [s/N] " ans 2>/dev/null </dev/tty; then
    read -rp "$1 [s/N] " ans || ans=""
  fi
  [[ "${ans:-}" =~ ^[sS]([iI])?$ ]]
}

if [ ! -f "$DOC_PDF" ]; then
  echo "Falta el PDF compilado: $DOC_PDF" >&2
  echo "Compila primero:" >&2
  echo "  (cd \"$SCRIPT_DIR\" && xelatex tarea03.tex && biber tarea03 && xelatex tarea03.tex)" >&2
  exit 1
fi

README_OK=0
[ -f "$README_SRC" ] && README_OK=1

# --- Resumen y confirmación ---
echo "== Resumen de la entrega =="
echo "  Documento   : $DOC_PDF"
echo "  README      : $([ $README_OK = 1 ] && echo "$README_SRC" || echo 'FALTA (README_SRC)')"
echo "  Diagramas   :"
for entry in "${DIAGRAMAS[@]}"; do
  src="${entry%%|*}"
  printf '    - %s\n' "$src"
done
echo "  .zip salida : $OUTPUT_ZIP"

confirm "¿Continuar con el empaquetado?" || { echo "Cancelado."; exit 1; }

if [ "$README_OK" = 0 ]; then
  confirm "Falta el README; ¿continuar sin él?" || { echo "Cancelado."; exit 1; }
fi

# --- Construir estructura en un temporal ---
WORK="$(mktemp -d /tmp/entrega.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$WORK/Docs" "$WORK/Diagramas"
ENTRIES=(Docs Diagramas)

cp "$DOC_PDF" "$WORK/Docs/${CAP}${NUM2}.pdf"

if [ "$README_OK" = 1 ]; then
  cp "$README_SRC" "$WORK/README_${EQUIPO_ZIP}.pdf"
  ENTRIES+=(README_${EQUIPO_ZIP}.pdf)
fi

for entry in "${DIAGRAMAS[@]}"; do
  src="${entry%%|*}"
  dst="${entry##*|}"
  if [ -f "$SCRIPT_DIR/$src" ]; then
    cp "$SCRIPT_DIR/$src" "$WORK/Diagramas/$dst"
  else
    echo "Advertencia: falta '$src' (se omite del zip)." >&2
  fi
done

# --- Empaquetar ---
if [ -f "$OUTPUT_ZIP" ]; then
  confirm "Ya existe $OUTPUT_ZIP; ¿sobrescribir?" || { echo "Cancelado."; exit 1; }
  rm -f "$OUTPUT_ZIP"
fi

( cd "$WORK" && zip -qr "$OUTPUT_ZIP" "${ENTRIES[@]}" )

echo "Contenido de $OUTPUT_ZIP:"
unzip -l "$OUTPUT_ZIP"
echo "Listo: $OUTPUT_ZIP"
