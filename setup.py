import re
from os.path import join, dirname
from setuptools import setup


# Reading package version (the same way the sqlalchemy does)
with open(join(dirname(__file__), 'grest', '__init__.py')) as v_file:
  package_version = re.compile(
      r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)


setup(name="pygrest",
      version=package_version,
      description="Build REST APIs with Neo4j and Flask, as quickly as possible!",
      url="https://github.com/mostafa/GRest",
      author="Mostafa Moradian",
      author_email="mostafamoradian0@gmail.com",
      license="GPLv3",
      packages=["grest"],
      long_description="""
gREST
=====

gREST (Graph-based REST API Framework) is a RESTful API development
framework on top of Python, Flask, Neo4j and Neomodel. Its primary
purpose is to ease development of RESTful APIs with little effort and
miminum amount of code.

For more information, visit github page of `the project <https://github.com/mostafa/GRest>`_.""",
      install_requires=[
          "flask",
          "flask_classful",
          "neomodel",
          "webargs",
          "markupsafe",
          "inflect",
          "autologging",
          "requests"
      ],
      classifiers=[
          # "Development Status :: 4 - Beta",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Framework :: Flask",
          "Topic :: Software Development :: Libraries",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3"
      ],
      # keywords='',
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'pytest-flask'],
      zip_safe=False)
