"""
Color Detection Module

Analyzes product images to extract dominant colors and generate color descriptions.
Uses computer vision techniques to identify colors and map them to human-readable names.

Usage:
    from src.color_detection import detect_colors, get_color_name
    
    colors = detect_colors("path/to/image.jpg")
    print(colors)  # ['red', 'blue', 'white']
"""

import os
import logging
from typing import List, Tuple, Optional
import colorsys
from collections import Counter

try:
    from PIL import Image
    import numpy as np
    from sklearn.cluster import KMeans
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL and sklearn not available. Install with: pip install Pillow scikit-learn")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Color name mapping - RGB values to human-readable names
COLOR_NAMES = {
    # Basic colors
    'black': [(0, 0, 0), (40, 40, 40)],
    'white': [(240, 240, 240), (255, 255, 255)],
    'gray': [(80, 80, 80), (180, 180, 180)],
    'grey': [(80, 80, 80), (180, 180, 180)],
    
    # Red family
    'red': [(180, 0, 0), (255, 80, 80)],
    'pink': [(255, 150, 150), (255, 220, 220)],
    'maroon': [(100, 0, 0), (150, 50, 50)],
    'burgundy': [(120, 0, 30), (160, 40, 70)],
    
    # Blue family
    'blue': [(0, 0, 180), (80, 80, 255)],
    'navy': [(0, 0, 80), (50, 50, 120)],
    'light blue': [(150, 200, 255), (200, 230, 255)],
    'sky blue': [(100, 180, 255), (150, 220, 255)],
    'teal': [(0, 120, 120), (50, 180, 180)],
    
    # Green family
    'green': [(0, 180, 0), (80, 255, 80)],
    'dark green': [(0, 80, 0), (50, 120, 50)],
    'lime': [(150, 255, 0), (200, 255, 100)],
    'olive': [(100, 100, 0), (150, 150, 50)],
    
    # Yellow family
    'yellow': [(200, 200, 0), (255, 255, 100)],
    'gold': [(200, 150, 0), (255, 200, 50)],
    'cream': [(240, 230, 200), (255, 250, 230)],
    'beige': [(200, 180, 150), (240, 220, 190)],
    
    # Orange family
    'orange': [(255, 100, 0), (255, 180, 50)],
    'coral': [(255, 120, 80), (255, 180, 140)],
    'peach': [(255, 200, 150), (255, 230, 200)],
    
    # Purple family
    'purple': [(120, 0, 120), (200, 80, 200)],
    'violet': [(150, 0, 200), (200, 100, 255)],
    'lavender': [(200, 180, 255), (230, 220, 255)],
    
    # Brown family
    'brown': [(100, 50, 0), (150, 100, 50)],
    'tan': [(180, 140, 100), (220, 180, 140)],
    'khaki': [(180, 170, 120), (220, 210, 160)],
    
    # Metallic
    'silver': [(180, 180, 190), (220, 220, 230)],
    'bronze': [(150, 100, 50), (200, 150, 100)],
}


