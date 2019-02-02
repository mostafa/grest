# -*- coding: utf-8 -*-

import neomodel
from flask import Flask

import config
from users import UsersView


if __name__ == "__main__":
    app = Flask(__name__)

    neomodel.config.DATABASE_URL = config.DB_URL
    neomodel.config.AUTO_INSTALL_LABELS = True

    UsersView.register(app, route_base="/users", trailing_slash=False)

    app.run(debug=config.DEBUG,
            host=config.IP_ADDRESS,
            port=config.PORT,
            threaded=True)
