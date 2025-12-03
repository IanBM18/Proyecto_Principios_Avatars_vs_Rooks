# gui/menu_principal.py
import tkinter as tk
from tkinter import messagebox
import os
import json
import queue
import time
from assets.MusicManager import MusicManager
from UserAutentication import UserAuthentication
from gui.ventanaimagen import VentanaImagen
from PIL import Image, ImageTk
from hardware import PicoController

# ---- Theme map (coincide con ajustes.THEMES) ----
THEME_MAP = {
    "dark": {"bg": "#121212", "fg": "white", "card": "#1e1e1e", "accent": "#2e8b57"},
    "light": {"bg": "white", "fg": "black", "card": "#f2f2f2", "accent": "#1e90ff"},
    "blue": {"bg": "#0f1724", "fg": "white", "card": "#071020", "accent": "#2563eb"},
    "green": {"bg": "#0b2b16", "fg": "white", "card": "#0f3a22", "accent": "#32cd32"},
    "red": {"bg": "#2b0a0a", "fg": "white", "card": "#3a0e0e", "accent": "#ff4d4d"},
    "purple": {"bg": "#12061a", "fg": "white", "card": "#231233", "accent": "#8b5cf6"},
}

ASSETS_AVATARS = os.path.join("assets", "avatars")

def apply_theme_to_window(theme_name, root=None):
    """Helper: apply theme globally (if root provided update it)."""
    theme = THEME_MAP.get(theme_name, THEME_MAP["blue"])
    if root:
        try:
            root.config(bg=theme["bg"])
        except Exception:
            pass
    # This helper can later be extended to update styles globally.

class MainMenu:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol
        self.button_widgets = []
        self.auth = UserAuthentication()
        self.music = MusicManager()

        # Load user settings and apply theme
        self.user_settings = self.auth.get_user_settings(usuario)
        theme = self.user_settings.get("theme_color", "blue")
        apply_theme_to_window(theme)

        # Start music if not playing
        if not self.music.playing:
            self.music.play(soundtrack_index=self.user_settings.get("soundtrack", 1),
                            volume=self.user_settings.get("volume", 0.5))

        self.root = tk.Tk()
        self.root.title("Menú Principal - Avatars VS Rooks")
        self.ventana_imagen = VentanaImagen(self.root, ruta_imagen="assets/fondos/mainmenu1.png")
        ancho, alto = 1000, 700
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.root.config(bg=THEME_MAP[theme]["bg"])

        # welcome label with avatar preview
        avatar_file = self.user_settings.get("avatar", None)
        avatar_img = None
        if avatar_file:
            p = os.path.join(ASSETS_AVATARS, avatar_file)
            if os.path.exists(p):
                try:
                    img = Image.open(p).resize((64,64), Image.Resampling.LANCZOS)
                    avatar_img = ImageTk.PhotoImage(img)
                except Exception:
                    avatar_img = None

        lbl_frame = tk.Frame(self.root, bg=THEME_MAP[theme]["card"])
        lbl_frame.place(x=300, y=140, width=400, height=80)
        if avatar_img:
            tk.Label(lbl_frame, image=avatar_img, bg=THEME_MAP[theme]["card"]).place(x=10, y=8)
            # keep ref
            self.avatar_img = avatar_img

        tk.Label(lbl_frame,
                 text=f"Bienvenido {self.usuario} ({self.rol})",
                 font=("Arial", 16, "bold"),
                 fg=THEME_MAP[theme]["fg"],
                 bg=THEME_MAP[theme]["card"]).place(x=90, y=20)

        # Buttons area
        frame_botones = tk.Frame(self.root, bg=THEME_MAP[theme]["bg"])
        frame_botones.pack(pady=180, side=tk.TOP)

        btn_opts = {"width":25, "bg": THEME_MAP[theme]["accent"], "fg":"white", "font":("Arial",12)}
        tk.Button(self.root, text="🎮 Iniciar Partida", **btn_opts, command=self.iniciar_juego).pack(pady=12)

        btn2_opts = {"width":25, "bg": "#333", "fg":"white", "font":("Arial",12)}
        tk.Button(self.root, text="🏆 Salón de la Fama", **btn2_opts, command=self.abrir_salon_fama).pack(pady=12)
        tk.Button(self.root, text="📘 Instrucciones", **btn2_opts, command=self.abrir_instrucciones).pack(pady=12)

        tk.Button(self.root, text="🚪 Cerrar Sesión", width=25, bg="#8b0000", fg="white", font=("Arial",12),
                  command=self.cerrar_sesion).pack(pady=12)

        ajustes_btn = tk.Button(self.root, text="⚙️ Ajustes", bg="#444", fg="white", font=("Arial",11),
                                width=12, command=self.abrir_ajustes)
        ajustes_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self._register_button(ajustes_btn, "#444")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._highlight_selection()
        self._setup_controller()

        self.root.mainloop()

    def iniciar_juego(self):
        info_sesion = {"usuario": self.usuario, "rol": self.rol}
        ruta_temp = os.path.join("data", "sesion_actual.json")
        os.makedirs(os.path.dirname(ruta_temp), exist_ok=True)
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