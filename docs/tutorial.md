# Tutorial

This quick tutorial will get you up and running with your first gREST project. Your project should include at most three files to have a working API for your first model. You project layout should be like this:

Note: By installing `pygrest` package, all the necessary dependencies would also be installed.

```
app/
    main.py         # Main gREST application
    models.py       # Database model of your first node (User)
    users_view.py   # User's endpoints is defined here
```

Your `main.py` file should setup a Flask application, configure database connection, enable logging and register a view:

```python
import os
import logging
import neomodel
from flask import Flask
from grest import global_config
from users_view import UsersView

def create_app():
    # create flask app
    app = Flask(__name__)

    # add a simple endpoint for testing purposes
    @app.route('/')
    def index():
        return "Hello World!"

    # configure connection to database
    neomodel.config.DATABASE_URL = global_config.DB_URL  # The bolt URL of your Neo4j instance
    neomodel.config.AUTO_INSTALL_LABELS = True
    neomodel.config.FORCE_TIMEZONE = True  # default False

    # attach logger to flask's app logger
    app.ext_logger = app.logger

    # register users' view
    UsersView.register(app, route_base="/users", trailing_slash=False)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="localhost", port=5000)
```

Next you should define your models with [Neomodel](http://neomodel.readthedocs.io/en/latest/getting_started.html#definition) syntax. Neomodel is easier to use than other ORMs and drivers. Your `models.py` file would be like this:

```python
from neomodel import (StructuredNode, UniqueIdProperty, StringProperty, BooleanProperty)
from grest import models

class User(StructuredNode, models.Node):
    user_id = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()
    email = StringProperty()
    is_enabled = BooleanProperty(default=False)
```

As you can see, we have imported `Node` from `grest.models`, so that we can use the `Node` mixin (which is used in JSON serialization of model data and automatic input validation). Also note that the `Person` class (model) is inheriting from two parents: `StructuredNode` and `Node`.

Now that you've defined your model, you should also define a simple view to contain your model (remember, we have registered this view in `main.py`). This is where the beauty of the gREST framework comes in:

```python
from grest import GRest
from models import User

class UsersView(GRest):
    __model__ = {"primary": User}
    __selection_field__ = {"primary": "user_id"}
```

The most important part of gREST is `__model__` and `__selection_field__` properties. They contain the logic to access your models and relations. As you see, our `primary` model is `User` and its primary key (so to say) is `user_id`, so the selection field of the primary model is `user_id`.

To run this app, simply execute it via the python command:

```bash
python main.py
```

A webserver would start on port 5000 in debug mode, so that you can test your endpoints. To test your new API, use a simple HTTP client (e.g. curl) to query the API:

```bash
curl -H "Content-Type: application/json" -X POST -d '{"first_name":"John","last_name":"Doe","email":"johndoe@example.com"}' http://localhost:5000/users
```

Result would be like this:
```bash
{"user_id":"937a8d5c1a3a4617bea9ff9b2428778a"}
```