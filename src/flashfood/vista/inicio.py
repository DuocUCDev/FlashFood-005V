"""Pantalla de inicio: estado de la operación y accesos al flujo."""

import tkinter as tk
from tkinter import ttk

from flashfood.vista.comun import (
    ATAJOS,
    MODULOS,
    Indicador,
    MAPA_ESTADO,
    Pantalla,
    Pastilla,
    boton,
    repartir,
    seccion,
    texto_fluido,
    titulo,
    viñetas,
)


class Inicio(Pantalla):
    def __init__(self, master, controlador, navegar, al_cambiar_condiciones=None):
        super().__init__(master, controlador)
        self._navegar = navegar
        self._al_cambiar = al_cambiar_condiciones
        self._sincronizando = False
        titulo(
            self,
            "Operación 13:00",
            "Arma el pedido, cobra, prepara y despacha. El stock baja solo cuando el pago se aprueba.",
        )

        self.metricas = ttk.Frame(self)
        self.metricas.pack(fill="x", pady=(0, 10))
        self.indicadores = {}
        for clave, etiqueta in (
            ("productos", "Productos"),
            ("clientes", "Clientes"),
            ("disponibles", "Repartidores libres"),
            ("activos", "Pedidos en curso"),
        ):
            self.indicadores[clave] = Indicador(self.metricas, etiqueta)
        self.metricas.bind("<Configure>", self._recolocar_metricas)

        self.estados = ttk.Frame(self)
        self.estados.pack(fill="x", pady=(0, 12))
        self.pastillas = {}
        nombres = ("Creado", "Pagado", "En preparación", "En camino", "Entregado", "Cancelado")
        for nombre in nombres:
            self.pastillas[nombre] = Pastilla(self.estados, nombre, MAPA_ESTADO[nombre])
        self.estados.bind("<Configure>", self._recolocar_estados)

        paneles = ttk.Frame(self)
        paneles.columnconfigure(0, weight=1)
        paneles.columnconfigure(1, weight=1)

        condiciones = seccion(paneles, "Condiciones del despacho")
        condiciones.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        aviso_condiciones = ttk.Label(
            condiciones,
            text="Se guardan al marcarlas y entran solo en los pedidos que crees después. Los que ya existen no cambian.",
            style="Ayuda.TLabel",
            justify="left",
        )
        aviso_condiciones.pack(fill="x", anchor="w", pady=(0, 8))
        texto_fluido(aviso_condiciones)
        self.hora_punta = tk.BooleanVar()
        self.lluvia = tk.BooleanVar()
        ttk.Checkbutton(
            condiciones,
            text="Aplicar hora punta",
            variable=self.hora_punta,
            command=self.aplicar_condiciones,
        ).pack(anchor="w")
        ttk.Checkbutton(
            condiciones,
            text="Aplicar recargo por lluvia",
            variable=self.lluvia,
            command=self.aplicar_condiciones,
        ).pack(anchor="w", pady=(6, 8))
        self.efecto = ttk.Label(condiciones, style="Ayuda.TLabel", justify="left")
        self.efecto.pack(fill="x", anchor="w")
        texto_fluido(self.efecto)

        calculo = seccion(paneles, "Cómo se calcula")
        calculo.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.reglas = ttk.Label(calculo, style="Ayuda.TLabel", justify="left")
        self.reglas.pack(fill="x", anchor="w")
        texto_fluido(self.reglas)

        etiquetas = dict(MODULOS)
        acceso = ttk.Frame(self)
        acceso.pack(fill="x", pady=(0, 12))
        grupos = []
        for nombre_grupo, items in ATAJOS:
            grupo = seccion(acceso, nombre_grupo)
            grupo.columnconfigure(1, weight=1)
            grupos.append(grupo)
            for fila, (clave, detalle) in enumerate(items):
                estilo = "Primario.TButton" if clave == "pedidos" else "TButton"
                boton(grupo, etiquetas[clave], lambda destino=clave: self._navegar(destino), estilo).grid(
                    row=fila, column=0, sticky="ew", pady=(8 if fila else 0, 0)
                )
                ayuda = ttk.Label(grupo, text=detalle, style="Ayuda.TLabel", justify="left")
                ayuda.grid(row=fila, column=1, sticky="ew", padx=(12, 0), pady=(8 if fila else 0, 0))
                texto_fluido(ayuda, margen=4)
        repartir(acceso, grupos[0], grupos[1], umbral=820)
        repartir(paneles, condiciones, calculo, umbral=820)
        paneles.pack(fill="x")

    def _recolocar_metricas(self, evento) -> None:
        if evento.widget is not self.metricas or evento.width <= 1:
            return
        columnas = 2 if evento.width < 760 else 4
        for indice, indicador in enumerate(self.indicadores.values()):
            fila, columna = divmod(indice, columnas)
            indicador.grid(
                row=fila,
                column=columna,
                sticky="ew",
                padx=(0 if columna == 0 else 8, 0),
                pady=(8 if fila else 0, 0),
            )
        for columna in range(4):
            self.metricas.columnconfigure(columna, weight=1 if columna < columnas else 0)

    def _recolocar_estados(self, evento) -> None:
        if evento.widget is not self.estados or evento.width <= 1:
            return
        columnas = 3 if evento.width < 760 else 6
        for indice, pastilla in enumerate(self.pastillas.values()):
            fila, columna = divmod(indice, columnas)
            pastilla.grid(
                row=fila,
                column=columna,
                sticky="ew",
                padx=(0 if columna == 0 else 6, 0),
                pady=(6 if fila else 0, 0),
            )
        for columna in range(6):
            self.estados.columnconfigure(columna, weight=1 if columna < columnas else 0)

    def refrescar(self) -> None:
        self.reglas.configure(text=viñetas(self.controlador.reglas()))
        self._sincronizando = True
        self.hora_punta.set(self.controlador.hora_punta)
        self.lluvia.set(self.controlador.lluvia)
        self._sincronizando = False
        self.efecto.configure(text=self._texto_efecto())
        datos = self.controlador.resumen()
        en_curso = sum(
            cantidad
            for estado, cantidad in datos["pedidos"].items()
            if estado not in {"Entregado", "Cancelado"}
        )
        self.indicadores["productos"].fijar(str(datos["productos"]))
        self.indicadores["clientes"].fijar(str(datos["clientes"]))
        self.indicadores["disponibles"].fijar(f"{datos['disponibles']} de {datos['repartidores']}")
        self.indicadores["activos"].fijar(str(en_curso))
        for estado, pastilla in self.pastillas.items():
            pastilla.fijar(datos["pedidos"].get(estado, 0))

    def _texto_efecto(self) -> str:
        hora = bool(self.hora_punta.get())
        lluvia = bool(self.lluvia.get())
        if hora and lluvia:
            return "Los pedidos que crees ahora incluirán hora punta y lluvia."
        if hora:
            return "Los pedidos que crees ahora incluirán hora punta."
        if lluvia:
            return "Los pedidos que crees ahora incluirán el recargo por lluvia."
        return "Los pedidos que crees ahora llevarán el despacho base, sin recargos."

    def aplicar_condiciones(self) -> None:
        if self._sincronizando:
            return
        self.ejecutar(
            lambda: self.controlador.definir_condiciones(bool(self.hora_punta.get()), bool(self.lluvia.get()))
        )
        self.refrescar()
        if self._al_cambiar:
            self._al_cambiar()
