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
xelatex tarea1.tex
biber tarea1
xelatex tarea1.tex
```

O también

```bash
lualatex tarea1.tex
biber tarea1
lualatex tarea1.tex
```

