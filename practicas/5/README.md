# Práctica 05: Lenguaje para Definición de Datos (DDL)

Práctica de **Fundamentos de Bases de Datos**, Facultad de Ciencias, UNAM (2027-I).
Equipo: **Dobles Comillas**.

## Contenido

- `practica05.tex` / `practica05.pdf`: documento de la práctica (restricciones de dominio, cambios al modelo, diagramas y evidencia del backup).
- `SQL/DDL.sql`: script DDL del modelo relacional.
- `Diagramas/`: modelo E-R y modelo relacional (`.drawio` y `.png`).
- `figuras/`: renders vectoriales usados por el documento y evidencias del backup.
- `escudos/`: escudos de la UNAM y la Facultad de Ciencias.
- `referencias.bib`: referencias en formato BibLaTeX/APA.
- `preparar_entrega.sh`: arma el `.zip` de entrega.

## Compilar

```bash
latexmk -pdf -xelatex practica05.tex
```

También:

```bash
xelatex practica05.tex
biber practica05
xelatex practica05.tex
xelatex practica05.tex
```

## Empaquetar

```bash
./preparar_entrega.sh
```

Genera `Practica05_DoblesComillas.zip` con `Docs/`, `Diagramas/`, `SQL/` y `README_DoblesComillas.pdf`.

## Renderizar los diagramas

```bash
node ../../tools/render/drawio-render.js Diagramas/RelacionalDoblesComillas.drawio -f svg -o figuras --no-backup
```

El flujo es `.drawio` → `.svg` → `.pdf` para el documento; el `.zip` incluye solo `.drawio` y `.png`.
