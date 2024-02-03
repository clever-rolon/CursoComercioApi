from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import ProductoModel
from main.auth.decorators import role_required

class Producto(Resource):
    '''Clase para operaciones por un solo producto'''

    def get(self,id):
        '''obtiene un producto'''
        producto = db.session.query(ProductoModel).get_or_404(id)
        try:
            return producto.to_json()
        except:
            return 'Resource not found', 404
        


    def put(self,id):
        '''Modifica los datos o todos los elementos de un producto'''
        producto = db.session.query(ProductoModel).get_or_404(id)
        data = request.get_json().items()
        for key, value in data:
            # set atributos
            setattr(producto, key, value)
        try:
            db.session.add(producto)
            db.session.commit()
            return producto.to_json(), 201
        except:
            return '',404
    


    # El decorador role_required recibe como parametro la lista de roles que pueden acceder a la funcion
    @role_required(roles=['Admin'])
    def delete(self, id):
        '''Elimina un producto'''
        # probar si existe el producto en la baes de datos
        producto = db.session.query(ProductoModel).get_or_404(id)
        try:
            db.session.delete(producto)
            db.session.commit()
            return 'Eliminado exitosamente', 200
        except:
            return '', 404


class Productos(Resource):
    '''Clase para consulta de todos los elementos y agregar un registro'''

    def get(self):
        '''Método GET para obtener todos los productos'''
        page = 1        # Número de la página actual
        per_page = 5    # Cantidad de registros por página
        max_per_page = 100  # Máximo número de registros por página

        # Consulta a la base de datos para obtener todos los productos
        productos = db.session.query(ProductoModel)
        
        # Si hay filtros en la solicitud, se aplican a la consulta
        if request.get_json():
            filters = request.get_json().items()
            for key, value in filters:
                if key == 'page':
                    # Asegura que la página sea al menos 1
                    page = max(1, int(value))  
                elif key == 'per_page':
                    # Asegura que per_page sea al menos 1
                    per_page = max(1, int(value))  
        
        try:
            # Pagina los resultados de la consulta
            productos = productos.paginate(page=page, per_page=min(per_page,max_per_page))
            
            # Devuelve los productos en formato JSON
            return jsonify({
                'Todos los productos':[producto.to_json() for producto in productos.items],
                'Registros': productos.total,
                'Páginas': productos.pages,
                'Página actual': page
            })
        except Exception as error:
            # Si ocurre un error, devuelve un mensaje de error
            return {'Mensaje de error':f'{type(error).__name__}. {error}'}, 400
        

    def post(self):
        '''Método POST para agregar un producto a la base de datos'''
        # Crea un nuevo producto a partir de los datos de la solicitud
        producto = ProductoModel.from_json(request.get_json())
        
        # Agrega el producto a la base de datos
        db.session.add(producto)
        db.session.commit()
        
        # Devuelve el producto agregado en formato JSON
        return producto.to_json(),201




