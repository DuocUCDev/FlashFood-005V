"""Alta, edición, eliminación y consulta de comidas y bebidas."""

import tkinter as tk
from tkinter import ttk

from flashfood.vista.comun import (
    Aviso,
    Pantalla,
    al_pulsar_enter,
    boton,
    crear_tabla,
    entrada,
    mostrar_error,
    pedir_confirmacion,
    pesos,
    pintar_stock,
    repartir,
    seccion,
    texto_fluido,
    titulo,
)


class Productos(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        self._producto_id: str | None = None
        titulo(
            self,
            "Productos",
            "Carga comidas y bebidas. Elige una fila para editarla. Quedan es lo que todavía puedes sumar a un pedido creado.",
        )
        self.aviso = Aviso(self)

        columnas = ttk.Frame(self)
        columnas.pack(fill="both", expand=True)
        formulario = seccion(columnas, "Datos del producto")
        self.tipo = tk.StringVar(value="Comida")
        self.nombre = tk.StringVar()
        self.precio = tk.StringVar()
        self.stock = tk.StringVar(value="0")
        self.extra = tk.StringVar()

        self.modo = ttk.Label(formulario, text="", style="Ayuda.TLabel", wraplength=300, justify="left")
        self.modo.grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(formulario, text="Tipo").grid(row=1, column=0, sticky="nw", pady=(8, 0))
        tipo_caja = ttk.Frame(formulario)
        tipo_caja.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(8, 0))
        self.tipo_combo = ttk.Combobox(
            tipo_caja, textvariable=self.tipo, values=("Comida", "Bebida"), state="readonly"
        )
        self.tipo_combo.pack(fill="x")
        self.pista_tipo = ttk.Label(tipo_caja, text="", style="Ayuda.TLabel", wraplength=280, justify="left")
        self.pista_tipo.pack(anchor="w", pady=(2, 0))
        self.tipo_combo.bind("<<ComboboxSelected>>", self._al_cambiar_tipo)

        self.entrada_nombre = entrada(formulario, 2, "Nombre", self.nombre, "Como aparecerá en el pedido.")
        self.entrada_precio = entrada(
            formulario, 3, "Precio (CLP)", self.precio, "Pesos, sin puntos ni comas. Ejemplo: 6500."
        )
        self.entrada_stock = entrada(formulario, 4, "Stock", self.stock, "Unidades enteras. Ejemplo: 24.")
        self.lbl_extra = ttk.Label(formulario, text="Categoría")
        self.lbl_extra.grid(row=5, column=0, sticky="nw", pady=(8, 0))
        extra_caja = ttk.Frame(formulario)
        extra_caja.grid(row=5, column=1, sticky="ew", padx=(12, 0), pady=(8, 0))
        self.entrada_extra = ttk.Entry(extra_caja, textvariable=self.extra)
        self.entrada_extra.pack(fill="x")
        self.pista_extra = ttk.Label(extra_caja, text="", style="Ayuda.TLabel", wraplength=280, justify="left")
        self.pista_extra.pack(anchor="w", pady=(2, 0))
        formulario.columnconfigure(1, weight=1)

        acciones = ttk.Frame(formulario)
        acciones.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        self.boton_eliminar = boton(acciones, "Eliminar", self.eliminar, "Peligro.TButton")
        self.boton_limpiar = boton(acciones, "Limpiar", self.limpiar)
        self.boton_guardar = boton(acciones, "Guardar", self.guardar, "Primario.TButton")
        self.boton_registrar = boton(acciones, "Registrar", self.registrar, "Primario.TButton")
        self.boton_eliminar.pack(side="left")
        self.boton_registrar.pack(side="right")
        self.boton_guardar.pack(side="right", padx=(0, 8))
        self.boton_limpiar.pack(side="right", padx=(0, 8))

        derecha = ttk.Frame(columnas)
        derecha.rowconfigure(0, weight=1)
        derecha.columnconfigure(0, weight=1)
        self.vacio = ttk.Label(derecha, text="", style="Ayuda.TLabel", justify="left")
        texto_fluido(self.vacio)
        marco, self.tabla = crear_tabla(
            derecha,
            ("tipo", "nombre", "precio", "stock", "disponible", "detalle"),
            ("Tipo", "Nombre", "Precio", "Stock", "Quedan", "Detalle"),
            (68, 112, 76, 52, 78, 88),
            altura=6,
        )
        marco.grid(row=0, column=0, sticky="nsew")
        self.vacio.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        repartir(columnas, formulario, derecha)
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)
        for campo in (self.entrada_nombre, self.entrada_precio, self.entrada_stock, self.entrada_extra):
            al_pulsar_enter(campo, self._confirmar)
        self.limpiar()

    def _confirmar(self) -> None:
        if str(self.boton_guardar.cget("state")) == "normal":
            self.guardar()
        else:
            self.registrar()

    def _al_cambiar_tipo(self, _evento=None) -> None:
        self.extra.set("")
        self._actualizar_extra()

    def _actualizar_extra(self) -> None:
        if self.tipo.get() == "Bebida":
            self.lbl_extra.configure(text="Mililitros")
            self.pista_extra.configure(text="Solo el número. Ejemplo: 350.")
            self.pista_tipo.configure(text="Bebida: el dato extra es el contenido del envase.")
        else:
            self.lbl_extra.configure(text="Categoría")
            self.pista_extra.configure(text="Por ejemplo: Sándwich, Acompañamiento o Postre.")
            self.pista_tipo.configure(text="Comida: el dato extra es la categoría del plato.")

    def _modo(self, editando: bool, nombre: str = "") -> None:
        self.boton_registrar.configure(
            state="disabled" if editando else "normal",
            style="TButton" if editando else "Primario.TButton",
        )
        self.boton_guardar.configure(
            state="normal" if editando else "disabled",
            style="Primario.TButton" if editando else "TButton",
        )
        self.boton_eliminar.configure(state="normal" if editando else "disabled")
        self.boton_limpiar.configure(text="Dejar de editar" if editando else "Limpiar")
        if editando:
            self.modo.configure(
                text=f"Estás editando «{nombre}». El tipo queda fijo: una comida no se convierte en bebida."
            )
        else:
            self.modo.configure(text="Completa los datos para sumar un producto al menú.")

    def refrescar(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for producto in self.controlador.listar_productos():
            self.tabla.insert(
                "",
                "end",
                iid=producto.id,
                values=(
                    producto.tipo_visible,
                    producto.nombre,
                    pesos(producto.precio),
                    producto.stock,
                    self.controlador.stock_disponible(producto.id),
                    producto.detalle,
                ),
            )
        agotados = pintar_stock(self.tabla)
        if not self.tabla.get_children():
            self.vacio.configure(text="Todavía no hay productos. Carga el primero con el formulario.")
        elif agotados:
            self.vacio.configure(text="Las filas en rojo no tienen unidades disponibles para un pedido nuevo.")
        else:
            self.vacio.configure(
                text="Stock es el inventario. Quedan descuenta lo que ya está reservado en pedidos creados."
            )

    def al_seleccionar(self, _evento=None) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        producto = self.controlador.obtener_producto(seleccion[0])
        self._producto_id = producto.id
        self.nombre.set(producto.nombre)
        self.precio.set(str(producto.precio))
        self.stock.set(str(producto.stock))
        self.tipo.set(producto.tipo_visible)
        self.extra.set(str(producto.mililitros) if producto.tipo == "bebida" else producto.categoria)
        self.tipo_combo.configure(state="disabled")
        self._actualizar_extra()
        self._modo(True, producto.nombre)
        self.aviso.limpiar()

    def limpiar(self) -> None:
        self._producto_id = None
        self.nombre.set("")
        self.precio.set("")
        self.stock.set("0")
        self.extra.set("")
        self.tipo.set("Comida")
        self.tipo_combo.configure(state="readonly")
        self._actualizar_extra()
        self._modo(False)
        if self.tabla.selection():
            self.tabla.selection_remove(self.tabla.selection())

    def registrar(self) -> None:
        self.aviso.limpiar()
        nombre = self.nombre.get().strip()
        ok, _producto = self.ejecutar(
            lambda: self.controlador.registrar_producto(
                self.tipo.get(), self.nombre.get(), self.precio.get(), self.stock.get(), self.extra.get()
            )
        )
        if not ok:
            return
        self.limpiar()
        self.refrescar()
        self.aviso.mostrar(f"«{nombre}» quedó en el catálogo.")
        self.entrada_nombre.focus_set()

    def guardar(self) -> None:
        self.aviso.limpiar()
        if not self._producto_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un producto de la tabla para editarlo.")
            return
        nombre = self.nombre.get().strip()
        ok, _producto = self.ejecutar(
            lambda: self.controlador.editar_producto(
                self._producto_id, self.nombre.get(), self.precio.get(), self.stock.get(), self.extra.get()
            )
        )
        if not ok:
            return
        self.limpiar()
        self.refrescar()
        self.aviso.mostrar(f"Los cambios de «{nombre}» quedaron guardados.")

    def eliminar(self) -> None:
        self.aviso.limpiar()
        if not self._producto_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un producto de la tabla para eliminarlo.")
            return
        nombre = self.nombre.get().strip() or "este producto"
        if not pedir_confirmacion(
            self.winfo_toplevel(),
            "Eliminar producto",
            f"¿Sacar «{nombre}» del catálogo? Si ya está en un pedido, no se podrá eliminar.",
        ):
            return
        ok, _resultado = self.ejecutar(lambda: self.controlador.eliminar_producto(self._producto_id))
        if not ok:
            return
        self.limpiar()
        self.refrescar()
        self.aviso.mostrar(f"«{nombre}» salió del catálogo.", "aviso")
