# Importamos la libreria que nos permite manejar archivos del sistema operativo
import os
# Importamos la clase Flask del módulo flask
from flask import Flask
# Importamos la función load_dotenv del módulo dotenv
from dotenv import load_dotenv


# Importamos la clase Api del módulo flask_restful
from flask_restful import Api
# Importo para trabajar con sql
from flask_sqlalchemy import SQLAlchemy
# Importo el modulo para trabajar con JWT
from flask_jwt_extended import JWTManager
# Importo el modulo para trabajar con mail
from flask_mail import Mail

# Creamos una instacia de la clase Mail
mailsender = Mail()

# Creamos una instancia de la clase Api
api = Api()

# Creamos una instancia de la clase sqlalchemy
db = SQLAlchemy()

# Creamos una instancia de la clase JWTManager
jwt = JWTManager()

# Definimos la función create_app
def create_app():
    '''Esta funcion crea app principal, configura base de datos, etc'''

    # Creamos una instancia de la clase Flask
    app = Flask(__name__)


    # Cargamos las variables de entorno del archivo .env
    load_dotenv()


    # CONFIGURACION DE LA BASE DE DATOS
    PATH = os.getenv("DATABASE_PATH")
    DB_NAME = os.getenv("DATEBASE_NAME")
    # Verifica si no existe la base de datos, lo debe crear
    if not os.path.exists(f'{PATH}{DB_NAME}'):
        # le indicamos que se dirija al directorio
        os.chdir(f'{PATH}')
        # Crea el archivo .db
        file = os.open(f'{DB_NAME}', os.O_CREAT)
    # Configurar la app para que la base de datos no trackee en todo momento para que funcione mas fluido
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Configuramos la direccion url de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{PATH}{DB_NAME}'
    # Inicializamos la clase db con la aplicación Flask
    db.init_app(app)


    # Importamos el módulo resources del paquete main
    import main.resources as resources
    # Añadimos los recursos a la API con sus respectivas rutas
    api.add_resource(resources.ClientesResource, '/clientes')
    api.add_resource(resources.ClienteResource, '/cliente/<id>')
    api.add_resource(resources.UsuariosResource,'/usuarios')
    api.add_resource(resources.UsuarioResource,'/usuario/<id>')
    api.add_resource(resources.ComprasResource,'/compras')
    api.add_resource(resources.CompraResource,'/compra/<id>')
    api.add_resource(resources.ProductosResource,'/productos')
    api.add_resource(resources.ProductoResource,'/producto/<id>')
    api.add_resource(resources.ProductosComprasResource,'/productos-compras')
    api.add_resource(resources.ProductoCompraResource,'/producto-compra/<id>')
    # Inicializamos la API con la aplicación Flask
    api.init_app(app)


    # Configurar el JWT
    app.config['JWT_SECRET_KEY']            = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES']  = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES'))
    # Inicializamos el JWT con la aplicacion Flask
    jwt.init_app(app)

    # Importa la ruta para login y register
    from main.auth.routes import auth
    app.register_blueprint(auth)


    # Importa la ruta de la funcion que envia el correo
    from main.mail.functions import mail
    app.register_blueprint(mail)
    # Configurar mail
    app.config['MAIL_HOSTNAME']      = os.getenv('MAIL_HOSTNAME')
    app.config['MAIL_SERVER']        = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT']          = os.getenv('MAIL_PORT')
    app.config['MAIL_USE_TLS']       = os.getenv('MAIL_USE_TLS')
    app.config['MAIL_USERNAME']      = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD']      = os.getenv('MAIL_PASSWORD')
    app.config['FLASKY_MAIL_SENDER'] = os.getenv('FLASKY_MAIL_SENDER')
    # Inicializamos el mailsender con la aplicacion Flask
    mailsender.init_app(app)


    # Devolvemos la aplicación Flask
    return app

