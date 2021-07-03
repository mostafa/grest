# -*- coding: utf-8 -*-
#
# Copyright (C) 2017- Mostafa Moradian <mostafamoradian0@gmail.com>
#
# This file is part of grest.
#
# grest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# grest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with grest.  If not, see <http://www.gnu.org/licenses/>.
#

from setuptools import setup  # type: ignore

from grest import __version__

# Extract requirements from requirements.txt
REQUIREMENTS = [r.rstrip() for r in open("requirements.txt").readlines()]

setup(name="pygrest",
      version=__version__,
      description="Build REST APIs with Neo4j and Flask, as quickly as possible!",
      url="https://github.com/mostafa/GRest",
      author="Mostafa Moradian",
      author_email="mostafamoradian0@gmail.com",
      license="GPLv3",
      include_package_data=True,
      packages=["grest", "grest.verbs"],
      long_description="""
gREST
=====

gREST (Graph-based REST API Framework) is a RESTful API development
framework on top of Python, Flask, Neo4j and Neomodel. Its primary
purpose is to ease development of RESTful APIs with little effort and
miminum amount of code.

For more information, visit github page of `the project <https://github.com/mostafa/GRest>`_.""",
      install_requires=REQUIREMENTS,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Framework :: Flask",
          "Topic :: Software Development :: Libraries",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7"
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'pytest-flask'],
      scripts=['bin/grest'],
      zip_safe=False)
