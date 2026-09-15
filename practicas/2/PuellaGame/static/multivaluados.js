document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".grupo-repetible").forEach((grupo) => {
    const filas = grupo.querySelector(".filas");
    const agregar = grupo.querySelector(".agregar-fila");
    if (!filas || !agregar) return;

    const limpiar = (fila) => {
      fila.querySelectorAll("input").forEach((input) => {
        input.value = "";
      });
      fila.querySelectorAll("select").forEach((select) => {
        select.selectedIndex = 0;
      });
    };

    const actualizar = () => {
      const total = filas.querySelectorAll(".fila").length;
      filas.querySelectorAll(".quitar-fila").forEach((boton) => {
        boton.disabled = total <= 1;
      });
    };

    agregar.addEventListener("click", () => {
      const ultima = filas.querySelector(".fila:last-child");
      const nueva = ultima.cloneNode(true);
      limpiar(nueva);
      filas.appendChild(nueva);
      actualizar();
    });

    filas.addEventListener("click", (evento) => {
      const boton = evento.target.closest(".quitar-fila");
      if (!boton) return;
      const fila = boton.closest(".fila");
      if (filas.querySelectorAll(".fila").length <= 1) {
        limpiar(fila);
        return;
      }
      fila.remove();
      actualizar();
    });

    actualizar();
  });
});
