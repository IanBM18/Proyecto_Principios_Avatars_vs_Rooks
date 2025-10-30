import tkinter as tk
from tkinter import ttk, messagebox
import json, os

class AdminMenu:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol
        self.ruta_usuarios = os.path.join("data", "usuarios.json")

        self.root = tk.Tk()
        self.root.title("Panel de Administrador - Avatars VS Rooks")
        self.root.geometry("550x400")
        self.root.config(bg="#121212")

        tk.Label(self.root, text=f"👑 Panel de Administración ({self.usuario})",
                 font=("Arial", 18, "bold"), fg="white", bg="#121212").pack(pady=15)

        tk.Button(self.root, text="📋 Ver Usuarios Registrados", width=30, bg="#333", fg="white",
                  font=("Arial", 12), command=self.ver_usuarios).pack(pady=8)
        tk.Button(self.root, text="🏆 Ver Salón de la Fama", width=30, bg="#333", fg="white",
                  font=("Arial", 12), command=self.abrir_salon_fama).pack(pady=8)
        tk.Button(self.root, text="🚪 Cerrar Sesión", width=30, bg="#8b0000", fg="white",
                  font=("Arial", 12), command=self.cerrar_sesion).pack(pady=20)

        self.root.mainloop()

    def ver_usuarios(self):
        if not os.path.exists(self.ruta_usuarios):
            messagebox.showwarning("Advertencia", "No hay usuarios registrados todavía.")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Usuarios Registrados")
        ventana.geometry("600x350")
        ventana.config(bg="#1a1a1a")

        columnas = ("Usuario", "Correo", "Rol")
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")
        tabla.heading("Usuario", text="Usuario")
        tabla.heading("Correo", text="Correo")
        tabla.heading("Rol", text="Rol")
        tabla.pack(padx=10, pady=10, fill="both", expand=True)

        try:
            with open(self.ruta_usuarios, "r") as archivo:
                usuarios = json.load(archivo)
        except json.JSONDecodeError:
            usuarios = []

        for u in usuarios:
            tabla.insert("", "end", values=(u.get("username"), u.get("email"), u.get("role")))

    def abrir_salon_fama(self):
        self.root.destroy()
        from gui.salon_fama import HallOfFameWindow
        HallOfFameWindow(self.usuario)

    def cerrar_sesion(self):
        confirm = messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar sesión?")
        if confirm:
            self.root.destroy()
            from gui.login import LoginWindow
            LoginWindow()
