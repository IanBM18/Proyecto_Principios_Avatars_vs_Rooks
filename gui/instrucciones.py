import tkinter as tk
import queue
from gui.menu_principal import MainMenu
from assets.MusicManager import MusicManager
from gui.ventanaimagen import VentanaImagen
from hardware import PicoController

class InstructionsWindow:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol

        # 🎵 Recuperar la música en ejecución sin reiniciarla
        self.music = MusicManager()  # 👈 SOLO esto, sin llamar a play()

        self.root = tk.Tk()
        self.root.title("Instrucciones - Avatars VS Rooks")
        self.ventana_imagen = VentanaImagen(self.root, ruta_imagen="assets/fondos/fondopre1.png")
        self.root.geometry("600x450+560+240")
        self.root.config(bg="#1e1e1e")

        tk.Label(
            self.root,
            text="📘 Instrucciones del Juego",
            font=("Arial", 18, "bold"),
            bg="#1e1e1e",
            fg="lightblue"
        ).pack(pady=20)

        instrucciones = (
            "1️⃣ El juego se desarrolla en una matriz de 9x5.\n\n"
            "2️⃣ Cada jugador controla un conjunto de piezas.\n\n"
            "3️⃣ El objetivo es derrotar a las piezas enemigas o capturar su base.\n\n"
            "4️⃣ Usa el teclado o el mouse para moverte según las reglas del modo.\n\n"
            "5️⃣ Pulsa 'ESC' para salir de la partida y regresar al menú principal.\n\n"
            "6️⃣ Los puntajes se guardan automáticamente al finalizar cada juego.\n\n"
            "¡Buena suerte, estratega! 🧠⚔️"
        )

        tk.Message(
            self.root,
            text=instrucciones,
            bg="#1e1e1e",
            fg="white",
            width=500,
            font=("Arial", 12),
            justify="left"
        ).pack(padx=30, pady=10)

        self.btn_volver = tk.Button(
            self.root,
            text="⬅ Volver al Menú",
            bg="#444",
            fg="white",
            font=("Arial", 12),
            command=self.volver_menu
        )
        self.btn_volver.pack(pady=20)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._setup_controller()

        self.root.mainloop()

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
        if event == "SELECT":
            self.volver_menu()
        elif event == "BACK":
            self.volver_menu()

    def _shutdown_controller(self) -> None:
        if getattr(self, "controller", None):
            self.controller.stop()
            self.controller = None

    def _on_close(self) -> None:
        self._shutdown_controller()
        self.root.destroy()