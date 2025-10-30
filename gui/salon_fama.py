# gui/salon_fama.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class HallOfFameWindow:
    def __init__(self, usuario=None):
        self.usuario = usuario
        self.ruta_puntajes = os.path.join("data", "puntuaciones.json")
        self.root = tk.Tk()
        self.root.title("Salón de la Fama - Avatars VS Rooks")
        self.root.geometry("500x400")
        self.root.config(bg="#1a1a1a")

        tk.Label(self.root, text="SALÓN DE LA FAMA", font=("Arial", 18, "bold"),
                 fg="white", bg="#1a1a1a").pack(pady=15)

        columnas = ("Jugador", "Puntaje")
        tabla = ttk.Treeview(self.root, columns=columnas, show="headings", height=8)
        tabla.heading("Jugador", text="Jugador")
        tabla.heading("Puntaje", text="Puntaje")
        tabla.pack(pady=10, padx=10)

        puntajes = self.cargar_puntajes()
        # Ordenar y tomar top 5
        puntajes = sorted(puntajes, key=lambda x: x.get("puntos", 0), reverse=True)[:5]
        for p in puntajes:
            tabla.insert("", "end", values=(p.get("nombre", "—"), p.get("puntos", 0)))

        btn_frame = tk.Frame(self.root, bg="#1a1a1a")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Volver al Menú", width=18, bg="#444", fg="white",
                  command=self.volver_menu).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Cerrar", width=18, bg="#333", fg="white",
                  command=self.root.destroy).pack(side="left", padx=8)

        self.root.mainloop()

    def cargar_puntajes(self):
        if not os.path.exists(self.ruta_puntajes):
            # crea archivo si no existe
            with open(self.ruta_puntajes, "w") as f:
                json.dump([], f)
            return []
        try:
            with open(self.ruta_puntajes, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def volver_menu(self):
        self.root.destroy()
        from gui.menu_principal import MainMenu
        # Si no hay usuario, pasar None
        MainMenu(self.usuario, getattr(self, "rol", "player"))
