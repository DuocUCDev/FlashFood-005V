"""Creación de pedidos y carga de productos."""

import tkinter as tk
from tkinter import ttk

from flashfood.vista.comun import (
    Aviso,
    Pantalla,
    al_pulsar_enter,
    boton,
    configurar_combo,
    crear_tabla,
    describir_condiciones,
    mostrar_error,
    pedir_confirmacion,
    pesos,
    pintar_estado,
    repartir,
    seccion,
    texto_fluido,
    titulo,
)


class Pedidos(Pantalla):
    def __init__(self, master, controlador, navegar=None):
        super().__init__(master, controlador)
        self._navegar = navegar
        self._clientes: dict[str, str] = {}
        self._productos: dict[str, str] = {}
        self._pedido_id: str | None = None
        titulo(
            self,
            "Pedidos",
            "Crea la orden, agrega productos y revisa el total. El cobro se hace en Pagos.",
        )
        self.aviso = Aviso(self)

        alta = seccion(self, "Nuevo pedido")
        alta.pack(fill="x")
        self.cliente = tk.StringVar()
        ttk.Label(alta, text="Cliente").grid(row=0, column=0, sticky="w")
        self.combo_cliente = ttk.Combobox(alta, textvariable=self.cliente, state="readonly")
        self.combo_cliente.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        boton(alta, "Crear pedido", self.crear, "Primario.TButton").grid(row=0, column=2, padx=(0, 8))
        self.boton_eliminar = boton(alta, "Cancelar pedido", self.eliminar, "Peligro.TButton")
        self.boton_eliminar.grid(row=0, column=3)
        aviso_alta = ttk.Label(
            alta,
            text="El cliente VIP y las condiciones de despacho quedan fijos en este momento.",
            style="Ayuda.TLabel",
            justify="left",
        )
        aviso_alta.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        texto_fluido(aviso_alta)
        alta.columnconfigure(1, weight=1)

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True, pady=(12, 0))

        lista = ttk.Frame(cuerpo)
        lista.rowconfigure(0, weight=1)
        lista.columnconfigure(0, weight=1)
        marco, self.tabla = crear_tabla(
            lista,
            ("id", "cliente", "estado", "total"),
            ("Pedido", "Cliente", "Estado", "Total"),
            (108, 112, 108, 78),
            altura=6,
        )
        marco.grid(row=0, column=0, sticky="nsew")
        self.vacio = ttk.Label(lista, text="", style="Ayuda.TLabel", justify="left")
        self.vacio.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

        edicion = seccion(cuerpo, "Productos del pedido")
        repartir(cuerpo, lista, edicion, umbral=980)
        edicion.columnconfigure(1, weight=1)
        self.producto = tk.StringVar()
        self.cantidad = tk.StringVar(value="1")
        ttk.Label(edicion, text="Producto").grid(row=0, column=0, sticky="w")
        self.combo_producto = ttk.Combobox(edicion, textvariable=self.producto, state="readonly")
        self.combo_producto.grid(row=0, column=1, columnspan=3, sticky="ew", padx=(8, 0))
        ttk.Label(edicion, text="Cantidad").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.entrada_cantidad = ttk.Entry(edicion, textvariable=self.cantidad, width=8)
        self.entrada_cantidad.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(8, 0))
        acciones = ttk.Frame(edicion)
        acciones.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        self.boton_agregar = boton(acciones, "Agregar al pedido", self.agregar, "Primario.TButton")
        self.boton_quitar = boton(acciones, "Quitar producto", self.quitar)
        self.boton_cobrar = boton(acciones, "Ir a cobrar", self.ir_a_cobrar, "Primario.TButton")
        self.boton_agregar.pack(side="left")
        self.boton_quitar.pack(side="left", padx=(8, 0))
        self.boton_cobrar.pack(side="right")
        aviso_cantidad = ttk.Label(
            edicion,
            text="Cantidad entera, sin puntos. No puedes pedir más de lo disponible.",
            style="Ayuda.TLabel",
            justify="left",
        )
        aviso_cantidad.grid(row=1, column=2, columnspan=2, sticky="ew", padx=(8, 0), pady=(8, 0))
        texto_fluido(aviso_cantidad)

        marco_lineas, self.lineas = crear_tabla(
            edicion,
            ("producto", "cantidad", "precio", "subtotal"),
            ("Producto", "Cantidad", "Precio", "Subtotal"),
            (160, 80, 90, 100),
            altura=4,
        )
        self.total_pedido = ttk.Label(edicion, text="", style="Total.TLabel")
        self.total_pedido.grid(row=3, column=0, columnspan=4, sticky="w", pady=(10, 0))
        self.totales = ttk.Label(edicion, justify="left")
        self.totales.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(2, 0))
        texto_fluido(self.totales)
        self.guia = ttk.Label(edicion, style="Ayuda.TLabel", justify="left")
        self.guia.grid(row=5, column=0, columnspan=4, sticky="ew", pady=(4, 0))
        texto_fluido(self.guia)
        marco_lineas.grid(row=6, column=0, columnspan=4, sticky="nsew", pady=(8, 0))
        edicion.rowconfigure(6, weight=1)
        al_pulsar_enter(self.entrada_cantidad, self.agregar)

    def preseleccionar(self, pedido_id: str) -> None:
        self._pedido_id = pedido_id

    def refrescar(self) -> None:
        self._clientes = {}
        for cliente in self.controlador.listar_clientes():
            vip = " · VIP" if cliente.es_vip else ""
            self._clientes[f"{cliente.nombre} · {cliente.direccion}{vip}"] = cliente.id
        configurar_combo(self.combo_cliente, list(self._clientes), self.cliente.get())
        self._productos = {
            f"{producto.nombre} · {pesos(producto.precio)} · quedan {self.controlador.stock_disponible(producto.id)}": producto.id
            for producto in self.controlador.listar_productos()
        }
        configurar_combo(self.combo_producto, list(self._productos), self.producto.get())

        seleccionado = self._pedido_id
        self.tabla.delete(*self.tabla.get_children())
        for pedido in self.controlador.listar_pedidos():
            self.tabla.insert(
                "",
                "end",
                iid=pedido.id,
                values=(
                    pedido.id,
                    self.controlador.nombre_cliente(pedido.cliente_id),
                    pedido.estado.etiqueta,
                    pesos(pedido.total),
                ),
            )
        pintar_estado(self.tabla, 2)
        if self.tabla.get_children():
            self.vacio.configure(text="El color de la fila indica el estado. Elige una para ver sus productos.")
        else:
            self.vacio.configure(text="Todavía no hay pedidos. Elige un cliente y crea el primero.")
        if seleccionado and self.tabla.exists(seleccionado):
            self.tabla.selection_set(seleccionado)
            self.tabla.see(seleccionado)
            self._mostrar(seleccionado)
        else:
            self._pedido_id = None
            self._mostrar(None)

    def crear(self) -> None:
        self.aviso.limpiar()
        cliente_id = self._clientes.get(self.cliente.get(), "")
        ok, pedido = self.ejecutar(lambda: self.controlador.crear_pedido(cliente_id))
        if not ok:
            return
        self._pedido_id = pedido.id
        self.refrescar()
        self.aviso.mostrar("Pedido creado. Agrega los productos: el precio de cada línea queda fijo al sumarla.")
        self.combo_producto.focus_set()

    def al_seleccionar(self, _evento=None) -> None:
        seleccion = self.tabla.selection()
        self._pedido_id = seleccion[0] if seleccion else None
        self._mostrar(self._pedido_id)

    def _mostrar(self, pedido_id: str | None) -> None:
        self.lineas.delete(*self.lineas.get_children())
        if not pedido_id:
            self.guia.configure(text="Elige un pedido de la lista, o crea uno, para ver sus productos.")
            self.totales.configure(text="")
            self.total_pedido.configure(text="")
            self._habilitar(False, False, False)
            return
        pedido = self.controlador.obtener_pedido(pedido_id)
        for detalle in pedido.detalles:
            self.lineas.insert(
                "",
                "end",
                iid=detalle.producto_id,
                values=(detalle.nombre, detalle.cantidad, pesos(detalle.precio_unitario), pesos(detalle.subtotal)),
            )
        self.totales.configure(
            text=(
                f"Subtotal {pesos(pedido.subtotal)}   ·   Descuento VIP {pesos(pedido.descuento)}   ·   "
                f"Despacho {pesos(pedido.costo_despacho)}\n"
                f"Condiciones al crear el pedido: {describir_condiciones(pedido)}."
            )
        )
        self.total_pedido.configure(text=f"Total {pesos(pedido.total)}")
        acciones = self.controlador.acciones(pedido_id)
        if acciones["puede_editar_items"]:
            guia = "Puedes agregar o quitar productos. El precio de cada línea queda fijo al agregarla."
            if not pedido.detalles:
                guia = "Este pedido todavía no tiene productos. Agrega al menos uno para poder cobrarlo."
        elif acciones["puede_cancelar"]:
            guia = (
                f"Estado: {pedido.estado.etiqueta}. Los productos ya no se editan. "
                "Si lo cancelas y estaba pagado, el stock vuelve."
            )
        else:
            guia = f"Estado: {pedido.estado.etiqueta}. Este pedido ya no se edita ni se cancela."
        self.guia.configure(text=guia)
        self._habilitar(
            acciones["puede_editar_items"],
            acciones["puede_cancelar"],
            acciones["puede_pagar"],
        )

    def _habilitar(self, editar: bool, cancelar: bool, pagar: bool) -> None:
        self.boton_agregar.configure(
            state="normal" if editar else "disabled",
            style="Primario.TButton" if editar and not pagar else "TButton",
        )
        self.boton_quitar.configure(state="normal" if editar else "disabled")
        self.boton_eliminar.configure(state="normal" if cancelar else "disabled")
        self.boton_cobrar.configure(
            state="normal" if pagar else "disabled",
            style="Primario.TButton" if pagar else "TButton",
        )

    def agregar(self) -> None:
        self.aviso.limpiar()
        if not self._pedido_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un pedido.")
            return
        producto_id = self._productos.get(self.producto.get(), "")
        nombre = self.producto.get().split(" · ")[0]
        ok, _pedido = self.ejecutar(
            lambda: self.controlador.agregar_producto(self._pedido_id, producto_id, self.cantidad.get())
        )
        if not ok:
            return
        self.refrescar()
        self.aviso.mostrar(f"{nombre} quedó en el pedido.")

    def quitar(self) -> None:
        self.aviso.limpiar()
        if not self._pedido_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un pedido.")
            return
        seleccion = self.lineas.selection()
        if not seleccion:
            mostrar_error(self.winfo_toplevel(), "Selecciona el producto que quieres quitar.")
            return
        ok, _pedido = self.ejecutar(lambda: self.controlador.quitar_producto(self._pedido_id, seleccion[0]))
        if not ok:
            return
        self.refrescar()
        self.aviso.mostrar("El producto salió del pedido.", "aviso")

    def eliminar(self) -> None:
        self.aviso.limpiar()
        if not self._pedido_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un pedido.")
            return
        if not pedir_confirmacion(
            self.winfo_toplevel(),
            "Cancelar pedido",
            "¿Cancelar este pedido? Si ya estaba pagado, el stock vuelve al inventario y el repartidor queda libre.",
        ):
            return
        pedido_id = self._pedido_id
        ok, _pedido = self.ejecutar(lambda: self.controlador.cancelar(pedido_id))
        if not ok:
            return
        self._pedido_id = None
        self.refrescar()
        self.aviso.mostrar("El pedido quedó cancelado.", "aviso")

    def ir_a_cobrar(self) -> None:
        if not self._pedido_id or not self._navegar:
            mostrar_error(self.winfo_toplevel(), "Selecciona un pedido creado que tenga productos.")
            return
        self._navegar("pagos", self._pedido_id)
