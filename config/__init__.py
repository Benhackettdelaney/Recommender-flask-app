import os
from config.config import DevelopmentConfig, ProductionConfig, TestingConfig

config_options = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}

# Set the default config based on the environment variable
config_name = os.getenv("FLASK_ENV", "development")
app_config = config_options[config_name]
