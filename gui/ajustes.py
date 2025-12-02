import tkinter as tk
from tkinter import ttk
import pygame
import queue
from UserAutentication import UserAuthentication
from assets.MusicManager import MusicManager
from gui.ventanaimagen import VentanaImagen
from hardware import PicoController

class AjustesWindow:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol
        self.auth = UserAuthentication()
        self.music = MusicManager()  # 🎵 Usa el Singleton global

        # Cargar ajustes del usuario
        self.user_settings = self.auth.get_user_settings(usuario)

        # 🪟 Configuración de ventana
        self.root = tk.Tk()
        self.root.geometry("400x380+560+240")
        self.ventana_imagen = VentanaImagen(self.root, ruta_imagen="assets/fondos/fondopre1.png")
        self.root.title("Ajustes de Audio")
        self.root.config(bg="#121212")

        # 🎧 Título
        tk.Label(
            self.root, text="🎧 Ajustes de Audio",
            font=("Arial", 16, "bold"), fg="white", bg="#121212"
        ).pack(pady=10)

        # ------------------------
        # 🔊 Control de Volumen
        # ------------------------
        tk.Label(self.root, text="Volumen general", fg="white", bg="#121212").pack()
        self.volumen_slider = ttk.Scale(
            self.root,
            from_=0,
            to=1,
            orient="horizontal",
            value=self.user_settings.get("volume", 0.5),
            command=self.cambiar_volumen
        )
        self.volumen_slider.pack(pady=10)

        # ------------------------
        # 🎶 Selector de Soundtrack
        # ------------------------
        tk.Label(
            self.root, text="🎵 Seleccionar soundtrack",
            fg="white", bg="#121212"
        ).pack(pady=5)

        self.soundtrack_var = tk.IntVar(value=self.user_settings.get("soundtrack", 1))


        self.lbl_track = tk.Label(
            self.root,
            text=f"Soundtrack actual: {self.soundtrack_var.get()}",
            fg="lightgray",
            bg="#121212"
        )
        self.lbl_track.pack()

        # ------------------------
        # 🔉 Botón de efecto y Guardar se registran después
        # ------------------------

        # ------------------------
        # ⬅ Volver al Menú
        # ------------------------
        self.button_widgets = []
        self.selected_index = 0

        # Registrar botones para navegación (NO incluir el slider, solo botones reales)
        btn_cambiar = tk.Button(
            self.root,
            text="Cambiar soundtrack",
            bg="#333",
            fg="white",
            command=self.cambiar_soundtrack
        )
        btn_cambiar.pack(pady=10)
        self._register_button(btn_cambiar, "#333")

        btn_probar = tk.Button(
            self.root,
            text="🔊 Probar efecto",
            bg="#333",
            fg="white",
            command=self.probar_efecto
        )
        btn_probar.pack(pady=10)
        self._register_button(btn_probar, "#333")

        btn_guardar = tk.Button(
            self.root,
            text="💾 Guardar configuración",
            bg="#2e8b57",
            fg="white",
            command=self.guardar
        )
        btn_guardar.pack(pady=10)
        self._register_button(btn_guardar, "#2e8b57")

        btn_volver = tk.Button(
            self.root,
            text="⬅ Volver al menú",
            bg="#8b0000",
            fg="white",
            command=self.volver_menu
        )
        btn_volver.pack(pady=20)
        self._register_button(btn_volver, "#8b0000")

        # Eliminar botones duplicados que ya registramos
        # (los que estaban antes en el código original)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._highlight_selection()
        self._setup_controller()

        self.root.mainloop()

    # -------------------------------------------------
    # 🔉 Funciones
    # -------------------------------------------------
    def cambiar_volumen(self, nuevo_valor):
        valor = float(nuevo_valor)
        self.user_settings["volume"] = valor
        self.music.set_volume(valor)

    def cambiar_soundtrack(self):
        """Alterna entre soundtrack 1 y 2 sin reiniciar toda la app."""
        actual = self.soundtrack_var.get()
        nuevo = 1 if actual == 2 else 2
        self.soundtrack_var.set(nuevo)
        self.lbl_track.config(text=f"Soundtrack actual: {nuevo}")

        self.user_settings["soundtrack"] = nuevo
        self.music.change_track(nuevo)  # 👈 Usa change_track para cambiar suavemente

    def probar_efecto(self):
        """Reproduce un sonido corto de prueba."""
        efecto = pygame.mixer.Sound("assets/sounds/click.wav")
        efecto.set_volume(self.user_settings.get("volume", 0.5))
        efecto.play()

    def guardar(self):
        """Guarda los ajustes del usuario."""
        self.auth.save_user_settings(self.usuario, self.user_settings)

    def volver_menu(self):
        """Vuelve al menú principal sin reiniciar música."""
        self.guardar()
        self._shutdown_controller()
        self.root.destroy()
        from gui.menu_principal import MainMenu
        MainMenu(self.usuario, self.rol)

    # ------------------------------------------------------------------
    # 🎮 Integración con el control físico
    # ------------------------------------------------------------------

    def _register_button(self, button: tk.Button, default_bg: str) -> None:
        self.button_widgets.append(
            {"widget": button, "default_bg": default_bg}
        )

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
        if event in ("UP", "LEFT"):
            self._move_selection(-1)
        elif event == "DOWN":
            self._move_selection(1)
        elif event == "RIGHT":
            self._move_selection(1)
        elif event == "SELECT":
            self._activate_selected()
        elif event == "BACK":
            self.volver_menu()

    def _move_selection(self, delta: int) -> None:
        if not self.button_widgets:
            return
        self.selected_index = (self.selected_index + delta) % len(self.button_widgets)
        self._highlight_selection()

    def _highlight_selection(self) -> None:
        highlight_color = "#f0b90b"
        for idx, data in enumerate(self.button_widgets):
            btn = data["widget"]
            # Solo cambiar bg si es un tk.Button (no ttk widgets)
            if isinstance(btn, tk.Button):
                target_color = highlight_color if idx == self.selected_index else data["default_bg"]
                btn.config(bg=target_color)

    def _activate_selected(self) -> None:
        if not self.button_widgets:
            return
        button = self.button_widgets[self.selected_index]["widget"]
        button.invoke()

    def _shutdown_controller(self) -> None:
        if getattr(self, "controller", None):
            self.controller.stop()
            self.controller = None

    def _on_close(self) -> None:
        self._shutdown_controller()
        self.root.destroy()