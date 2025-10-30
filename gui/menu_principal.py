import tkinter as tk
from tkinter import messagebox
import os
import json
from juego.main_game import GameWindow  # 🔹 Import directo

class MainMenu:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol

        self.root = tk.Tk()
        self.root.title("Menú Principal - Avatars VS Rooks")
        self.root.geometry("500x400")
        self.root.config(bg="#121212")

        tk.Label(self.root, text=f"Bienvenido {self.usuario} ({self.rol})",
                 font=("Arial", 16, "bold"), fg="white", bg="#121212").pack(pady=20)

        tk.Button(self.root, text="🎮 Iniciar Partida", width=25, bg="#2e8b57", fg="white", font=("Arial", 12),
                  command=self.iniciar_juego).pack(pady=10)

        tk.Button(self.root, text="🏆 Salón de la Fama", width=25, bg="#333", fg="white", font=("Arial", 12),
                  command=self.abrir_salon_fama).pack(pady=10)

        tk.Button(self.root, text="📘 Instrucciones", width=25, bg="#333", fg="white", font=("Arial", 12),
                  command=self.abrir_instrucciones).pack(pady=10)

        tk.Button(self.root, text="🚪 Cerrar Sesión", width=25, bg="#8b0000", fg="white", font=("Arial", 12),
                  command=self.cerrar_sesion).pack(pady=20)

        self.root.mainloop()

    def iniciar_juego(self):
        # Guardar la sesión actual (por si se necesita en otra parte)
        info_sesion = {"usuario": self.usuario, "rol": self.rol}
        ruta_temp = os.path.join("data", "sesion_actual.json")
        with open(ruta_temp, "w") as f:
            json.dump(info_sesion, f)

        # Cerrar menú y abrir la ventana del juego (mismo proceso)
        self.root.destroy()
        GameWindow(self.usuario, self.rol)

    def abrir_salon_fama(self):
        self.root.destroy()
        from gui.salon_fama import HallOfFameWindow
        HallOfFameWindow(self.usuario, self.rol)  # 🔹 Pasar rol también

    def abrir_instrucciones(self):
        self.root.destroy()
        from gui.instrucciones import InstructionsWindow
        InstructionsWindow(self.usuario, self.rol)  # 🔹 Pasar rol también

    def cerrar_sesion(self):
        confirm = messagebox.askyesno("Cerrar sesión", "¿Seguro que deseas cerrar sesión?")
        if confirm:
            self.root.destroy()
            from gui.login import LoginWindow
            LoginWindow()
