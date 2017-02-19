import os
from flask import Flask
from flask_bootstrap import Bootstrap


app = Flask(__name__)

# export FLASK_CONFIG_FILE=default.cfg for default settings (no email)
app.config.from_envvar('FLASK_CONFIG_FILE')

bootstrap = Bootstrap(app)

# Register blueprints
from app.auth import auth
app.register_blueprint(auth, url_prefix='/')
from app.main import main
app.register_blueprint(main, url_prefix='/')

from app.main.views import *
from app.auth.views import *
from app.main.errors import *