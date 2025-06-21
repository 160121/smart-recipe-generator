# 🍳 Smart Recipe Generator using Gemini + LangGraph

A modular, AI-powered recipe assistant that transforms your available ingredients and dietary preferences into complete, personalized recipes — with nutritional tips, cooking time estimates, and alternative versions — using Google Gemini API and LangGraph.

---

## 🚀 Features

- 🧠 Input validation and smart parsing
- 🥦 Ingredient filtering based on dietary preferences (Vegetarian, Vegan, Gluten-Free, etc.)
- 🍽️ AI-generated recipe (title, ingredients, instructions)
- ⏱️ Estimated total cooking/prep time
- 💡 Nutritional benefits and health tips
- 🔄 Alternative recipe generation
- 📝 Feedback logging for user improvements
- 📊 LangGraph-powered stateful recipe pipeline
- 🎨 Streamlit UI support

---

## 🧱 Tech Stack

- **LangGraph** – Agent-based graph orchestration
- **LangChain** – LLM interaction interface
- **Google Gemini API** – Generative LLM for reasoning
- **Streamlit** – Web interface (optional)
- **Python 3.10+**

---

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/160121/smart-recipe-generator.git
cd smart-recipe-generator
```
### 2. Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

```
### 3. Install dependencies

```bash
pip install -r requirements.txt
```
### 4. Configure .env
Create a .env file in the root and add:

```bash
GEMINI_API_KEY=your_gemini_api_key
```
## 🚀 Usage

### 🖥️ Run with Streamlit

To launch the interactive Smart Recipe Generator UI, use:

```bash
streamlit run ui/streamlit_app.py
```
## 🧠 Agents Overview

This system uses a modular, agent-based design orchestrated via LangGraph. Each agent has a specific responsibility in the recipe generation workflow:

### 🔍 InputValidatorAgent
- **Purpose**: Validates and cleans raw user inputs.
- **Tasks**:
  - Parses free-text ingredients.
  - Validates dietary preferences.
  - Identifies potential conflicts or missing data.

### 🚫 IngredientFilterAgent
- **Purpose**: Applies dietary restrictions to the ingredient list.
- **Tasks**:
  - Removes ingredients that violate dietary preferences.
  - Suggests alternatives for removed items (e.g., tofu for chicken).

### 🍳 RecipeGeneratorAgent
- **Purpose**: Generates a complete recipe.
- **Tasks**:
  - Uses filtered ingredients and preferences to create a recipe.
  - Returns the recipe title, ingredient list, and step-by-step instructions.

### ⏱️ RecipeTimeEstimatorAgent
- **Purpose**: Estimates total prep and cook time.
- **Tasks**:
  - Analyzes recipe instructions to estimate overall cooking time in minutes.

### 💡 HealthTipsAgent
- **Purpose**: Provides nutritional insights and wellness advice.
- **Tasks**:
  - Lists benefits of the recipe.
  - Offers tips for healthier preparation.
  - Highlights potential dietary warnings.

### 🔄 AlternateRecipeAgent
- **Purpose**: Generates a creative variant of the original recipe.
- **Tasks**:
  - Uses similar ingredients or style.
  - Adjusts cuisine or method while respecting preferences.

### 📝 FeedbackLoggerAgent
- **Purpose**: Logs feedback from the user interface.
- **Tasks**:
  - Tracks user ratings or reactions.
  - Can be used to improve future suggestions or analytics.

Each agent contributes to the shared `state` object, ensuring smooth handoffs and traceable outputs throughout the pipeline.

