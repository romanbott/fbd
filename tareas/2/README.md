# Plantilla para tareas - UNAM FCiencias.

Plantilla base para la **Tarea 02: Modelo Entidad -- Relación**.

## Estructura

```
tarea02.tex        Documento principal (portada + secciones + \input de respuestas)
respuestas/        Un archivo por ejercicio (enunciado + respuesta)
  01a.tex .. 01e.tex   Sección 1: Conceptos del Modelo E-R
  02i.tex, 02ii.tex    Sección 2: Entendiendo el Modelo E-R
  03a.tex .. 03c.tex   Sección 3: Mini-mundos
Figuras/           Diagramas (.drawio) y sus renders (.png)
  original/          Renders previos (respaldo)
escudos/           Escudos de la UNAM y la Facultad de Ciencias
tools/render/      Herramienta (Puppeteer) para renderizar los .drawio a PNG
customcode.sty     Paquete casero de formato de código
referencias.bib    Referencias bibliográficas (BibLaTeX / APA)
```

## Para compilar

```bash
xelatex tarea02.tex
biber tarea02
xelatex tarea02.tex
```

## Para renderizar los diagramas

```bash
cd tools/render
npm install      # solo la primera vez
npm run render   # regenera Figuras/*.png a partir de Figuras/*.drawio
```
