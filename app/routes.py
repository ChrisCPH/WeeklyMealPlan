from flask import request, jsonify
from database import get_db
from recipescraper import scrape_recipe_jsonld
import re

def register_routes(app):

    @app.route('/add_recipe_from_url', methods=['POST'])
    def add_recipe_from_url():
        data = request.json
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        recipes = scrape_recipe_jsonld(url)
        if not recipes:
            return jsonify({'error': 'Failed to scrape recipe'}), 500

        recipe_data = recipes[0]

        db = get_db()
        cursor = db.cursor()

        # Insert into recipe table
        cursor.execute('''
            INSERT INTO recipe (
                name, url, description, author, servings, 
                prep_time_minutes, cook_time_minutes, total_time_minutes, 
                rating_value, rating_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            recipe_data['name'],
            url,
            recipe_data.get('description'),
            recipe_data.get('author'),
            recipe_data.get('servings'),
            convert_to_minutes(recipe_data.get('prep_time')),
            convert_to_minutes(recipe_data.get('cook_time')),
            convert_to_minutes(recipe_data.get('total_time')),
            float(recipe_data.get('rating', {}).get('value') or 0),
            int(recipe_data.get('rating', {}).get('count') or 0)
        ))

        recipe_id = cursor.lastrowid

        # Insert ingredients
        for ingredient in recipe_data.get('ingredients', []):
            cursor.execute('''
                INSERT INTO ingredients (recipe_id, name)
                VALUES (?, ?)
            ''', (recipe_id, ingredient))

        # Insert nutrition
        if 'nutrition' in recipe_data and recipe_data['nutrition']:
            cursor.execute('''
                INSERT INTO nutrition (recipe_id, calories, protein, carbs, fat, saturatedFat, unsaturatedFat, cholesterol, fiber,  sodium, sugar)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe_id,
                clean_numeric(recipe_data['nutrition'].get('calories')),
                clean_numeric(recipe_data['nutrition'].get('protein')),
                clean_numeric(recipe_data['nutrition'].get('carbs')),
                clean_numeric(recipe_data['nutrition'].get('fat')),
                clean_numeric(recipe_data['nutrition'].get('saturatedFat')),
                clean_numeric(recipe_data['nutrition'].get('unsaturatedFat')),
                clean_numeric(recipe_data['nutrition'].get('cholesterol')),
                clean_numeric(recipe_data['nutrition'].get('fiber')),
                clean_numeric(recipe_data['nutrition'].get('sodium')),
                clean_numeric(recipe_data['nutrition'].get('sugar'))

            ))

        # Insert steps
        for idx, step in enumerate(recipe_data.get('instructions', []), start=1):
            cursor.execute('''
                INSERT INTO recipe_steps (recipe_id, step_number, step_text)
                VALUES (?, ?, ?)
            ''', (recipe_id, idx, step))

        db.commit()

        return jsonify({'message': 'Recipe added successfully', 'recipe_id': recipe_id})


def convert_to_minutes(duration_str):
    if not duration_str:
        return None
    match = re.search(r'(?:(\d+)h)?\s*(?:(\d+)m)?', duration_str)
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        return hours * 60 + minutes
    return None

def clean_numeric(value):
    if not value:
        return None
    return float(re.sub(r'[^\d.]+', '', str(value)))
