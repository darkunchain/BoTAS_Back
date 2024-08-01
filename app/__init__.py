from flask import Flask

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Cargar la configuración
    app.config.from_object('app.config.Config')
    app.config.from_pyfile('config.py', silent=True)

    # Registrar Blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
