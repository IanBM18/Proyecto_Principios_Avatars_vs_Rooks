import re #Permite buscar patrones en el texto
import datetime #Permite trabajar con fechas y horas
from enum import Enum #Crea opciones predefinidas
from typing import Dict, List, Optional #Para especificar el tipo de dato que se espera en la función
from UserAutentication import UserAuthentication

class UserRole(Enum):
    ADMIN = "admin"
    PLAYER = "player"

class UserRegistration:
    def __init__(self):
        self.max_image_size_mb = 5
        self.allowed_image_formats = ['jpg', 'jpeg', 'png']

    def ValidateUsername(self, username: str) -> List[str]:
        errors = []
        if not username:
            errors.append("El nombre de usuario no puede estar vacío.")
        elif len(username) < 3 or len(username) > 12:
            errors.append("El nombre de usuario debe tener entre 3 y 12 caracteres.")
        elif not re.match("^[A-Za-z0-9_]+$", username):
            errors.append("El nombre de usuario solo puede contener letras, números y guiones bajos.")
        return errors

    def ValidateEmail(self, email: str) -> List[str]:
        errors = []
        if not email:
            errors.append("Digite un correo electrónico válido.")
        else:
            EmailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(EmailPattern, email):
                errors.append("El formato del correo electrónico no es válido.")
        return errors

    def ValidatePassword(self, password: str) -> List[str]:
        errors = []
        if not password:
            errors.append("La contraseña no puede estar vacía.")
        else:
            if len(password) < 12:
                errors.append("La contraseña debe tener al menos 12 caracteres.")
            if not re.search(r'[A-Z]', password):
                errors.append("Debe contener al menos una letra mayúscula.")
            if not re.search(r'[a-z]', password):
                errors.append("Debe contener al menos una letra minúscula.")
            if not re.search(r'[0-9]', password):
                errors.append("Debe contener al menos un número.")
            if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
                errors.append("Debe contener al menos un carácter especial.")
        return errors

    def ValidateProfilePhoto(self, photo_info: Dict) -> List[str]:
        errors = []
        if not photo_info:
            errors.append("La foto es requerida para administradores.")
            return errors
        format_valid = photo_info.get('format', '').lower() in self.allowed_image_formats
        if not format_valid:
            errors.append(f"Formato inválido. Debe ser uno de: {', '.join(self.allowed_image_formats)}.")
        size_valid = photo_info.get('size_mb', 0) <= self.max_image_size_mb
        if not size_valid:
            errors.append(f"El tamaño de la imagen no debe exceder {self.max_image_size_mb} MB.")
        return errors

    def ValidateDateOfBirth(self, DateOfBirth: str) -> List[str]:
        errors = []
        if not DateOfBirth:
            errors.append("La fecha de nacimiento es requerida para administradores.")
            return errors
        try:
            DateOfBirthObj = datetime.datetime.strptime(DateOfBirth, "%Y-%m-%d")
            age = (datetime.datetime.now() - DateOfBirthObj).days // 365
            if age < 18:
                errors.append("El usuario debe ser mayor de 18 años.")
        except ValueError:
            errors.append("El formato de la fecha debe ser AAAA-MM-DD.")
        return errors


class RegistrationService:
    def __init__(self):
        self.validator = UserRegistration()
        self.auth = UserAuthentication()

    def RegisterUser(self, UserData: Dict) -> Dict:
        errors = []
        role = UserData.get('role', UserRole.PLAYER)

        errors.extend(self.validator.ValidateUsername(UserData.get('username', '')))
        errors.extend(self.validator.ValidateEmail(UserData.get('email', '')))
        errors.extend(self.validator.ValidatePassword(UserData.get('password', '')))

        if self.auth.user_exists(UserData.get('username'), UserData.get('email')):
            errors.append("El usuario o correo ya están registrados.")

        if role == UserRole.ADMIN:
            errors.extend(self.validator.ValidateProfilePhoto(UserData.get('profile_photo')))
            errors.extend(self.validator.ValidateDateOfBirth(UserData.get('date_of_birth')))
            if not UserData.get('full_name'):
                errors.append("El nombre completo es requerido para administradores.")

        if errors:
            return {'success': False, 'errors': errors, 'message': "Error en el registro."}

        try:
            # Encriptar contraseña
            hashed_password = self.auth.hash_password(UserData['password'])
            UserData['password'] = hashed_password

            # Convertir Enum a string
            if hasattr(UserData["role"], "value"):
                UserData["role"] = UserData["role"].value

            usuarios = self.auth.load_users()
            usuarios.append(UserData)
            self.auth.save_users(usuarios)

            self.SendConfirmationEmail(UserData['email'])
            return {'success': True, 'message': "Usuario registrado exitosamente."}

        except Exception as e:
            return {'success': False, 'errors': [f'Error del sistema: {str(e)}'], 'message': "Error en el registro."}

    def SendConfirmationEmail(self, email: str):
        print(f"Enviando correo de confirmación a {email}...")