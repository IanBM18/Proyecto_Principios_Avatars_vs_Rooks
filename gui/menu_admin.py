import tkinter as tk
from tkinter import ttk, messagebox
import json, os
import queue
from hardware import PicoController

class AdminMenu:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol
        self.ruta_usuarios = os.path.join("data", "usuarios.json")

        self.root = tk.Tk()
        self.root.title("Panel de Administrador - Avatars VS Rooks")
        self.root.geometry("550x400+560+240")
        self.root.config(bg="#121212")

        tk.Label(self.root, text=f"👑 Panel de Administración ({self.usuario})",
                 font=("Arial", 18, "bold"), fg="white", bg="#121212").pack(pady=15)

        
        self.button_widgets = []
        self.selected_index = 0
        
        ajustes_btn = tk.Button(self.root, text="⚙️ Ajustes", bg="#444", fg="white",
                        font=("Arial", 11), width=12, command=self.abrir_ajustes)
        ajustes_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self._register_button(ajustes_btn, "#444")

        # Registrar botones principales
        btn_usuarios = tk.Button(self.root, text="📋 Ver Usuarios Registrados", width=30, bg="#333", fg="white",
                  font=("Arial", 12), command=self.ver_usuarios)
        btn_usuarios.pack(pady=8)
        self._register_button(btn_usuarios, "#333")
        
        btn_salon = tk.Button(self.root, text="🏆 Ver Salón de la Fama", width=30, bg="#333", fg="white",
                  font=("Arial", 12), command=self.abrir_salon_fama)
        btn_salon.pack(pady=8)
        self._register_button(btn_salon, "#333")
        
        btn_cerrar = tk.Button(self.root, text="🚪 Cerrar Sesión", width=30, bg="#8b0000", fg="white",
                  font=("Arial", 12), command=self.cerrar_sesion)
        btn_cerrar.pack(pady=20)
        self._register_button(btn_cerrar, "#8b0000")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._highlight_selection()
        self._setup_controller()

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
        self._shutdown_controller()
        self.root.destroy()
        from gui.salon_fama import HallOfFameWindow
        HallOfFameWindow(self.usuario, self.rol)

    def cerrar_sesion(self):
        confirm = messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar sesión?")
        if confirm:
            self._shutdown_controller()
            self.root.destroy()
            from gui.login import LoginWindow
            LoginWindow()

    def abrir_ajustes(self):
        self._shutdown_controller()
        self.root.destroy()
        from gui.ajustes import AjustesWindow
        AjustesWindow(self.usuario, self.rol)

    # ------------------------------------------------------------------
    # 🎮 Integración con el control físico
    # ------------------------------------------------------------------

    def _register_button(self, button: tk.Button, default_bg: str) -> None:
        self.button_widgets.append(
            {"widget": button, "default_bg": default_bg}
        )

    def _setup_controller(self) -> None:
        self.controller_queue: queue.Queue[str] = queue.Queue()
        self.controller = PicoController(self.controller_queue)
        self.controller.start()
        self.root.after(50, self._process_controller_events)

    def _process_controller_events(self) -> None:
        if hasattr(self, "controller_queue"):
            while not self.controller_queue.empty():
                event = self.controller_queue.get()
                self._handle_controller_event(event)
        self.root.after(50, self._process_controller_events)

    def _handle_controller_event(self, event: str) -> None:
        event = event.upper()
        if event in ("UP", "LEFT"):
            self._move_selection(-1)
        elif event == "DOWN":
            self._move_selection(1)
        elif event == "RIGHT":
            self._move_selection(1)
        elif event == "SELECT":
            self._activate_selected()
        elif event == "BACK":
            self.cerrar_sesion()

    def _move_selection(self, delta: int) -> None:
        if not self.button_widgets:
            return
        self.selected_index = (self.selected_index + delta) % len(self.button_widgets)
        self._highlight_selection()

    def _highlight_selection(self) -> None:
        highlight_color = "#f0b90b"
        for idx, data in enumerate(self.button_widgets):
            btn = data["widget"]
            target_color = highlight_color if idx == self.selected_index else data["default_bg"]
            btn.config(bg=target_color)

    def _activate_selected(self) -> None:
        if not self.button_widgets:
            return
        try:
            button = self.button_widgets[self.selected_index]["widget"]
            # Verificar que el botón aún existe antes de invocarlo
            if button.winfo_exists():
                button.invoke()
        except (tk.TclError, AttributeError):
            # El botón fue destruido, ignorar
            pass

    def _shutdown_controller(self) -> None:
        if getattr(self, "controller", None):
            self.controller.stop()
            self.controller = None

    def _on_close(self) -> None:
        self._shutdown_controller()
        self.root.destroy()
