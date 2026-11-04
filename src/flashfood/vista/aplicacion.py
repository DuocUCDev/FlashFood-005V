"""Ventana principal y menú de navegación."""

import tkinter as tk
from tkinter import ttk

from flashfood.controladores.controlador import Controlador
from flashfood.vista import comun
from flashfood.vista.clientes import Clientes
from flashfood.vista.comun import GRUPOS, MODULOS, activar_dpi, aplicar_tema, area_de_trabajo, informar
from flashfood.vista.detalle import Detalle
from flashfood.vista.inicio import Inicio
from flashfood.vista.pagos import Pagos
from flashfood.vista.pedidos import Pedidos
from flashfood.vista.productos import Productos
from flashfood.vista.repartidores import Repartidores
from flashfood.vista.seguimiento import Seguimiento


class Aplicacion(tk.Tk):
    def __init__(self, controlador: Controlador):
        activar_dpi()
        super().__init__()
        self.controlador = controlador
        self.title("FlashFood — Operación 13:00")
        self._encajar_en_pantalla()
        aplicar_tema(self)
        self._crear_menu()
        etiquetas = dict(MODULOS)
        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)
        barra = tk.Frame(cuerpo, bg=comun.OSCURO, width=208, height=400)
        barra.pack(side="left", fill="y")
        barra.pack_propagate(False)
        marca = tk.Frame(barra, bg=comun.OSCURO)
        pie = tk.Frame(barra, bg=comun.OSCURO)
        pie.pack(side="bottom", fill="x")
        self._estado_operacion = tk.Label(
            pie,
            text="",
            bg=comun.OSCURO,
            fg="#f5f5f4",
            font=(comun.FUENTE, 9),
            anchor="w",
            justify="left",
            wraplength=180,
        )
        self._estado_operacion.pack(fill="x", padx=16, pady=(8, 2))
        tk.Label(
            pie,
            text="Cada cambio queda guardado.",
            bg=comun.OSCURO,
            fg="#a8a29e",
            font=(comun.FUENTE, 9),
            anchor="w",
            justify="left",
            wraplength=180,
        ).pack(fill="x", padx=16, pady=(0, 12))
        marca.pack(side="top", fill="x", padx=16, pady=(16, 6))
        tk.Label(
            marca,
            text="FlashFood",
            bg=comun.OSCURO,
            fg="#ffffff",
            font=(comun.FUENTE, 18, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            marca,
            text="Operación 13:00",
            bg=comun.OSCURO,
            fg="#a8a29e",
            font=(comun.FUENTE, 10),
            anchor="w",
        ).pack(fill="x", pady=(2, 0))
        self._nav_lienzo = tk.Canvas(barra, bg=comun.OSCURO, highlightthickness=0, borderwidth=0)
        self._nav_lienzo.pack(side="top", fill="both", expand=True)
        navegacion = tk.Frame(self._nav_lienzo, bg=comun.OSCURO)
        self._nav_ventana = self._nav_lienzo.create_window((0, 0), window=navegacion, anchor="nw")
        navegacion.bind("<Configure>", self._ajustar_nav)
        self._nav_lienzo.bind("<Configure>", self._ajustar_nav_ancho)
        self._botones_nav = {}
        for titulo_grupo, claves in GRUPOS:
            if titulo_grupo:
                tk.Label(
                    navegacion,
                    text=titulo_grupo.upper(),
                    bg=comun.OSCURO,
                    fg="#a8a29e",
                    font=(comun.FUENTE, 8, "bold"),
                    anchor="w",
                ).pack(fill="x", padx=18, pady=(16, 4))
            for clave in claves:
                boton = ttk.Button(
                    navegacion,
                    text=etiquetas[clave],
                    style="Nav.TButton",
                    cursor="hand2",
                    command=lambda destino=clave: self.abrir(destino),
                )
                boton.pack(fill="x", padx=10, pady=2)
                self._botones_nav[clave] = boton
        linea = tk.Frame(cuerpo, bg=comun.LINEA, width=1)
        linea.pack_propagate(False)
        linea.pack(side="left", fill="y")
        self._lienzo = tk.Canvas(cuerpo, bg=comun.FONDO, highlightthickness=0, borderwidth=0)
        self._scroll_y = ttk.Scrollbar(cuerpo, orient="vertical", command=self._lienzo.yview)
        self._lienzo.configure(yscrollcommand=self._scroll_y.set)
        self._scroll_y.pack(side="right", fill="y")
        self._lienzo.pack(side="left", fill="both", expand=True)
        self._contenido = ttk.Frame(self._lienzo)
        self._ventana = self._lienzo.create_window((0, 0), window=self._contenido, anchor="nw")
        self._ajustando = False
        self._lienzo.bind("<Configure>", self._ajustar_vista)
        self.bind_all("<MouseWheel>", self._rueda)
        self.bind_all("<Button-4>", self._rueda)
        self.bind_all("<Button-5>", self._rueda)
        self._pantallas = {
            "inicio": Inicio(self._contenido, controlador, self.abrir, self.actualizar_pie),
            "productos": Productos(self._contenido, controlador),
            "clientes": Clientes(self._contenido, controlador),
            "pedidos": Pedidos(self._contenido, controlador, self.abrir),
            "detalle": Detalle(self._contenido, controlador),
            "pagos": Pagos(self._contenido, controlador),
            "repartidores": Repartidores(self._contenido, controlador),
            "seguimiento": Seguimiento(self._contenido, controlador, self.abrir),
        }
        self._actual = None
        self.mostrar("inicio")

    def _crear_menu(self) -> None:
        etiquetas = dict(MODULOS)
        barra = tk.Menu(self)
        archivo = tk.Menu(barra, tearoff=0)
        archivo.add_command(label="Salir", command=self.destroy)
        barra.add_cascade(label="Archivo", menu=archivo)
        modulos = tk.Menu(barra, tearoff=0)
        primero = True
        for _titulo, claves in GRUPOS:
            if not primero:
                modulos.add_separator()
            primero = False
            for clave in claves:
                modulos.add_command(label=etiquetas[clave], command=lambda destino=clave: self.abrir(destino))
        barra.add_cascade(label="Módulos", menu=modulos)
        self.configure(menu=barra)

    def _encajar_en_pantalla(self) -> None:
        disponible_ancho, disponible_alto = area_de_trabajo()
        ancho = max(640, min(1440, disponible_ancho - 16))
        alto = max(480, min(960, disponible_alto - 16))
        self.minsize(min(860, ancho), min(500, alto))
        self.geometry(f"{ancho}x{alto}+0+0")
        self.resizable(True, True)

    def _ajustar_nav(self, _evento=None) -> None:
        region = self._nav_lienzo.bbox("all")
        if region is not None:
            self._nav_lienzo.configure(scrollregion=region)

    def _ajustar_nav_ancho(self, evento) -> None:
        self._nav_lienzo.itemconfigure(self._nav_ventana, width=evento.width)

    def _dentro_de(self, widget, ancestro) -> bool:
        actual = widget
        while actual is not None:
            if actual == ancestro:
                return True
            actual = getattr(actual, "master", None)
        return False

    def _pasos_rueda(self, evento) -> int:
        delta = getattr(evento, "delta", 0)
        if delta:
            return -1 if delta > 0 else 1
        if getattr(evento, "num", None) == 4:
            return -1
        if getattr(evento, "num", None) == 5:
            return 1
        return 0

    def _ajustar_vista(self, _evento=None) -> None:
        if self._ajustando:
            return
        ancho_vista = self._lienzo.winfo_width()
        alto_vista = self._lienzo.winfo_height()
        if ancho_vista <= 1 or alto_vista <= 1:
            return
        self._ajustando = True
        try:
            self._lienzo.itemconfigure(self._ventana, width=ancho_vista)
            self.update_idletasks()
            alto = max(alto_vista, self._contenido.winfo_reqheight())
            self._lienzo.itemconfigure(self._ventana, width=ancho_vista, height=alto)
            self.update_idletasks()
            alto = max(alto_vista, self._contenido.winfo_reqheight())
            self._lienzo.itemconfigure(self._ventana, width=ancho_vista, height=alto)
            self._lienzo.configure(scrollregion=(0, 0, ancho_vista, alto))
        finally:
            self._ajustando = False

    def _rueda(self, evento) -> str | None:
        pasos = self._pasos_rueda(evento)
        if not pasos or isinstance(evento.widget, ttk.Treeview):
            return None
        if self._dentro_de(evento.widget, self._nav_lienzo):
            self._nav_lienzo.yview_scroll(pasos, "units")
            return "break"
        self._lienzo.yview_scroll(pasos, "units")
        return "break"

    def actualizar_pie(self) -> None:
        hora = "Hora punta activa" if self.controlador.hora_punta else "Sin hora punta"
        lluvia = "Lluvia activa" if self.controlador.lluvia else "Sin lluvia"
        self._estado_operacion.configure(text=f"Pedidos nuevos\n{hora}\n{lluvia}")

    def abrir(self, destino: str, pedido_id: str | None = None) -> None:
        pantalla = self._pantallas.get(destino)
        if pedido_id and pantalla is not None and hasattr(pantalla, "preseleccionar"):
            pantalla.preseleccionar(pedido_id)
        self.mostrar(destino)

    def mostrar(self, nombre: str) -> None:
        if self._actual is not None:
            self._actual.pack_forget()
        pantalla = self._pantallas[nombre]
        pantalla.refrescar()
        pantalla.pack(fill="both", expand=True)
        self._actual = pantalla
        self.after_idle(self._ajustar_vista)
        self._lienzo.yview_moveto(0)
        for clave, boton in self._botones_nav.items():
            boton.configure(style="NavActivo.TButton" if clave == nombre else "Nav.TButton")
        self.actualizar_pie()


def iniciar(directorio=None) -> None:
    controlador = Controlador(directorio)
    aplicacion = Aplicacion(controlador)
    if controlador.advertencia:
        aplicacion.after(200, lambda: informar(aplicacion, "Datos", controlador.advertencia))
    aplicacion.mainloop()
