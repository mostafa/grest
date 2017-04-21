from setuptools import setup

setup(name="pygrest",
      version="0.1b1",
      description="Build REST APIs with Neo4j and Flask, as quickly as possible!",
      url="https://github.com/mostafa/grest",
      author="Mostafa Moradian",
      author_email="mostafamoradian0@gmail.com",
      license="GPLv3",
      packages=["grest"],
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
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Framework :: Flask",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7"
      ],
      # keywords='',
      zip_safe=False)
