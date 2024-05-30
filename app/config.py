import os

class Config:
    # General Configurations
    SECRET_KEY = os.environ.get('PAY_GATEWAY_MOCK_SECRET_KEY') or 'you-will-never-guess'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database Configurations
    SQLALCHEMY_DATABASE_URI = os.environ.get('PAY_GATEWAY_MOCK_DATABASE_URL') or 'sqlite:///app.db'
    WEBHOOK_URL = 'https://asapportal.local/m/r.php?sn=callbackIntegration&SYSID=PPCALL&SUBID=PPCALLBACK'
    SHOPPER_RESULT_URL = 'https://asapportal.local/m/web.php?SN=peachReturnShopper&params='


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

    WEBHOOK_URL = 'https://asapportal.local/m/r.php?sn=callbackIntegration&SYSID=PPCALL&SUBID=PPCALLBACK'
    SHOPPER_RESULT_URL = 'https://asapportal.local/m/web.php?SN=peachReturnShopper&params='

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_ECHO = False

    WEBHOOK_URL = 'https://asapportal.local/m/r.php?sn=callbackIntegration&SYSID=PPCALL&SUBID=PPCALLBACK'
    SHOPPER_RESULT_URL = 'https://asapportal.local/m/web.php?SN=peachReturnShopper&params='

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PAY_GATEWAY_MOCK_DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_ECHO = False

    WEBHOOK_URL = 'https://asapportal.local/m/r.php?sn=callbackIntegration&SYSID=PPCALL&SUBID=PPCALLBACK'
    SHOPPER_RESULT_URL = 'https://asapportal.local/m/web.php?SN=peachReturnShopper&params='

# Dictionary to map the configuration names to their corresponding classes
config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

# Default configuration
key = Config.SECRET_KEY
