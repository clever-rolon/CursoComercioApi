from .. import db

class ProductoCompra(db.Model):

    id          = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    producto    = db.relationship('Producto', back_populates='productoscompras', uselist=False, single_parent=True)
    compra_id   = db.Column(db.Integer, db.ForeignKey('compra.id'), nullable=False)
    compra      = db.relationship('Compra', back_populates='productoscompras', uselist=False, single_parent=True)

    def __repr__(self):
        return [self.id, self.producto_id, self.compra_id]
    
    def to_json(self):
        productocompra_json = {
            'id'        :self.id,
            'producto'  :self.producto.to_json(),
            'compra'    :self.compra.to_json()
        }
        return productocompra_json
    
    @staticmethod
    def from_json(productocompra_json):
        id          = productocompra_json.get('id')
        producto_id = productocompra_json.get('producto_id')
        compra_id   = productocompra_json.get('compra_id')
        # Retorno un objeto
        return ProductoCompra(
            id          = id,
            producto_id = producto_id,
            compra_id   = compra_id
        )
