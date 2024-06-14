import base64
import os

class Config:
    # General Configurations
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database Configurations
    SQLALCHEMY_DATABASE_URI = os.environ.get('PAY_GATEWAY_MOCK_DATABASE_URL') or 'sqlite:///app.db'
    WEBHOOK_URL = 'http://asapportal.local/m/r.php?sn=callbackIntegration&SYSID=PPCALL&SUBID=PPCALLBACK'
    SHOPPER_RESULT_URL = 'http://asapportal.local/m/web.php?SN=peachReturnShopper&params='
    ENCRYPTION_KEY = 'D1A8F3C7B2E5A4D6C9F1E7B3A2D4F5C8E6A1B9D7C3E5F8A4B2D1E6C7F3A9E1F2'  # Replace with your actual 32-byte key


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

    WEBHOOK_URL = 'http://asapportal.local/m/r.php?sn=callbackIntegration&SYSID=PPCALL&SUBID=PPCALLBACK'
    SHOPPER_RESULT_URL = 'http://asapportal.local/m/web.php?SN=peachReturnShopper&params='
    ENCRYPTION_KEY = 'D1A8F3C7B2E5A4D6C9F1E7B3A2D4F5C8E6A1B9D7C3E5F8A4B2D1E6C7F3A9E1F2'  # Replace with your actual 32-byte key

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_ECHO = False

    WEBHOOK_URL = 'http://asapportal.local/m/r.php?sn=callbackIntegration&SYSID=PPCALL&SUBID=PPCALLBACK'
    SHOPPER_RESULT_URL = 'http://asapportal.local/m/web.php?SN=peachReturnShopper&params='
    ENCRYPTION_KEY = 'D1A8F3C7B2E5A4D6C9F1E7B3A2D4F5C8E6A1B9D7C3E5F8A4B2D1E6C7F3A9E1F2'  # Replace with your actual 32-byte key

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PAY_GATEWAY_MOCK_DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_ECHO = False

    WEBHOOK_URL = 'http://asapportal.local/m/r.php?sn=callbackIntegration&SYSID=PPCALL&SUBID=PPCALLBACK'
    SHOPPER_RESULT_URL = 'http://asapportal.local/m/web.php?SN=peachReturnShopper&params='
    ENCRYPTION_KEY = 'D1A8F3C7B2E5A4D6C9F1E7B3A2D4F5C8E6A1B9D7C3E5F8A4B2D1E6C7F3A9E1F2'  # Replace with your actual 32-byte key

# Dictionary to map the configuration names to their corresponding classes
config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)
