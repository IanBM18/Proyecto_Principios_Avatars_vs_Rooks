# gui/salon_fama.py
import tkinter as tk
import json
import os
from gui.menu_principal import MainMenu
from assets.MusicManager import MusicManager 
from gui.ventanaimagen import VentanaImagen 

class HallOfFameWindow:
    RUTA_SALON = os.path.join("DATA", "salon_fama.json")

    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol

        # Recuperar la música en ejecución sin reiniciarla
        self.music = MusicManager()

        # 🪟 Configuración de ventana
        self.root = tk.Tk()
        self.root.title("Salón de la Fama - Avatars VS Rooks")
        self.ventana_imagen = VentanaImagen(self.root, ruta_imagen="assets/fondos/fondopre1.png")
        self.root.geometry("900x700")
        self.root.config(bg="#1c1c1c")

        tk.Label(
            self.root,
            text="🏆 Salón de la Fama 🏆",
            font=("Arial", 18, "bold"),
            bg="#1c1c1c",
            fg="gold"
        ).pack(pady=20)

        self.frame_puntajes = tk.Frame(self.root, bg="#1c1c1c")
        self.frame_puntajes.pack(pady=10)

        self.cargar_puntajes()

        tk.Button(
            self.root,
            text="⬅ Volver al Menú",
            bg="#444",
            fg="white",
            font=("Arial", 12),
            command=self.volver_menu
        ).pack(side=tk.BOTTOM, anchor= tk.SE, pady=20, padx=20)

        self.root.mainloop()

    def cargar_puntajes(self):
        """Carga los tiempos desde el JSON y los muestra."""
        if not os.path.exists(self.RUTA_SALON):
            with open(self.RUTA_SALON, "w") as f:
                json.dump({}, f)  # diccionario vacío

        try:
            with open(self.RUTA_SALON, "r") as f:
                salon = json.load(f)
        except json.JSONDecodeError:
            salon = {}

        # Si no hay tiempos registrados
        if not salon:
            tk.Label(
                self.frame_puntajes,
                text="No hay puntajes registrados todavía.",
                bg="#1c1c1c",
                fg="white",
                font=("Arial", 12)
            ).pack()
            return

        # Mostrar todos los usuarios y sus tiempos ordenados por menor tiempo
        for usuario, tiempos in salon.items():
            if not tiempos:
                continue
            tk.Label(
                self.frame_puntajes,
                text=f"👤 {usuario}:",
                bg="#1c1c1c",
                fg="cyan",
                font=("Arial", 14, "bold")
            ).pack(anchor="w", padx=20, pady=(5,0))

            # ordenar por tiempo ascendente
            tiempos_ordenados = sorted(tiempos, key=lambda x: x["tiempo"])
            for i, p in enumerate(tiempos_ordenados[:5]):  # mostrar top 5 por usuario
                texto = f"   {i + 1}. Nivel {p['nivel']} - Tiempo: {p['tiempo']:.2f} s"
                tk.Label(
                    self.frame_puntajes,
                    text=texto,
                    bg="#1c1c1c",
                    fg="white",
                    font=("Arial", 12)
                ).pack(anchor="w", padx=40, pady=2)

    @staticmethod
    def registrar_tiempo(usuario, nivel, tiempo):
        """Guarda un tiempo en el salón de la fama."""
        ruta = HallOfFameWindow.RUTA_SALON
        if not os.path.exists(ruta):
            salon = {}
        else:
            try:
                with open(ruta, "r") as f:
                    salon = json.load(f)
            except json.JSONDecodeError:
                salon = {}

        salon.setdefault(usuario, []).append({"nivel": nivel, "tiempo": tiempo})

        with open(ruta, "w") as f:
            json.dump(salon, f, indent=4)

    def volver_menu(self):
        self.root.destroy()
        MainMenu(self.usuario, self.rol)