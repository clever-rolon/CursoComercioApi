from .. import jwt 
from flask_jwt_extended import verify_jwt_in_request, get_jwt

from .. import db
from main.models import UsuarioModel

# Definimos un decorador para verificar si el usuario sigue activo y el rol del mismo
def role_required(roles):
    
    def decorator(funcion):

        def wrapper(*args, **kwargs):

            # Verificamos que el JWT es correcto
            verify_jwt_in_request()

            # Obtenemos los claims (peticiones), que están dentro del JWT
            claims = get_jwt()

            # Buscamos los datos del usuario actual en la base de datos
            user = db.session.query(UsuarioModel).get_or_404(claims['sub']['usuario_id'])

            # Si el usuario no está activo retorna un mensaje, sino, pasa a la siguiente verificacion.
            if user.estado is not True:
                return {'Mensaje':f'{user.nombre} {user.apellido}. Su usuario fue dado de baja'},403
            
            # Si el rol del usuario está en los roles permitidos, ejecutamos la función
            if claims['sub']['role'] in roles:
                return funcion(*args, **kwargs)
            else:
                # Sino, devolvemos un mensaje de error y el código de estado 403 (Prohibido)
                return 'Acceso no permitido', 403
            
        return wrapper
    
    return decorator



# Redefinimos el decorador user_identity_loader (Cargador de identidades de usuario) del JWT
@jwt.user_identity_loader
def user_identity_lookup(usuario):
    '''Búsqueda de identidad de usuario'''
    # Devolvemos un diccionario con el id y el rol del usuario. Estos son los contenidos que se guardan en el token
    # Esto es útil para tener acceso rápido a ciertos detalles del usuario desde el token
    return {
        "usuario_id": usuario.id,
        "role": usuario.role
    }




# Redefinimos el decorador additional_headers_loader del JWT
@jwt.additional_headers_loader # Cargador de cabeceras adicional
def add_claims_to_access_token(usuario): 
    '''Adición de claims al token de acceso'''
    # Devolvemos un diccionario con los claims que queremos añadir al token de acceso
    # Los claims son declaraciones sobre el usuario que se pueden verificar independientemente
    # En este caso, estamos añadiendo el id y el rol del usuario a los claims
    claims = {
        'id': usuario.id,
        'role':usuario.role
    }
    return claims

    '''
    En el contexto de la autenticación y autorización, un “claim” se refiere a una declaración que una entidad 
    (generalmente un usuario) hace acerca de sí misma. Es una forma de representar la identidad del usuario y 
    sus atributos en el sistema.
    En este código, los “claims” son los datos del usuario que se guardan en el token JWT (JSON Web Token). Estos 
    pueden incluir detalles como el ID del usuario y el rol del usuario. Estos 
    “claims” se utilizan para verificar la identidad del usuario y controlar el acceso a los recursos en función 
    del rol del usuario.
    Por ejemplo, en este código, el “claim” ‘role’ se utiliza para verificar si el usuario tiene permiso para 
    acceder a una función específica. Si el rol del usuario está en los roles permitidos, se ejecuta la función. 
    Si no, se devuelve un mensaje de error. Esto es lo que hace la función role_required
    '''
