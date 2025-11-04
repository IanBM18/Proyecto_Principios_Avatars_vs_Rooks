import json
import os
import bcrypt  # librería para encriptar contraseñas


class UserAuthentication:
    def __init__(self, data_path="DATA/usuarios.json"):
        """
        Maneja el registro, autenticación y configuración de usuarios.
        """
        self.data_path = data_path
        print(f"[DEBUG] Archivo de usuarios se está guardando en: {os.path.abspath(self.data_path)}")

        # Crear el archivo si no existe
        if not os.path.exists(self.data_path):
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, "w") as f:
                json.dump([], f, indent=4)

        # Asegurar que todos los usuarios tengan sección de settings
        self.ensure_all_users_have_settings()

    # --------------------------
    #     MÉTODOS BÁSICOS
    # --------------------------

    def load_users(self):
        """Carga todos los usuarios desde el archivo JSON."""
        try:
            with open(self.data_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_users(self, users):
        """Guarda los usuarios en el archivo JSON."""
        with open(self.data_path, "w") as file:
            json.dump(users, file, indent=4)

    def hash_password(self, password: str) -> str:
        """Genera un hash seguro de la contraseña."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña ingresada coincide con el hash."""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    def find_user(self, username):
        """Busca un usuario por su nombre."""
        users = self.load_users()
        for user in users:
            if user["username"].lower() == username.lower():
                return user
        return None

    def verify_credentials(self, username, password):
        """Verifica usuario y contraseña."""
        user = self.find_user(username)
        if user and self.check_password(password, user["password"]):
            return {"success": True, "role": user.get("role", "player"), "user": user}
        return {"success": False, "message": "Usuario o contraseña incorrectos"}

    def user_exists(self, username, email):
        """Comprueba si ya existe un usuario o correo en el sistema."""
        users = self.load_users()
        for user in users:
            if user["username"] == username or user["email"] == email:
                return True
        return False

    # --------------------------
    #  CONFIGURACIÓN PERSONAL
    # --------------------------

    def get_default_settings(self):
        """Devuelve los valores por defecto para un nuevo usuario."""
        return {
            "volume": 0.5,  # volumen general (0 a 1)
            "music_enabled": True,  # música de fondo
            "effects_enabled": True,  # efectos de clics, botones, etc.
            "language": "es",  # idioma
            "theme_color": "blue",  # color principal del tema
            "avatar": "default.png"  # imagen de perfil
        }

    def ensure_all_users_have_settings(self):
        """Se asegura de que todos los usuarios tengan el campo 'settings'."""
        users = self.load_users()
        changed = False
        for user in users:
            if "settings" not in user:
                user["settings"] = self.get_default_settings()
                changed = True
            else:
                # completar si faltan claves nuevas
                defaults = self.get_default_settings()
                for key, value in defaults.items():
                    if key not in user["settings"]:
                        user["settings"][key] = value
                        changed = True
        if changed:
            self.save_users(users)

    def get_user_settings(self, username):
        """Obtiene los ajustes del usuario, o crea los valores por defecto si no existen."""
        users = self.load_users()
        for user in users:
            if user["username"].lower() == username.lower():
                if "settings" not in user:
                    user["settings"] = self.get_default_settings()
                    self.save_users(users)
                return user["settings"]
        return self.get_default_settings()  # si no se encuentra el usuario

    def save_user_settings(self, username, new_settings):
        """Guarda los ajustes actualizados del usuario (todos los valores)."""
        users = self.load_users()
        for user in users:
            if user["username"].lower() == username.lower():
                user["settings"] = new_settings
                self.save_users(users)
                return True
        return False

    def update_user_setting(self, username, key, value):
        """Actualiza un ajuste individual (ej. volumen o idioma)."""
        users = self.load_users()
        for user in users:
            if user["username"].lower() == username.lower():
                if "settings" not in user:
                    user["settings"] = self.get_default_settings()
                user["settings"][key] = value
                self.save_users(users)
                return True
        return False