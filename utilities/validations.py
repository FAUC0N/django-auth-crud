from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re

def validate_username(username):
    """
    Valida si el nombre de usuario cumple con los criterios de formato y si ya existe en la base de datos.
    """
    if not (5 < len(username) <= 100):
        raise ValidationError("El nombre de usuario debe tener entre 6 y 100 caracteres.")
    
    if not re.search(r"[a-zA-Z]", username):
        raise ValidationError("El nombre de usuario debe contener al menos una letra.")
    
    if not re.fullmatch(r"[a-zA-Z0-9@/_-]+", username):
        raise ValidationError(
            "El nombre de usuario solo puede contener letras, números y los caracteres @ / _ -."
        )
    
    # Verificar si el username ya existe en la base de datos
    if User.objects.filter(username=username).exists():
        raise ValidationError("El nombre de usuario ya está registrado.")
    
    return username

def validate_password(password):
    """
    Valida si la contraseña cumple con los criterios.
    """
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
    
    if not re.search(r"[A-Z]", password):
        raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
    
    if not re.search(r"\d", password):
        raise ValidationError("La contraseña debe contener al menos un número.")
    
    return password

def validate_passwords(password1, password2):
    """
    Valida si las contraseñas coinciden y si cumplen con los criterios.
    """
    if password1 != password2:
        raise ValidationError("Las contraseñas no coinciden.")
    
    # Validar la seguridad de la contraseña
    validate_password(password1)
    return password1
