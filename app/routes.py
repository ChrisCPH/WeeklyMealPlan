from flask import Blueprint, render_template, request, redirect, url_for
from app.database import get_db
from app.recipescraper import scrape_recipe

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/add', methods=['POST'])
def add_recipe():
    url = request.form['url']
    recipe = scrape_recipe(url)
    db = get_db()
    db.execute('''
        INSERT INTO recipes (title, ingredients, instructions, url)
        VALUES (?, ?, ?, ?)
    ''', (recipe['title'], recipe['ingredients'], recipe['instructions'], url))
    db.commit()
    return redirect(url_for('main.view_recipes'))

@bp.route('/recipes')
def view_recipes():
    db = get_db()
    recipes = db.execute('SELECT * FROM recipes').fetchall()
    return render_template('recipes.html', recipes=recipes)
