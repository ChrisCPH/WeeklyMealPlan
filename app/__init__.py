from flask import Flask
from app.database import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize DB
    init_db(app)

    # Register routes
    from app.routes import bp
    app.register_blueprint(bp)

    return app
