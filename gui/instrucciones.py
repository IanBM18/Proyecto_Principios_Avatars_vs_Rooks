# gui/instrucciones.py
import tkinter as tk
from tkinter import messagebox

class InstructionsWindow:
    def __init__(self, usuario=None):
        self.usuario = usuario
        self.root = tk.Tk()
        self.root.title("Instrucciones - Avatars VS Rooks")
        self.root.geometry("600x500")
        self.root.config(bg="#202020")

        titulo = tk.Label(self.root, text="INSTRUCCIONES DE USO", font=("Arial", 18, "bold"),
                          fg="white", bg="#202020")
        titulo.pack(pady=10)

        texto = (
            "Bienvenido a Avatars VS Rooks 🛡️\n\n"
            "Objetivo:\n"
            "Derrota a los enemigos utilizando tus avatares y gana monedas para mejorar tus habilidades.\n\n"
            "Controles básicos durante la partida (Pygame):\n"
            "- Movimiento: Flechas del teclado\n"
            "- Acción/Atacar: Barra espaciadora\n"
            "- Pausa: P\n"
            "- Salir de la partida: Esc (regresa al menú principal)\n\n"
            "Consejos:\n"
            "- Aprovecha las monedas para regenerar energía y mejorar tus personajes.\n"
            "- Cada nivel aumenta la dificultad de los enemigos.\n"
            "- Consulta el Salón de la Fama para ver los mejores jugadores."
        )

        caja_texto = tk.Text(self.root, wrap="word", width=70, height=20, bg="#2b2b2b", fg="white",
                             font=("Arial", 12))
        caja_texto.insert(tk.END, texto)
        caja_texto.config(state="disabled")
        caja_texto.pack(pady=10, padx=10)

        btn_frame = tk.Frame(self.root, bg="#202020")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Volver al Menú", width=18, bg="#444", fg="white",
                  command=self.volver_menu).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Cerrar", width=18, bg="#333", fg="white",
                  command=self.root.destroy).pack(side="left", padx=8)

        self.root.mainloop()

    def volver_menu(self):
        self.root.destroy()
        from gui.menu_principal import MainMenu
        MainMenu(self.usuario, getattr(self, "rol", "player"))
