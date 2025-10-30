import json
import os
import bcrypt  # librería para encriptar contraseñas

class UserAuthentication:
    def __init__(self, data_path="data/usuarios.json"):
        self.data_path = data_path
        if not os.path.exists(self.data_path):
            with open(self.data_path, "w") as f:
                json.dump([], f)

    def load_users(self):
        """Carga todos los usuarios desde el archivo JSON"""
        try:
            with open(self.data_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_users(self, users):
        """Guarda los usuarios en el archivo JSON"""
        with open(self.data_path, "w") as file:
            json.dump(users, file, indent=4)

    def hash_password(self, password: str) -> str:
        """Genera un hash seguro de la contraseña"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña ingresada coincide con el hash"""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    def find_user(self, username):
        """Busca un usuario por su nombre"""
        users = self.load_users()
        for user in users:
            if user["username"].lower() == username.lower():
                return user
        return None

    def verify_credentials(self, username, password):
        """Verifica usuario y contraseña"""
        user = self.find_user(username)
        if user and self.check_password(password, user["password"]):
            return {"success": True, "role": user.get("role", "player")}
        return {"success": False, "message": "Usuario o contraseña incorrectos"}

    def user_exists(self, username, email):
        """Comprueba si ya existe un usuario o correo en el sistema"""
        users = self.load_users()
        for user in users:
            if user["username"] == username or user["email"] == email:
                return True
        return False
