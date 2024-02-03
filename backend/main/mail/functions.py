# Importamos las librerías necesarias
from .. import mailsender, db
from flask import current_app, render_template, Blueprint
from flask_mail import Message
from smtplib import SMTPException
from main.models import UsuarioModel, ProductoModel
from main.auth.decorators import role_required

# Definimos una función para enviar correos. Parametros(para, asunto, plantilla, **kwargs)
def send_mail(to, subject, template, **kwargs):
    # Creamos un nuevo mensaje
    msg = Message(subject, sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=to)
    try:
        # Intentamos renderizar la plantilla y enviar el correo
        msg.body = render_template(f'{template}.txt', **kwargs)
        # El template puede ser un html, no necesariamente debe ser .txt
        mailsender.send(msg)
    except SMTPException as error:
        # Si hay un error, lo capturamos y devolvemos un mensaje de error
        return f'La entrega del correo falló. {type(error).__name__}, {error}'
    else:
        # Si todo va bien, devolvemos True
        return True


# Creamos un nuevo Blueprint para el correo
mail = Blueprint('mail', __name__, url_prefix='/mail')


# A mail, agregamos una ruta para el envío de newsletters (Boletin)
@mail.route('/newsletter', methods=['POST'])
@role_required(roles=['Admin'])  # Solo los usuarios con rol 'Admin' pueden acceder a esta ruta
def newsletter():
    # Consultar en la base de datos todos los cliente
    usuarios = db.session.query(UsuarioModel).filter(UsuarioModel.role == 'Cliente').all()
    # Consutar todos los productos
    productos = db.session.query(ProductoModel).all()

    try:
        # Por cada cliente activo intenta enviar botetin de productos
        for usuario in usuarios:
            if usuario.estado == True:
                # Llama a la funcion send_mail
                send_mail([usuario.email],'Productos en venta','newsletter',usuario=usuario, productos=[producto.nombre for producto in productos])
    
    except SMTPException as error:
        return f'La entrega del correo falló. {type(error).__name__}, {error}'
    
    else:
        return 'Correos enviados'