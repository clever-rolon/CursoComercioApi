# Importamos las librerías necesarias
from flask import request, Blueprint
from flask_jwt_extended import create_access_token
import datetime as dt
from .. import db
from main.models import UsuarioModel
from main.auth.decorators import user_identity_lookup
from main.mail.functions import send_mail

# Creamos un nuevo Blueprint para la autenticación
'''Crea un nuevo Blueprint llamado ‘auth’. Este Blueprint se utilizará para agrupar todas las rutas y funciones relacionadas 
con la autenticación.'''
auth = Blueprint('auth',__name__, url_prefix='/auth')



'''Aquí, define una ruta de login en el Blueprint ‘auth’. Cuando un usuario hace una petición POST a ‘/auth/login’, 
Flask ejecutará la función login().'''
# Definimos la ruta de login
@auth.route('/login',methods=['POST'])
def login():
    # Buscamos al usuario en la base de datos por su correo electrónico
    usuario = db.session.query(UsuarioModel).filter(UsuarioModel.email == request.get_json().get('email')).first_or_404()

    # Si el usuario no se encuentra activo, retorna un mensaje de prohibido.
    if usuario.estado is not True:
        return {'Mensaje':f'{usuario.nombre} {usuario.apellido}. Su usuario fue dado de baja'}, 403
    
    # Verificamos si la contraseña es correcta
    if usuario.validate_pass(request.get_json().get('password')):

        # Si la contraseña es correcta, creamos un token de acceso
        access_token = create_access_token(identity=usuario)

        # Preparamos la respuesta
        data = {'access_token':access_token}

        # Devolvemos la respuesta y el código de estado 200 (OK)
        return data, 200
    else:
        # Si la contraseña es incorrecta, devolvemos un mensaje de error y el código de estado 401 (No autorizado)
        return {'Login':'Contraseña incorrecta'}, 401



'''Define una ruta de registro en el Blueprint ‘auth’. Cuando un usuario hace una petición POST a ‘/auth/register’, 
Flask ejecutará la función register()'''
# Definimos la ruta de registro
@auth.route('/register', methods=['POST'])
def register():
    # Creamos un nuevo usuario a partir de los datos recibidos en el cuerpo de la petición
    usuario = UsuarioModel.from_json(request.get_json())

    # Verificamos si el correo electrónico ya existe en la base de datos
    exits = db.session.query(UsuarioModel).filter(UsuarioModel.email == usuario.email).scalar() is not None

    # Si el correo electrónico ya existe, devolvemos un mensaje de error y el código de estado 409 (Conflicto)
    if exits:
        return {'Mensaje':f'El correo {usuario.email} ya se encuentra en uso. Por favor, ingrese otro.'}, 409
    else:
        try:
            # Intentamos convertir la fecha de registro que es un string a objeto datetime de python
            fecha_registro_str = request.get_json().get('fecha_registro')
            fecha_registro = dt.datetime.strptime(fecha_registro_str, '%Y-%m-%d %H:%M:%S.%f')
            usuario.fecha_registro = fecha_registro

            # Asigna el rol Cliente
            usuario.role = "Cliente"
            
            # Intentamos agregar el nuevo usuario a la base de datos
            db.session.add(usuario)
            db.session.commit()

            # Enviar correo de bienvenida al cliente que acaba de registrarse
            send_mail([usuario.email], 'Bienvenido', 'register', usuario=usuario)

        except Exception as error:
            # Si ocurre un error, hacemos rollback de la transacción y devolvemos un mensaje de error
            db.session.rollback()
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 409
        
        else:
            # Si todo sale bien, devolvemos los datos del nuevo usuario y el código de estado 201 (Creado)
            return {
                'Mensaje':'Registro exitoso',
                'Usuario':[usuario.to_json()]
                }, 201

