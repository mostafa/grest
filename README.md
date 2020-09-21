[![](https://rawgit.com/mostafa/grest/master/assets/gREST-logo.png)](https://github.com/mostafa/grest)

Build REST APIs with Neo4j and Flask, as quickly as possible!

[![PyPI version](https://badge.fury.io/py/pygrest.svg)](https://badge.fury.io/py/pygrest)
[![GitHub license](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://raw.githubusercontent.com/mostafa/grest/master/LICENSE)
[![Travis](https://img.shields.io/travis/mostafa/grest.svg)](https://travis-ci.org/mostafa/grest)
[![Coverage Status](https://coveralls.io/repos/github/mostafa/grest/badge.svg?branch=master)](https://coveralls.io/github/mostafa/grest?branch=master)
[![Join the chat at https://gitter.im/pygrest/Lobby](https://badges.gitter.im/pygrest/Lobby.svg)](https://gitter.im/pygrest/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmostafa%2Fgrest.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmostafa%2Fgrest?ref=badge_shield)
[![Known Vulnerabilities](https://snyk.io/test/github/mostafa/grest/badge.svg)](https://snyk.io/test/github/mostafa/grest)
[![Updates](https://pyup.io/repos/github/mostafa/grest/shield.svg)](https://pyup.io/repos/github/mostafa/grest/)
[![Downloads](https://pepy.tech/badge/pygrest)](https://pepy.tech/project/pygrest)
[![Downloads](https://pepy.tech/badge/pygrest/month)](https://pepy.tech/project/pygrest/month)
[![Downloads](https://pepy.tech/badge/pygrest/week)](https://pepy.tech/project/pygrest/week)

gREST (Graph-based REST API Framework) is a RESTful API development framework on top of Python, Flask, Neo4j and Neomodel. Its primary purpose is to ease development of RESTful APIs with little effort and minimum amount of code.

## Python Version Compatibility

If you want to use gREST with Python 2.7, you will need to stick with the good old [1.4.0](https://pypi.org/project/pygrest/1.4.0/) version. For Python 3.x onwards, use the latest version starting with 2.x.x or the `master` branch.

## Who's Using gREST?

If you're using gREST on your project, please let me know on [Twitter](https://twitter.com/MosiMoradian) or [open an issue](https://github.com/mostafa/grest/issues/new).

## Features

- Supported HTTP verbs: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- Supported response serialization methods (based on accept header): JSON, XML, YAML
- Indexing with skip/limit and order support
- Helper functions for handling of nodes and relations
- Simple configuration management
- Automatic validation of input data (plus monkey-patching of manual validation rules)
- Deep relationship support between nodes: _/primary_model/primary_model_item/related_model/related_model_item_
- Support for getting/posting relationship data between nodes
- Support for user-defined authentication and authorization
- Support for unicode routes (e.g. unicode tags)

## Installation

To install gREST, you can use setuptools (install from source) or use a python package manager (e.g. pip or easy_install).

- To install from `source code`, clone the repository (you should have git installed) and then run setup.py:

```bash
$ git clone https://github.com/mostafa/grest.git
$ cd grest
$ python setup.py install
```

- To install using a python package manager via `binary package`, simply run this command (in this case we've used pip, but any package manager is accepted as long as it uses [PyPI](https://pypi.python.org/pypi)):

```bash
$ pip install pygrest
```

### Edit mode installation

```bash
$ cd path/to/project
$ pip install -e .
```

## Documentation

For detailed documentation, please visit [http://grest.readthedocs.io/](http://grest.readthedocs.io/).

## Examples

You can find an example app in [examples](https://github.com/mostafa/grest/tree/master/examples) directory.

- `app.py` is a simple grest app that contains only one route `(/persons)`.
- `extended_app.py` is the extended version of the above app and contains another route `(/pets)`, its relationship with `Person` model and a custom method (route) to handle `RelationshipFrom` properties. The `RelationshipTo` is automatically constructed using secondary model and secondary selection field of the `PersonsView`.

## grest Command

The package ships a very simple command that can help you create a boilerplate Flask application. Simply run the following command:

```bash
grest <project_name>
```

## Usage

In order to build an API, you should make a simple Flask app (or you may already have one).

A simple Flask app:

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
```

To use gREST, you should define your models with [Neomodel](http://neomodel.readthedocs.io/en/latest/getting_started.html#definition) syntax. Neomodel is easier to use than other ORMs and drivers. Take a look at this example:

```python
from neomodel import (StructuredNode, UniqueIdProperty, StringProperty)
from grest import models

class Person(StructuredNode, models.Node):
    uid = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()
```

As you can see, we have imported `models` from `grest`, so that we can use the `Node` mixin (which is used in JSON serialization of model data). Also note that the `Person` class (model) is inheriting from two parents: `StructuredNode` and `Node`.

Then we should inherit from `grest` to make a new view of our model (so that it accepts RESTful verbs):

```python
from grest import GRest

class PersonsView(GRest):
    __model__ = {"primary": Person}
    __selection_field__ = {"primary": "uid"}
```

The most important part of grest is `__model__` and `__selection_field__` properties. They contain the logic to access your models and relations. As you see, our `primary` model is `Person` and its primary key (so to say) is `uid`, so the selection field of the primary model is `uid`.

You should register this view:

```python
PersonsView.register(app, route_base="/persons", trailing_slash=False)
```

User input should never be trusted, so input validation is done by using [webargs](https://github.com/sloria/webargs):
To include input validation in each model, you should include `__validation_rules__` property, which is a mapping dictionary of keys (models' fields) and values (data type and validation rules).

`__validation_rules__` property is there for customization of validation rules, with the release of version 0.2.1, validation rules are inferred and constructred from your models' properties, so it is unnecessary to define it in most cases.

```python
from neomodel import (StructuredNode, UniqueIdProperty, StringProperty)
from grest import models
from webargs import fields

class Person(StructuredNode, models.Node):
    __validation_rules__ = {
        "uid": fields.Str(),
        "first_name": fields.Str(),
        "last_name": fields.Str()
    }

    uid = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()
```

You can override default behavior of HTTP verbs (index, get, post, put, patch and delete) and also make custom endpoints under this `PersonsView` class.

Last but not least, you should set up your app's connection to the database (Neo4j), which is done by setting the `DATABASE_URL` propery of `neomodel.config`:

```python
neomodel.config.DATABASE_URL = "bolt://neo4j:neo4j@localhost:7687"
```

One last part is to connect the logger of grest to Flask, or use a custom logger:

```python
app.ext_logger = app.logger
```

`app.ext_logger` is the variable grest looks for, to log messages.

## Deployment

You can run this app either in development or production environments:

As it is the same flask application, you can run it in development like this:

```bash
$ python app.py
```

For production purposes, you can use docker using `tiangolo/uwsgi-nginx-flask:python2.7` image or use your own setup.

## Contribution

Contribution is always welcome! To report bugs, simply open an issue and fill it with related information. To fix a bug, fork the repository, fix the bug, push to your own fork, make a pull request and done!

## License

[GPLv3](https://github.com/mostafa/grest/blob/master/LICENSE)

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmostafa%2Fgrest.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmostafa%2Fgrest?ref=badge_large)
