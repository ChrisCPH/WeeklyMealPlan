from flask import Flask
from database import init_db
from routes import register_routes

def create_app():
    app = Flask(__name__)

    app.config['DATABASE'] = 'instance/recipes.db'

    init_db(app)

    register_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
