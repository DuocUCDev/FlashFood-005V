"""Registro, consulta y asignación de repartidores disponibles."""

import tkinter as tk
from tkinter import ttk

from flashfood.vista.comun import (
    Aviso,
    Pantalla,
    al_pulsar_enter,
    boton,
    configurar_combo,
    crear_tabla,
    entrada,
    mostrar_error,
    pedir_confirmacion,
    pintar_estado,
    repartir,
    seccion,
    texto_fluido,
    titulo,
)


class Repartidores(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        self._pedidos: dict[str, str] = {}
        self._repartidores: dict[str, str] = {}
        self._repartidor_id: str | None = None
        self._pendiente: str | None = None
        titulo(
            self,
            "Repartidores",
            "Asigna a alguien cuando el pedido está en preparación. Cada persona lleva una sola entrega a la vez.",
        )
        self.aviso = Aviso(self)

        asignacion = seccion(self, "Asignar entrega")
        asignacion.pack(fill="x")
        self.pedido = tk.StringVar()
        self.repartidor = tk.StringVar()
        ttk.Label(asignacion, text="Pedido en preparación").grid(row=0, column=0, sticky="w", pady=4)
        self.combo_pedido = ttk.Combobox(asignacion, textvariable=self.pedido, state="readonly")
        self.combo_pedido.grid(row=0, column=1, sticky="ew", padx=(8, 12), pady=4)
        ttk.Label(asignacion, text="Repartidor libre").grid(row=0, column=2, sticky="w", pady=4)
        self.combo_repartidor = ttk.Combobox(asignacion, textvariable=self.repartidor, state="readonly")
        self.combo_repartidor.grid(row=0, column=3, sticky="ew", padx=(8, 12), pady=4)
        boton(asignacion, "Asignar repartidor", self.asignar, "Primario.TButton").grid(row=0, column=4, pady=4)
        self.pista_asignacion = ttk.Label(
            asignacion, text="", style="Ayuda.TLabel", justify="left"
        )
        texto_fluido(self.pista_asignacion)
        self.pista_asignacion.grid(row=1, column=0, columnspan=5, sticky="w", pady=(4, 0))
        asignacion.columnconfigure(1, weight=1)
        asignacion.columnconfigure(3, weight=1)

        columnas = ttk.Frame(self)
        columnas.pack(fill="both", expand=True, pady=(12, 0))
        formulario = seccion(columnas, "Datos del repartidor")
        self.nombre = tk.StringVar()
        self.vehiculo = tk.StringVar()
        self.modo = ttk.Label(formulario, text="", style="Ayuda.TLabel", wraplength=280, justify="left")
        self.modo.grid(row=0, column=0, columnspan=2, sticky="w")
        self.entrada_nombre = entrada(formulario, 1, "Nombre", self.nombre, "Nombre y apellido.")
        self.entrada_vehiculo = entrada(formulario, 2, "Vehículo", self.vehiculo, "Por ejemplo: moto, bicicleta o auto.")
        acciones = ttk.Frame(formulario)
        acciones.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        self.boton_eliminar = boton(acciones, "Eliminar", self.eliminar, "Peligro.TButton")
        self.boton_limpiar = boton(acciones, "Limpiar", self.limpiar)
        self.boton_guardar = boton(acciones, "Guardar", self.guardar, "Primario.TButton")
        self.boton_registrar = boton(acciones, "Registrar", self.registrar, "Primario.TButton")
        self.boton_eliminar.pack(side="left")
        self.boton_registrar.pack(side="right")
        self.boton_guardar.pack(side="right", padx=(0, 8))
        self.boton_limpiar.pack(side="right", padx=(0, 8))
        formulario.columnconfigure(1, weight=1)

        derecha = ttk.Frame(columnas)
        derecha.rowconfigure(0, weight=1)
        derecha.columnconfigure(0, weight=1)
        self.vacio = ttk.Label(derecha, text="", style="Ayuda.TLabel", justify="left")
        texto_fluido(self.vacio)
        marco, self.tabla = crear_tabla(
            derecha,
            ("nombre", "vehiculo", "estado"),
            ("Nombre", "Vehículo", "Estado"),
            (160, 120, 110),
            altura=6,
        )
        marco.grid(row=0, column=0, sticky="nsew")
        self.vacio.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        repartir(columnas, formulario, derecha)
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)
        for campo in (self.entrada_nombre, self.entrada_vehiculo):
            al_pulsar_enter(campo, self._confirmar)
        self.limpiar()

    def _confirmar(self) -> None:
        if str(self.boton_guardar.cget("state")) == "normal":
            self.guardar()
        else:
            self.registrar()

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
            self.modo.configure(text=f"Estás editando a {nombre}.")
        else:
            self.modo.configure(text="Registra a quien puede salir a entregar.")

    def preseleccionar(self, pedido_id: str) -> None:
        self._pendiente = pedido_id

    def refrescar(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for repartidor in self.controlador.listar_repartidores():
            self.tabla.insert(
                "",
                "end",
                iid=repartidor.id,
                values=(repartidor.nombre, repartidor.vehiculo, "Disponible" if repartidor.disponible else "En entrega"),
            )
        pintar_estado(self.tabla, 2)
        if self.tabla.get_children():
            self.vacio.configure(text="Verde: puede recibir un pedido. Ámbar: ya va en una entrega.")
        else:
            self.vacio.configure(text="Todavía no hay repartidores. Sin alguien libre no se puede despachar.")

        self._pedidos = {}
        etiquetas_pedidos = []
        for pedido in self.controlador.listar_pedidos():
            if not self.controlador.acciones(pedido.id)["puede_asignar"]:
                continue
            etiqueta = f"{pedido.id} — {self.controlador.nombre_cliente(pedido.cliente_id)}"
            self._pedidos[etiqueta] = pedido.id
            etiquetas_pedidos.append(etiqueta)
        pedido_actual = self.pedido.get()
        if self._pendiente:
            for etiqueta, identificador in self._pedidos.items():
                if identificador == self._pendiente:
                    pedido_actual = etiqueta
                    break
            self._pendiente = None
        configurar_combo(self.combo_pedido, etiquetas_pedidos, pedido_actual)

        self._repartidores = {
            f"{item.nombre} — {item.vehiculo}": item.id
            for item in self.controlador.listar_repartidores()
            if item.disponible
        }
        configurar_combo(self.combo_repartidor, list(self._repartidores), self.repartidor.get())
        if not etiquetas_pedidos:
            self.pista_asignacion.configure(
                text="No hay pedidos en preparación esperando repartidor. Primero inicia la preparación en Seguimiento."
            )
        elif not self._repartidores:
            self.pista_asignacion.configure(text="No hay repartidores libres. Todos están en una entrega.")
        else:
            self.pista_asignacion.configure(
                text="Al asignar, el pedido queda listo para despachar en Seguimiento."
            )

    def al_seleccionar(self, _evento=None) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        repartidor = self.controlador.obtener_repartidor(seleccion[0])
        self._repartidor_id = repartidor.id
        self.nombre.set(repartidor.nombre)
        self.vehiculo.set(repartidor.vehiculo)
        self._modo(True, repartidor.nombre)
        self.aviso.limpiar()

    def limpiar(self) -> None:
        self._repartidor_id = None
        self.nombre.set("")
        self.vehiculo.set("")
        self._modo(False)
        if self.tabla.selection():
            self.tabla.selection_remove(self.tabla.selection())

    def registrar(self) -> None:
        self.aviso.limpiar()
        nombre = self.nombre.get().strip()
        ok, _repartidor = self.ejecutar(
            lambda: self.controlador.registrar_repartidor(self.nombre.get(), self.vehiculo.get())
        )
        if not ok:
            return
        self.limpiar()
        self.refrescar()
        self.aviso.mostrar(f"{nombre} ya puede recibir una entrega.")
        self.entrada_nombre.focus_set()

    def guardar(self) -> None:
        self.aviso.limpiar()
        if not self._repartidor_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un repartidor de la tabla para editarlo.")
            return
        nombre = self.nombre.get().strip()
        ok, _repartidor = self.ejecutar(
            lambda: self.controlador.editar_repartidor(self._repartidor_id, self.nombre.get(), self.vehiculo.get())
        )
        if not ok:
            return
        self.limpiar()
        self.refrescar()
        self.aviso.mostrar(f"Los datos de {nombre} quedaron guardados.")

    def eliminar(self) -> None:
        self.aviso.limpiar()
        if not self._repartidor_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un repartidor de la tabla para eliminarlo.")
            return
        nombre = self.nombre.get().strip() or "este repartidor"
        if not pedir_confirmacion(
            self.winfo_toplevel(),
            "Eliminar repartidor",
            f"¿Sacar a {nombre} del equipo? Si está asignado a un pedido, no se podrá eliminar.",
        ):
            return
        ok, _resultado = self.ejecutar(lambda: self.controlador.eliminar_repartidor(self._repartidor_id))
        if not ok:
            return
        self.limpiar()
        self.refrescar()
        self.aviso.mostrar(f"{nombre} salió del equipo.", "aviso")

    def asignar(self) -> None:
        self.aviso.limpiar()
        pedido_id = self._pedidos.get(self.pedido.get(), "")
        repartidor_id = self._repartidores.get(self.repartidor.get(), "")
        if not pedido_id or not repartidor_id:
            mostrar_error(
                self.winfo_toplevel(),
                "Selecciona un pedido en preparación y un repartidor libre.",
            )
            return
        ok, _pedido = self.ejecutar(lambda: self.controlador.asignar_repartidor(pedido_id, repartidor_id))
        if not ok:
            return
        self.refrescar()
        self.aviso.mostrar("Repartidor asignado. Ya puedes despachar el pedido en Seguimiento.")
