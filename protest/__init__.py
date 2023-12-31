import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # can read config from toml file to possilby automate creation of db
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE="protest_organization_main", SECRET_ORGANIZER="org"
    )
    app.config.from_mapping(test_config)

    # if database had password it should be in instance directory
    # don't upload this to VCS
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    from . import api_auth
    from . import api_add
    from . import api_query

    db.init_app(app)
    app.register_blueprint(api_auth.bp)
    app.register_blueprint(api_add.bp)
    app.register_blueprint(api_query.bp)

    return app
