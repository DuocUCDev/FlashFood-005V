"""Piezas compartidas por las pantallas: tema, tablas y avisos."""

import re
import sys
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from flashfood.modelo.errores import PersistenciaError, ReglaNegocioError
from flashfood.modelo.formato import pesos

FONDO = "#f6f4ef"
TARJETA = "#ffffff"
TINTA = "#1c1917"
TINTA_SUAVE = "#57534e"
LINEA = "#e4dfd6"
OSCURO = "#1c1917"
ACENTO = "#c2410c"
ACENTO_ACTIVO = "#9a3412"
PELIGRO = "#9f1239"
PELIGRO_FONDO = "#fff1f2"
FUENTE = "Segoe UI"

MODULOS = (
    ("inicio", "Inicio"),
    ("productos", "Productos"),
    ("clientes", "Clientes"),
    ("pedidos", "Pedidos"),
    ("detalle", "Detalle del pedido"),
    ("pagos", "Pagos"),
    ("repartidores", "Repartidores"),
    ("seguimiento", "Seguimiento"),
    ("configuracion", "Configuración"),
)

GRUPOS = (
    ("", ("inicio",)),
    ("Catálogo", ("productos", "clientes")),
    ("Pedido", ("pedidos", "pagos", "detalle")),
    ("Entrega", ("repartidores", "seguimiento")),
    ("Sistema", ("configuracion",)),
)

ATAJOS = (
    (
        "Antes del servicio",
        (
            ("productos", "Carga el menú y revisa cuánto queda disponible."),
            ("clientes", "Registra a quién entregamos y si es cliente VIP."),
            ("repartidores", "Deja personas libres para cuando empiece la cocina."),
        ),
    ),
    (
        "Durante el pedido",
        (
            ("pedidos", "Abre la orden y agrega los productos."),
            ("pagos", "Cobra. Si el pago se rechaza, el stock no baja."),
            ("seguimiento", "Pasa a preparación, despacho y entrega."),
            ("detalle", "Revisa líneas, totales, pago y recorrido."),
        ),
    ),
)

COLORES_FILA = {
    "base": "#ffffff",
    "zebra": "#fafaf9",
    "creado": "#fef3c7",
    "pagado": "#dbeafe",
    "preparacion": "#e0e7ff",
    "camino": "#ffedd5",
    "entregado": "#dcfce7",
    "cancelado": "#fee2e2",
    "vip": "#ede9fe",
}

MAPA_ESTADO = {
    "Creado": "creado",
    "Pagado": "pagado",
    "En preparación": "preparacion",
    "En camino": "camino",
    "Entregado": "entregado",
    "Cancelado": "cancelado",
    "Disponible": "entregado",
    "En entrega": "camino",
    "Sí": "vip",
}

TONOS_AVISO = {
    "ok": ("#ecfdf3", "#166534"),
    "aviso": ("#fffbeb", "#92400e"),
    "info": ("#eff6ff", "#1e3a8a"),
    "error": ("#fff1f2", "#9f1239"),
}

PASOS = ("Creado", "Pagado", "En preparación", "En camino", "Entregado")
PASTILLA = {
    "creado": ("#fef3c7", "#92400e"),
    "pagado": ("#dbeafe", "#1e40af"),
    "preparacion": ("#e0e7ff", "#3730a3"),
    "camino": ("#ffedd5", "#9a3412"),
    "entregado": ("#dcfce7", "#166534"),
    "cancelado": ("#fee2e2", "#9f1239"),
}


