# Installation

You have 3 options to install gREST:

## Install Using Binary Package

You can use a python package manager (e.g. pip or easy_install) to install the binary package distributed on [Python Package Index (PYPI)](https://pypi.org/project/pygrest/):

```bash
pip install pygrest
```

## Install From Source Codes

To install from source codes, clone the gREST's repository using git command (which you should have it installed) and then run setup.py:

```bash
git clone https://github.com/mostafa/grest.git
cd grest
python setup.py install
```

## Installation In Edit Mode <sup>(developer-friendly way)</sup>

If you want to edit the project and fix bugs or add new features, simply clone the repository and then install the package in edit-mode:

```bash
git clone https://github.com/mostafa/grest.git
cd grest
pip install -e .
```
