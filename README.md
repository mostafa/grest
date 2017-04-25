# gREST

Build REST APIs with Neo4j and Flask, as quickly as possible!

[![PyPI version](https://badge.fury.io/py/pygrest.svg)](https://badge.fury.io/py/pygrest)
[![GitHub license](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://raw.githubusercontent.com/mostafa/grest/master/LICENSE)
[![Travis](https://img.shields.io/travis/rust-lang/rust.svg)](https://github.com/mostafa/grest)
[![Coveralls](https://img.shields.io/coveralls/jekyll/jekyll.svg)](https://github.com/mostafa/grest)
[![Join the chat at https://gitter.im/pygrest/Lobby](https://badges.gitter.im/pygrest/Lobby.svg)](https://gitter.im/pygrest/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

gREST (Graph-based REST API Framework) is a RESTful API development framework on top of Python, Flask, Neo4j and Neomodel. Its primary purpose is to ease development of RESTful APIs with little effort and miminum amount of code.

## Installation
To install gREST, you can use setuptools (install from source) or use a python package manager (e.g. pip or easy_install).

+ To install from `source code`, clone the repository (you should have git installed) and then run setup.py:
```bash
$ git clone https://github.com/mostafa/grest.git
$ cd grest
$ python setup.py install
```
+ To install using a python package manager via `binary package`, simply run this command (in this case we've used pip, but any package manager is accepted as long as it uses [PyPI](https://pypi.python.org/pypi)):
```bash
$ pip install pygrest
```

### Edit mode installation

```bash
$ cd path/to/project
$ pip install -e .
```

## Examples
You can find an example app in [examples](https://github.com/mostafa/grest/tree/master/examples) directory.
+ `app.py` is a simple grest app that contains only one route `(/persons)`.
+ `extended_app.py` is the extended version of the above app and contains another route `(/pets)`, its relationship with `Person` model and a custom method (route) to handle `RelationshipFrom` properties. The `RelationshipTo` is automatically constructed using secondary model and secondary selection field of the `PersonsView`.

## Usage
In order to build an API, you should make a simple Flask app (or you may already have one).

A simple Flask app:
~~~~
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
~~~~

To use gREST, you should define your models with [Neomodel](http://neomodel.readthedocs.io/en/latest/getting_started.html#definition) syntax. Neomodel is easier to use than other ORMs and drivers. Take a look at this example:

~~~~
from neomodel import (StructuredNode, UniqueIdProperty, StringProperty)
from grest import utils

class Person(StructuredNode, utils.Node):
    uid = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()
~~~~
As you can see, we have imported `utils` from `grest`, so that we can use the `Node` mixin (which is used in JSON serialization of model data). Also note that the `Person` class (model) is inheriting from two parents: `StructuredNode` and `Node`.

Then we should inherit from `grest` to make a new view of our model (so that it accepts RESTful verbs):
~~~~
from grest import grest

class PersonsView(grest):
    __model__ = {"primary": Person}
    __selection_field__ = {"primary": "uid"}
~~~~
The most important part of grest is `__model__` and `__selection_field__` properties. They contain the logic to access your models and relations. As you see, our `primary` model is `Person` and its primary key (so to say) is `uid`, so the selection field of the primary model is `uid`.

You should register this view:
~~~~
PersonsView.register(app, route_base="/persons", trailing_slash=False)
~~~~

User input should never be trusted, so input validation is done through using [webargs](https://github.com/sloria/webargs):
To include input validation in each model, you should include `__validation_rules__` property, which is a mapping dictionary of keys (models' fields) and values (data type and validation rules).

~~~~
from neomodel import (StructuredNode, UniqueIdProperty, StringProperty)
from grest import utils
from webargs import fields

class Person(StructuredNode, utils.Node):
    __validation_rules__ = {
        "uid": fields.Str(),
        "first_name": fields.Str(),
        "last_name": fields.Str()
    }

    uid = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()
~~~~

You can override default behavior of HTTP verbs (index, get, post, put, patch and delete) and also make custom endpoints under this `PersonsView` class.

Last but not least, you should set up connection to your database, which is achieved by setting the `DATABASE_URL` propery of `neomodel.config`:
~~~~
neomodel.config.DATABASE_URL = "bolt://neo4j:neo4j@localhost:7687"
~~~~

One last part is to connect the logger of grest to Flask, or use a custom logger:
~~~~
app.ext_logger = app.logger
~~~~

`app.ext_logger` is the variable grest looks for, to log messages.

## Deployment
You can run this app either in development or production:

As it is the same flask application, you can run it in development like this:
~~~~
$ python app.py
~~~~

For production, you can use docker using `tiangolo/uwsgi-nginx-flask:flask` image or use your own setup.

## Contribution
Contribution is always welcome!

## License
[GPLv3](https://github.com/mostafa/grest/blob/master/LICENSE)
