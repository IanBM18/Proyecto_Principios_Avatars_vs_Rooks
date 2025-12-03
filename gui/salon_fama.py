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

# --- Dropbox ---
from dropbox_manager import DropboxManager


class HallOfFameWindow:
    RUTA_SALON = os.path.join("DATA", "salon_fama.json")

    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol
        self.music = MusicManager()

        # Ventanas
        self.root = tk.Tk()
        self.root.title("Salón de la Fama - Avatars VS Rooks")
        self.root.geometry("900x700")
        self.root.resizable(False, False)

        # Fondo SIEMPRE atrás
        self.ventana_imagen = VentanaImagen(self.root, ruta_imagen="assets/fondos/fondopre1.png")
        if self.ventana_imagen.label_fondo:
            self.ventana_imagen.label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
            self.ventana_imagen.label_fondo.lower()

        # Título
        tk.Label(
            self.root,
            text="🏆 SALÓN DE LA FAMA 🏆",
            font=("Arial", 28, "bold"),
            bg="#1c1c1c",
            fg="gold",
        ).pack(pady=25)

        # Frame de puntajes (adelante)
        self.frame_puntajes = tk.Frame(self.root, bg="#1c1c1c")
        self.frame_puntajes.pack(pady=10)

        # Sincronizar y cargar puntajes
        self.sincronizar_desde_nube()
        self.cargar_puntajes()

        # Botón volver SIEMPRE visible
        btn = tk.Button(
            self.root,
            text="⬅ Volver al Menú",
            bg="#444",
            fg="white",
            font=("Arial", 14),
            command=self.volver_menu
        )
        btn.place(relx=0.95, rely=0.95, anchor="se")

        def bring_button_front():
            btn.lift()
            self.root.after(100, bring_button_front)

        bring_button_front()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._setup_controller()

        self.root.mainloop()

    # ================================
    # DESCARGAR DE DROPBOX → LOCAL
    # ================================
    def sincronizar_desde_nube(self):
        try:
            datos = DropboxManager.descargar_json("salon_fama.json")

            # Reparar formatos incorrectos
            if not isinstance(datos, list):
                datos = []

            os.makedirs("DATA", exist_ok=True)
            with open(self.RUTA_SALON, "w") as f:
                json.dump(datos, f, indent=4)

        except Exception as e:
            print(f"⚠ Error al sincronizar desde Dropbox: {e}")
            print("Usando datos locales.")

    # ================================
    # CARGAR Y MOSTRAR PUNTAJES
    # ================================
    def cargar_puntajes(self):
        # Leer archivo local
        if not os.path.exists(self.RUTA_SALON):
            with open(self.RUTA_SALON, "w") as f:
                json.dump([], f)

        try:
            with open(self.RUTA_SALON, "r") as f:
                registros = json.load(f)
        except:
            registros = []

        # Reparar formato
        if not isinstance(registros, list):
            registros = []

        # --- 🔥 Filtrar mejor tiempo por usuario ---
        mejores = {}
        for r in registros:
            user = r["usuario"]
            time = r["tiempo"]

            if user not in mejores or time < mejores[user]["tiempo"]:
                mejores[user] = r

        # Convertir diccionario → lista
        lista_final = list(mejores.values())

        # Ordenar (mejores tiempos primero)
        lista_ordenada = sorted(lista_final, key=lambda x: x["tiempo"])

        # Limpiar frame
        for widget in self.frame_puntajes.winfo_children():
            widget.destroy()

        if len(lista_ordenada) == 0:
            tk.Label(
                self.frame_puntajes, text="No hay registros todavía.",
                bg="#1c1c1c", fg="white", font=("Arial", 16)
            ).pack()
            return

        # Mostrar lista final
        for i, entry in enumerate(lista_ordenada, start=1):
            texto = f"{i}. 👤 {entry['usuario']} - ⏱ {entry['tiempo']:.2f} s"
            tk.Label(
                self.frame_puntajes,
                text=texto,
                bg="#1c1c1c",
                fg="white",
                font=("Arial", 16)
            ).pack(anchor="w", padx=20, pady=5)

    # ================================
    # REGISTRAR TIEMPO
    # ================================
    @staticmethod
    def registrar_tiempo(usuario, tiempo):
        # Descargar lista existente
        data = DropboxManager.descargar_json("salon_fama.json")
        if not isinstance(data, list):
            data = []

        # Buscar si el usuario ya tiene un tiempo guardado
        encontrado = False
        for entry in data:
            if entry["usuario"] == usuario:
                encontrado = True
                # reemplazar solo si es mejor tiempo
                if tiempo < entry["tiempo"]:
                    entry["tiempo"] = tiempo
                break

        # Si no existía, agregarlo
        if not encontrado:
            data.append({"usuario": usuario, "tiempo": tiempo})

        # 🔥 Guardar localmente
        os.makedirs("DATA", exist_ok=True)
        with open(HallOfFameWindow.RUTA_SALON, "w") as f:
            json.dump(data, f, indent=4)

        # 🔥 Subir actualizado a Dropbox
        DropboxManager.subir_json("salon_fama.json", data)

        print("✔ Tiempo registrado correctamente.")


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