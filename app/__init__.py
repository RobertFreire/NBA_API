from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.routes import main  # Importando o Blueprint corretamente
    app.register_blueprint(main)  # Registrando o Blueprint

    return app
