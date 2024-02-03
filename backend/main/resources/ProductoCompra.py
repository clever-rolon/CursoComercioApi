from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import ProductoCompraModel
from main.auth.decorators import role_required

class ProductoCompra(Resource):
    '''Esta clase maneja las solicitudes individuales de los detalles de compras'''

    def get(self, id):
        '''Este método devuelve el detalle con el id especificado, también el producto y la compra al que pertenece'''
        detalle_compra = db.session.query(ProductoCompraModel).get_or_404(id)
        try:
            return detalle_compra.to_json(),200  # Devuelve el detalle de compra en formato JSON
        except Exception as error:
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400
    
    def put(self, id):
        '''Este método modifica el detalle de compra con el id especificado con los datos proporcionados'''
        try:
            Deta_a_modificar = db.session.query(ProductoCompraModel).get_or_404(id)  # Obtiene el detalle de compra a modificar
            datos_deta = request.get_json().items()  # Obtiene los datos del detalle de compra desde la solicitud
            for key, value in datos_deta:
                setattr(Deta_a_modificar, key, value)  # Modifica los atributos del detalle de compra

            db.session.add(Deta_a_modificar)  # Agrega el detalle de compra modificado a la sesión
            db.session.commit()  # Confirma los cambios en la base de datos
            return Deta_a_modificar.to_json(),201  # Devuelve el detalle de compra modificado en formato JSON
        
        except Exception as error:
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400
        
    # El decorador role_required recibe como parametro la lista de roles que pueden acceder a la funcion
    @role_required(roles=['admin'])    
    def delete(self, id):
        '''Este método elimina el detalle de compra con el id especificado'''
        try:
            Deta_a_eliminar = db.session.query(ProductoCompraModel).get_or_404(id)  # Obtiene el detalle de compra a eliminar
            db.session.delete(Deta_a_eliminar)  # Elimina el detalle de compra de la sesión
            db.session.commit()  # Confirma los cambios en la base de datos
            return {'Mensaje':'Detalle eleminado exitosamente'},200  # Devuelve un mensaje de éxito
        
        except Exception as error:
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400
        

class ProductosCompras(Resource):
    '''Esta clase maneja las solicitudes a nivel de colección de los detalles de compras'''

    def get(self):
        '''Este método devuelve los detalles de compra, paginado'''
        page = 1        # Pagina
        per_page = 5    # cantidad de registro por pagina
        max_per_page = 100  # Máximo número de registros por página

        Detalles_compra = db.session.query(ProductoCompraModel)
        if request.get_json():
            filters = request.get_json().items()
            for key, value in filters:
                if key == 'page':
                    page = max(1, int(value))  # Asegura que la página sea al menos 1
                elif key == 'per_page':
                    per_page = max(1, int(value))  # Asegura que per_page sea al menos 1
        try:
            Detalles_compra = Detalles_compra.paginate(page=page, per_page=min(per_page,max_per_page))
            return jsonify({
                'Productos':[detalle.to_json() for detalle in Detalles_compra.items],  # Cambia 'detalle' a 'producto'
                'Total de registros': Detalles_compra.total,
                'Total de páginas': Detalles_compra.pages,
                'página actual': page
            })
        except Exception as error:
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400

        
    # El decorador role_required recibe como parametro la lista de roles que pueden acceder a la funcion
    @role_required(roles=['Admin'])
    def post(self):
        '''Este método agrega un nuevo detalle de compra con los datos proporcionados'''
        nuevo_detalle = ProductoCompraModel.from_json(request.get_json())  # Crea un nuevo detalle de compra a partir de los datos proporcionados
        try:
            db.session.add(nuevo_detalle)  # Agrega el nuevo detalle de compra a la sesión
            db.session.commit()  # Confirma los cambios en la base de datos
            return nuevo_detalle.to_json(),200  # Devuelve el nuevo detalle de compra en formato JSON
        except Exception as error:
            db.session.rollback()  # Deshace los cambios en la sesión
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400
        
    # El decorador role_required recibe como parametro la lista de roles que pueden acceder a la funcion
    @role_required(roles=['Admin'])
    def delete(self):
        '''Este método elimina todos los detalles de compra'''
        try:
            Deta_a_elimiar = db.session.query(ProductoCompraModel).all()  # Obtiene todos los detalles de compra
            for deta in Deta_a_elimiar:
                db.session.delete(deta)  # Elimina cada detalle de compra de la sesión
            db.session.commit()  # Confirma los cambios en la base de datos
            return {'Mensaje':'Detalles eleminados exitosamente'},404  # Devuelve un mensaje de éxito
        
        except Exception as error:
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400
