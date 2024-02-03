from main import db
from werkzeug.security import generate_password_hash, check_password_hash

# Crea una clase que es un modelo de la base de datos
class Usuario(db.Model):

    id              = db.Column(db.Integer, primary_key=True)
    nombre          = db.Column(db.String(45), nullable=False)
    apellido        = db.Column(db.String(45), nullable=False)
    email           = db.Column(db.String(45), nullable=False, unique=True, index=True)
    role            = db.Column(db.String(45), nullable=False)
    telefono        = db.Column(db.String(15), nullable=False)
    password        = db.Column(db.String(100), nullable=False)
    fecha_registro  = db.Column(db.DateTime, nullable=False)
    estado          = db.Column(db.Boolean, default=True, nullable=False) # La columna estado agregue por mi cuenta.
    compras         = db.relationship('Compra',back_populates='usuario', cascade='all, delete-orphan')

    @property
    def plain_password(self):
        raise AttributeError('Password con\'t be read')

    @plain_password.setter
    def plain_password(self, password):
        '''Toma la contraseña de texto plano, la convierte en hash'''
        # texto plano se puede convertir a hash, pero hash no se puede convertir a texto plano
        self.password = generate_password_hash(password)
    
    def validate_pass(self, password):
        '''Crea un hash de la contrasena proveida por el usuario y compara con el hash guardado en la 
        base de datos. Retorna falso o verdadero'''
        return check_password_hash(self.password, password) 
        

    def __repr__(self):
        return f'ID: {self.id} Nombre: {self.nombre}'
    
    def to_json(self):
        usuario_json = {
            "id"            :self.id,
            "nombre"        :self.nombre,
            "apellido"      :self.apellido,
            "email"         :self.email,
            "role"          :self.role,
            "telefono"      :self.telefono,
            "fecha_registro":str(self.fecha_registro),
            "estado"        :int(self.estado)
        }
        return usuario_json
    
    @staticmethod
    def from_json(usuario_json):
        '''Este metodo convierte un json a objeto de python'''
        
        id              = usuario_json.get('id')
        nombre          = usuario_json.get('nombre')
        apellido        = usuario_json.get('apellido')
        email           = usuario_json.get('email')
        role            = usuario_json.get('role')
        telefono        = usuario_json.get('telefono')
        password        = usuario_json.get('password')
        fecha_registro  = usuario_json.get('fecha_registro')
        estado          = usuario_json.get('estado')

        # retorna un objrto usuario
        return Usuario(
            id              = id,
            nombre          = nombre,
            apellido        = apellido,
            email           = email,
            role            = role,
            telefono        = telefono,
            plain_password  = password, # genera el hash de la contra
            fecha_registro  = fecha_registro,
            estado          = estado
        )