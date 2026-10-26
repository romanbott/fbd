# Plantilla para tareas - UNAM FCiencias.


Es necesario editar las variables:

- `\documentoTitulo`
- `\documentoSubtitulo`
- `\integranteUno`
- `\integranteDos`
- `\integranteTres`
- `\integranteCuatro`


# Para compilar

```bash
xelatex practica3.tex
biber practica3
xelatex practica3.tex
```

O también

```bash
lualatex practica3.tex
biber practica3
lualatex practica3.tex
```

