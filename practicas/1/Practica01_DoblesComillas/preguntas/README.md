# Plantilla para tareas - UNAM FCiencias.


Es necesario editar las variables:

- `\documentoTitulo`
- `\documentoSubtitulo`
- `\integranteUno`
- `\integranteDos`
- `\integranteTres`
- `\integranteCuatro`


# Para compilar
Para compilar es necesario compilar, procesar las referencias y volver a compilar:


```bash
xelatex preguntas.tex
biber preguntas
xelatex preguntas.tex
```

Otra opción es usar `tectonic` que maneja automáticamente las bibliotecas:

```bash
tectonic -Z search-path=$(dirname $(kpsewhich biblatex.sty)) preguntas.tex
```
