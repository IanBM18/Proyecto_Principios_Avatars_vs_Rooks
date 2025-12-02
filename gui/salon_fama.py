import tkinter as tk
from tkinter import ttk
import json
import os
import queue
import time
from gui.menu_principal import MainMenu
from assets.MusicManager import MusicManager
from gui.ventanaimagen import VentanaImagen
from hardware import PicoController


class HallOfFameWindow:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol

        # Archivo principal de mejores puntajes
        self.ruta_salon_fama = os.path.join("DATA", "salon_fama.json")
        # Respaldo: historial completo de puntuaciones
        self.ruta_puntuaciones = os.path.join("DATA", "puntuaciones.json")

        # 🎵 Recuperar la música en ejecución sin reiniciarla
        self.music = MusicManager()  # 👈 SOLO esto, sin .play()

        # 🪟 Configuración de ventana
        self.root = tk.Tk()
        self.root.title("Salón de la Fama - Avatars VS Rooks")
        self.ventana_imagen = VentanaImagen(
            self.root, ruta_imagen="assets/fondos/fondopre1.png"
        )
        # Ventana ligeramente más compacta
        self.root.geometry("800x600")
        self.root.config(bg="#1c1c1c")

        tk.Label(
            self.root,
            text="🏆 Salón de la Fama 🏆",
            font=("Arial", 20, "bold"),
            bg="#1c1c1c",
            fg="gold",
        ).pack(pady=25)

        # Contenedor centrado para la tabla (sin scrollbar)
        self.frame_puntajes = tk.Frame(self.root, bg="#1c1c1c")
        self.frame_puntajes.pack(pady=10)

        # Variables para control de scroll ya no necesarias (sin scrollbar)
        
        self._crear_tabla()
        self._cargar_puntajes()

        self.btn_volver = tk.Button(
            self.root,
            text="⬅ Volver al Menú",
            bg="#444",
            fg="white",
            font=("Arial", 12),
            command=self.volver_menu,
        )
        self.btn_volver.pack(side=tk.BOTTOM, anchor=tk.SE, pady=20, padx=20)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._setup_controller()

        self.root.mainloop()

    # ------------------------------------------------------------------
    # 📊 Tabla de mejores puntajes
    # ------------------------------------------------------------------

    def _crear_tabla(self):
        # Columnas: posición, usuario, puntaje y tiempo empleado
        columnas = ("posicion", "usuario", "score", "tiempo")

        # Frame para tabla (sin scrollbar)
        frame_tabla = tk.Frame(self.frame_puntajes, bg="#1c1c1c")
        frame_tabla.pack()

        self.tree = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            height=10,  # Mostrar 10 filas para ver todos los puntajes sin scroll
        )

        self.tree.heading("posicion", text="#")
        self.tree.heading("usuario", text="Usuario")
        self.tree.heading("score", text="Puntaje")
        self.tree.heading("tiempo", text="Tiempo")

        # Columnas más angostas para una tabla compacta
        self.tree.column("posicion", width=40, anchor="center")
        self.tree.column("usuario", width=200, anchor="w")
        self.tree.column("score", width=90, anchor="center")
        self.tree.column("tiempo", width=120, anchor="center")

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview",
            background="#222222",
            foreground="white",
            fieldbackground="#222222",
            rowheight=26,
        )
        estilo.configure("Treeview.Heading", background="#333333", foreground="gold")

        # Sin scrollbar - la tabla muestra todos los 10 puntajes directamente
        # Empaquetar solo la tabla
        self.tree.pack(padx=10, pady=5)

    def _leer_archivo(self, ruta):
        if not os.path.exists(ruta):
            return []
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _cargar_puntajes(self):
        # Priorizar el archivo específico de salón de la fama
        puntajes = self._leer_archivo(self.ruta_salon_fama)

        # Si está vacío, caer al historial general de puntuaciones
        if not puntajes:
            puntajes = self._leer_archivo(self.ruta_puntuaciones)

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not puntajes:
            self.tree.insert(
                "",
                "end",
                values=("", "No hay puntajes registrados todavía.", "", ""),
            )
            return

        # Ordenar por menor tiempo (y a igualdad de tiempo, mayor puntaje)
        def clave_orden(p):
            # tiempo puede venir como "tiempo" o "time" (en segundos)
            t = p.get("tiempo")
            if t is None:
                t = p.get("time")
            # si no hay tiempo, mandarlo al final
            if not isinstance(t, (int, float)):
                t = float("inf")
            score = p.get("score", 0)
            return (t, -score)

        # Limitar a solo los primeros 10 puntajes
        puntajes_ordenados = sorted(puntajes, key=clave_orden)[:10]

        for idx, p in enumerate(puntajes_ordenados, start=1):
            usuario = p.get("usuario", "Desconocido")
            score = p.get("score", 0)

            t = p.get("tiempo")
            if t is None:
                t = p.get("time")

            # Formato de tiempo simple: "Xs" (segundos) o "-" si no hay dato
            if isinstance(t, (int, float)):
                tiempo_str = f"{t:.0f} s"
            else:
                tiempo_str = "-"

            self.tree.insert(
                "",
                "end",
                values=(idx, usuario, score, tiempo_str),
            )

    # ------------------------------------------------------------------
    # 🔙 Navegación
    # ------------------------------------------------------------------

    def volver_menu(self):
        self._shutdown_controller()
        self.root.destroy()
        MainMenu(self.usuario, self.rol)

    # ------------------------------------------------------------------
    # 🎮 Integración con el control físico
    # ------------------------------------------------------------------

    def _setup_controller(self) -> None:
        self.controller_queue: queue.Queue[str] = queue.Queue()
        self.controller = PicoController(self.controller_queue)
        self.controller.start()
        self.root.after(50, self._process_controller_events)

    def _process_controller_events(self) -> None:
        if hasattr(self, "controller_queue"):
            while not self.controller_queue.empty():
                event = self.controller_queue.get()
                self._handle_controller_event(event)
        self.root.after(50, self._process_controller_events)

    def _handle_controller_event(self, event: str) -> None:
        event = event.upper()
        current_time = time.time()
        
        # Filtrar eventos vacíos
        if not event or event == "NONE" or len(event.strip()) == 0:
            return
        
        # Ya no hay scroll - todos los puntajes son visibles directamente
        # Los eventos UP/DOWN se ignoran aquí
        
        # Botón DERECHA (GP4) = Volver al menú principal
        if event == "BACK":
            self.volver_menu()

    def _shutdown_controller(self) -> None:
        if getattr(self, "controller", None):
            self.controller.stop()
            self.controller = None

    def _on_close(self) -> None:
        self._shutdown_controller()
        self.root.destroy()