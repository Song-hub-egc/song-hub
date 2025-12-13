import os
from app import create_app

# Determine config based on environment
config_name = os.getenv('FLASK_ENV', 'production')
app = create_app(config_name=config_name)
