import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration - Using postgres superuser
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'food_nutrition_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

# App Configuration
APP_TITLE = "Global Food & Nutrition Explorer"
APP_ICON = "🍎"
LAYOUT = "wide"

# Color scheme for visualizations
COLORS = {
    'primary': '#FF6B6B',
    'secondary': '#4ECDC4',
    'success': '#95E1D3',
    'warning': '#F38181',
    'info': '#3D5A80'
}

# Nutrition grade colors
GRADE_COLORS = {
    'a': '#00C853',
    'b': '#64DD17',
    'c': '#FFD600',
    'd': '#FF6D00',
    'e': '#DD2C00'
}