from flask_restful import Resource, request
from flask_jwt_extended import get_jwt_identity
from flask import jsonify

import datetime as dt

from .. import db
from sqlalchemy.exc import IntegrityError

from main.models import UsuarioModel
from main.auth.decorators import role_required


class Cliente(Resource):
    '''Esta clase maneja las solicitudes individuales de los clientes'''

    @role_required(roles=['Cliente'])
    def get(self, id):
        # Busca el registro que tenga el id especificado en la variable
        cliente = db.session.query(UsuarioModel).get_or_404(id)

        # Obtiene el token del usuario
        usuario_actual = get_jwt_identity() 

        try:
            if usuario_actual['usuario_id'] == cliente.id:
                 return cliente.to_json(), 200
            
            else:
                return 'No puede obtener datos de otros clientes', 401

        except Exception as error:
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400
        


    # El cliente solo puede modificar su propio registro
    @role_required(roles=['Cliente'])
    def put(self, id):
        # Obtiene los datos del usuario actual, que se encuentran en el JWT
        usuario_actual = get_jwt_identity()

        try:
            # busca en la db el registro y lo guarda en la variable usuario como objeto de pyton
            usuario = db.session.query(UsuarioModel).get_or_404(id)
            datos_usuario = request.get_json().items()

            if usuario_actual['usuario_id'] == usuario.id:
                # Por cada elemento del registro del usuario a modificar
                for key, value in datos_usuario:

                    # Convierte el string de fecha a un objeto datetime y python
                    if key == 'fecha_registro':
                        value = usuario.fecha_registro # Asi evita que se cambie la fecha de registro
                        
                    # Evita que de baja.Cualquier número distinto a 0 es True
                    elif key == 'estado': 
                        value = bool(int(1)) 

                    # Verifica si se cambia el role, vuelve a colocar a cliente
                    elif key == 'role':
                        value = 'Cliente'

                    # set atributo al objeto
                    setattr(usuario,key,value)

                # como estamos en una consulta POST add modifica el registro, no agrega uno nuevo
                db.session.add(usuario)

                # confirma el/los cambio/s en la base de datos
                db.session.commit()

                # Retorna los datos ya modificados
                return usuario.to_json(), 202

            else:
                return 'No puede modificar datos de otros cliente', 401
            
        except Exception as error:
            # deshace el cambio aplicado en la base de datos
            db.session.rollback()
            return {'Mensaje de error',f'{type(error).__name__}. {str(error)}'}



class Clientes(Resource):
    '''Esta clase maneja las solicitudes a nivel de colección para los clientes'''

    @role_required(roles=['Admin'])
    def get(self):
        page = 1            # Pagina
        per_page = 5        # cantidad de registro por pagina
        max_per_page = 100  # Máximo número de registros por página

        # Obtiene la lista de todos los cliente registrados
        lista_clientes = db.session.query(UsuarioModel).filter(UsuarioModel.role == 'Cliente').order_by(UsuarioModel.apellido)
        
        if request.get_json():
            filters = request.get_json().items()
            for key, value in filters:
                if key == 'page':
                    page = max(1, int(value))  # Asegura que la página sea al menos 1
                elif key == 'per_page':
                    per_page = max(1, int(value))  # Asegura que per_page sea al menos 1
        try:
            lista_clientes = lista_clientes.paginate(page=page, per_page=min(per_page,max_per_page))
            return jsonify({
                'Clientes':[cliente.to_json() for cliente in lista_clientes.items],
                'Total de registros': lista_clientes.total,
                'Total de páginas': lista_clientes.pages,
                'Página actual': page
            })
        except Exception as error:
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400

        
    @role_required(roles=['Admin'])
    def post(self):
        try:
            # Convierte el JSON de la solicitud en un objeto UsuarioModel
            cliente_json = UsuarioModel.from_json(request.get_json())
            # Establece el rol del usuario como "Cliente"
            cliente_json.role = "Cliente"
            # Convierte la fecha de registro de una cadena a un objeto datetime
            cliente_json.fecha_registro = dt.datetime.strptime(cliente_json.fecha_registro, '%Y-%m-%d %H:%M:%S.%f')
            # Agrega el nuevo cliente a la base de datos
            db.session.add(cliente_json)
            # Confirma los cambios en la base de datos
            db.session.commit()
            # Devuelve el nuevo cliente como JSON
            return cliente_json.to_json(),201
        
        except IntegrityError:
            # Si el correo electrónico ya está en uso, deshace los cambios y devuelve un mensaje de error
            db.session.rollback()
            return {'Mensaje':f'El correo {cliente_json.email} ya se encuentra en uso. Ingrese otro correo'}, 400
        
        except Exception as error:
            # Si ocurre otro error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400
