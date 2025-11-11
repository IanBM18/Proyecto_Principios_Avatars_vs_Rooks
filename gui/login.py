# Autenticacion de Usuarios
import tkinter as tk
from tkinter import messagebox
import json, os
from UserAutentication import UserAuthentication
from assets.MusicManager import MusicManager
from gui.ventanaimagen import VentanaImagen

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Inicio de Sesión - Avatars VS Rooks")
        self.root.geometry("500x450")
        self.root.config(bg="#1a1a1a")
        self.root.resizable(False, False)
        self.ventana_imagen = VentanaImagen(self.root, ruta_imagen="assets/fondos/login.jpg")
        self.CenterWindow(500, 450)
        #Titulo de inicio de sesión
        tk.Label(self.root, text="Inicie Sesión Para Jugar", font=("Arial", 16, "bold"), bg= "#1a1a1a", fg="white").place(relx=0.5, rely=0.15, anchor="center")
        #Usuario 
        
        self.entry_user = tk.Entry(self.root, width=30)
        self.entry_user.place(relx=0.5, rely=0.43, anchor="center", width=200)
        #Contraseña
        
        self.entry_pass = tk.Entry(self.root, width=30, show="*")
        self.entry_pass.place(relx=0.5, rely=0.53, anchor="center", width=200)

        #Botones
        tk.Button(self.root, text="Iniciar Sesión", width=37, height=1, bg="#03bb85", fg="white", command=self.login).place(relx=0.51, rely=0.63, anchor="center")
        tk.Button(self.root, text="Registrarse", width=20, bg="#444", fg="white", command=self.abrir_registro).place(relx=0.5, rely=0.80, anchor="center")
        tk.Button(self.root, text="Salir", width=20, bg="#555", fg="white", command=self.root.destroy).place(relx=0.5, rely=0.90, anchor="center")

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

    def CenterWindow(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")