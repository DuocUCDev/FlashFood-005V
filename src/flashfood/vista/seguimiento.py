"""Consulta y avance del estado de los pedidos."""

import tkinter as tk
from tkinter import ttk

from flashfood.vista.comun import (
    Aviso,
    Pantalla,
    Recorrido,
    boton,
    crear_tabla,
    mostrar_error,
    pedir_confirmacion,
    pesos,
    pintar_estado,
    texto_fluido,
    titulo,
)


class Seguimiento(Pantalla):
    def __init__(self, master, controlador, navegar=None):
        super().__init__(master, controlador)
        self._navegar = navegar
        self._pedido_id: str | None = None
        self._destino: str | None = None
        titulo(
            self,
            "Seguimiento",
            "Avanza el pedido en orden. Cancelar solo se puede antes de que salga a la calle.",
        )
        self.recorrido = Recorrido(self)
        self.aviso = Aviso(self)
        self.historial = ttk.Label(self, style="Ayuda.TLabel", justify="left")
        self.historial.pack(fill="x", anchor="w", pady=(0, 8))
        texto_fluido(self.historial)
        acciones = ttk.Frame(self)
        acciones.pack(fill="x", pady=(0, 8))
        self.botones = {
            "preparar": boton(acciones, "Iniciar preparación", self.preparar),
            "despachar": boton(acciones, "Despachar", self.despachar),
            "entregar": boton(acciones, "Marcar entregado", self.entregar),
            "cancelar": boton(acciones, "Cancelar pedido", self.cancelar, "Peligro.TButton"),
        }
        self.botones["preparar"].grid(row=0, column=0, padx=(0, 8), pady=(0, 6), sticky="w")
        self.botones["despachar"].grid(row=0, column=1, padx=(0, 8), pady=(0, 6), sticky="w")
        self.botones["entregar"].grid(row=0, column=2, padx=(0, 8), pady=(0, 6), sticky="w")
        self.boton_atajo = boton(acciones, "Siguiente paso", self._abrir_destino, "Primario.TButton")
        self.boton_atajo.grid(row=1, column=0, columnspan=2, sticky="w")
        self.boton_atajo.grid_remove()
        self.botones["cancelar"].grid(row=1, column=2, sticky="w")
        marco, self.tabla = crear_tabla(
            self,
            ("id", "cliente", "estado", "repartidor", "total"),
            ("Pedido", "Cliente", "Estado", "Repartidor", "Total"),
            (140, 160, 130, 140, 100),
            altura=6,
        )
        marco.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)
        self._aplicar(None)

    def refrescar(self) -> None:
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
                    self.controlador.nombre_repartidor(pedido.repartidor_id),
                    pesos(pedido.total),
                ),
            )
        pintar_estado(self.tabla, 2)
        if seleccionado and self.tabla.exists(seleccionado):
            self.tabla.selection_set(seleccionado)
            self.al_seleccionar()
        else:
            self._pedido_id = None
            self.historial.configure(text="Selecciona un pedido para ver su recorrido.")
            self.recorrido.mostrar(None)
            self.aviso.mostrar("Selecciona un pedido para ver en qué paso está y qué puedes hacer.", "info")
            self._aplicar(None)
            self._actualizar_atajo(None, None)

    def al_seleccionar(self, _evento=None) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            self._pedido_id = None
            self.historial.configure(text="Selecciona un pedido para ver su recorrido.")
            self.recorrido.mostrar(None)
            self.aviso.mostrar("Selecciona un pedido para ver en qué paso está y qué puedes hacer.", "info")
            self._aplicar(None)
            self._actualizar_atajo(None, None)
            return
        self._pedido_id = seleccion[0]
        pedido = self.controlador.obtener_pedido(self._pedido_id)
        acciones = self.controlador.acciones(self._pedido_id)
        self.historial.configure(text=f"Recorrido: {pedido.historial_texto()}")
        self.recorrido.mostrar(pedido.estado.etiqueta)
        self.aviso.mostrar(*self._guia(pedido, acciones))
        self._aplicar(acciones)
        self._actualizar_atajo(pedido, acciones)

    def _guia(self, pedido, acciones: dict) -> tuple[str, str]:
        estado = pedido.estado.etiqueta
        if estado == "Creado" and acciones["puede_pagar"]:
            return "Listo para cobrar. El stock baja solo si el pago se aprueba.", "aviso"
        if estado == "Creado":
            return "Faltan productos. Agrégalos en Pedidos antes de cobrar.", "aviso"
        if estado == "Pagado":
            return "Pago aprobado. El siguiente paso es iniciar la preparación.", "info"
        if estado == "En preparación" and acciones["puede_asignar"]:
            return "En cocina. Asigna un repartidor libre para poder despachar.", "aviso"
        if estado == "En preparación":
            return "Ya tiene repartidor. Puedes despachar.", "info"
        if estado == "En camino":
            return "Va en camino. Márcalo entregado cuando el cliente lo reciba.", "info"
        if estado == "Entregado":
            return "Entregado. Este pedido queda cerrado.", "ok"
        if estado == "Cancelado":
            return "Cancelado. No vuelve a cambiar de estado.", "error"
        return f"Estado: {estado}.", "info"

    def _aplicar(self, acciones: dict | None) -> None:
        habilitado = {
            "preparar": False,
            "despachar": False,
            "entregar": False,
            "cancelar": False,
        }
        if acciones:
            habilitado = {
                "preparar": acciones["puede_preparar"],
                "despachar": acciones["puede_despachar"],
                "entregar": acciones["puede_entregar"],
                "cancelar": acciones["puede_cancelar"],
            }
        for clave, widget in self.botones.items():
            activo = habilitado[clave]
            if clave == "cancelar":
                widget.configure(state="normal" if activo else "disabled")
            elif activo:
                widget.configure(state="normal", style="Primario.TButton")
            else:
                widget.configure(state="disabled", style="TButton")

    def _actualizar_atajo(self, pedido, acciones: dict | None) -> None:
        self._destino = None
        if pedido is None or acciones is None or self._navegar is None:
            self.boton_atajo.grid_remove()
            return
        estado = pedido.estado.etiqueta
        if estado == "Creado" and acciones["puede_pagar"]:
            self._destino = "pagos"
            texto = "Ir a cobrar"
        elif estado == "Creado":
            self._destino = "pedidos"
            texto = "Ir a agregar productos"
        elif estado == "En preparación" and acciones["puede_asignar"]:
            self._destino = "repartidores"
            texto = "Asignar repartidor"
        else:
            self.boton_atajo.grid_remove()
            return
        self.boton_atajo.configure(text=texto, state="normal")
        self.boton_atajo.grid()

    def _abrir_destino(self) -> None:
        if not self._navegar or not self._destino or not self._pedido_id:
            return
        self._navegar(self._destino, self._pedido_id)

    def preparar(self) -> None:
        self._operar(lambda: self.controlador.preparar(self._pedido_id or ""))

    def despachar(self) -> None:
        self._operar(lambda: self.controlador.despachar(self._pedido_id or ""))

    def entregar(self) -> None:
        self._operar(lambda: self.controlador.entregar(self._pedido_id or ""))

    def cancelar(self) -> None:
        if not self._pedido_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un pedido.")
            return
        if not pedir_confirmacion(
            self.winfo_toplevel(),
            "Cancelar pedido",
            "¿Cancelar el pedido seleccionado? Si ya estaba pagado, el stock vuelve y el repartidor queda libre.",
        ):
            return
        self._operar(lambda: self.controlador.cancelar(self._pedido_id))

    def _operar(self, accion) -> None:
        if not self._pedido_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un pedido.")
            return
        ok, _pedido = self.ejecutar(accion)
        if not ok:
            return
        self.refrescar()
