#!/usr/bin/env bash
set -euo pipefail

# ==========================================
# CONFIGURACIÓN (EDITAR AQUÍ)
# ==========================================
EQUIPO="Dobles Comillas"
README_SRC="../../README_DoblesComillas.pdf"   # <-- ruta al README_<Equipo>.pdf (placeholder)

# ==========================================

confirm() {  # confirm "mensaje"  -> 0 solo con una respuesta afirmativa
  local ans=""
  if ! read -rp "$1 [s/N] " ans 2>/dev/null </dev/tty; then
    read -rp "$1 [s/N] " ans || ans=""
  fi
  [[ "${ans:-}" =~ ^[sS]([iI])?$ ]]
}

if [ "$#" -ne 2 ]; then
  echo "Uso: $0 <tarea|practica> <numero>" >&2
  exit 1
fi

TIPO="$1"
NUM="$2"

case "$TIPO" in
  tarea|practica) ;;
  *) echo "Tipo inválido: $TIPO (usa 'tarea' o 'practica')" >&2; exit 1 ;;
esac

[[ "$NUM" =~ ^[0-9]+$ ]] || { echo "Número inválido: $NUM" >&2; exit 1; }

NUM2=$(printf '%02d' "$NUM")
CAP=$([ "$TIPO" = tarea ] && echo Tarea || echo Practica)
EQUIPO_ZIP=${EQUIPO// /}
OUTPUT_ZIP="${CAP}${NUM2}_${EQUIPO_ZIP}.zip"

# --- Localizar el .tex principal (carpeta de nombre variable) ---
mapfile -t TEX_FILES < <(
  grep -rl --include='*.tex' -e '\\documentclass' . 2>/dev/null \
    | grep -v '/\.' || true
)

if [ "${#TEX_FILES[@]}" -eq 0 ]; then
  echo "No se encontró ningún .tex principal (\\documentclass) bajo $(pwd)" >&2
  exit 1
fi

if [ "${#TEX_FILES[@]}" -gt 1 ]; then
  echo "Varios .tex principales encontrados; sé explícito:" >&2
  printf '  %s\n' "${TEX_FILES[@]}" >&2
  exit 1
fi

MAIN_TEX="${TEX_FILES[0]}"
SRC_DIR=$(dirname "$MAIN_TEX")
TEX_BASE=$(basename "$MAIN_TEX" .tex)
PDF="$SRC_DIR/$TEX_BASE.pdf"

if [ ! -f "$PDF" ]; then
  echo "Falta el artefacto $PDF" >&2
  echo "Compila primero:" >&2
  echo "  (cd \"$SRC_DIR\" && xelatex \"$TEX_BASE.tex\" && biber \"$TEX_BASE\" && xelatex \"$TEX_BASE.tex\")" >&2
  exit 1
fi

FOUND=()
for d in Diagramas SQL SRC; do
  [ -d "$SRC_DIR/$d" ] && FOUND+=("$d")
done

README_OK=0
[ -n "$README_SRC" ] && [ -f "$README_SRC" ] && README_OK=1

# --- Resumen y confirmación ---
echo "== Resumen de la entrega =="
echo "  Fuente          : $SRC_DIR"
echo "  .tex principal  : $MAIN_TEX"
echo "  PDF artefacto   : $PDF"
echo "  Carpetas        : ${FOUND[*]:-(ninguna)}"
echo "  README          : $([ $README_OK = 1 ] && echo "$README_SRC" || echo 'FALTA (README_SRC)')"
echo "  .zip de salida  : $OUTPUT_ZIP"

confirm "¿Continuar con el empaquetado?" || { echo "Cancelado."; exit 1; }

if [ "$README_OK" = 0 ]; then
  confirm "Falta README_${EQUIPO_ZIP}.pdf; ¿continuar sin él?" || { echo "Cancelado."; exit 1; }
fi

# --- Construir estructura en un temporal ---
WORK=$(mktemp -d /tmp/entrega.XXXXXX)
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$WORK/Docs"

ENTRIES=()
if [ "$README_OK" = 1 ]; then
  cp "$README_SRC" "$WORK/README_${EQUIPO_ZIP}.pdf"
  ENTRIES+=("README_${EQUIPO_ZIP}.pdf")
fi

cp "$PDF" "$WORK/Docs/${CAP}${NUM2}.pdf"
ENTRIES+=("Docs")

for d in "${FOUND[@]}"; do
  cp -r "$SRC_DIR/$d" "$WORK/$d"
  ENTRIES+=("$d")
done

# --- Empaquetar ---
if [ -f "$OUTPUT_ZIP" ]; then
  confirm "Ya existe $OUTPUT_ZIP; ¿sobrescribir?" || { echo "Cancelado."; exit 1; }
  rm -f "$OUTPUT_ZIP"
fi

( cd "$WORK" && zip -qr "$OLDPWD/$OUTPUT_ZIP" "${ENTRIES[@]}" )

echo "Contenido de $OUTPUT_ZIP:"
unzip -l "$OUTPUT_ZIP"
echo "Done!"
