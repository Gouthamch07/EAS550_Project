import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'food_nutrition_db'),
    'user': os.getenv('DB_USER', 'analyst_user'),
    'password': os.getenv('DB_PASSWORD', 'analyst_pass')
}

# App Configuration
APP_TITLE = "Global Food & Nutrition Explorer"
APP_ICON = "🍎"
LAYOUT = "wide"

# Color scheme
COLORS = {
    'primary': '#FF6B6B',
    'secondary': '#4ECDC4',
    'success': '#95E1D3',
    'warning': '#F38181',
    'info': '#3D5A80'
}