def rgb_distance(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """
    Calculate Euclidean distance between two RGB colors.
    
    Args:
        rgb1: First RGB color tuple
        rgb2: Second RGB color tuple
        
    Returns:
        Distance between colors
    """
    return sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5


def get_color_name(rgb: Tuple[int, int, int]) -> str:
    """
    Map RGB color to human-readable color name.
    
    Args:
        rgb: RGB color tuple (r, g, b)
        
    Returns:
        Human-readable color name
    """
    r, g, b = rgb
    
    # Check for grayscale first
    if abs(r - g) < 30 and abs(g - b) < 30 and abs(r - b) < 30:
        if r < 50:
            return 'black'
        elif r > 200:
            return 'white'
        else:
            return 'gray'
    
    # Find closest color name
    min_distance = float('inf')
    closest_color = 'unknown'
    
    for color_name, color_ranges in COLOR_NAMES.items():
        for color_range in color_ranges:
            if len(color_range) == 2:
                # Range format: [(min_r, min_g, min_b), (max_r, max_g, max_b)]
                min_rgb, max_rgb = color_range
                if (min_rgb[0] <= r <= max_rgb[0] and 
                    min_rgb[1] <= g <= max_rgb[1] and 
                    min_rgb[2] <= b <= max_rgb[2]):
                    return color_name
            else:
                # Single color format
                distance = rgb_distance(rgb, color_range)
                if distance < min_distance:
                    min_distance = distance
                    closest_color = color_name
    
    # If no exact match, use closest color if distance is reasonable
    if min_distance < 100:  # Threshold for acceptable color match
        return closest_color
    
    # Fallback to basic color detection
    if r > g and r > b:
        return 'red'
    elif g > r and g > b:
        return 'green'
    elif b > r and b > g:
        return 'blue'
    elif r > 150 and g > 150 and b < 100:
        return 'yellow'
    elif r > 150 and g < 100 and b > 150:
        return 'purple'
    elif r > 150 and g > 100 and b < 100:
        return 'orange'
    else:
        return 'multicolor'


def extract_dominant_colors(image_path: str, num_colors: int = 5) -> List[Tuple[int, int, int]]:
    """
    Extract dominant colors from an image using K-means clustering.
    
    Args:
        image_path: Path to the image file
        num_colors: Number of dominant colors to extract
        
    Returns:
        List of RGB color tuples
    """
    if not PIL_AVAILABLE:
        logger.warning("PIL not available, cannot extract colors")
        return []
    
    try:
        # Open and resize image for faster processing
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to reduce computation time
            img = img.resize((150, 150))
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Reshape to list of pixels
            pixels = img_array.reshape(-1, 3)
            
            # Remove very dark and very light pixels (likely shadows/highlights)
            filtered_pixels = []
            for pixel in pixels:
                brightness = sum(pixel) / 3
                if 20 < brightness < 235:  # Filter out very dark/light pixels
                    filtered_pixels.append(pixel)
            
            if len(filtered_pixels) < 10:
                # Fallback to all pixels if filtering removed too many
                filtered_pixels = pixels
            
            filtered_pixels = np.array(filtered_pixels)
            
            # Use K-means to find dominant colors
            kmeans = KMeans(n_clusters=min(num_colors, len(filtered_pixels)), random_state=42, n_init=10)
            kmeans.fit(filtered_pixels)
            
            # Get cluster centers (dominant colors)
            colors = kmeans.cluster_centers_.astype(int)
            
            # Get cluster sizes to sort by dominance
            labels = kmeans.labels_
            label_counts = Counter(labels)
            
            # Sort colors by frequency
            sorted_colors = []
            for i in range(len(colors)):
                count = label_counts[i]
                sorted_colors.append((count, tuple(colors[i])))
            
            sorted_colors.sort(reverse=True, key=lambda x: x[0])
            
            # Return just the RGB tuples
            return [color for count, color in sorted_colors]
            
    except Exception as e:
        logger.error(f"Error extracting colors from {image_path}: {e}")
        return []


def detect_colors(image_path: str, max_colors: int = 3) -> List[str]:
    """
    Detect and return human-readable color names from an image.
    
    Args:
        image_path: Path to the image file
        max_colors: Maximum number of colors to return
        
    Returns:
        List of color names (e.g., ['red', 'blue', 'white'])
    """
    if not os.path.exists(image_path):
        logger.warning(f"Image not found: {image_path}")
        return []
    
    # Extract dominant colors
    rgb_colors = extract_dominant_colors(image_path, num_colors=max_colors + 2)
    
    if not rgb_colors:
        return []
    
    # Convert to color names
    color_names = []
    seen_colors = set()
    
    for rgb in rgb_colors:
        color_name = get_color_name(rgb)
        
        # Avoid duplicates and unknown colors
        if color_name not in seen_colors and color_name != 'unknown':
            color_names.append(color_name)
            seen_colors.add(color_name)
            
            if len(color_names) >= max_colors:
                break
    
    return color_names


def generate_color_description(colors: List[str], primary_color: str = None) -> str:
    """
    Generate a natural language description of product colors.
    
    Args:
        colors: List of detected color names
        primary_color: Primary/dominant color (optional)
        
    Returns:
        Natural language color description
    """
    if not colors:
        return ""
    
    # Remove duplicates while preserving order
    unique_colors = []
    seen = set()
    for color in colors:
        if color not in seen:
            unique_colors.append(color)
            seen.add(color)
    
    colors = unique_colors
    
    if len(colors) == 1:
        color = colors[0]
        # Single color descriptions
        descriptions = {
            'black': 'Classic black color',
            'white': 'Pure white color',
            'gray': 'Neutral gray tone',
            'grey': 'Neutral grey tone',
            'red': 'Vibrant red color',
            'pink': 'Soft pink hue',
            'maroon': 'Deep maroon shade',
            'burgundy': 'Rich burgundy tone',
            'blue': 'Classic blue color',
            'navy': 'Deep navy blue',
            'light blue': 'Light blue shade',
            'sky blue': 'Sky blue tone',
            'teal': 'Teal blue-green',
            'green': 'Fresh green color',
            'dark green': 'Deep green shade',
            'lime': 'Bright lime green',
            'olive': 'Olive green tone',
            'yellow': 'Bright yellow color',
            'gold': 'Golden yellow shade',
            'cream': 'Creamy off-white',
            'beige': 'Neutral beige tone',
            'orange': 'Vibrant orange color',
            'coral': 'Coral orange-pink',
            'peach': 'Soft peach tone',
            'purple': 'Rich purple color',
            'violet': 'Deep violet shade',
            'lavender': 'Soft lavender purple',
            'brown': 'Warm brown color',
            'tan': 'Light tan brown',
            'khaki': 'Khaki brown tone',
            'silver': 'Metallic silver',
            'bronze': 'Bronze metallic tone'
        }
        return descriptions.get(color, f'{color.title()} color')
    
    elif len(colors) == 2:
        # Two color combinations
        color1, color2 = colors[0], colors[1]
        
        # Special combinations
        combinations = {
            ('black', 'white'): 'Classic black and white combination',
            ('white', 'black'): 'Classic white and black combination',
            ('red', 'white'): 'Bold red and white design',
            ('blue', 'white'): 'Fresh blue and white combination',
            ('navy', 'white'): 'Elegant navy and white styling',
            ('black', 'gray'): 'Sophisticated black and gray tones',
            ('red', 'black'): 'Striking red and black combination',
            ('blue', 'navy'): 'Tonal blue and navy shades',
            ('brown', 'tan'): 'Warm brown and tan tones',
            ('green', 'white'): 'Natural green and white combination'
        }
        
        combo_key = (color1, color2)
        if combo_key in combinations:
            return combinations[combo_key]
        
        # Generic two-color description
        return f'{color1.title()} and {color2} combination'
    
    else:
        # Multiple colors (3+)
        if primary_color and primary_color in colors:
            other_colors = [c for c in colors if c != primary_color]
            if len(other_colors) == 1:
                return f'Primarily {primary_color} with {other_colors[0]} accents'
            elif len(other_colors) == 2:
                return f'Primarily {primary_color} with {other_colors[0]} and {other_colors[1]} accents'
            else:
                return f'Primarily {primary_color} with multicolor accents'
        else:
            # No primary color specified
            if len(colors) == 3:
                return f'{colors[0].title()}, {colors[1]}, and {colors[2]} multicolor design'
            else:
                return f'Multicolor design featuring {colors[0]}, {colors[1]}, and other colors'


def analyze_product_colors(image_directory: str, article_id: str) -> dict:
    """
    Analyze colors for a specific product by article ID.
    
    Args:
        image_directory: Base directory containing product images
        article_id: Product article ID
        
    Returns:
        Dictionary with 'colors', 'primary_color', and 'description' keys
    """
    # Try different image path formats
    possible_paths = [
        os.path.join(image_directory, f"{article_id}.jpg"),
        os.path.join(image_directory, article_id[:3], f"{article_id}.jpg"),
        os.path.join(image_directory, "images_128_128", article_id[:3], f"{article_id}.jpg"),
    ]
    
    for image_path in possible_paths:
        if os.path.exists(image_path):
            logger.debug(f"Analyzing colors for {article_id}: {image_path}")
            colors = detect_colors(image_path, max_colors=3)
            if colors:
                primary_color = colors[0] if colors else None
                description = generate_color_description(colors, primary_color)
                return {
                    'colors': colors,
                    'primary_color': primary_color,
                    'description': description
                }
    
    logger.warning(f"No image found for article {article_id}")
    return {
        'colors': [],
        'primary_color': None,
        'description': ""
    }


def batch_analyze_colors(image_directory: str, article_ids: List[str], max_workers: int = 4) -> dict:
    """
    Analyze colors for multiple products in batch.
    
    Args:
        image_directory: Base directory containing product images
        article_ids: List of article IDs to analyze
        max_workers: Number of parallel workers
        
    Returns:
        Dictionary mapping article_id to color analysis results
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = {}
    
    def analyze_single(article_id):
        color_data = analyze_product_colors(image_directory, article_id)
        return article_id, color_data
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_article = {
            executor.submit(analyze_single, article_id): article_id 
            for article_id in article_ids
        }
        
        # Collect results
        for future in as_completed(future_to_article):
            try:
                article_id, color_data = future.result()
                results[article_id] = color_data
                if len(results) % 100 == 0:
                    logger.info(f"Processed {len(results)}/{len(article_ids)} products")
            except Exception as e:
                article_id = future_to_article[future]
                logger.error(f"Error processing {article_id}: {e}")
                results[article_id] = {
                    'colors': [],
                    'primary_color': None,
                    'description': ""
                }
    
    return results


# Test function
if __name__ == "__main__":
    """Test color detection functionality."""
    
    print("=" * 60)
    print("COLOR DETECTION TEST")
    print("=" * 60)
    
    # Test color name mapping
    test_colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 255), # White
        (0, 0, 0),      # Black
        (128, 128, 128), # Gray
        (255, 192, 203), # Pink
        (255, 165, 0),  # Orange
    ]
    
    print("\nColor name mapping test:")
    for rgb in test_colors:
        name = get_color_name(rgb)
        print(f"  RGB{rgb} -> {name}")
    
    # Test with sample image if available
    sample_image_paths = [
        "Project149/datasets/images_128_128/010/0108775015.jpg",
        "datasets/images_128_128/010/0108775015.jpg",
        "frontend/public/no-image.png"
    ]
    
    for image_path in sample_image_paths:
        if os.path.exists(image_path):
            print(f"\nTesting with image: {image_path}")
            colors = detect_colors(image_path)
            print(f"  Detected colors: {colors}")
            break
    else:
        print("\nNo sample images found for testing")
    
    print("\n" + "=" * 60)
    print("✓ COLOR DETECTION TEST COMPLETE")
    print("=" * 60)