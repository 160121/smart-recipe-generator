"""
Streamlit UI for the Smart Recipe Generator with Bonus Features
"""
# ui/streamlit_app.py
import streamlit as st
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.pipeline.recipe_graph import RecipeGraph
from app.utils.pdf_generator import RecipePDFGenerator 
from app.agents.image_to_text import ImageToTextAgent
load_dotenv()

st.set_page_config(
    page_title="Smart Recipe Generator",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .recipe-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF6B6B;
        margin: 1rem 0;
    }
    .ingredient-tag {
        background-color: #e3f2fd;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.9rem;
    }
    .time-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    .feedback-buttons {
        display: flex;
        gap: 10px;
        justify-content: center;
        margin: 20px 0;
    }
    .shopping-section {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'recipe_generated' not in st.session_state:
        st.session_state.recipe_generated = False
    if 'current_recipe' not in st.session_state:
        st.session_state.current_recipe = None
    if 'recipe_graph' not in st.session_state:
        try:
            st.session_state.recipe_graph = RecipeGraph()
        except ValueError as e:
            st.error(f"Error initializing recipe generator: {e}")
            st.error("Please make sure your Azure OpenAI credentials are set in the environment variables.")
            st.stop()

def main():
    """Main Streamlit application."""
    initialize_session_state()

    # Header
    st.markdown('<h1 class="main-header">🍳 Smart Recipe Generator</h1>', unsafe_allow_html=True)
    st.markdown("Transform your ingredients into delicious recipes with AI-powered suggestions!")

    # Sidebar for inputs
    with st.sidebar:
        st.header("Recipe Preferences")
        # In your sidebar, before the input_method logic:
        if "ingredients_text" not in st.session_state:
            st.session_state.ingredients_text = ""

        # Ingredients input
        st.subheader("🥕 Ingredients")
        input_method = st.radio(
            "How would you like to provide your ingredients?",
            ("Type ingredients", "Upload image"),
            horizontal=True
        )

        if input_method == "Type ingredients":
            st.session_state.ingredients_text = st.text_area(
                "Enter your available ingredients (comma-separated):",
                value=st.session_state.ingredients_text,
                placeholder="e.g., chicken breast, broccoli, rice, garlic, olive oil",
                height=120,
                help="List all the ingredients you have available. Separate each ingredient with a comma."
            )
        elif input_method == "Upload image":
            uploaded_image = st.file_uploader(
                "Upload an image of your ingredients (jpg, png):",
                type=["jpg", "jpeg", "png"],
                key="image_input"
            )
            if uploaded_image is not None:
                st.image(uploaded_image, caption="Uploaded Ingredients Image", use_container_width=True)
                if st.button("Extract ingredients from image"):
                    with st.spinner("Extracting ingredients from image..."):
                        try:
                            agent = ImageToTextAgent()
                            image_ingredients = agent.extract_ingredients(uploaded_image.read())
                            st.success("Extraction complete!")
                            st.write("**Extracted Ingredients:**", image_ingredients)
                            # Set the extracted text in the text area for editing
                            st.session_state.ingredients_text = image_ingredients
                        except Exception as e:
                            st.error(f"Image extraction failed: {e}")

            # Always show the text area for editing after extraction
            st.session_state.ingredients_text = st.text_area(
                "Extracted ingredients (edit if needed):",
                value=st.session_state.ingredients_text,
                height=120,
                help="Edit the extracted ingredients if needed before generating the recipe."
            )

        # Dietary preferences
        st.subheader("🥗 Dietary Preferences")
        dietary_options = [
            "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", 
            "Eggetarian","Low-Carb", "High-Protein", "Mediterranean"
        ]
        selected_dietary = st.multiselect(
            "Select dietary restrictions:",
            dietary_options,
            help="Choose any dietary restrictions or preferences you want to follow"
        )

        # Time constraint
        st.subheader("⏰ Time Constraint")
        max_time = st.slider(
            "Maximum cooking time (minutes):",
            min_value=15,
            max_value=180,
            value=60,
            step=15,
            help="Set the maximum time you want to spend cooking"
        )

        # Generate button
        generate_button = st.button(
            "🚀 Generate Recipe",
            type="primary",
            use_container_width=True
        )

    # Main content area
    if generate_button:
        if not st.session_state.ingredients_text.strip():
            st.error("Please enter some ingredients to generate a recipe!")
        else:
            generate_recipe(st.session_state.ingredients_text, selected_dietary, max_time)

    # Display recipe if generated
    if st.session_state.recipe_generated and st.session_state.current_recipe:
        display_recipe(st.session_state.current_recipe)

        # Feedback section
        display_feedback_section()

def generate_recipe(ingredients_text, dietary_preferences, max_time):
    """Generate recipe using the LangGraph pipeline."""
    with st.spinner("🤖 AI is cooking up something delicious..."):
        try:
            recipe_result = st.session_state.recipe_graph.generate_recipe(
                ingredients=ingredients_text,
                dietary_preferences=dietary_preferences,
                max_time=max_time,
                uploaded_image=None
            )

            st.session_state.current_recipe = recipe_result
            st.session_state.recipe_generated = True

            st.success("🎉 Recipe generated successfully!")

        except Exception as e:
            st.error(f"Error generating recipe: {str(e)}")
            st.error("Please check your API credentials and try again.")

def display_recipe(recipe_data):
    """Display the generated recipe in a visually appealing two-column layout, with an option to generate an alternate recipe."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Recipe title and basic info
        st.markdown(f"## 🍽️ {recipe_data.get('recipe_title', 'Delicious Recipe')}")

        # Time badge
        st.markdown(
            f'<span class="time-badge">⏱️ {recipe_data.get("estimated_cook_time", "N/A")} min</span>',
            unsafe_allow_html=True
        )

        # Ingredients section
        st.markdown("### 🛒 Ingredients")
        ingredients = recipe_data.get('recipe_ingredients', [])
        if ingredients:
            for ingredient in ingredients:
                st.markdown(f"• {ingredient}")
        else:
            filtered_ingredients = recipe_data.get('filtered_ingredients', [])
            for ingredient in filtered_ingredients:
                st.markdown(f'<span class="ingredient-tag">{ingredient}</span>', unsafe_allow_html=True)

        # Instructions section
        st.markdown("### 👨‍🍳 Instructions")
        instructions = recipe_data.get('recipe_instructions', [])
        if instructions:
            for i, instruction in enumerate(instructions, 1):
                st.markdown(f"**{i}.** {instruction}")
        if st.button("📄 Export PDF", use_container_width=True):
            export_recipe_pdf()
        # --- Alternate Recipe Button ---
        st.markdown("---")
    
        if st.button("🔄 Generate Alternate Recipe"):
            with st.spinner("Generating alternate recipe..."):
                try:
                    # Generate alternate recipe and display
                    alternate_result = st.session_state.recipe_graph.alternate_agent.generate_alternate(recipe_data)
                    display_alternate_recipe(alternate_result)  # Display the alternate recipe
                except Exception as e:
                    st.error(f"Error generating alternate recipe: {e}")
        if st.button("🛒 Shopping List"):
            missing = recipe_data.get("missed_ingredients", [])

            st.markdown("#### 🛒 Shopping List (Additional Ingredients)")
            if missing:
                for item in missing:
                    st.markdown(f"- {item}")
            else:
                st.success("You have all the ingredients needed for this recipe!")

    with col2:
        # Health tips and nutritional info
        st.markdown("### 🌱 Health & Nutrition")

        # Nutritional benefits
        benefits = recipe_data.get('nutritional_benefits', '')
        if benefits:
            st.markdown("**Nutritional Benefits:**")
            st.info(benefits)

        # Health tips
        health_tips = recipe_data.get('health_tips', '')
        if health_tips:
            st.markdown("**Health Tips:**")
            st.success(health_tips)

        # Healthier suggestions
        healthier_suggestions = recipe_data.get('healthier_suggestions', '')
        if healthier_suggestions:
            st.markdown("**Make it Healthier:**")
            st.warning(healthier_suggestions)

        # Health warnings
        warnings = recipe_data.get('health_warnings', '')
        if warnings and warnings.lower() != 'none' and warnings.lower() != 'none.':
            st.markdown("**⚠️ Health Warnings:**")
            st.error(warnings)
def export_recipe_pdf():
    """Export recipe as PDF."""
    try:
        pdf_generator = RecipePDFGenerator()
        pdf_buffer = pdf_generator.generate_recipe_pdf(st.session_state.current_recipe)
        
        recipe_name = st.session_state.current_recipe.get('recipe_title', 'recipe')
        filename = f"{recipe_name.replace(' ', '_').lower()}_recipe.pdf"
        
        st.download_button(
            label="Download recipe pdf",
            data=pdf_buffer.getvalue(),
            file_name=filename,
            mime="application/pdf",
            key="auto_download_pdf",
            use_container_width=True,
            
        )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
def display_alternate_recipe(alternate_data):
    """Display the alternate recipe in a similar two-column layout."""
    st.markdown("---")
    st.markdown("### 🔄 Alternate Recipe")
    # st.write(alternate_data)
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"#### 🍽️ {alternate_data.get('alternate_recipe_name', 'Alternate Recipe')}")
        st.markdown(f"**Cuisine Style:** {alternate_data.get('alternate_cuisine_style', 'Fusion')}")
        st.markdown(f"**Flavor Profile:** {alternate_data.get('alternate_flavor_profile', '')}")

        # Alternate ingredients
        st.markdown("**Ingredients:**")
        alt_ingredients = alternate_data.get('alternate_ingredients', [])
        for ingredient in alt_ingredients:
            st.markdown(f"• {ingredient}")

        # Alternate instructions
        st.markdown("**Instructions:**")
        alt_instructions = alternate_data.get('alternate_instructions', [])
        for i, instruction in enumerate(alt_instructions, 1):
            st.markdown(f"**{i}.** {instruction}")

    with col2:
        # Display difficulty and servings
        st.markdown(f"**Difficulty:** {alternate_data.get('alternate_difficulty', 'Medium')}")
        st.markdown(f"**Servings:** {alternate_data.get('alternate_servings', 4)}")
def display_feedback_section():
    st.markdown("---")
    st.subheader("📝 Did you like this recipe?")

    feedback_col1, feedback_col2 = st.columns(2)

    with feedback_col1:
        if st.button("👍 Thumbs Up"):
            submit_feedback("thumbs_up")

    with feedback_col2:
        if st.button("👎 Thumbs Down"):
            submit_feedback("thumbs_down")

def submit_feedback(feedback_type):
    try:
        feedback_state = st.session_state.current_recipe.copy()
        feedback_state.update({
            "feedback_type": feedback_type
        })

        result_state = st.session_state.recipe_graph.feedback_logger.log_feedback(feedback_state)

        if result_state.get("feedback_log_success"):
            emoji = "👍" if feedback_type == "thumbs_up" else "👎"
            st.success(f"Thank you for your feedback! {emoji}")

            stats = st.session_state.recipe_graph.get_feedback_statistics()
            if stats.get('total_feedback', 0) > 0:
                st.info(f"📊 Total feedback: {stats['total_feedback']} | 👍 Satisfaction: {stats['satisfaction_rate']}%")
        else:
            st.error("⚠️ Feedback could not be logged.")
    except Exception as e:
        st.error(f"Error submitting feedback: {e}")

if __name__ == "__main__":
    main()