def aplicar_tema(raiz: tk.Misc) -> None:
    global FUENTE
    familias = set(tkfont.families(raiz))
    for candidata in ("Segoe UI", "Calibri", "Helvetica", "Arial"):
        if candidata in familias:
            FUENTE = candidata
            break
    raiz.configure(background=FONDO)
    estilo = ttk.Style(raiz)
    if "clam" in estilo.theme_names():
        estilo.theme_use("clam")
    estilo.configure(".", background=FONDO, foreground=TINTA, font=(FUENTE, 10))
    estilo.configure("TFrame", background=FONDO, borderwidth=0)
    estilo.configure("TLabel", background=FONDO, foreground=TINTA, font=(FUENTE, 10))
    estilo.configure("TLabelframe", background=FONDO, bordercolor=LINEA, relief="solid", borderwidth=1)
    estilo.configure(
        "TLabelframe.Label",
        background=FONDO,
        foreground=TINTA,
        font=(FUENTE, 11, "bold"),
    )
    estilo.configure("TCheckbutton", background=FONDO, foreground=TINTA, font=(FUENTE, 10))
    estilo.map("TCheckbutton", background=[("active", FONDO)])
    estilo.configure("TRadiobutton", background=FONDO, foreground=TINTA, font=(FUENTE, 10))
    estilo.map("TRadiobutton", background=[("active", FONDO)])
    estilo.configure("Titulo.TLabel", font=(FUENTE, 22, "bold"), background=FONDO, foreground=TINTA)
    estilo.configure("Ayuda.TLabel", font=(FUENTE, 10), background=FONDO, foreground=TINTA_SUAVE)
    estilo.configure("Ceja.TLabel", font=(FUENTE, 9, "bold"), background=FONDO, foreground=ACENTO)
    estilo.configure("Total.TLabel", font=(FUENTE, 20, "bold"), background=FONDO, foreground=ACENTO)
    estilo.configure("TEntry", padding=6)
    estilo.configure("TCombobox", padding=5)
    estilo.configure(
        "TButton",
        background=TARJETA,
        foreground=TINTA,
        padding=(12, 8),
        font=(FUENTE, 10),
        borderwidth=1,
        relief="solid",
    )
    estilo.map(
        "TButton",
        background=[("pressed", "#f5f5f4"), ("active", "#fafaf9"), ("disabled", "#f5f5f4")],
        foreground=[("disabled", "#a8a29e")],
    )
    estilo.configure(
        "Primario.TButton",
        background=ACENTO,
        foreground="#ffffff",
        padding=(14, 8),
        font=(FUENTE, 10, "bold"),
        borderwidth=0,
    )
    estilo.map(
        "Primario.TButton",
        background=[("pressed", ACENTO_ACTIVO), ("active", "#ea580c"), ("disabled", "#fdba74")],
        foreground=[("disabled", "#fff7ed")],
    )
    estilo.configure(
        "Peligro.TButton",
        background=PELIGRO_FONDO,
        foreground=PELIGRO,
        padding=(12, 8),
        font=(FUENTE, 10, "bold"),
        borderwidth=0,
    )
    estilo.map(
        "Peligro.TButton",
        background=[("pressed", "#ffe4e6"), ("active", "#ffe4e6"), ("disabled", "#f5f5f4")],
        foreground=[("disabled", "#a8a29e")],
    )
    estilo.configure(
        "Nav.TButton",
        background=OSCURO,
        foreground="#f5f5f4",
        padding=(12, 8),
        anchor="w",
        font=(FUENTE, 10),
        borderwidth=0,
        relief="flat",
    )
    estilo.map(
        "Nav.TButton",
        background=[("pressed", "#44403c"), ("active", "#292524")],
        foreground=[("pressed", "#ffffff"), ("active", "#ffffff")],
        relief=[("pressed", "flat"), ("active", "flat")],
    )
    estilo.configure(
        "NavActivo.TButton",
        background=ACENTO,
        foreground="#ffffff",
        padding=(12, 8),
        anchor="w",
        font=(FUENTE, 10, "bold"),
        borderwidth=0,
        relief="flat",
    )
    estilo.map(
        "NavActivo.TButton",
        background=[("pressed", ACENTO_ACTIVO), ("active", "#ea580c")],
        foreground=[("pressed", "#ffffff"), ("active", "#ffffff")],
        relief=[("pressed", "flat"), ("active", "flat")],
    )
    estilo.configure(
        "Treeview",
        font=(FUENTE, 10),
        rowheight=32,
        background=TARJETA,
        fieldbackground=TARJETA,
        foreground=TINTA,
        borderwidth=0,
    )
    estilo.configure(
        "Treeview.Heading",
        font=(FUENTE, 10, "bold"),
        background="#f3f1ec",
        foreground="#44403c",
        relief="flat",
        padding=8,
    )
    estilo.map("Treeview", background=[("selected", "#fed7aa")], foreground=[("selected", TINTA)])
    estilo.configure("Kpi.TFrame", background=TARJETA)
    estilo.configure("KpiEtiqueta.TLabel", background=TARJETA, foreground=TINTA_SUAVE, font=(FUENTE, 9))
    estilo.configure("KpiValor.TLabel", background=TARJETA, foreground=TINTA, font=(FUENTE, 20, "bold"))
    for nombre, (fondo, tinta) in PASTILLA.items():
        estilo.configure(f"Pastilla.{nombre}.TFrame", background=fondo)
        estilo.configure(f"Pastilla.{nombre}.TLabel", background=fondo, foreground=tinta, font=(FUENTE, 9))
        estilo.configure(
            f"PastillaValor.{nombre}.TLabel",
            background=fondo,
            foreground=tinta,
            font=(FUENTE, 16, "bold"),
        )


