import sqlite3
from flask import g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('instance/recipes.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS recipe (
                recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                author TEXT,
                servings TEXT,
                prep_time_minutes INTEGER,
                cook_time_minutes INTEGER,
                total_time_minutes INTEGER,
                rating_value REAL DEFAULT 0.0,
                rating_count INTEGER DEFAULT 0
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS ingredients (
                ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                measurement TEXT,
                count REAL,
                notes TEXT,
                FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id)
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS nutrition (
                nutrition_id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                calories REAL,
                protein REAL,
                carbs REAL,
                fat REAL,
                saturatedFat REAL,
                unsaturatedFat REAL,
                cholesterol REAL,
                fiber REAL,
                sodium REAL,
                sugar REAL,
                FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id)
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS recipe_steps (
                recipe_steps_id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                step_number INTEGER NOT NULL,
                step_text TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id)
            )
        ''')

        db.commit()
