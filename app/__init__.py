"""Initialize Flask app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ddtrace import patch_all
import configparser, sys
from flask_login import LoginManager
from logging.config import fileConfig

config = configparser.ConfigParser()
config.read("app/VideoWebConfig.ini")

if len(sys.argv) > 1 and sys.argv[1] == "PROD":
    app_url = config['PROD'].get('url', "192.168.0.30")
    app_port = config['PROD'].get('port', '5000')
else:
    app_url = config['LOCAL'].get('url', "127.0.0.1")
    app_port = config['LOCAL'].get('port', '5000')

db_config = config['MYSQL_DB']
db_user = db_config.get('user', 'root')

if len(sys.argv) > 1 and sys.argv[1] == "PROD":
    db_pwd = db_config.get('pwd', 'root')
else:
    db_pwd = 'root'

db_url = db_config.get('url', '127.0.0.1')
db_port = db_config.get('port', '3306')
db_database = db_config.get('database', 'MovieDevo')

db = SQLAlchemy()
patch_all()
app = Flask(__name__)
fileConfig('app/VideoWebConfig.ini')
login = LoginManager(app)


def create_app():
    """Construct the core application."""
    # app = Flask(__name__)
    app.config[
        "SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://" + db_user + ":" + db_pwd + "@" + db_url + ":" + db_port + "/" + db_database
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config['SECRET_KEY'] = 'DontTellAnyone'

    db.init_app(app)
    login.login_view = 'login'

    with app.app_context():
        from . import routes  # Import routes

        from app.src.user.user import user_bp
        app.register_blueprint(user_bp)
        db.create_all()  # Create database tables for our data models

        return app
