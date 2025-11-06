import tkinter as tk
from gui.menu_principal import MainMenu
from assets.MusicManager import MusicManager  # 👈 Agregar esto

class InstructionsWindow:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol

        # 🎵 Recuperar la música en ejecución sin reiniciarla
        self.music = MusicManager()  # 👈 SOLO esto, sin llamar a play()

        self.root = tk.Tk()
        self.root.title("Instrucciones - Avatars VS Rooks")
        self.root.geometry("600x450+560+240")
        self.root.config(bg="#1e1e1e")

        tk.Label(
            self.root,
            text="📘 Instrucciones del Juego",
            font=("Arial", 18, "bold"),
            bg="#1e1e1e",
            fg="lightblue"
        ).pack(pady=20)

        instrucciones = (
            "1️⃣ El juego se desarrolla en una matriz de 9x5.\n\n"
            "2️⃣ Cada jugador controla un conjunto de piezas.\n\n"
            "3️⃣ El objetivo es derrotar a las piezas enemigas o capturar su base.\n\n"
            "4️⃣ Usa el teclado o el mouse para moverte según las reglas del modo.\n\n"
            "5️⃣ Pulsa 'ESC' para salir de la partida y regresar al menú principal.\n\n"
            "6️⃣ Los puntajes se guardan automáticamente al finalizar cada juego.\n\n"
            "¡Buena suerte, estratega! 🧠⚔️"
        )

        tk.Message(
            self.root,
            text=instrucciones,
            bg="#1e1e1e",
            fg="white",
            width=500,
            font=("Arial", 12),
            justify="left"
        ).pack(padx=30, pady=10)

        tk.Button(
            self.root,
            text="⬅ Volver al Menú",
            bg="#444",
            fg="white",
            font=("Arial", 12),
            command=self.volver_menu
        ).pack(pady=20)

        self.root.mainloop()

    def volver_menu(self):
        self.root.destroy()
        MainMenu(self.usuario, self.rol)