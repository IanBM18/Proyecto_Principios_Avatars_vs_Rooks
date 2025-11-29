# gui/ajustes.py
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import os
import pygame

from UserAutentication import UserAuthentication
from assets.MusicManager import MusicManager
from gui.ventanaimagen import VentanaImagen
from gui.menu_principal import apply_theme_to_window  # helper to preview theme on-save

ASSETS_AVATARS = os.path.join("assets", "avatars")  # carpeta donde pondrás avatars (crear si no existe)

THEMES = {
    "dark": {"bg": "#121212", "fg": "white", "card": "#1e1e1e", "accent": "#2e8b57"},
    "light": {"bg": "white", "fg": "black", "card": "#f2f2f2", "accent": "#1e90ff"},
    "blue": {"bg": "#0f1724", "fg": "white", "card": "#071020", "accent": "#2563eb"},
    "green": {"bg": "#0b2b16", "fg": "white", "card": "#0f3a22", "accent": "#32cd32"},
    "red": {"bg": "#2b0a0a", "fg": "white", "card": "#3a0e0e", "accent": "#ff4d4d"},
    "purple": {"bg": "#12061a", "fg": "white", "card": "#231233", "accent": "#8b5cf6"},
}

class AjustesWindow:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol
        self.auth = UserAuthentication()
        self.music = MusicManager()  # instancia global

        # cargar ajustes del usuario (persistidos)
        self.user_settings = self.auth.get_user_settings(usuario)

        # ventana
        self.root = tk.Tk()
        self.root.title("Ajustes - Avatars VS Rooks")
        self.ventana_imagen = VentanaImagen(self.root, ruta_imagen="assets/fondos/fondopre1.png")
        self.root.geometry("900x750")
        self.root.config(bg=THEMES.get(self.user_settings.get("theme_color","blue"))["bg"])

        # container (card)
        self.card = tk.Frame(self.root, bg=THEMES.get(self.user_settings.get("theme_color","blue"))["card"], bd=0)
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=800, height=650)

        # título
        tk.Label(self.card, text="⚙️ Ajustes", font=("Arial", 18, "bold"),
                 bg=self.card["bg"], fg=THEMES[self.user_settings.get("theme_color","blue")]["accent"]).place(x=20, y=15)

        # ---- Volumen ----
        tk.Label(self.card, text="Volumen general", bg=self.card["bg"], fg=THEMES[self.user_settings.get("theme_color","blue")]["fg"]).place(x=20, y=60)
        self.vol_slider = ttk.Scale(self.card, from_=0, to=1, orient="horizontal",
                                    value=self.user_settings.get("volume", 0.5),
                                    command=self.cambiar_volumen)
        self.vol_slider.place(x=20, y=90, width=300)

        # sonido efecto
        tk.Button(self.card, text="🔊 Probar efecto", bg="#333", fg="white", command=self.probar_efecto).place(x=340, y=85, width=120)

        # ---- Soundtrack ----
        tk.Label(self.card, text="Soundtrack", bg=self.card["bg"], fg=THEMES[self.user_settings.get("theme_color","blue")]["fg"]).place(x=20, y=130)
        self.soundtrack_var = tk.IntVar(value=self.user_settings.get("soundtrack", 1))
        tk.Radiobutton(self.card, text="Track 1", variable=self.soundtrack_var, value=1, bg=self.card["bg"], fg=THEMES[self.user_settings.get("theme_color","blue")]["fg"]).place(x=20, y=160)
        tk.Radiobutton(self.card, text="Track 2", variable=self.soundtrack_var, value=2, bg=self.card["bg"], fg=THEMES[self.user_settings.get("theme_color","blue")]["fg"]).place(x=120, y=160)
        tk.Button(self.card, text="Cambiar soundtrack", bg="#333", fg="white", command=self.cambiar_soundtrack).place(x=240, y=155, width=140)

        # ---- Tema ----
        tk.Label(self.card, text="Tema visual", bg=self.card["bg"], fg=THEMES[self.user_settings.get("theme_color","blue")]["fg"]).place(x=20, y=210)
        self.theme_var = tk.StringVar(value=self.user_settings.get("theme_color", "blue"))
        xpos = 20
        for key in THEMES.keys():
            tk.Radiobutton(self.card, text=key.capitalize(), variable=self.theme_var, value=key,
                           bg=self.card["bg"], fg=THEMES[key]["fg"], command=self.preview_theme).place(x=xpos, y=240)
            xpos += 110

        # ---- Avatar selection ----
        tk.Label(self.card, text="Avatar", bg=self.card["bg"], fg=THEMES[self.user_settings.get("theme_color","blue")]["fg"]).place(x=20, y=290)
        self.avatar_frame = tk.Frame(self.card, bg=self.card["bg"])
        self.avatar_frame.place(x=20, y=320, width=460, height=150)

        # cargar avatares desde carpeta
        self.available_avatars = self._load_avatars()
        self.selected_avatar = tk.StringVar(value=self.user_settings.get("avatar", "default.png"))

        # grid de thumbnails
        self._render_avatar_thumbs()

        # preview a la derecha
        self.preview_label = tk.Label(self.card, text="Preview", bg=self.card["bg"], fg=THEMES[self.user_settings.get("theme_color","blue")]["fg"])
        self.preview_label.place(x=520, y=320)
        self.preview_img_label = tk.Label(self.card, bg=self.card["bg"])
        self.preview_img_label.place(x=520, y=350, width=160, height=120)
        self._update_preview_image(self.selected_avatar.get())

        # botón para subir avatar personalizado
        tk.Button(self.card, text="Subir avatar...", bg="#333", fg="white", command=self.subir_avatar).place(x=520, y=480, width=160)

        # ---- Guardar y volver ----
        tk.Button(self.card, text="💾 Guardar", bg=THEMES[self.user_settings.get("theme_color","blue")]["accent"],
                  fg="white", command=self.guardar).place(x=650, y=220, width=160, height=36)

        tk.Button(self.card, text="⬅ Volver al menú", bg="#8b0000", fg="white", command=self.volver_menu).place(x=650, y=260, width=160, height=36)

        self.root.mainloop()

    # -------------------------
    # AVATARS
    # -------------------------
    def _load_avatars(self):
        if not os.path.exists(ASSETS_AVATARS):
            os.makedirs(ASSETS_AVATARS, exist_ok=True)
        files = []
        for f in os.listdir(ASSETS_AVATARS):
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                files.append(f)
        # si no hay ninguno, crear uno placeholder
        if not files:
            # crear un placeholder simple
            placeholder = "default.png"
            p = os.path.join(ASSETS_AVATARS, placeholder)
            if not os.path.exists(p):
                surf = Image.new("RGBA", (128,128), (80,140,200,255))
                surf.save(p)
            files.append(placeholder)
        return files

    def _render_avatar_thumbs(self):
        for widget in self.avatar_frame.winfo_children():
            widget.destroy()
        cols = 6
        thumb_w = 64
        thumb_h = 64
        for i, fname in enumerate(self.available_avatars):
            full = os.path.join(ASSETS_AVATARS, fname)
            try:
                img = Image.open(full).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                tkimg = ImageTk.PhotoImage(img)
            except Exception:
                tkimg = None
            btn = tk.Radiobutton(self.avatar_frame, image=tkimg, variable=self.selected_avatar, value=fname,
                                 indicatoron=False, width=thumb_w, height=thumb_h,
                                 bg=self.card["bg"], selectcolor="#444",
                                 command=lambda fn=fname: self._update_preview_image(fn))
            btn.image = tkimg
            r = i // cols
            c = i % cols
            btn.place(x=c*(thumb_w+8), y=r*(thumb_h+8))
        # si hay muchos, podrías añadir scrollbar (no necesario por ahora)

    def _update_preview_image(self, fname):
        path = os.path.join(ASSETS_AVATARS, fname)
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize((160,120), Image.Resampling.LANCZOS)
            tkimg = ImageTk.PhotoImage(img)
            self.preview_img_label.configure(image=tkimg)
            self.preview_img_label.image = tkimg
        else:
            self.preview_img_label.configure(image="", text="No image", fg="white")

    def subir_avatar(self):
        file = filedialog.askopenfilename(filetypes=[("Images","*.png;*.jpg;*.jpeg")])
        if not file:
            return
        # copiar a carpeta assets/avatars
        base = os.path.basename(file)
        dest = os.path.join(ASSETS_AVATARS, base)
        try:
            with open(file, "rb") as rf, open(dest, "wb") as wf:
                wf.write(rf.read())
            # recargar lista y render
            self.available_avatars = self._load_avatars()
            self._render_avatar_thumbs()
        except Exception as e:
            print("Error al subir avatar:", e)

    # -------------------------
    # AUDIO / SOUNDTRACK
    # -------------------------
    def cambiar_volumen(self, nuevo_valor):
        valor = float(nuevo_valor)
        self.user_settings["volume"] = valor
        # aplicar volumen en MusicManager
        try:
            self.music.set_volume(valor)
        except Exception:
            pass

    def probar_efecto(self):
        try:
            efecto = pygame.mixer.Sound("assets/sounds/click.wav")
            efecto.set_volume(self.user_settings.get("volume", 0.5))
            efecto.play()
        except Exception as e:
            print("Error reproducir efecto:", e)

    def cambiar_soundtrack(self):
        nuevo = int(self.soundtrack_var.get())
        self.user_settings["soundtrack"] = nuevo
        try:
            self.music.change_track(nuevo)
        except Exception:
            # fallback: play with index
            self.music.play(soundtrack_index=nuevo, volume=self.user_settings.get("volume", 0.5))

    # -------------------------
    # TEMA / PREVIEW
    # -------------------------
    def preview_theme(self):
        tema = self.theme_var.get()
        # aplicar temporalmente al card para preview
        colors = THEMES.get(tema, THEMES["blue"])
        self.card.config(bg=colors["card"])
        # actualizar labels etc (simplificado)
        for w in self.card.winfo_children():
            try:
                if isinstance(w, tk.Label) or isinstance(w, tk.Button) or isinstance(w, tk.Radiobutton):
                    w.config(bg=colors["card"], fg=colors["fg"])
            except Exception:
                pass

    # -------------------------
    # GUARDAR
    # -------------------------
    def guardar(self):
        # actualizar settings en memoria
        self.user_settings["volume"] = float(self.vol_slider.get())
        self.user_settings["soundtrack"] = int(self.soundtrack_var.get())
        self.user_settings["theme_color"] = str(self.theme_var.get())
        self.user_settings["avatar"] = str(self.selected_avatar.get())

        # persistir
        self.auth.save_user_settings(self.usuario, self.user_settings)

        # aplicar theme a la ventana principal (si está abierta de nuevo al entrar)
        try:
            apply_theme_to_window(self.user_settings["theme_color"])
        except Exception:
            pass

        tk.messagebox.showinfo("Guardado", "Ajustes guardados correctamente.")
        self.root.destroy()
        from gui.menu_principal import MainMenu
        MainMenu(self.usuario, self.rol)

    def volver_menu(self):
        self.root.destroy()
        from gui.menu_principal import MainMenu
        MainMenu(self.usuario, self.rol)
