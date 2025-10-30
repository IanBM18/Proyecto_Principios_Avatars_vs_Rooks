# gui/salon_fama.py
import tkinter as tk
import json
import os
from tkinter import messagebox
from gui.menu_principal import MainMenu


class HallOfFameWindow:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol
        self.ruta_puntajes = os.path.join("data", "puntuaciones.json")

        self.root = tk.Tk()
        self.root.title("Salón de la Fama - Avatars VS Rooks")
        self.root.geometry("500x400")
        self.root.config(bg="#1c1c1c")

        tk.Label(self.root, text="🏆 Salón de la Fama 🏆",
                 font=("Arial", 18, "bold"), bg="#1c1c1c", fg="gold").pack(pady=20)

        self.frame_puntajes = tk.Frame(self.root, bg="#1c1c1c")
        self.frame_puntajes.pack(pady=10)

        self.cargar_puntajes()

        tk.Button(self.root, text="⬅ Volver al Menú", bg="#444", fg="white",
                  font=("Arial", 12), command=self.volver_menu).pack(pady=20)

        self.root.mainloop()

    def cargar_puntajes(self):
        if not os.path.exists(self.ruta_puntajes):
            with open(self.ruta_puntajes, "w") as f:
                json.dump([], f)

        try:
            with open(self.ruta_puntajes, "r") as f:
                puntajes = json.load(f)
        except json.JSONDecodeError:
            puntajes = []

        if not puntajes:
            tk.Label(self.frame_puntajes, text="No hay puntajes registrados todavía.",
                     bg="#1c1c1c", fg="white", font=("Arial", 12)).pack()
            return

        # Mostrar los puntajes
        for i, p in enumerate(sorted(puntajes, key=lambda x: x.get("puntaje", 0), reverse=True)[:5]):
            texto = f"{i + 1}. {p['usuario']} - {p['puntaje']} pts"
            tk.Label(self.frame_puntajes, text=texto,
                     bg="#1c1c1c", fg="white", font=("Arial", 12)).pack(anchor="w", padx=60, pady=3)

    def volver_menu(self):
        self.root.destroy()
        MainMenu(self.usuario, self.rol)