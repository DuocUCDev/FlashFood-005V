"""Registro y consulta de clientes."""

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
    pintar_estado,
    repartir,
    seccion,
    texto_fluido,
    titulo,
)


class Clientes(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        self._cliente_id: str | None = None
        titulo(
            self,
            "Clientes",
            "Registra a quién entregamos. El descuento VIP queda fijo al crear el pedido: cambiarlo aquí no reescribe pedidos anteriores.",
        )
        self.aviso = Aviso(self)
        columnas = ttk.Frame(self)
        columnas.pack(fill="both", expand=True)
        formulario = seccion(columnas, "Datos del cliente")
        self.nombre = tk.StringVar()
        self.telefono = tk.StringVar()
        self.direccion = tk.StringVar()
        self.es_vip = tk.BooleanVar()
        self.modo = ttk.Label(formulario, text="", style="Ayuda.TLabel", wraplength=300, justify="left")
        self.modo.grid(row=0, column=0, columnspan=2, sticky="w")
        self.entrada_nombre = entrada(formulario, 1, "Nombre", self.nombre, "Nombre y apellido, como en la entrega.")
        self.entrada_telefono = entrada(
            formulario, 2, "Teléfono", self.telefono, "Al menos 8 dígitos. Ejemplo: +56911112222."
        )
        self.entrada_direccion = entrada(
            formulario, 3, "Dirección", self.direccion, "Calle y número donde se entrega el pedido."
        )
        ttk.Checkbutton(
            formulario,
            text="Cliente VIP — 10% de descuento en pedidos nuevos",
            variable=self.es_vip,
        ).grid(row=4, column=1, sticky="w", padx=(12, 0), pady=(8, 0))
        acciones = ttk.Frame(formulario)
        acciones.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(14, 0))
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
            ("nombre", "telefono", "direccion", "vip"),
            ("Nombre", "Teléfono", "Dirección", "VIP"),
            (120, 120, 160, 52),
            altura=6,
        )
        marco.grid(row=0, column=0, sticky="nsew")
        self.vacio.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        repartir(columnas, formulario, derecha)
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)
        for campo in (self.entrada_nombre, self.entrada_telefono, self.entrada_direccion):
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
            self.modo.configure(text="Completa los datos para que esta persona pueda pedir.")

    def refrescar(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for cliente in self.controlador.listar_clientes():
            self.tabla.insert(
                "",
                "end",
                iid=cliente.id,
                values=(cliente.nombre, cliente.telefono, cliente.direccion, "Sí" if cliente.es_vip else "No"),
            )
        pintar_estado(self.tabla, 3)
        if self.tabla.get_children():
            self.vacio.configure(text="Las filas en violeta son clientes VIP.")
        else:
            self.vacio.configure(text="Todavía no hay clientes. Registra el primero con el formulario.")

    def al_seleccionar(self, _evento=None) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        cliente = self.controlador.obtener_cliente(seleccion[0])
        self._cliente_id = cliente.id
        self.nombre.set(cliente.nombre)
        self.telefono.set(cliente.telefono)
        self.direccion.set(cliente.direccion)
        self.es_vip.set(cliente.es_vip)
        self._modo(True, cliente.nombre)
        self.aviso.limpiar()

    def limpiar(self) -> None:
        self._cliente_id = None
        self.nombre.set("")
        self.telefono.set("")
        self.direccion.set("")
        self.es_vip.set(False)
        self._modo(False)
        if self.tabla.selection():
            self.tabla.selection_remove(self.tabla.selection())

    def registrar(self) -> None:
        self.aviso.limpiar()
        nombre = self.nombre.get().strip()
        ok, _cliente = self.ejecutar(
            lambda: self.controlador.registrar_cliente(
                self.nombre.get(),
                self.telefono.get(),
                self.direccion.get(),
                bool(self.es_vip.get()),
            )
        )
        if not ok:
            return
        self.limpiar()
        self.refrescar()
        self.aviso.mostrar(f"{nombre} ya puede hacer pedidos.")
        self.entrada_nombre.focus_set()

    def guardar(self) -> None:
        self.aviso.limpiar()
        if not self._cliente_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un cliente de la tabla para editarlo.")
            return
        nombre = self.nombre.get().strip()
        ok, _cliente = self.ejecutar(
            lambda: self.controlador.editar_cliente(
                self._cliente_id,
                self.nombre.get(),
                self.telefono.get(),
                self.direccion.get(),
                bool(self.es_vip.get()),
            )
        )
        if not ok:
            return
        self.limpiar()
        self.refrescar()
        self.aviso.mostrar(f"Los datos de {nombre} quedaron guardados.")

    def eliminar(self) -> None:
        self.aviso.limpiar()
        if not self._cliente_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un cliente de la tabla para eliminarlo.")
            return
        nombre = self.nombre.get().strip() or "este cliente"
        if not pedir_confirmacion(
            self.winfo_toplevel(),
            "Eliminar cliente",
            f"¿Sacar a {nombre} del registro? Si tiene pedidos, no se podrá eliminar.",
        ):
            return
        ok, _resultado = self.ejecutar(lambda: self.controlador.eliminar_cliente(self._cliente_id))
        if not ok:
            return
        self.limpiar()
        self.refrescar()
        self.aviso.mostrar(f"{nombre} salió del registro.", "aviso")
