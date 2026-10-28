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
xelatex practica05.tex
biber practica05
xelatex practica05.tex
```

O también

```bash
lualatex practica05.tex
biber practica05
lualatex practica05.tex
```

