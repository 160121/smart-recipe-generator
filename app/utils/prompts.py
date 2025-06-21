"""
Prompt templates for the Smart Recipe Generator agents.
"""

INPUT_VALIDATOR_PROMPT = """
You are an input validator for a recipe generator. Your task is to clean and validate user inputs.

User provided ingredients: {ingredients}
User dietary preferences: {dietary_preferences}
Maximum cooking time: {max_time} minutes

Please:
1. Clean and standardize the ingredient list (remove duplicates, fix typos, standardize names)
2. Validate that the ingredients are actual food items
4. Return a structured response

Format your response as:
CLEANED_INGREDIENTS: [list of cleaned ingredients]
VALID_PREFERENCES: [list of dietary preferences]
ISSUES: [any issues found or "None"]
"""

INGREDIENT_FILTER_PROMPT = """
You are a dietary restriction specialist. Filter ingredients based on dietary preferences.

Ingredients: {ingredients}
Dietary restrictions: {dietary_preferences}

Please filter the ingredients and suggest alternatives if needed:
1. Remove ingredients that don't match dietary restrictions
2. Suggest suitable alternatives for removed ingredients
3. Ensure the remaining ingredients can make a complete dish

Format your response as:
FILTERED_INGREDIENTS: [list of suitable ingredients]
REMOVED_INGREDIENTS: [list of removed ingredients with reasons]
SUGGESTED_ALTERNATIVES: [alternatives for removed ingredients]
"""
RECIPE_GENERATION_PROMPT = """
You are a professional chef and recipe generator.

Using only the following ingredients: {ingredients}
You may add up to two additional **basic cooking essentials only** (such as oil, salt, pepper). Do **not** add other ingredients like vegetables, dairy, or proteins not listed. 
List these under 'Additional Ingredients Needed:' in your response.

Dietary preferences: {dietary_preferences}
Maximum cooking time: {max_time} minutes

Please generate a complete recipe including:
- A catchy recipe title
- A clear list of ingredients using ONLY the provided ingredients
- Step-by-step cooking instructions that fit within the max time

Format your response as:

TITLE: Recipe title here

INGREDIENTS:
- ingredient 1
- ingredient 2
- ...

INSTRUCTIONS:
1. Step one
2. Step two
...

ADDITIONAL INGREDIENTS NEEDED: [Only basic essentials like oil, salt, or pepper used apart from the provided ingredients]

Make sure the recipe is coherent, practical, and respects the dietary preferences.
"""


RECIPE_TIME_ESTIMATOR_PROMPT = """
You are a professional chef and cooking time expert.

Given the following recipe instructions:

{instructions}

Please estimate the total cooking and preparation time in minutes for these steps.

Answer in the following format:

Estimated total cooking time: <number> minutes
"""

HEALTH_TIPS_PROMPT = """
You are a nutrition expert. Provide health tips and nutritional insights for the recipe.

Recipe name: {recipe_name}
Ingredients: {ingredients}
Dietary preferences: {dietary_preferences}

Provide:
1. Key nutritional benefits
2. Health tips related to the ingredients
3. Suggestions for making it healthier
4. Any nutritional warnings if applicable

Format your response as:
NUTRITIONAL_BENEFITS: [key benefits]
HEALTH_TIPS: [practical health tips]
HEALTHIER_SUGGESTIONS: [ways to make it healthier]
WARNINGS: [any warnings or "None"]
"""

IMAGE_TO_TEXT_PROMPT = """
You are an image analysis expert specializing in food and ingredients.

Analyze the uploaded image and identify all visible ingredients or food items.

Please:
1. List all identifiable ingredients
2. Estimate quantities if possible
3. Note the condition/freshness of ingredients
4. Suggest what type of dish these ingredients might be suitable for

Format your response as:
IDENTIFIED_INGREDIENTS: [list of ingredients with estimated quantities]
CONDITION_NOTES: [freshness/condition observations]
DISH_SUGGESTIONS: [types of dishes these ingredients could make]
"""

ALTERNATE_RECIPE_PROMPT = """
You are a creative chef. Generate an alternate recipe using similar ingredients but with a different cooking style or cuisine.
Each time you are asked, create a new alternate recipe, even if the ingredients and preferences are the same. Be creative and do not repeat previous alternates.
Original recipe: {original_recipe}
Available ingredients: {ingredients}
Dietary preferences: {dietary_preferences}

Create a completely different recipe that:
1.  Uses ONLY the available ingredients listed above (do not add any new ingredients)
2. Has a different cooking method or cuisine style
3. Offers a unique flavor profile
4. Maintains the dietary restrictions

Format your response as:
ALTERNATE_RECIPE_NAME: [creative alternate name]
CUISINE_STYLE: [cuisine type or cooking method]
INGREDIENTS_NEEDED: [list with quantities]
INSTRUCTIONS: [numbered step-by-step instructions]
DIFFICULTY: [Easy/Medium/Hard]
SERVINGS: [number of servings]
FLAVOR_PROFILE: [description of taste and style differences]
"""