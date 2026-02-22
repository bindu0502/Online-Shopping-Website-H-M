"""
Intelligent Color Generator

Generates colors and color descriptions for products based on:
1. Product name analysis
2. Product category/group
3. Fashion industry standards
4. Fallback generation for incomplete data

Ensures every product has color and color description information.
"""

import re
import logging
from typing import Tuple, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ColorInfo:
    """Color information for a product."""
    color: str
    color_description: str
    confidence: float  # 0.0 to 1.0, higher means more confident

class ColorGenerator:
    """Intelligent color generator for fashion products."""
    
    # Color keywords that might appear in product names
    COLOR_KEYWORDS = {
        # Basic colors
        'black': ('black', 'Classic black color with timeless elegance'),
        'white': ('white', 'Pure white color for a clean, fresh look'),
        'gray': ('gray', 'Neutral gray tone that pairs well with everything'),
        'grey': ('gray', 'Neutral gray tone that pairs well with everything'),
        
        # Red family
        'red': ('red', 'Vibrant red color that makes a bold statement'),
        'pink': ('pink', 'Soft pink hue with feminine charm'),
        'rose': ('pink', 'Delicate rose pink with romantic appeal'),
        'coral': ('coral', 'Warm coral tone with tropical vibes'),
        'burgundy': ('burgundy', 'Rich burgundy shade with sophisticated depth'),
        'maroon': ('maroon', 'Deep maroon color with classic elegance'),
        'crimson': ('red', 'Intense crimson red with dramatic flair'),
        
        # Blue family
        'blue': ('blue', 'Classic blue color that never goes out of style'),
        'navy': ('navy', 'Deep navy blue perfect for professional wear'),
        'royal': ('blue', 'Royal blue with regal sophistication'),
        'sky': ('light blue', 'Light sky blue with airy freshness'),
        'teal': ('teal', 'Sophisticated teal with blue-green harmony'),
        'turquoise': ('teal', 'Vibrant turquoise with oceanic beauty'),
        'denim': ('blue', 'Classic denim blue with casual appeal'),
        
        # Green family
        'green': ('green', 'Fresh green color inspired by nature'),
        'olive': ('olive', 'Earthy olive green with military chic'),
        'mint': ('green', 'Cool mint green with refreshing appeal'),
        'emerald': ('green', 'Luxurious emerald green with jewel-like richness'),
        'forest': ('dark green', 'Deep forest green with natural elegance'),
        'lime': ('lime', 'Bright lime green with energetic vibes'),
        
        # Yellow family
        'yellow': ('yellow', 'Bright yellow color that radiates sunshine'),
        'gold': ('gold', 'Luxurious gold tone with metallic glamour'),
        'cream': ('cream', 'Soft cream color with warm undertones'),
        'beige': ('beige', 'Neutral beige tone with versatile appeal'),
        'tan': ('tan', 'Warm tan shade with earthy sophistication'),
        'camel': ('tan', 'Rich camel tone with desert-inspired warmth'),
        'mustard': ('yellow', 'Bold mustard yellow with vintage charm'),
        
        # Orange family
        'orange': ('orange', 'Vibrant orange color with energetic warmth'),
        'peach': ('peach', 'Soft peach tone with gentle femininity'),
        'apricot': ('peach', 'Delicate apricot shade with subtle sweetness'),
        'rust': ('orange', 'Earthy rust orange with autumn appeal'),
        
        # Purple family
        'purple': ('purple', 'Rich purple color with royal elegance'),
        'violet': ('violet', 'Delicate violet shade with floral beauty'),
        'lavender': ('lavender', 'Soft lavender with calming serenity'),
        'plum': ('purple', 'Deep plum color with sophisticated richness'),
        'mauve': ('purple', 'Muted mauve with vintage sophistication'),
        
        # Brown family
        'brown': ('brown', 'Warm brown color with earthy appeal'),
        'chocolate': ('brown', 'Rich chocolate brown with luxurious depth'),
        'coffee': ('brown', 'Deep coffee brown with aromatic warmth'),
        'khaki': ('khaki', 'Practical khaki with military-inspired style'),
        'taupe': ('tan', 'Sophisticated taupe with neutral elegance'),
        
        # Metallic
        'silver': ('silver', 'Sleek silver with modern metallic shine'),
        'bronze': ('bronze', 'Warm bronze with antique metallic appeal'),
        'copper': ('bronze', 'Rich copper tone with artisanal charm'),
        
        # Patterns and special
        'floral': ('multicolor', 'Delicate floral pattern with feminine charm'),
        'striped': ('multicolor', 'Classic striped pattern with timeless appeal'),
        'leopard': ('multicolor', 'Bold leopard print with wild sophistication'),
        'zebra': ('multicolor', 'Striking zebra pattern with graphic impact'),
        'polka': ('multicolor', 'Playful polka dot pattern with retro charm'),
    }
    
    # Category-based color defaults
    CATEGORY_DEFAULTS = {
        # Upper body
        'garment upper body': ('white', 'Classic white perfect for layering and versatile styling'),
        'jersey basic': ('white', 'Soft jersey fabric in versatile white'),
        'blouse': ('white', 'Elegant white blouse for professional and casual wear'),
        'shirt': ('white', 'Crisp white shirt with timeless appeal'),
        'top': ('white', 'Versatile white top that pairs with everything'),
        't-shirt': ('white', 'Classic white t-shirt for everyday comfort'),
        'tank': ('white', 'Simple white tank top for layering'),
        'sweater': ('gray', 'Cozy gray sweater with neutral sophistication'),
        'cardigan': ('gray', 'Versatile gray cardigan for layering'),
        'hoodie': ('gray', 'Comfortable gray hoodie for casual wear'),
        
        # Lower body
        'garment lower body': ('blue', 'Classic blue denim perfect for everyday wear'),
        'jeans': ('blue', 'Traditional denim blue with authentic wash'),
        'pants': ('black', 'Versatile black pants suitable for any occasion'),
        'trousers': ('black', 'Professional black trousers with tailored fit'),
        'shorts': ('blue', 'Casual blue shorts perfect for warm weather'),
        'skirt': ('black', 'Classic black skirt with timeless elegance'),
        'leggings': ('black', 'Sleek black leggings for comfort and style'),
        
        # Dresses
        'dress': ('black', 'Elegant black dress suitable for any occasion'),
        'gown': ('black', 'Sophisticated black gown with formal elegance'),
        'sundress': ('white', 'Fresh white sundress perfect for summer'),
        
        # Underwear & Lingerie
        'underwear': ('white', 'Classic white underwear with comfortable fit'),
        'bra': ('white', 'Essential white bra with supportive design'),
        'lingerie': ('black', 'Elegant black lingerie with sophisticated appeal'),
        'panties': ('white', 'Comfortable white panties with seamless design'),
        
        # Socks & Tights
        'socks & tights': ('black', 'Classic black hosiery with versatile appeal'),
        'stockings': ('black', 'Elegant black stockings with sheer finish'),
        'tights': ('black', 'Smooth black tights with comfortable stretch'),
        'socks': ('white', 'Essential white socks for everyday comfort'),
        
        # Accessories
        'accessories': ('black', 'Versatile black accessory that complements any outfit'),
        'bag': ('black', 'Classic black bag with timeless style'),
        'belt': ('black', 'Essential black belt with versatile appeal'),
        'scarf': ('multicolor', 'Stylish scarf with versatile color palette'),
        
        # Shoes
        'shoes': ('black', 'Classic black shoes suitable for any occasion'),
        'sneakers': ('white', 'Clean white sneakers with sporty appeal'),
        'boots': ('black', 'Versatile black boots with durable style'),
        'heels': ('black', 'Elegant black heels perfect for formal occasions'),
        'sandals': ('brown', 'Comfortable brown sandals with natural appeal'),
        
        # Outerwear
        'jacket': ('black', 'Versatile black jacket for layering'),
        'coat': ('black', 'Classic black coat with sophisticated warmth'),
        'blazer': ('black', 'Professional black blazer with tailored fit'),
        'vest': ('gray', 'Stylish gray vest for layering'),
    }
    
    def __init__(self):
        """Initialize the color generator."""
        pass
    
    def extract_color_from_name(self, product_name: str) -> Optional[ColorInfo]:
        """
        Extract color information from product name.
        
        Args:
            product_name: Product name to analyze
            
        Returns:
            ColorInfo if color found, None otherwise
        """
        if not product_name:
            return None
        
        name_lower = product_name.lower()
        
        # Look for color keywords in the product name
        for keyword, (color, description) in self.COLOR_KEYWORDS.items():
            if keyword in name_lower:
                # Higher confidence if the color word is at the beginning or end
                if name_lower.startswith(keyword) or name_lower.endswith(keyword):
                    confidence = 0.9
                else:
                    confidence = 0.7
                
                return ColorInfo(
                    color=color,
                    color_description=description,
                    confidence=confidence
                )
        
        return None
    
    def generate_from_category(self, product_group: str, department_name: str = None) -> ColorInfo:
        """
        Generate color based on product category.
        
        Args:
            product_group: Product group/category
            department_name: Department name (optional)
            
        Returns:
            ColorInfo with generated color
        """
        if not product_group:
            product_group = 'fashion item'
        
        group_lower = product_group.lower()
        
        # Try exact match first
        if group_lower in self.CATEGORY_DEFAULTS:
            color, description = self.CATEGORY_DEFAULTS[group_lower]
            return ColorInfo(
                color=color,
                color_description=description,
                confidence=0.6
            )
        
        # Try partial matches
        for category, (color, description) in self.CATEGORY_DEFAULTS.items():
            if any(word in group_lower for word in category.split()):
                return ColorInfo(
                    color=color,
                    color_description=description,
                    confidence=0.5
                )
        
        # Department-based fallback
        if department_name:
            dept_lower = department_name.lower()
            if 'women' in dept_lower or 'ladies' in dept_lower:
                return ColorInfo(
                    color='black',
                    color_description='Versatile black color perfect for women\'s fashion',
                    confidence=0.4
                )
            elif 'men' in dept_lower:
                return ColorInfo(
                    color='navy',
                    color_description='Classic navy blue suitable for men\'s wear',
                    confidence=0.4
                )
        
        # Ultimate fallback
        return ColorInfo(
            color='black',
            color_description='Classic black color with timeless versatility',
            confidence=0.3
        )
    
    def generate_color_info(self, product_name: str, product_group: str, 
                          department_name: str = None, existing_colors: str = None) -> ColorInfo:
        """
        Generate complete color information for a product.
        
        Args:
            product_name: Product name
            product_group: Product category/group
            department_name: Department name (optional)
            existing_colors: Existing color data (optional)
            
        Returns:
            ColorInfo with color and description
        """
        # If we already have colors, use the first one
        if existing_colors:
            colors_list = [c.strip() for c in existing_colors.split(',') if c.strip()]
            if colors_list:
                primary_color = colors_list[0]
                
                # Generate description for existing color
                if len(colors_list) == 1:
                    description = self._get_single_color_description(primary_color)
                elif len(colors_list) == 2:
                    description = f"{colors_list[0].title()} and {colors_list[1]} combination"
                else:
                    description = f"Primarily {primary_color} with {colors_list[1]} and other accent colors"
                
                return ColorInfo(
                    color=primary_color,
                    color_description=description,
                    confidence=1.0
                )
        
        # Try to extract from product name
        name_color = self.extract_color_from_name(product_name)
        if name_color and name_color.confidence > 0.6:
            return name_color
        
        # Generate from category
        category_color = self.generate_from_category(product_group, department_name)
        
        # Use the higher confidence option
        if name_color and name_color.confidence > category_color.confidence:
            return name_color
        else:
            return category_color
    
    def _get_single_color_description(self, color: str) -> str:
        """Get description for a single color."""
        color_lower = color.lower()
        
        # Look up in our color keywords
        for keyword, (_, description) in self.COLOR_KEYWORDS.items():
            if keyword == color_lower:
                return description
        
        # Fallback descriptions
        descriptions = {
            'black': 'Classic black color with timeless elegance',
            'white': 'Pure white color for a clean, fresh look',
            'gray': 'Neutral gray tone that pairs well with everything',
            'red': 'Vibrant red color that makes a bold statement',
            'blue': 'Classic blue color that never goes out of style',
            'green': 'Fresh green color inspired by nature',
            'yellow': 'Bright yellow color that radiates sunshine',
            'orange': 'Vibrant orange color with energetic warmth',
            'purple': 'Rich purple color with royal elegance',
            'brown': 'Warm brown color with earthy appeal',
            'pink': 'Soft pink hue with feminine charm',
            'navy': 'Deep navy blue perfect for professional wear',
            'beige': 'Neutral beige tone with versatile appeal',
            'multicolor': 'Stylish multicolor design with versatile appeal',
        }
        
        return descriptions.get(color_lower, f'{color.title()} color with stylish appeal')

# Global instance
color_generator = ColorGenerator()