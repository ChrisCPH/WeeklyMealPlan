import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'recipes.db')

class Config:
    SECRET_KEY = 'supersecretkey'
    DATABASE = DB_PATH
