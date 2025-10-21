import re #Permite buscar patrones en el texto
import datetime #Permite trabajar con fechas y horas
from enum import Enum #Crea opciones predefinidas
from typing import Dict, List, Optional #Para especificar el tipo de dato que se espera en la función

class UserRole(Enum): #se busca una organización clara de los roles de usuario
    ADMIN = "admin"
    PLAYER = "player"

class UserRegistration:
    def __init__(self): #validara las imagenes del perfil
        self.max_image_size_mb = 5
        self.allowed_image_formats = ['jpg', 'jpeg', 'png']

    def ValidateUsername(self, username: str) -> List[str]: #Esta funcion permite validar el nombre de usuario
        errors = []
        if not username:
            errors.append("El nombre de usuario no puede estar vacío.")
        elif len(username) < 3 or len(username) > 12:
            errors.append("El nombre de usuario debe tener entre 3 y 12 caracteres.") #En user stories dice que deben de ser 12, pero no se especifica si mayor/igual/menor, favor revisar!!
        elif not re.match("^[A-Za-z0-9_]+$", username):
            errors.append("El nombre de usuario solo puede contener letras, números y guiones bajos.")
        return errors

    def ValidateEmail(self, email:str) -> List[str]: #Esta funcion valida el correo electronico
        errors = []
        if not email:
            errors.append("Digite un correo electrónico válido.")
        else:
            EmailPatern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(EmailPatern, email):
                errors.append("El formato del correo electrónico no es válido.")
        return errors
    
    def ValidatePassword(self, password: str) -> List[str]: #Esta función valida la contraseña con los requisitos del cliente
        errors = []
        if not password:
            errors.append("La contraseña no puede estar vacía.")
        else: 
            if len(password) < 12:
                errors.append("La contraseña debe tener al menos 12 caracteres.")
            if not re.search(r'[A-Z]', password):
                errors.append("La contraseña debe contener al menos una letra mayúscula.")
            if not re.search(r'[a-z]', password):
                errors.append("La contraseña debe contener al menos una letra minúscula.")
            if not re.search(r'[0-9]', password):
                errors.append("La contraseña debe contener al menos un número.")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                errors.append("La contraseña debe contener al menos un carácter especial.")
        return errors

    def ValidateProfilePhoto(self, photo_info: Dict) -> List[str]: #Esta función valida la foto de perfil
        errors = []
        if not photo_info:
            errors.append("La foto es requerida para administradores")
            return errors  # La foto de perfil es opcional

        FormatValid = photo_info.get('format', '').lower() in self.allowed_image_formats #En el caso de que la foto presente un formato invalido
        if not FormatValid:
            errors.append(f"El formato de la imagen debe ser uno de los siguientes: {', '.join(self.allowed_image_formats)}.")

        size_valid = photo_info.get('size_mb', 0) <= self.max_image_size_mb #En caso de que la foto exceda el tamaño permitido
        if not size_valid:
            errors.append(f"El tamaño de la imagen no debe exceder {self.max_image_size_mb} MB.")
        return errors
    
    def ValidateDateOfBirth(self, DateOfBirth: str) -> List[str]: #Esta función valida la fecha de nacimiento para administradores
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
            errors.append("El formato de la fecha de nacimiento debe ser AAAA-MM-DD.")
        return errors
    
class RegistrationService:
    def __init__(self):
        self.validator = UserRegistration() #Aqui se simula una base de datos simple
        self.existing_users = set()
        self.existing_emails = set()

    def CheckUserExists(self, username: str, email:str) -> List[str]: #Esta funcion verifica si el usuario o el email ingresado ya existe
        errors = []
        if username in self.existing_users:
            errors.append("El nombre de usuario ya existe.")
        if email in self.existing_emails:
            errors.append("El correo electrónico ya está registrado.")
        return errors
    
    def RegisterUser(self, UserData: Dict) -> Dict: #Registra un nuevo usuario segun los requisitos del cliente
        errors = [] #El argumento UserData es un diccionario que contiene los datos del usuario a registrar
        role = UserData.get('role', UserRole.PLAYER) #El argumento Dict devuelve el resultado del registro con exito o error
        errors.extend(self.validator.ValidateUsername(UserData.get('username', ''))) #Validaciones basicas para todos los usuarios
        errors.extend(self.validator.ValidateEmail(UserData.get('email', '')))
        errors.extend(self.validator.ValidatePassword(UserData.get('password', '')))

        if not errors:
            errors.extend(self.CheckUserExists(UserData.get('username', ''), UserData.get('email', '')))

        if role == UserRole.ADMIN: #Validaciones adicionales para administradores
            errors.extend(self.validator.ValidateProfilePhoto(UserData.get('profile_photo')))
            errors.extend(self.validator.ValidateDateOfBirth(UserData.get('date_of_birth')))
            if not UserData.get('full_name'):
                errors.append("El nombre completo es requerido para administradores.")

        if errors: 
            return {'success': False, 'errors': errors, 'message': "Error en el registro del usuario."}
        
        try:
            self.existing_users.add(UserData.get('username'))
            self.existing_emails.add(UserData.get('email'))
            self.send_confirmation_email(UserData['email'])
            return {'success': True, 'message': "Usuario registrado exitosamente.", 'userid': f"user_{len(self.existing_users)}"}

        except Exception as e:
            return {'success': False, 'errors': [f'Error del sistema:{str(e)}'], 'message': "Error en el registro del usuario."}
       
    def SendConfirmationEmail(self, email: str): #Simula el envio de un correo de confirmacion
        print(f"Enviando correo de confirmación a {email}...") #Si se llegara a implementar realmente, debe de ser intercambiado por el codigo correspondiente