import tkinter as tk
from tkinter import ttk
import pygame
from UserAutentication import UserAuthentication
from assets.MusicManager import MusicManager

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

        tk.Button(
            self.root,
            text="Cambiar soundtrack",
            bg="#333",
            fg="white",
            command=self.cambiar_soundtrack
        ).pack(pady=10)

        self.lbl_track = tk.Label(
            self.root,
            text=f"Soundtrack actual: {self.soundtrack_var.get()}",
            fg="lightgray",
            bg="#121212"
        )
        self.lbl_track.pack()

        # ------------------------
        # 🔉 Botón de efecto
        # ------------------------
        tk.Button(
            self.root,
            text="🔊 Probar efecto",
            bg="#333",
            fg="white",
            command=self.probar_efecto
        ).pack(pady=10)

        # ------------------------
        # 💾 Guardar Configuración
        # ------------------------
        tk.Button(
            self.root,
            text="💾 Guardar configuración",
            bg="#2e8b57",
            fg="white",
            command=self.guardar
        ).pack(pady=10)

        # ------------------------
        # ⬅ Volver al Menú
        # ------------------------
        tk.Button(
            self.root,
            text="⬅ Volver al menú",
            bg="#8b0000",
            fg="white",
            command=self.volver_menu
        ).pack(pady=20)

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
        self.root.destroy()
        from gui.menu_principal import MainMenu
        MainMenu(self.usuario, self.rol)