import tkinter as tk
from tkinter import messagebox, filedialog
import json, os
from Register import RegistrationService, UserRole

class RegisterWindow:
    def __init__(self):
        self.ruta_usuarios = os.path.join("data", "usuarios.json")
        self.root = tk.Tk()
        self.root.title("Registro - Avatars VS Rooks")
        self.root.geometry("480x550")
        self.root.config(bg="#1a1a1a")

        tk.Label(self.root, text="Registro de Usuario", font=("Arial", 16, "bold"),
                 fg="white", bg="#1a1a1a").pack(pady=10)

        # Campos básicos
        self.crear_campo("Usuario:", "usuario")
        self.crear_campo("Correo:", "email")
        self.crear_campo("Contraseña:", "password", show="*")

        # Selección de rol
        tk.Label(self.root, text="Rol:", bg="#1a1a1a", fg="white").pack()
        self.rol_var = tk.StringVar(value="player")
        tk.Radiobutton(self.root, text="Jugador", variable=self.rol_var, value="player",
                       bg="#1a1a1a", fg="white", selectcolor="#333",
                       command=self.toggle_campos_admin).pack()
        tk.Radiobutton(self.root, text="Administrador", variable=self.rol_var, value="admin",
                       bg="#1a1a1a", fg="white", selectcolor="#333",
                       command=self.toggle_campos_admin).pack()

        # Campos extra para admin
        self.frame_admin = tk.Frame(self.root, bg="#1a1a1a")
        tk.Label(self.frame_admin, text="Nombre Completo:", bg="#1a1a1a", fg="white").pack()
        self.entry_nombre = tk.Entry(self.frame_admin, width=35)
        self.entry_nombre.pack(pady=3)

        tk.Label(self.frame_admin, text="Fecha de Nacimiento (AAAA-MM-DD):", bg="#1a1a1a", fg="white").pack()
        self.entry_fecha = tk.Entry(self.frame_admin, width=35)
        self.entry_fecha.pack(pady=3)

        tk.Button(self.frame_admin, text="Seleccionar Foto de Perfil", bg="#444", fg="white",
                  command=self.seleccionar_foto).pack(pady=5)
        self.label_foto = tk.Label(self.frame_admin, text="Ninguna seleccionada", bg="#1a1a1a", fg="gray")
        self.label_foto.pack()

        # Inicialmente ocultar campos admin
        self.frame_admin.pack_forget()

        # Botones finales
        tk.Button(self.root, text="Registrar", width=20, bg="#333", fg="white",
                  command=self.registrar_usuario).pack(pady=10)
        tk.Button(self.root, text="Volver al Login", width=20, bg="#444", fg="white",
                  command=self.volver_login).pack(pady=5)

        self.root.mainloop()

    def crear_campo(self, texto, atributo, show=None):
        tk.Label(self.root, text=texto, bg="#1a1a1a", fg="white").pack()
        entry = tk.Entry(self.root, width=35, show=show)
        entry.pack(pady=3)
        setattr(self, f"entry_{atributo}", entry)

    def toggle_campos_admin(self):
        if self.rol_var.get() == "admin":
            self.frame_admin.pack(pady=10)
        else:
            self.frame_admin.pack_forget()

    def seleccionar_foto(self):
        archivo = filedialog.askopenfilename(title="Seleccionar imagen de perfil",
                                             filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png")])
        if archivo:
            self.foto_path = archivo
            nombre_archivo = os.path.basename(archivo)
            self.label_foto.config(text=nombre_archivo, fg="lightgreen")
        else:
            self.foto_path = None
            self.label_foto.config(text="Ninguna seleccionada", fg="gray")

    def registrar_usuario(self):
        username = self.entry_usuario.get()
        email = self.entry_email.get()
        password = self.entry_password.get()
        rol = self.rol_var.get()

        # Crear servicio de registro
        servicio = RegistrationService()

        # Datos básicos
        datos = {
            "username": username,
            "email": email,
            "password": password,
            "role": UserRole.ADMIN if rol == "admin" else UserRole.PLAYER,
        }

        # Si el rol es admin → agregar datos adicionales
        if rol == "admin":
            full_name = self.entry_nombre.get()
            fecha = self.entry_fecha.get()
            foto = getattr(self, "foto_path", None)
            photo_info = None
            if foto:
                tamaño_mb = os.path.getsize(foto) / (1024 * 1024)
                formato = foto.split(".")[-1]
                photo_info = {"format": formato, "size_mb": tamaño_mb}

            datos.update({
                "full_name": full_name,
                "date_of_birth": fecha,
                "profile_photo": photo_info
            })

        # Ejecutar validación y registro
        resultado = servicio.RegisterUser(datos)

        if resultado["success"]:
            self.guardar_usuario(datos)
            messagebox.showinfo("Éxito", "Usuario registrado correctamente. ¡Inicia sesión!")
            self.root.destroy()
            from gui.login import LoginWindow
            LoginWindow()
        else:
            errores = "\n".join(resultado["errors"])
            messagebox.showerror("Error en el registro", errores)

    def guardar_usuario(self, datos_usuario):
        # Convertir Enum a string antes de guardar
        if hasattr(datos_usuario["role"], "value"):
            datos_usuario["role"] = datos_usuario["role"].value

        if os.path.exists(self.ruta_usuarios):
            try:
                with open(self.ruta_usuarios, "r") as archivo:
                    usuarios = json.load(archivo)
            except json.JSONDecodeError:
                usuarios = []
        else:
            usuarios = []

        usuarios.append(datos_usuario)

        with open(self.ruta_usuarios, "w") as archivo:
            json.dump(usuarios, archivo, indent=4)

    def volver_login(self):
        self.root.destroy()
        from gui.login import LoginWindow
        LoginWindow()
