import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_recipe_jsonld(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        json_scripts = soup.find_all('script', type='application/ld+json')
        
        recipes = []
        
        for script in json_scripts:
            try:
                json_data = json.loads(script.string)
                
                if isinstance(json_data, list):
                    items = json_data
                else:
                    items = [json_data]
                
                for item in items:
                    if item.get('@type') == 'Recipe' or 'Recipe' in str(item.get('@type', '')):
                        recipe = extract_recipe_data(item)
                        if recipe:
                            recipes.append(recipe)
                            
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON-LD: {e}")
                continue
        
        return recipes
        
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []

def extract_recipe_data(recipe_json):
    recipe = {}
    
    recipe['name'] = recipe_json.get('name', 'Unknown Recipe')
    recipe['description'] = recipe_json.get('description', '')
    
    author = recipe_json.get('author')
    if author:
        if isinstance(author, dict):
            recipe['author'] = author.get('name', 'Unknown Author')
        elif isinstance(author, list) and author:
            recipe['author'] = author[0].get('name', 'Unknown Author') if isinstance(author[0], dict) else str(author[0])
        else:
            recipe['author'] = str(author)
    
    recipe['prep_time'] = parse_duration(recipe_json.get('prepTime'))
    recipe['cook_time'] = parse_duration(recipe_json.get('cookTime'))
    recipe['total_time'] = parse_duration(recipe_json.get('totalTime'))
    
    recipe['servings'] = recipe_json.get('recipeYield') or recipe_json.get('yield')
    
    ingredients = recipe_json.get('recipeIngredient', [])
    recipe['ingredients'] = [clean_text(ingredient) for ingredient in ingredients]
    
    instructions = recipe_json.get('recipeInstructions', [])
    recipe['instructions'] = []
    
    for instruction in instructions:
        if isinstance(instruction, dict):
            text = instruction.get('text') or instruction.get('name', '')
        else:
            text = str(instruction)
        if text:
            recipe['instructions'].append(clean_text(text))
    
    nutrition = recipe_json.get('nutrition')
    if nutrition and isinstance(nutrition, dict):
        recipe['nutrition'] = {
            'calories': nutrition.get('calories'),
            'protein': nutrition.get('proteinContent'),
            'carbs': nutrition.get('carbohydrateContent'),
            'fat': nutrition.get('fatContent'),
        }
    
    rating = recipe_json.get('aggregateRating')
    if rating and isinstance(rating, dict):
        recipe['rating'] = {
            'value': rating.get('ratingValue'),
            'count': rating.get('ratingCount'),
            'best': rating.get('bestRating'),
            'worst': rating.get('worstRating')
        }
    
    return recipe

def parse_duration(duration_str):
    if not duration_str:
        return None
    
    if isinstance(duration_str, str) and duration_str.startswith('PT'):
        # Parse ISO 8601 duration
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration_str)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            return f"{hours}h {minutes}m" if hours else f"{minutes}m"
    
    return str(duration_str)

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', str(text).strip())

def print_recipe(recipe):
    print(f"Name: {recipe['name']}")
    
    if recipe.get('author'):
        print(f"Author: {recipe['author']}")
    
    if recipe.get('description'):
        print(f"Description: {recipe['description']}")
    
    times = []
    if recipe.get('prep_time'):
        times.append(f"Prep: {recipe['prep_time']}")
    if recipe.get('cook_time'):
        times.append(f"Cook: {recipe['cook_time']}")
    if recipe.get('total_time'):
        times.append(f"Total: {recipe['total_time']}")
    if times:
        print(f"{' | '.join(times)}")
    
    if recipe.get('servings'):
        print(f"Servings: {recipe['servings']}")
    
    if recipe.get('rating'):
        rating = recipe['rating']
        if rating.get('value'):
            print(f"Rating: {rating['value']}/5 ({rating.get('count', 0)} reviews)")
    
    if recipe.get('ingredients'):
        print("\nINGREDIENTS:")
        for i, ingredient in enumerate(recipe['ingredients'], 1):
            print(f"  {i}. {ingredient}")
    
    if recipe.get('instructions'):
        print("\nINSTRUCTIONS:")
        for i, instruction in enumerate(recipe['instructions'], 1):
            print(f"  {i}. {instruction}")
    
    if recipe.get('nutrition'):
        nutrition = recipe['nutrition']
        print("\nNUTRITION:")
        for key, value in nutrition.items():
            if value:
                print(f" {key.title()}: {value}")
    
    print("\n")

# Example usage
if __name__ == "__main__":
    # Test URLs
    test_urls = [
        "https://www.allrecipes.com/recipe/222037/tater-tots-r-casserole/",
        "https://www.food.com/recipe/chocolate-chip-cookies-25037",
        #"https://www.arla.dk/opskrifter/pisket-smor/",
        #"https://www.bbcgoodfood.com/recipes/easy-chocolate-cake",
        #"https://www.simplyrecipes.com/recipes/perfect_guacamole/",
        # Add recipe URLs here
    ]
    
    for url in test_urls:
        print(f"\n🔍 Scraping: {url}")
        recipes = scrape_recipe_jsonld(url)
        
        if recipes:
            print(f"Found {len(recipes)} recipe(s)!")
            for recipe in recipes:
                print_recipe(recipe)
        else:
            print("No recipes found or error occurred")