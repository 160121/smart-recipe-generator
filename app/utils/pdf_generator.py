"""
PDF Generator utility for exporting recipes.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from typing import Dict, Any


class RecipePDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the PDF."""
        self.styles.add(ParagraphStyle(
            name='RecipeTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkgreen,
            borderWidth=1,
            borderColor=colors.darkgreen,
            borderPadding=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='IngredientItem',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=6
        ))
    
    def generate_recipe_pdf(self, recipe_data: Dict[str, Any]) -> BytesIO:
        """Generate a PDF from recipe data (simplified, only meaningful info)."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)

        story = []

        # Title
        title = recipe_data.get('recipe_title', 'Recipe')
        story.append(Paragraph(title, self.styles['RecipeTitle']))
        story.append(Spacer(1, 20))

        # Ingredients section
        story.append(Paragraph("Ingredients", self.styles['SectionHeader']))
        ingredients = recipe_data.get('recipe_ingredients', recipe_data.get('filtered_ingredients', []))
        for ingredient in ingredients:
            story.append(Paragraph(f"• {ingredient}", self.styles['IngredientItem']))
        story.append(Spacer(1, 20))

        # Instructions section
        story.append(Paragraph("Instructions", self.styles['SectionHeader']))
        instructions = recipe_data.get('recipe_instructions', [])
        for i, instruction in enumerate(instructions, 1):
            story.append(Paragraph(f"{i}. {instruction}", self.styles['Normal']))
            story.append(Spacer(1, 10))

        # Health tips section
        if recipe_data.get('health_tips'):
            story.append(Spacer(1, 20))
            story.append(Paragraph("Health Tips", self.styles['SectionHeader']))
            story.append(Paragraph(recipe_data['health_tips'], self.styles['Normal']))

        # Nutritional benefits
        if recipe_data.get('nutritional_benefits'):
            story.append(Spacer(1, 20))
            story.append(Paragraph("Nutritional Benefits", self.styles['SectionHeader']))
            story.append(Paragraph(recipe_data['nutritional_benefits'], self.styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer
    def generate_shopping_list_pdf(self, recipe_data: Dict[str, Any]) -> BytesIO:
        """Generate a shopping list PDF."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
        
        story = []
        
        # Title
        recipe_name = recipe_data.get('recipe_name', 'Recipe')
        story.append(Paragraph(f"Shopping List for {recipe_name}", self.styles['RecipeTitle']))
        story.append(Spacer(1, 20))
        
        # Shopping sections
        sections = [
            ('shopping_produce', 'Produce Section'),
            ('shopping_meat', 'Meat & Seafood'),
            ('shopping_dairy', 'Dairy & Eggs'),
            ('shopping_pantry', 'Pantry Staples'),
            ('shopping_frozen', 'Frozen Section')
        ]
        
        for key, title in sections:
            items = recipe_data.get(key, [])
            if items:
                story.append(Paragraph(title, self.styles['SectionHeader']))
                for item in items:
                    story.append(Paragraph(f"☐ {item}", self.styles['IngredientItem']))
                story.append(Spacer(1, 15))
        
        # Estimated cost
        if recipe_data.get('shopping_cost'):
            story.append(Paragraph("Estimated Cost", self.styles['SectionHeader']))
            story.append(Paragraph(recipe_data['shopping_cost'], self.styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
