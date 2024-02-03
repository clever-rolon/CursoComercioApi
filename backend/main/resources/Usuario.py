from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from flask import request, jsonify
from .. import db
import datetime as dt
from main.models import UsuarioModel
from main.auth.decorators import role_required

class Usuario(Resource):
    '''Esta clase maneja las solicitudes individuales de los usuarios'''

    # El decorador role_required recibe como parametro la lista de roles que pueden acceder a la funcion
    @role_required(roles=['Admin'])
    def get(self, id):
        usuario = db.session.query(UsuarioModel).get_or_404(id)
        try:
            return usuario.to_json(), 200
        except:
            return '', 404
        

    # El decorador role_required recibe como parametro la lista de roles que pueden acceder a la funcion
    @role_required(roles=['Admin'])
    def delete(self, id):
        # Buscamos en la base de datos al usuario al que se quiere dar de baja
        usuario = db.session.query(UsuarioModel).get_or_404(id)
        nombre = f'{usuario.nombre} {usuario.apellido}'
        try:
            # Admin puede dar de baja a cualquier usuario, el ciente solo puede darse de baja a sí mismo
            usuario.estado = False
            db.session.add(usuario)

        except Exception as error:
            db.session.rollback()
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400
        
        else:
            # Si no hubo inconvenientes, confirma el cambio
            db.session.commit()
            return f'El usuario {nombre} fue dado de baja exitosamente', 200



    # El admin puede modificar todos los registros, el cliente solo puede modificar su propio registro
    @role_required(roles=['Admin','Cliente'])
    def put(self, id):
        # Obtiene los datos del usuario actual, que se encuentran en el JWT
        usuario_actual = get_jwt_identity()

        try:
            # busca en la db el registro y lo guarda en la variable usuario como objeto de pyton
            usuario = db.session.query(UsuarioModel).get_or_404(id)
            datos_usuario = request.get_json().items()

            if usuario_actual['role'] == 'Admin':
                Realizar_cambio = True
            
            elif usuario_actual['usuario_id'] == usuario.id:
                Realizar_cambio = True

            else:
                Realizar_cambio = False
                
            if Realizar_cambio:
                # Por cada elemento del registro del usuario a modificar
                for key, value in datos_usuario:

                    # Convierte el string de fecha a un objeto datetime y python
                    if key == 'fecha_registro':
                        value = dt.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
                        
                    # Cualquier número distinto a 0 es True
                    elif key == 'estado': 
                        value = bool(int(value)) 

                    # set atributo al objeto
                    setattr(usuario,key,value)

                # como estamos en una consulta POST add modifica el registro, no agrega uno nuevo
                db.session.add(usuario)

                # confirma el/los cambio/s en la base de datos
                db.session.commit()

                # Retorna los datos ya modificados
                return usuario.to_json(), 202
            
            else:
                return 'No puede modificar datos de otros usuarios', 401
            
        except Exception as error:
            # deshace el cambio aplicado en la base de datos
            db.session.rollback()
            return {'Mensaje de error',f'{type(error).__name__}. {str(error)}'}
    



class Usuarios(Resource):
    '''Esta clase maneja las solicitudes a nivel de coleccion'''

    # Solo admin puede ver todas los usuarios registrados en el sistema
    @role_required(roles=['Admin'])
    def get(self):
        page = 1        # Pagina
        per_page = 5    # cantidad de registro por pagina
        max_per_page = 100  # Máximo número de registros por página

        lista_usuarios = db.session.query(UsuarioModel).order_by(UsuarioModel.apellido)
        
        if request.get_json():
            filters = request.get_json().items()
            for key, value in filters:
                if key == 'page':
                    page = max(1, int(value))  # Asegura que la página sea al menos 1
                elif key == 'per_page':
                    per_page = max(1, int(value))  # Asegura que per_page sea al menos 1
        try:
            lista_usuarios = lista_usuarios.paginate(page=page, per_page=min(per_page,max_per_page))
            return jsonify({
                'Usuarios':[usuario.to_json() for usuario in lista_usuarios.items],
                'Total de registros': lista_usuarios.total,
                'Total de páginas': lista_usuarios.pages,
                'Página actual': page
            })
        except Exception as error:
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400
    

