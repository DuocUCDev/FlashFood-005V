"""Elección de la persistencia: archivos JSON o base de datos MySQL."""

import tkinter as tk
from tkinter import ttk

from flashfood.vista.comun import (
    Aviso,
    Pantalla,
    al_pulsar_enter,
    boton,
    entrada,
    mostrar_error,
    repartir,
    seccion,
    texto_fluido,
    titulo,
)


class Configuracion(Pantalla):
    def __init__(self, master, controlador, al_aplicar=None):
        super().__init__(master, controlador)
        self._al_aplicar = al_aplicar
        titulo(
            self,
            "Configuración",
            "Elige dónde guarda FlashFood sus datos. El cambio se aplica al instante y queda guardado para la próxima vez.",
        )
        self.aviso = Aviso(self)
        columnas = ttk.Frame(self)
        columnas.pack(fill="both", expand=True)

        formulario = seccion(columnas, "Dónde se guardan los datos")
        self.motor = tk.StringVar(value="json")
        motores = ttk.Frame(formulario)
        motores.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        ttk.Radiobutton(
            motores,
            text="Archivos JSON (carpeta data/)",
            value="json",
            variable=self.motor,
            command=self.mostrar_campos,
        ).pack(anchor="w")
        ttk.Radiobutton(
            motores,
            text="Base de datos MySQL (XAMPP)",
            value="mysql",
            variable=self.motor,
            command=self.mostrar_campos,
        ).pack(anchor="w", pady=(6, 0))
        self.host = tk.StringVar()
        self.puerto = tk.StringVar()
        self.usuario = tk.StringVar()
        self.contrasena = tk.StringVar()
        self.base_datos = tk.StringVar()
        self._campos = [
            entrada(formulario, 1, "Servidor", self.host, "En XAMPP: 127.0.0.1."),
            entrada(formulario, 2, "Puerto", self.puerto, "En XAMPP: 3306."),
            entrada(formulario, 3, "Usuario", self.usuario, "En XAMPP: root."),
            entrada(formulario, 4, "Contraseña", self.contrasena, "En XAMPP recién instalado va vacía."),
            entrada(formulario, 5, "Base de datos", self.base_datos, "La que crea el script: flashfood."),
        ]
        self._campos[3].configure(show="•")
        acciones = ttk.Frame(formulario)
        acciones.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        self.boton_probar = boton(acciones, "Probar conexión", self.probar)
        self.boton_deshacer = boton(acciones, "Deshacer", self.deshacer)
        self.boton_guardar = boton(acciones, "Guardar y aplicar", self.guardar, "Primario.TButton")
        self.boton_probar.pack(side="left")
        self.boton_guardar.pack(side="right")
        self.boton_deshacer.pack(side="right", padx=(8, 8))
        formulario.columnconfigure(1, weight=1)

        en_uso = seccion(columnas, "En uso")
        self.estado = ttk.Label(en_uso, justify="left")
        self.estado.pack(fill="x", anchor="w", pady=(0, 10))
        texto_fluido(self.estado, margen=36)
        nota = ttk.Label(
            en_uso,
            text=(
                "Las tablas se crean con database/01_esquema.sql y los datos de ejemplo con "
                "database/02_datos_ejemplo.sql.\n\n"
                "Los datos de JSON y de MySQL son independientes: cambiar de uno a otro no copia registros.\n\n"
                "La contraseña queda en texto plano en config.ini, que no se sube al repositorio."
            ),
            style="Ayuda.TLabel",
            justify="left",
        )
        nota.pack(fill="x", anchor="w")
        texto_fluido(nota, margen=36)
        repartir(columnas, formulario, en_uso)
        for campo in self._campos:
            al_pulsar_enter(campo, self.guardar)
        self.refrescar()

    def refrescar(self) -> None:
        configuracion = self.controlador.configuracion
        self.motor.set(configuracion.motor)
        self.host.set(configuracion.mysql.host)
        self.puerto.set(str(configuracion.mysql.puerto))
        self.usuario.set(configuracion.mysql.usuario)
        self.contrasena.set(configuracion.mysql.contrasena)
        self.base_datos.set(configuracion.mysql.base_datos)
        lineas = [
            f"En uso: {self.controlador.origen_datos}",
            f"Archivo: {self.controlador.archivo_configuracion}",
        ]
        if self.controlador.motor_activo != configuracion.motor:
            lineas.append(
                "Atención: la configuración guardada pide MySQL, pero se está trabajando con JSON "
                "porque no se pudo conectar."
            )
        self.estado.configure(text="\n".join(lineas))
        self.mostrar_campos()

    def deshacer(self) -> None:
        self.aviso.limpiar()
        self.refrescar()

    def mostrar_campos(self) -> None:
        estado = "normal" if self.motor.get() == "mysql" else "disabled"
        for campo in self._campos:
            campo.configure(state=estado)
        self.boton_probar.configure(state=estado)

    def _conexion(self) -> tuple[str, str, str, str, str]:
        return (
            self.host.get(),
            self.puerto.get(),
            self.usuario.get(),
            self.contrasena.get(),
            self.base_datos.get(),
        )

    def probar(self) -> None:
        self.aviso.limpiar()
        if self.motor.get() != "mysql":
            mostrar_error(self.winfo_toplevel(), "Elige Base de datos MySQL para probar la conexión.")
            return
        ok, version = self.ejecutar(lambda: self.controlador.probar_mysql(*self._conexion()))
        if not ok:
            return
        self.aviso.mostrar(f"Conexión correcta: MySQL respondió (versión {version}) y las tablas de FlashFood existen.")

    def guardar(self) -> None:
        self.aviso.limpiar()
        ok, _resultado = self.ejecutar(
            lambda: self.controlador.aplicar_configuracion(self.motor.get(), *self._conexion())
        )
        if not ok:
            return
        self.refrescar()
        if self._al_aplicar is not None:
            self._al_aplicar()
        self.aviso.mostrar(f"FlashFood ahora trabaja con {self.controlador.origen_datos}.")
