"""Selección del medio de pago y simulación de la transacción."""

import tkinter as tk
from tkinter import ttk

from flashfood.vista.comun import (
    Aviso,
    Pantalla,
    al_pulsar_enter,
    boton,
    configurar_combo,
    informar,
    mostrar_error,
    pesos,
    seccion,
    texto_fluido,
    titulo,
)


class Pagos(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        self._pedidos: dict[str, str] = {}
        self._pendiente: str | None = None
        titulo(
            self,
            "Pagos",
            "Cobra un pedido creado que ya tenga productos. Un rechazo no confirma la compra ni descuenta stock. Un pedido pagado no se vuelve a cobrar.",
        )
        self.aviso = Aviso(self)

        formulario = seccion(self, "Datos del cobro")
        formulario.pack(fill="x")
        ttk.Label(formulario, text="Pedido a cobrar").pack(anchor="w")
        ttk.Label(
            formulario,
            text="Solo aparecen pedidos creados que ya tienen productos.",
            style="Ayuda.TLabel",
        ).pack(anchor="w", pady=(2, 4))
        self.pedido = tk.StringVar()
        self.combo = ttk.Combobox(formulario, textvariable=self.pedido, state="readonly")
        self.combo.pack(fill="x")
        self.combo.bind("<<ComboboxSelected>>", lambda _evento: self.mostrar_total())
        self.total = ttk.Label(formulario, text="", style="Total.TLabel")
        self.total.pack(anchor="w", pady=(10, 12))

        ttk.Label(formulario, text="Medio de pago").pack(anchor="w")
        self.medio = tk.StringVar(value="Tarjeta")
        self.combo_medio = ttk.Combobox(
            formulario,
            textvariable=self.medio,
            values=("Tarjeta", "Efectivo", "Billetera digital", "Transferencia"),
            state="readonly",
        )
        self.combo_medio.pack(fill="x", pady=(4, 0))
        self.combo_medio.bind("<<ComboboxSelected>>", lambda _evento: self.mostrar_campos())

        self.rechazar_tarjeta = tk.BooleanVar()
        self.monto = tk.StringVar()
        self.saldo = tk.StringVar()
        self.operacion = tk.StringVar()
        self.rechazar_transferencia = tk.BooleanVar()
        self.zona = ttk.Frame(formulario)
        self.zona.pack(fill="x", pady=(12, 0))
        self.marco_tarjeta = self._marco_check(
            self.zona,
            "Ensayar un rechazo. El pedido sigue creado y el stock no baja.",
            self.rechazar_tarjeta,
        )
        self.marco_efectivo = self._marco_entrada(
            self.zona,
            "Monto que entrega el cliente",
            self.monto,
            "Sin puntos ni comas. Ejemplo: 10000. Si no alcanza, el pago se rechaza. Si sobra, verás el vuelto.",
        )
        self.marco_billetera = self._marco_entrada(
            self.zona,
            "Saldo de la billetera",
            self.saldo,
            "Sin puntos ni comas. Ejemplo: 15000. Si el saldo no alcanza, el pago se rechaza.",
        )
        self.marco_transferencia = ttk.Frame(self.zona)
        ttk.Label(self.marco_transferencia, text="Número de operación").pack(anchor="w")
        self.entrada_operacion = ttk.Entry(self.marco_transferencia, textvariable=self.operacion)
        self.entrada_operacion.pack(fill="x", pady=(4, 4))
        ttk.Label(
            self.marco_transferencia,
            text="Tal como figura en el comprobante.",
            style="Ayuda.TLabel",
        ).pack(anchor="w", pady=(0, 8))
        ttk.Checkbutton(
            self.marco_transferencia,
            text="Ensayar un rechazo. No se confirma el pedido.",
            variable=self.rechazar_transferencia,
        ).pack(anchor="w")

        self.boton_cobrar = boton(formulario, "Cobrar pedido", self.procesar, "Primario.TButton")
        self.boton_cobrar.pack(anchor="e", pady=(16, 0))
        al_pulsar_enter(self._entrada_de(self.marco_efectivo), self.procesar)
        al_pulsar_enter(self._entrada_de(self.marco_billetera), self.procesar)
        al_pulsar_enter(self.entrada_operacion, self.procesar)
        self.mostrar_campos()

    def _marco_check(self, parent, texto: str, variable: tk.BooleanVar) -> ttk.Frame:
        marco = ttk.Frame(parent)
        ttk.Checkbutton(marco, text=texto, variable=variable).pack(anchor="w")
        return marco

    def _marco_entrada(self, parent, texto: str, variable: tk.StringVar, pista: str) -> ttk.Frame:
        marco = ttk.Frame(parent)
        ttk.Label(marco, text=texto).pack(anchor="w")
        ttk.Entry(marco, textvariable=variable).pack(fill="x", pady=(4, 2))
        ayuda = ttk.Label(marco, text=pista, style="Ayuda.TLabel", justify="left")
        ayuda.pack(fill="x", anchor="w")
        texto_fluido(ayuda)
        return marco

    def _entrada_de(self, marco: ttk.Frame) -> ttk.Entry:
        for hijo in marco.winfo_children():
            if isinstance(hijo, ttk.Entry):
                return hijo
        raise RuntimeError("El marco de pago no tiene campo de texto")

    def preseleccionar(self, pedido_id: str) -> None:
        self._pendiente = pedido_id

    def refrescar(self) -> None:
        actual = self.pedido.get()
        self._pedidos = {}
        etiquetas = []
        for pedido in self.controlador.listar_pedidos():
            if not self.controlador.acciones(pedido.id)["puede_pagar"]:
                continue
            etiqueta = f"{pedido.id} — {self.controlador.nombre_cliente(pedido.cliente_id)} — {pesos(pedido.total)}"
            self._pedidos[etiqueta] = pedido.id
            etiquetas.append(etiqueta)
        if self._pendiente:
            for etiqueta, identificador in self._pedidos.items():
                if identificador == self._pendiente:
                    actual = etiqueta
                    break
            self._pendiente = None
        configurar_combo(self.combo, etiquetas, actual)
        self.mostrar_total()

    def mostrar_total(self) -> None:
        pedido_id = self._pedidos.get(self.pedido.get())
        if not pedido_id:
            self.total.configure(text="No hay pedidos listos para cobrar")
            self.boton_cobrar.configure(state="disabled", style="TButton")
            return
        pedido = self.controlador.obtener_pedido(pedido_id)
        self.total.configure(text=f"Total a cobrar  {pesos(pedido.total)}")
        self.boton_cobrar.configure(state="normal", style="Primario.TButton")

    def mostrar_campos(self) -> None:
        for marco in (self.marco_tarjeta, self.marco_efectivo, self.marco_billetera, self.marco_transferencia):
            marco.pack_forget()
        elegido = {
            "Tarjeta": self.marco_tarjeta,
            "Efectivo": self.marco_efectivo,
            "Billetera digital": self.marco_billetera,
            "Transferencia": self.marco_transferencia,
        }.get(self.medio.get(), self.marco_tarjeta)
        elegido.pack(fill="x")

    def procesar(self) -> None:
        self.aviso.limpiar()
        pedido_id = self._pedidos.get(self.pedido.get(), "")
        if not pedido_id:
            mostrar_error(self.winfo_toplevel(), "Selecciona un pedido creado que tenga productos.")
            return
        medio = self.medio.get()
        rechazar = self.rechazar_tarjeta.get() if medio == "Tarjeta" else self.rechazar_transferencia.get()
        ok, resultado = self.ejecutar(
            lambda: self.controlador.pagar(
                pedido_id,
                medio,
                rechazar if medio in {"Tarjeta", "Transferencia"} else False,
                self.monto.get(),
                self.saldo.get(),
                self.operacion.get(),
            )
        )
        if not ok:
            return
        titulo_aviso = "Pago aprobado" if resultado.aprobado else "Pago rechazado"
        informar(self.winfo_toplevel(), titulo_aviso, resultado.mensaje)
        self.aviso.mostrar(resultado.mensaje, "ok" if resultado.aprobado else "error")
        self.refrescar()
