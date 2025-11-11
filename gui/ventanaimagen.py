import tkinter as tk
from PIL import Image, ImageTk
import os

class VentanaImagen:
    def __init__(self, ventana, ruta_imagen=None):
        self.ventana = ventana
        self.ruta_imagen = ruta_imagen
        self.imagen_fondo = None
        self.label_fondo = None
        self.ventana.config(bg="#1a1a1a")

        if ruta_imagen and os.path.exists(ruta_imagen):
            self.cargar_imagen_fondo(ruta_imagen)

            self.ventana.bind('<Configure>', self.redimensionar_fondo)

    def cargar_imagen_fondo(self, ruta_imagen):
        try: 
            self.imagen_pil_original = Image.open(ruta_imagen)
            self.actualizar_imagen_fondo()
        except Exception as e:
            print(f"Error al cargar la imagen de fondo: {e}")

    def actualizar_imagen_fondo(self):
        
        try:
            
            ancho_ventana = self.ventana.winfo_width()
            alto_ventana = self.ventana.winfo_height()
            
            
            if ancho_ventana < 10 or alto_ventana < 10:
                ancho_ventana = 500  
                alto_ventana = 450
            
            
            imagen_redimensionada = self.imagen_pil_original.resize(
                (ancho_ventana, alto_ventana), 
                Image.Resampling.LANCZOS
            )
            
            
            self.imagen_fondo = ImageTk.PhotoImage(imagen_redimensionada)
            
           
            if self.label_fondo:
                self.label_fondo.configure(image=self.imagen_fondo)
            else:
                self.label_fondo = tk.Label(self.ventana, image=self.imagen_fondo)
                self.label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
                self.label_fondo.lower()
                
        except Exception as e:
            print(f"Error al actualizar imagen de fondo: {e}")

    def redimensionar_fondo(self, event=None):
        """Se ejecuta cuando la ventana cambia de tamaño"""
        if event and event.widget == self.ventana:
            self.actualizar_imagen_fondo()

    def centrar_ventana(self, ancho, alto):
        self.ventana.update_idletasks()
        ancho_ventana = self.ventana.winfo_screenwidth()
        alto_pantalla = self.ventana.winfo_screenheight()
        x = (ancho_ventana - ancho) // 2
        y = (alto_pantalla - alto) // 2
        self.ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

        self.ventana.after(100, self.actualizar_imagen_fondo)

    def crear_label(self, **kwargs):
        if "bg" not in kwargs:
            kwargs["bg"] = self.ventana.cget("bg")
        return tk.Label(self.ventana, **kwargs)
    
    def crear_boton(self, **kwargs):
        if 'bg' not in kwargs:
            kwargs['bg'] = "#333"
        if 'fg' not in kwargs:
            kwargs['fg'] = "white"
        if 'relief' not in kwargs:
            kwargs['relief'] = "flat"
        return tk.Button(self.ventana, **kwargs)
    
    def crear_entry(self, **kwargs):
        if 'bg' not in kwargs:
            kwargs['bg'] = "#2a2a2a"
        if 'fg' not in kwargs:
            kwargs['fg'] = "white"
        if 'insertbackground' not in kwargs:
            kwargs['insertbackground'] = "white"
        return tk.Entry(self.ventana, **kwargs)