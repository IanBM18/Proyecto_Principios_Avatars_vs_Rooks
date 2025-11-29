# gui/salon_fama.py
import tkinter as tk
import json
import os
from gui.menu_principal import MainMenu
from assets.MusicManager import MusicManager
from gui.ventanaimagen import VentanaImagen

# --- Dropbox ---
from dropbox_manager import DropboxManager


class HallOfFameWindow:
    RUTA_SALON = os.path.join("DATA", "salon_fama.json")

    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol
        self.music = MusicManager()

        # Ventana
        self.root = tk.Tk()
        self.root.title("Salón de la Fama - Avatars VS Rooks")
        self.root.geometry("900x700")
        self.root.resizable(False, False)

        # Fondo
        self.ventana_imagen = VentanaImagen(self.root, ruta_imagen="assets/fondos/fondopre1.png")
        if self.ventana_imagen.label_fondo:
            self.ventana_imagen.label_fondo.lower()

        # Título
        tk.Label(
            self.root,
            text="🏆 SALÓN DE LA FAMA 🏆",
            font=("Arial", 28, "bold"),
            bg="#1c1c1c",
            fg="gold"
        ).pack(pady=20)

        # Frame de puntajes
        self.frame_puntajes = tk.Frame(self.root, bg="#1c1c1c")
        self.frame_puntajes.pack(pady=10)

        # Sincronizar desde nube
        self.sincronizar_desde_nube()

        # Cargar puntajes
        self.cargar_puntajes()

        # Botón volver
        tk.Button(
            self.root,
            text="⬅ Volver al Menú",
            bg="#444",
            fg="white",
            font=("Arial", 14),
            command=self.volver_menu
        ).pack(side=tk.BOTTOM, anchor=tk.SE, pady=20, padx=20)

        self.root.mainloop()

    # ================================
    # DESCARGAR DE DROPBOX → LOCAL
    # ================================
    def sincronizar_desde_nube(self):
        try:
            datos = DropboxManager.descargar_json("salon_fama.json")

            # Reparar formatos incorrectos
            if not isinstance(datos, list):
                datos = []

            os.makedirs("DATA", exist_ok=True)
            with open(self.RUTA_SALON, "w") as f:
                json.dump(datos, f, indent=4)

        except Exception as e:
            print(f"⚠ Error al sincronizar desde Dropbox: {e}")
            print("Usando datos locales.")

    # ================================
    # CARGAR Y MOSTRAR PUNTAJES
    # ================================
    def cargar_puntajes(self):
        # Leer archivo local
        if not os.path.exists(self.RUTA_SALON):
            with open(self.RUTA_SALON, "w") as f:
                json.dump([], f)

        try:
            with open(self.RUTA_SALON, "r") as f:
                registros = json.load(f)
        except:
            registros = []

        # Reparar formato
        if not isinstance(registros, list):
            registros = []

        # Limpiar frame
        for widget in self.frame_puntajes.winfo_children():
            widget.destroy()

        if len(registros) == 0:
            tk.Label(
                self.frame_puntajes,
                text="No hay registros todavía.",
                bg="#1c1c1c",
                fg="white",
                font=("Arial", 16)
            ).pack()
            return

        # Ordenar por tiempo
        registros = sorted(registros, key=lambda x: x["tiempo"])[:10]

        # Mostrar lista
        for i, entry in enumerate(registros, start=1):
            texto = f"{i}. 👤 {entry['usuario']} - ⏱ {entry['tiempo']:.2f} s"
            tk.Label(
                self.frame_puntajes,
                text=texto,
                bg="#1c1c1c",
                fg="white",
                font=("Arial", 16)
            ).pack(anchor="w", padx=20, pady=5)

    # ================================
    # REGISTRAR TIEMPO
    # ================================
    @staticmethod
    def registrar_tiempo(usuario, tiempo):
        # Descargar lista
        data = DropboxManager.descargar_json("salon_fama.json")
        if not isinstance(data, list):
            data = []

        # Agregar nuevo registro
        data.append({"usuario": usuario, "tiempo": tiempo})

        # Ordenar
        data = sorted(data, key=lambda x: x["tiempo"])[:10]

        # Subir
        DropboxManager.subir_json("salon_fama.json", data)

        print("✔ Tiempo registrado correctamente.")

    def volver_menu(self):
        self.root.destroy()
        MainMenu(self.usuario, self.rol)
