import os
from flaskr import hvps_overview
from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    #UPLOAD_FOLDER = './uploads'
    #app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config.from_mapping(SECRET_KEY="caendev")

    # Limit the maximum size of a file upload, else raise RequestEntityTooLarge exception
    app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # apply the blueprints to the app
    #app.register_blueprint(auth.bp)
    app.register_blueprint(hvps_overview.bp)
    #app.register_blueprint(asset.bp)
    #app.register_blueprint(scan.bp)

    app.add_url_rule("/", endpoint="index")

    return app
