from main import create_app, db
import os

# Crea la app
app = create_app() 
# Nos permite acceder a las propiedades de la aplicacion desde cualquier parte del sistema.
app.app_context().push()  

if __name__ == '__main__':
    # Crea todas las tablas de la base de datos antes de iniciar el servidor
    db.create_all()
    # Leemos el puerto para pasar a la app
    # debug=True Nos permite refrescar en el servidor automaticamente cada cambio que hacemos en la app
    app.run(port=os.getenv('PORT'), debug=True) 