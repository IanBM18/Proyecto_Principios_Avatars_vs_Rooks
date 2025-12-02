import tkinter as tk
from tkinter import messagebox
import os
import json
import queue
import time
from assets.MusicManager import MusicManager
from UserAutentication import UserAuthentication
from gui.ventanaimagen import VentanaImagen
from hardware import PicoController

class MainMenu:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol
        self.auth = UserAuthentication()
        # 🟢 Obtener la instancia global de música
        self.music = MusicManager()

        # ⚠️ Solo iniciar la música si no está sonando ya
        if not self.music.playing:
            user_settings = self.auth.get_user_settings(usuario)
            self.music.play(
                soundtrack_index=user_settings.get("soundtrack", 1),
                volume=user_settings.get("volume", 0.5)
            )

        # 🪟 Configuración de la ventana
        self.root = tk.Tk()
        self.root.title("Menú Principal - Avatars VS Rooks")
        self.ventana_imagen = VentanaImagen(self.root, ruta_imagen="assets/fondos/mainmenu1.png")
        self.root.update_idletasks()
        ancho, alto = 1000, 700
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.root.config(bg="#121212")

        # 💬 Etiqueta de bienvenida
        tk.Label(
            self.root,
            text=f"Bienvenido {self.usuario} ({self.rol})",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#121212"
        ).place(x=370, y=200)

        self.button_widgets = []
        self.selected_index = 0
        self.last_navigation_time = time.time()  # Inicializar con tiempo actual
        self.navigation_delay = 0.2  # Delay mínimo entre navegaciones (segundos)
        frame_botones = tk.Frame(self.root, bg="#121212")
        frame_botones.place(relx=0.5, rely=0.55, anchor="center")

        button_specs = [
            ("🎮 Iniciar Partida", "#2e8b57", self.iniciar_juego),
            ("🏆 Salón de la Fama", "#333", self.abrir_salon_fama),
            ("📘 Instrucciones", "#333", self.abrir_instrucciones),
            ("🚪 Cerrar Sesión", "#8b0000", self.cerrar_sesion),
        ]

        for text, color, cmd in button_specs:
            btn = tk.Button(
                frame_botones,
                text=text,
                width=25,
                bg=color,
                fg="white",
                font=("Arial", 12),
                command=cmd,
                relief="flat",
                borderwidth=2,
                highlightthickness=0
            )
            btn.pack(pady=12)
            self._register_button(btn, color)

        ajustes_btn = tk.Button(
            self.root,
            text="⚙️ Ajustes",
            bg="#444",
            fg="white",
            font=("Arial", 11),
            width=12,
            command=self.abrir_ajustes,
            relief="flat",
            borderwidth=2,
            highlightthickness=0
        )
        ajustes_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self._register_button(ajustes_btn, "#444")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._highlight_selection()
        self._setup_controller()

        self.root.mainloop()

    # ------------------------------
    # 📂 FUNCIONES DEL MENÚ PRINCIPAL
    # ------------------------------

    def iniciar_juego(self):
        """Guarda la sesión actual y abre la ventana del juego."""
        info_sesion = {"usuario": self.usuario, "rol": self.rol}
        ruta_temp = os.path.join("data", "sesion_actual.json")
        with open(ruta_temp, "w") as f:
            json.dump(info_sesion, f)

        from juego.main_game import GameWindow
        self._shutdown_controller()
        self.root.destroy()
        GameWindow(self.usuario, self.rol)

    def abrir_salon_fama(self):
        from gui.salon_fama import HallOfFameWindow
        self._shutdown_controller()
        self.root.destroy()
        HallOfFameWindow(self.usuario, self.rol)

    def abrir_instrucciones(self):
        from gui.instrucciones import InstructionsWindow
        self._shutdown_controller()
        self.root.destroy()
        InstructionsWindow(self.usuario, self.rol)

    def cerrar_sesion(self):
        """Finaliza la sesión y detiene la música."""
        confirm = messagebox.askyesno("Cerrar sesión", "¿Seguro que deseas cerrar sesión?")
        if confirm:
            self.music.stop()
            self._shutdown_controller()
            self.root.destroy()
            from gui.login import LoginWindow
            LoginWindow()

    def abrir_ajustes(self):
        """Abre la ventana de configuración sin detener la música."""
        self._shutdown_controller()
        self.root.destroy()
        from gui.ajustes import AjustesWindow
        AjustesWindow(self.usuario, self.rol)

    # ------------------------------------------------------------------
    # 🎮 Integración con el control físico
    # ------------------------------------------------------------------

    def _register_button(self, button: tk.Button, default_bg: str) -> None:
        # Guardar el texto original del botón
        texto_original = button.cget("text")
        self.button_widgets.append(
            {"widget": button, "default_bg": default_bg, "texto_original": texto_original}
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
        current_time = time.time()
        
        # Filtrar eventos vacíos o inválidos que pueden venir cuando el joystick vuelve a neutral
        if not event or event == "NONE" or len(event.strip()) == 0:
            return
        
        # Solo navegar si ha pasado suficiente tiempo desde la última navegación
        # Esto evita que el joystick active botones accidentalmente
        if event in ("UP", "DOWN", "LEFT", "RIGHT"):
            if current_time - self.last_navigation_time < self.navigation_delay:
                return  # Ignorar eventos muy rápidos
            self.last_navigation_time = current_time
            
            # Joystick solo navega, NO activa botones
            if event in ("UP", "LEFT"):
                self._move_selection(-1)
            elif event in ("DOWN", "RIGHT"):
                self._move_selection(1)
            return  # Importante: salir aquí para no procesar otros eventos
        
        # Botón ABAJO (GP5) o botón JOYSTICK (GP28) = Seleccionar
        if event == "SELECT":
            self._activate_selected()
        # Botón DERECHA (GP4) = Regresar al menú principal
        elif event == "BACK":
            self.cerrar_sesion()

    def _move_selection(self, delta: int) -> None:
        if not self.button_widgets:
            return
        self.selected_index = (self.selected_index + delta) % len(self.button_widgets)
        self._highlight_selection()

    def _highlight_selection(self) -> None:
        """Resalta el botón seleccionado con subrayado."""
        for idx, data in enumerate(self.button_widgets):
            btn = data["widget"]
            try:
                if not btn.winfo_exists():
                    continue
                    
                # Obtener el texto original del botón
                texto_original = data.get("texto_original", btn.cget("text"))
                if "texto_original" not in data:
                    data["texto_original"] = texto_original
                    
                if idx == self.selected_index:
                    # Botón seleccionado: subrayado usando font underline
                    btn.config(
                        text=texto_original,
                        bg=data["default_bg"],
                        fg="#f0b90b",  # Color dorado para el texto seleccionado
                        relief="flat",
                        borderwidth=2,
                        font=("Arial", 12, "underline"),  # Subrayado
                        activebackground=data["default_bg"],
                        activeforeground="#f0b90b"
                    )
                else:
                    # Botón no seleccionado: texto normal sin subrayado
                    btn.config(
                        text=texto_original,
                        bg=data["default_bg"],
                        fg="white",
                        relief="flat",
                        borderwidth=2,
                        font=("Arial", 12),  # Sin subrayado
                        activebackground=data["default_bg"],
                        activeforeground="white"
                    )
                    
            except (tk.TclError, AttributeError):
                # El botón fue destruido, continuar con el siguiente
                continue

    def _activate_selected(self) -> None:
        if not self.button_widgets:
            return
        try:
            button = self.button_widgets[self.selected_index]["widget"]
            # Verificar que el botón aún existe antes de invocarlo
            if button.winfo_exists():
                button.invoke()
        except (tk.TclError, AttributeError):
            # El botón fue destruido, ignorar
            pass

    def _shutdown_controller(self) -> None:
        if getattr(self, "controller", None):
            self.controller.stop()
            self.controller = None

    def _on_close(self) -> None:
        self._shutdown_controller()
        self.root.destroy()