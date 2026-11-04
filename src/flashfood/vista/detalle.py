"""Consulta del detalle, los totales y el historial de un pedido."""

import tkinter as tk
from tkinter import ttk

from flashfood.vista.comun import (
    Pantalla,
    configurar_combo,
    crear_tabla,
    describir_condiciones,
    pesos,
    repartir,
    seccion,
    texto_fluido,
    titulo,
)


class Detalle(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        self._pedidos: dict[str, str] = {}
        titulo(
            self,
            "Detalle del pedido",
            "Consulta las líneas, el total, el pago y el recorrido. Desde aquí no se modifica el pedido.",
        )
        selector = seccion(self, "Pedido")
        selector.pack(fill="x")
        ttk.Label(
            selector,
            text="Incluye el código, el cliente y el estado.",
            style="Ayuda.TLabel",
        ).pack(anchor="w", pady=(0, 6))
        self.pedido = tk.StringVar()
        self.combo = ttk.Combobox(selector, textvariable=self.pedido, state="readonly")
        self.combo.pack(fill="x")
        self.combo.bind("<<ComboboxSelected>>", lambda _evento: self.mostrar())

        paneles = ttk.Frame(self)
        paneles.pack(fill="both", expand=True, pady=(12, 0))
        marco, self.tabla = crear_tabla(
            paneles,
            ("producto", "cantidad", "precio", "subtotal"),
            ("Producto", "Cantidad", "Precio congelado", "Subtotal"),
            (160, 80, 130, 110),
            altura=6,
        )
        resumen = seccion(paneles, "Resumen")
        self.resumen = ttk.Label(resumen, justify="left")
        self.resumen.pack(anchor="nw", fill="x")
        texto_fluido(self.resumen)
        repartir(paneles, marco, resumen, umbral=900)

    def refrescar(self) -> None:
        actual = self.pedido.get()
        self._pedidos = {}
        etiquetas = []
        for pedido in self.controlador.listar_pedidos():
            etiqueta = f"{pedido.id} — {self.controlador.nombre_cliente(pedido.cliente_id)} — {pedido.estado.etiqueta}"
            self._pedidos[etiqueta] = pedido.id
            etiquetas.append(etiqueta)
        configurar_combo(self.combo, etiquetas, actual)
        self.mostrar()

    def mostrar(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        pedido_id = self._pedidos.get(self.pedido.get())
        if not pedido_id:
            self.resumen.configure(text="No hay pedidos para consultar.")
            return
        pedido = self.controlador.obtener_pedido(pedido_id)
        for detalle in pedido.detalles:
            self.tabla.insert(
                "",
                "end",
                values=(detalle.nombre, detalle.cantidad, pesos(detalle.precio_unitario), pesos(detalle.subtotal)),
            )
        if pedido.pago is None:
            pago = "Sin pago. El stock todavía no se descuenta."
        else:
            pago = f"{pedido.pago.medio} · {pedido.pago.referencia or 'sin referencia'}\n{pedido.pago.mensaje}"
        cantidad_lineas = len(pedido.detalles)
        if cantidad_lineas == 0:
            productos = "Sin productos."
        elif cantidad_lineas == 1:
            productos = "1 línea."
        else:
            productos = f"{cantidad_lineas} líneas."
        self.resumen.configure(
            text=(
                f"Estado: {pedido.estado.etiqueta}\n"
                f"Cliente: {self.controlador.nombre_cliente(pedido.cliente_id)}\n"
                f"Repartidor: {self.controlador.nombre_repartidor(pedido.repartidor_id)}\n"
                f"Productos: {productos}\n"
                f"Condiciones al crear: {describir_condiciones(pedido)}.\n\n"
                f"Subtotal: {pesos(pedido.subtotal)}\n"
                f"Descuento VIP: {pesos(pedido.descuento)}\n"
                f"Despacho: {pesos(pedido.costo_despacho)}\n"
                f"Total: {pesos(pedido.total)}\n\n"
                f"Pago: {pago}\n"
                f"Recorrido: {pedido.historial_texto()}"
            )
        )
