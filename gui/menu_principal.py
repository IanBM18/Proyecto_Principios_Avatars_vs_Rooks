import tkinter as tk
from tkinter import messagebox
import os
import json
from assets.MusicManager import MusicManager
from UserAutentication import UserAuthentication

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
        self.root.geometry("500x400")
        self.root.config(bg="#121212")

        # 💬 Etiqueta de bienvenida
        tk.Label(
            self.root,
            text=f"Bienvenido {self.usuario} ({self.rol})",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#121212"
        ).pack(pady=20)

        # 🎮 Botones principales
        tk.Button(
            self.root, text="🎮 Iniciar Partida", width=25, bg="#2e8b57", fg="white", font=("Arial", 12),
            command=self.iniciar_juego
        ).pack(pady=10)

        tk.Button(
            self.root, text="🏆 Salón de la Fama", width=25, bg="#333", fg="white", font=("Arial", 12),
            command=self.abrir_salon_fama
        ).pack(pady=10)

        tk.Button(
            self.root, text="📘 Instrucciones", width=25, bg="#333", fg="white", font=("Arial", 12),
            command=self.abrir_instrucciones
        ).pack(pady=10)

        # 🚪 Cerrar sesión
        tk.Button(
            self.root, text="🚪 Cerrar Sesión", width=25, bg="#8b0000", fg="white", font=("Arial", 12),
            command=self.cerrar_sesion
        ).pack(pady=20)

        # ⚙️ Botón de Ajustes
        ajustes_btn = tk.Button(
            self.root, text="⚙️ Ajustes", bg="#444", fg="white",
            font=("Arial", 11), width=12, command=self.abrir_ajustes
        )
        ajustes_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

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
        self.root.destroy()
        GameWindow(self.usuario, self.rol)

    def abrir_salon_fama(self):
        from gui.salon_fama import HallOfFameWindow
        self.root.destroy()
        HallOfFameWindow(self.usuario, self.rol)

    def abrir_instrucciones(self):
        from gui.instrucciones import InstructionsWindow
        self.root.destroy()
        InstructionsWindow(self.usuario, self.rol)

    def cerrar_sesion(self):
        """Finaliza la sesión y detiene la música."""
        confirm = messagebox.askyesno("Cerrar sesión", "¿Seguro que deseas cerrar sesión?")
        if confirm:
            self.music.stop()
            self.root.destroy()
            from gui.login import LoginWindow
            LoginWindow()

    def abrir_ajustes(self):
        """Abre la ventana de configuración sin detener la música."""
        self.root.destroy()
        from gui.ajustes import AjustesWindow
        AjustesWindow(self.usuario, self.rol)