from flask_restful import Resource
from flask import request, jsonify
from .. import db
import datetime as dt
from main.models import CompraModel
from main.auth.decorators import role_required
from sqlalchemy.orm.exc import NoResultFound

class Compra(Resource):

    def get(self, id):
        compra = db.session.query(CompraModel).get_or_404(id)
        try:
            return compra.to_json(),200
        except Exception as e:
            return f'Error: {type(e).__name__}. Detalle: {e}',404
    

    # El decorador role_required recibe como parametro la lista de roles que pueden acceder a la funcion
    @role_required(roles=['Admin'])
    def put(self, id):
        compra = db.session.query(CompraModel).get_or_404(id)
        data = request.get_json().items()
        for key, value in data:
            if key == 'fecha_compra':
                # Convierte fecha_compra a un objeto datetime antes de modificar en la base de datos
                value = dt.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
            setattr(compra, key, value)
        try:
            db.session.add(compra)
            db.session.commit()
            return compra.to_json(), 201
        except Exception as e:
            return f'Error: {type(e).__name__}. Detalle: {e}', 404
        

    # El decorador role_required recibe como parametro la lista de roles que pueden acceder a la funcion
    @role_required(roles=['Admin'])
    def delete(self, id):
        compra = db.session.query(CompraModel).get_or_404(id)
        if compra is None: 
            return {'Mensaje de error':f'ID {id} no existe'},404
        try:
            db.session.delete(compra)
            db.session.commit()
            return {"Mensaje":"Compra eliminada exitosamente"},200
            
        except Exception as error:
            # deshace los cambios y devuelve un mensaje de error
            db.session.rollback()
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'},400


class Compras(Resource):

    @role_required(roles=['Admin'])
    def get(self):
        page = 1        # Pagina
        per_page = 5    # cantidad de registro por pagina
        max_per_page = 100  # Máximo número de registros por página
        # realiza la query y ordena por fecha de forma descendente
        compras = db.session.query(CompraModel).order_by(CompraModel.fecha_compra.desc())
        if request.get_json():
            filters = request.get_json().items()
            for key, value in filters:
                if key == 'page':
                    page = max(1, int(value))  # Asegura que la página sea al menos 1
                elif key == 'per_page':
                    per_page = max(1, int(value))  # Asegura que per_page sea al menos 1
        try:
            compras = compras.paginate(page=page, per_page=min(per_page,max_per_page))
            return jsonify({
                'Productos':[detalle.to_json() for detalle in compras.items],  # Cambia 'detalle' a 'producto'
                'Total de registros': compras.total,
                'Total de páginas': compras.pages,
                'página actual': page
            })
        except Exception as error:
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400

    @role_required(roles=['Admin'])
    def post(self):
        compra = CompraModel.from_json(request.get_json())
        db.session.add(compra)
        # commit para aplicar los cambios
        db.session.commit()
        return compra.to_json(), 201