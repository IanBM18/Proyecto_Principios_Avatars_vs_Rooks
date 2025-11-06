# Autenticacion de Usuarios
import tkinter as tk
from tkinter import messagebox
import json, os
from UserAutentication import UserAuthentication
from assets.MusicManager import MusicManager

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login - Avatars VS Rooks")
        self.root.geometry("400x330+560+240")
        self.root.config(bg="#1a1a1a")

        tk.Label(self.root, text="Iniciar Sesión", font=("Arial", 18, "bold"), bg="#1a1a1a", fg="white").pack(pady=15)

        tk.Label(self.root, text="Usuario:", bg="#1a1a1a", fg="white").pack()
        self.entry_user = tk.Entry(self.root, width=30)
        self.entry_user.pack(pady=5)

        tk.Label(self.root, text="Contraseña:", bg="#1a1a1a", fg="white").pack()
        self.entry_pass = tk.Entry(self.root, width=30, show="*")
        self.entry_pass.pack(pady=5)

        tk.Button(self.root, text="Iniciar Sesión", width=20, bg="#333", fg="white", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Registrarse", width=20, bg="#444", fg="white", command=self.abrir_registro).pack(pady=5)
        tk.Button(self.root, text="Salir", width=20, bg="#555", fg="white", command=self.root.destroy).pack(pady=10)

        self.root.mainloop()

    def login(self):
        user = self.entry_user.get()
        pw = self.entry_pass.get()

        if not user or not pw:
            messagebox.showwarning("Error", "Por favor ingresa todos los campos.")
            return

        auth = UserAuthentication()
        resultado = auth.verify_credentials(user, pw)

        if resultado["success"]:
            rol = resultado["role"]

            # 🎵 Iniciar música del usuario solo después del login
            music = MusicManager()
            user_settings = auth.get_user_settings(user)
            music.play(soundtrack_index=user_settings.get("soundtrack", 1),
                       volume=user_settings.get("volume", 0.5))

            # 🧭 Abrir el menú según el rol
            if rol == "admin":
                messagebox.showinfo("Bienvenido", f"👑 Bienvenido, Administrador {user}!")
                self.root.destroy()
                from gui.menu_admin import AdminMenu
                AdminMenu(user, rol)
            else:
                messagebox.showinfo("Bienvenido", f"🎮 Bienvenido jugador {user}!")
                self.root.destroy()
                from gui.menu_principal import MainMenu
                MainMenu(user, rol)
        else:
            messagebox.showerror("Error", resultado["message"])

    def abrir_registro(self):
        self.root.destroy()
        from gui.registro import RegisterWindow
        RegisterWindow()