def activar_dpi() -> None:
    """En Windows, usa los píxeles reales de la pantalla antes de crear la ventana."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            return


def area_de_trabajo() -> tuple[int, int]:
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            rect = wintypes.RECT()
            if ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0):
                return max(rect.right - rect.left, 640), max(rect.bottom - rect.top, 480)
        except Exception:
            pass
    return 1280, 720


def texto_fluido(etiqueta: tk.Widget, margen: int = 8) -> None:
    """El texto baja de línea según el ancho real del contenedor."""

    def ajustar(evento, etiqueta=etiqueta, margen=margen) -> None:
        if evento.widget is not etiqueta.master or evento.width <= 1:
            return
        etiqueta.configure(wraplength=max(140, evento.width - margen))

    etiqueta.master.bind("<Configure>", ajustar, add="+")


def repartir(marco: tk.Misc, izquierda: tk.Widget, derecha: tk.Widget, umbral: int = 860) -> None:
    """Dos columnas cuando hay ancho; una debajo de la otra cuando la ventana es estrecha."""

    def aplicar(evento=None) -> None:
        ancho = marco.winfo_width() if evento is None else evento.width
        if ancho <= 1:
            return
        if ancho < umbral:
            izquierda.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 8))
            derecha.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=0, pady=0)
            marco.columnconfigure(0, weight=1)
            marco.columnconfigure(1, weight=0)
            marco.rowconfigure(0, weight=0)
            marco.rowconfigure(1, weight=1)
        else:
            izquierda.grid(row=0, column=0, columnspan=1, sticky="new", padx=(0, 12), pady=0)
            derecha.grid(row=0, column=1, columnspan=1, sticky="nsew", padx=0, pady=0)
            marco.columnconfigure(0, weight=0)
            marco.columnconfigure(1, weight=1)
            marco.rowconfigure(0, weight=1)
            marco.rowconfigure(1, weight=0)

    marco.bind("<Configure>", aplicar)
    marco.after_idle(aplicar)


def informar(parent: tk.Misc, titulo_aviso: str, mensaje: str) -> None:
    messagebox.showinfo(titulo_aviso, mensaje, parent=parent)


def mostrar_error(parent: tk.Misc, mensaje: str) -> None:
    messagebox.showerror("No se pudo completar", mensaje, parent=parent)


def pedir_confirmacion(parent: tk.Misc, titulo_aviso: str, mensaje: str) -> bool:
    return bool(messagebox.askyesno(titulo_aviso, mensaje, parent=parent))


def titulo(parent: tk.Misc, texto: str, bajada: str = "") -> ttk.Frame:
    marco = ttk.Frame(parent)
    marco.pack(fill="x", pady=(0, 12))
    ttk.Label(marco, text=texto, style="Titulo.TLabel").pack(anchor="w")
    if bajada:
        bajada_texto = ttk.Label(marco, text=bajada, style="Ayuda.TLabel", justify="left")
        bajada_texto.pack(fill="x", anchor="w", pady=(4, 0))
        texto_fluido(bajada_texto)
    return marco


def seccion(parent: tk.Misc, texto: str) -> ttk.LabelFrame:
    return ttk.LabelFrame(parent, text=texto, padding=14)


def boton(parent: tk.Misc, texto: str, comando, estilo: str = "TButton", **kwargs) -> ttk.Button:
    return ttk.Button(parent, text=texto, command=comando, style=estilo, cursor="hand2", **kwargs)


def entrada(
    parent: tk.Misc,
    fila: int,
    etiqueta: str,
    variable: tk.Variable,
    pista: str = "",
    ancho_pista: int = 230,
) -> ttk.Entry:
    ttk.Label(parent, text=etiqueta).grid(row=fila, column=0, sticky="nw", pady=(8, 0))
    caja = ttk.Frame(parent)
    caja.grid(row=fila, column=1, sticky="ew", padx=(12, 0), pady=(8, 0))
    campo = ttk.Entry(caja, textvariable=variable)
    campo.pack(fill="x")
    if pista:
        ttk.Label(caja, text=pista, style="Ayuda.TLabel", wraplength=ancho_pista, justify="left").pack(
            anchor="w", pady=(2, 0)
        )
    return campo


def al_pulsar_enter(widget: tk.Widget, accion) -> None:
    widget.bind("<Return>", lambda _evento: (accion(), "break")[1])


def crear_tabla(
    parent: tk.Misc,
    columnas: tuple[str, ...],
    encabezados: tuple[str, ...],
    anchos: tuple[int, ...],
    altura: int = 8,
) -> tuple[ttk.Frame, ttk.Treeview]:
    marco = ttk.Frame(parent)
    tabla = ttk.Treeview(
        marco,
        columns=columnas,
        show="headings",
        height=altura,
        selectmode="browse",
    )
    scroll_y = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    scroll_x = ttk.Scrollbar(marco, orient="horizontal", command=tabla.xview)
    tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    flexibles = {"nombre", "direccion", "detalle", "cliente", "producto"}
    for columna, encabezado, ancho in zip(columnas, encabezados, anchos):
        anchor = "e" if columna in {"precio", "stock", "disponible", "cantidad", "subtotal", "total"} else "w"
        tabla.heading(columna, text=encabezado, anchor=anchor)
        tabla.column(columna, width=ancho, minwidth=40, anchor=anchor, stretch=True if columna in flexibles else False)
    for nombre, color in COLORES_FILA.items():
        tabla.tag_configure(nombre, background=color)
    tabla.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")
    marco.rowconfigure(0, weight=1)
    marco.columnconfigure(0, weight=1)
    tabla.bind("<MouseWheel>", lambda evento: _rueda(tabla, evento))
    return marco, tabla


def _rueda(tabla: ttk.Treeview, evento: tk.Event) -> str:
    tabla.yview_scroll(int(-evento.delta / 120), "units")
    return "break"


def configurar_combo(combo: ttk.Combobox, etiquetas: list[str], actual: str) -> None:
    combo["values"] = etiquetas
    if actual in etiquetas:
        combo.set(actual)
    elif etiquetas:
        combo.current(0)
    else:
        combo.set("")


def pintar_estado(tabla: ttk.Treeview, indice: int) -> None:
    for fila, iid in enumerate(tabla.get_children()):
        valores = tabla.item(iid, "values")
        tag = "base"
        if indice < len(valores):
            tag = MAPA_ESTADO.get(str(valores[indice]), "zebra" if fila % 2 else "base")
        tabla.item(iid, tags=(tag,))


def pintar_stock(tabla: ttk.Treeview, indice: int = 4) -> bool:
    hay_agotados = False
    for fila, iid in enumerate(tabla.get_children()):
        valores = tabla.item(iid, "values")
        tag = "zebra" if fila % 2 else "base"
        if indice < len(valores):
            try:
                if int(valores[indice]) <= 0:
                    tag = "cancelado"
                    hay_agotados = True
            except (TypeError, ValueError):
                pass
        tabla.item(iid, tags=(tag,))
    return hay_agotados


def describir_condiciones(pedido) -> str:
    condiciones = []
    if pedido.es_vip:
        condiciones.append("cliente VIP")
    if pedido.hora_punta:
        condiciones.append("hora punta")
    if pedido.lluvia:
        condiciones.append("lluvia")
    if not condiciones:
        return "sin recargos ni descuento"
    return ", ".join(condiciones)


def dinero_legible(texto: str) -> str:
    return re.sub(r"\$(\d+)", lambda coincidencia: pesos(int(coincidencia.group(1))), texto)


def viñetas(texto: str) -> str:
    partes = [parte.strip() for parte in texto.split(". ") if parte.strip()]
    lineas = []
    for parte in partes:
        parte = dinero_legible(parte)
        if not parte.endswith("."):
            parte += "."
        lineas.append(f"• {parte}")
    return "\n".join(lineas)


class Aviso(tk.Frame):
    """Confirmación visible en la pantalla, sin tapar el formulario."""

    def __init__(self, master: tk.Misc):
        super().__init__(master, bg=FONDO, highlightthickness=0)
        self._etiqueta = tk.Label(
            self,
            text="",
            anchor="w",
            justify="left",
            wraplength=200,
            font=(FUENTE, 10),
            bg=FONDO,
            fg=FONDO,
        )
        self._etiqueta.pack(fill="x")
        self.pack(fill="x")
        self.bind("<Configure>", self._ajustar_ancho)

    def _ajustar_ancho(self, evento) -> None:
        if evento.widget is self and evento.width > 1:
            self._etiqueta.configure(wraplength=max(140, evento.width - 8))

    def mostrar(self, texto: str, tono: str = "ok") -> None:
        fondo, tinta = TONOS_AVISO.get(tono, TONOS_AVISO["info"])
        self.configure(bg=fondo)
        self._etiqueta.configure(text=texto, bg=fondo, fg=tinta, padx=12, pady=8)
        self.pack_configure(pady=(0, 12))

    def limpiar(self) -> None:
        self.configure(bg=FONDO)
        self._etiqueta.configure(text="", bg=FONDO, fg=FONDO, padx=0, pady=0)
        self.pack_configure(pady=0)


class Indicador(ttk.Frame):
    def __init__(self, master: tk.Misc, etiqueta: str):
        super().__init__(master, style="Kpi.TFrame", padding=(14, 12))
        ttk.Label(self, text=etiqueta, style="KpiEtiqueta.TLabel").pack(anchor="w")
        self.valor = ttk.Label(self, text="—", style="KpiValor.TLabel")
        self.valor.pack(anchor="w", pady=(2, 0))

    def fijar(self, texto: str) -> None:
        self.valor.configure(text=texto)


class Pastilla(ttk.Frame):
    def __init__(self, master: tk.Misc, etiqueta: str, tono: str):
        super().__init__(master, style=f"Pastilla.{tono}.TFrame", padding=(10, 8))
        ttk.Label(self, text=etiqueta, style=f"Pastilla.{tono}.TLabel").pack(anchor="w")
        self.valor = ttk.Label(self, text="0", style=f"PastillaValor.{tono}.TLabel")
        self.valor.pack(anchor="w")

    def fijar(self, cantidad: int) -> None:
        self.valor.configure(text=str(cantidad))


class Recorrido(tk.Frame):
    """Dónde está el pedido dentro de Creado → Entregado."""

    def __init__(self, master: tk.Misc):
        super().__init__(master, bg=FONDO, highlightthickness=0)
        self._pasos: list[tk.Label] = []
        self._celdas: list[tk.Label] = []
        for indice, nombre in enumerate(PASOS):
            if indice:
                self._celdas.append(
                    tk.Label(self, text="→", bg=FONDO, fg=TINTA_SUAVE, font=(FUENTE, 12))
                )
            etiqueta = tk.Label(
                self,
                text=nombre,
                bg="#efece6",
                fg=TINTA_SUAVE,
                font=(FUENTE, 10),
                padx=10,
                pady=6,
            )
            self._pasos.append(etiqueta)
            self._celdas.append(etiqueta)
        self.bind("<Configure>", self._recolocar)
        self.after_idle(lambda: self._recolocar_ancho(self.winfo_width()))
        self.pack(fill="x", pady=(0, 10))

    def mostrar(self, estado: str | None) -> None:
        if estado not in PASOS:
            for paso in self._pasos:
                paso.configure(bg="#efece6", fg="#a8a29e", font=(FUENTE, 10))
            return
        actual = PASOS.index(estado)
        for indice, paso in enumerate(self._pasos):
            if indice < actual:
                paso.configure(bg="#dcfce7", fg="#166534", font=(FUENTE, 10))
            elif indice == actual:
                paso.configure(bg=ACENTO, fg="#ffffff", font=(FUENTE, 10, "bold"))
            else:
                paso.configure(bg="#efece6", fg="#a8a29e", font=(FUENTE, 10))

    def _recolocar(self, evento) -> None:
        if evento.widget is not self or evento.width <= 1:
            return
        self._recolocar_ancho(evento.width)

    def _recolocar_ancho(self, disponible: int) -> None:
        if disponible <= 1:
            return
        for celda in self._celdas:
            celda.grid_forget()
        fila = 0
        columna = 0
        usado = 0
        for celda in self._celdas:
            ancho = celda.winfo_reqwidth() + 8
            if columna and usado + ancho > disponible:
                fila += 1
                columna = 0
                usado = 0
            if columna == 0 and str(celda.cget("text")) == "→":
                continue
            celda.grid(row=fila, column=columna, sticky="w", padx=(0, 4), pady=2)
            usado += ancho
            columna += 1


class Pantalla(ttk.Frame):
    """Las pantallas llaman al controlador. Las reglas viven en el modelo."""

    def __init__(self, master: tk.Misc, controlador):
        super().__init__(master, padding=(16, 12, 16, 12))
        self.controlador = controlador

    def refrescar(self) -> None:
        return None

    def ejecutar(self, accion):
        try:
            return True, accion()
        except (ReglaNegocioError, PersistenciaError) as error:
            mostrar_error(self.winfo_toplevel(), str(error))
            return False, None


__all__ = [
    "ATAJOS",
    "Aviso",
    "FONDO",
    "FUENTE",
    "GRUPOS",
    "Indicador",
    "LINEA",
    "MAPA_ESTADO",
    "MODULOS",
    "OSCURO",
    "Pantalla",
    "Pastilla",
    "Recorrido",
    "TINTA_SUAVE",
    "al_pulsar_enter",
    "aplicar_tema",
    "boton",
    "configurar_combo",
    "crear_tabla",
    "describir_condiciones",
    "dinero_legible",
    "entrada",
    "informar",
    "mostrar_error",
    "pedir_confirmacion",
    "pesos",
    "pintar_estado",
    "pintar_stock",
    "seccion",
    "titulo",
    "viñetas",
]
