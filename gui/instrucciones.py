import tkinter as tk
import queue
from gui.menu_principal import MainMenu
from assets.MusicManager import MusicManager
from gui.ventanaimagen import VentanaImagen
from hardware import PicoController

class InstructionsWindow:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol

        self.music = MusicManager()

        self.root = tk.Tk()
        self.root.title("Instrucciones - Avatars VS Rooks")
        self.root.geometry("750x600+530+230")
        self.root.config(bg="#1e1e1e")

        # Fondo post-apocalíptico
        self.ventana_imagen = VentanaImagen(self.root, ruta_imagen="assets/fondos/fondopre1.png")

        # ---------- Título ----------
        titulo = tk.Label(
            self.root,
            text="📘 Instrucciones del Juego",
            font=("Arial", 22, "bold"),
            bg="#1e1e1e",
            fg="lightblue"
        )
        titulo.pack(pady=10)

        # ---------- Frame con scroll ----------
        contenedor = tk.Frame(self.root, bg="#1e1e1e")
        contenedor.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(contenedor, bg="#1e1e1e", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        texto_frame = tk.Frame(canvas, bg="#1e1e1e")
        canvas.create_window((0, 0), window=texto_frame, anchor="nw")

        # ---------- Texto real según requerimientos ----------
        instrucciones = [
            "🎯 OBJETIVO DEL JUEGO:",
            "Sobrevive colocando torres defensivas para evitar que los Avatars enemigos lleguen a tu base.",

            "\n⚔️ AVATARS:",
            "- Aparecen automáticamente cada 10 segundos.",
            "- Se mueven hacia tu base fila por fila.",
            "- Si uno llega a tu base → PIERDES.",

            "\n💰 MONEDAS:",
            "- Aparecen automáticamente cada 5 segundos.",
            "- Haz clic sobre ellas para recolectarlas.",
            "- Al eliminar un Avatar ganas **75 monedas** adicionales.",

            "\n🏰 TORRES (Rooks):",
            "- Se colocan usando monedas.",
            "- Atacan automáticamente cada **4 segundos**.",
            "- No puedes colocar una torre si no tienes suficiente dinero.",

            "\n🕹 CONTROLES:",
            "- Clic izquierdo: colocar torres.",
            "- Clic en monedas: recolectarlas.",
            "- ESC: regresar al menú desde la partida.",

            "\n🏆 VICTORIA:",
            "- Sobrevive hasta que el temporizador termine.",

            "\n💀 DERROTA:",
            "- Pierdes si un Avatar alcanza tu base.",

            "\n📄 NOTA:",
            "Los puntajes se registran automáticamente y se envían al Salón de la Fama."
        ]

        for linea in instrucciones:
            label = tk.Label(
                texto_frame,
                text=linea,
                bg="#1e1e1e",
                fg="white",
                justify="left",
                anchor="w",
                font=("Arial", 13)
            )
            label.pack(fill="x", pady=2)

        texto_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Activar scroll con la rueda del mouse
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # ---------- Botón Volver ----------
        tk.Button(
            self.root,
            text="⬅ Volver al Menú",
            bg="#444",
            fg="white",
            font=("Arial", 14),
            width=20,
            command=self.volver_menu
        ).pack(pady=15)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._setup_controller()

        self.root.mainloop()

    def _on_close(self):
            self.root.destroy()

    def volver_menu(self):
        self.root.destroy()
        MainMenu(self.usuario, self.rol)
