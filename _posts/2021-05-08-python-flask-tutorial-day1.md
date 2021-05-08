---
layout: post
title:  RESTful Application Development with Python Flask, Part 1
date:   2021-05-08 05:00:00 +0600
categories: python flask restful api professional
---
[Flask](https://pypi.org/project/Flask) is a popular micro-framework written in Python. It has a very small core and it is very easy to extend. There are barely any restrictions or fixed structures for Flask framework, which means, it is also very easy to mess things up. In this tutorial series, I will try to demonstrate how to build a Flask RESTful application from scratch.

There are already tons of tutorials out there on building Flask RESTful applications. Flask itself is very well documented. There are lots of options to quick-start a Flask application, for example, [cookiecutter-flask-restful](https://github.com/karec/cookiecutter-flask-restful). These are all very good resources, and should be explored. However, almost none of them are suitable for starting a codebase that can support a long term real world projects. Having worked on several large Flask projects over the last couple of years, I think the best way to learn Flask application development is to start from scratch. The main goal of this tutorial series is to guide the reader though every steps of designing, testing, distributing a RESTful application using Flask. I will try to include as many references as possible along with tips on best practices where applicable.

In part 1 of this series, we will focus on:

* Preparing project directory
* Creating and configuring an application
* Adding a resource endpoint and testing
* Preparing distribution packages and testing

Complete source code for **part 1** can be checked out from [here](https://github.com/zobayer1/flask-tutorial).

### Add initial files

Alright, let's start by creating our project's root directory, let's call it `flask-tutorial`. All our project files will reside within this directory. Let's quickly create three essential files within this directory:

* `README.md`: A README file. It often serves the purpose of an introductory page for the project. We should include developer instructions in this file. [Here's an example README file](https://raw.githubusercontent.com/zobayer1/flask-tutorial/main/README.md).
* `LICENSE`: A license file. Typically this will contain copyright notices for our project. For this exercise, we will simply start with a [MIT license](https://github.com/zobayer1/flask-tutorial/blob/main/LICENSE). [https://choosealicense.com](https://choosealicense.com) is quite helpful for finding the correct license.
* `.gitignore`: A gitignore file. We do not want everything from our project directory to end up in the version control tree. [Here is an example gitignore file](https://raw.githubusercontent.com/zobayer1/flask-tutorial/main/.gitignore).

At this point, our project directory will look like this:

```bash
flask-tutorial
├── .gitignore
├── LICENSE
└── README.md
```

### Initialize Git

Now we can `git init` and add our favorite remote origin. Let's add our first commit:

```bash
git init
git remote add origin <origin_url>
git branch -M main
git add . --all
git commit -am "Initial commit"
git push -u origin main
```

### Initialize virtualenv

As a server application, it is highly unlikely that we will make this server compatible with a lot of different python versions or platforms. However, build specifications can be changed anytime later on. Let's create our virtual environment with Python 3.8:

```bash
python3.8 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install wheel setuptools-scm
```

### Add packaging files

We should be able to create source and binary distribution packages for our project. In order to do so, we have to add a few files, namely, `setup.py`, `setup.cfg` and `MANIFEST.in` at the root of our project.

**`setup.py`** is a python file, the presence of which is an indication that the package we are about to install has likely been packaged and distributed with Distutils, which is the standard for distributing Python Modules. Learn more about [writing setup scripts here](https://docs.python.org/3/distutils/setupscript.html). Let's start with a simple `setup.py` file for our project, feel free to add or change values in `setup()` as necessary:

```python
# -*- coding: utf-8 -*-
from os import path
from setuptools import find_packages, setup

setup_dependencies = [
    "wheel",
    "setuptools-scm",
]

install_dependencies = [
    "flask-cors",
    "flask-restful",
    "python-dotenv",
]

setup(
    name="flask-tutorial",
    url="https://github.com/zobayer1/flask-tutorial",
    license="MIT",
    author="Zobayer Hasan",
    use_scm_version=True,
    setup_requires=setup_dependencies,
    packages=find_packages(exclude=["docs", "tests"]),
    include_package_data=True,
    zip_safe=True,
    platforms=["posix"],
    install_requires=install_dependencies,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
```

**`setup.cfg`** simply configures the behavior of the various setup commands for our project. This file is used in conjunction with `setup.py` file to supply metadata to the `setup()` function. We won't need to add much in `setup.cfg` file:

```conf
[metadata]
license_files = LICENSE

[options]
setup_requires =
    wheel==0.36.2
    setuptools-scm==6.0.1
```

**`MANIFEST.in`** is a manifest template file that contains instructions about how to generate the `MANIFEST` file, which is the exact list of files to include in our source distribution. Let's start with adding inclusion and exclusion rules for our project:

```bash
exclude .pre-commit-config.yaml
exclude .gitignore
include requirements.txt
include README.md
include .coveragerc
include tox.ini
recursive-include tests *.py
```

Note that, we haven't created some of these files yet. Don't worry about these files now, we will be creating them in the next section. At this point, our directory should look like this:

```bash
flask-tutorial
├── .gitignore
├── instance
├── LICENSE
├── MANIFEST.in
├── README.md
├── setup.cfg
├── setup.py
└── venv
```

Let's generate a source and wheel distribution to test that setup.py is working as expected:

```bash
python setup.py sdist bdist_wheel
```

Two new directories have been created: `build/` and `dist/`. Inside `dist/`, there will be a `.tar.gz` file and a `.whl` file. We can extract the `.tar.gz` file, and the `.whl` file can be installed with pip. They are our source package and wheel distribution respectively.

### Add code styling and testing suite

At this point, our project does not have any real source code. Let's fix this. Let's create two python packages named `myapi` and `tests`. A python package is a directory with a `__init__.py` file.

Before adding any real source code, let's add some more files in the project root that will help with testing and code styling for the project. It is extremely important for a large project that our codebase remain consistent, both at source and functional level.

First, we will add pre-commit, a python library to create pre-commit hooks. Pre-commit will run on every commit and make sure our source code is consistent. [Learn more about pre-commit](https://pre-commit.com). To install pre-commit, simply run:

```bash
pip install pre-commit
pre-commit install
```

To define some pre-commit hooks, let's create a file **`.pre-commit-config.yaml`**:

```yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v3.4.0
    hooks:
    -   id: end-of-file-fixer
    -   id: trailing-whitespace
-   repo: https://github.com/mgedmin/check-manifest
    rev: "0.46"
    hooks:
    -   id: check-manifest
-   repo: https://github.com/psf/black
    rev: 21.4b2
    hooks:
    -   id: black
```

We have added some hooks such as `end-of-file-fixer`, `trailing-whitespace`, `check-manifest` and `black`. Now, we do not have to worry too much about code styling, `black` will convert our code to a standard python style that is followed by the majority of python community. I have discussed about code styling with black briefly in [this post]({% post_url 2020-08-23-adopting-black-code-formatter %}). [Don't forget to check official github to learn more about black](https://github.com/psf/black).

We need to add one more file named **`pyproject.toml`**. This file allows us to add configurations from non-build development tools to a single file which is very convenient.

```toml
[build-system]
requires = ["setuptools>=42", "wheel", "setuptools_scm[toml]>=3.4"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
write_to = "myapi/version.py"
write_to_template = "# -*- coding: utf-8 -*-\n\n__version__ = '{version}'\n"
version_scheme = "release-branch-semver"

[tool.check-manifest]
ignore = ["myapi/version.py"]

[tool.black]
line-length = 120
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.pytest_cache
  | \.tox
  | \.venv
  | scripts
  | build
  | dist
)/
'''
```
We have configured some of the tools that we have already added, for example, `setuptools_scm`. This allows us to find the package version automatically from git tags and commits. We will be using [semantic versioning](https://semver.org) for tagging in this project. Note that we are using a temporary file `myapi/version.py` to write the version string. This file does not need to be tracked in git.

`pre-commit` will handle installing all of the hooks on its own. Simply run the following:

```bash
git add . --all
pre-commit autoupdate
pre-commit run --all-files
```

Let's add our test frameworks. We will use `tox` and `pytest` for testing this project, and `coverage` to generate code coverage reports. Let's start by installing the dependencies:

```bash
pip install tox flake8 codecov pytest pytest-cov python-dotenv
```

So far we have added a few pip libraries in our venv, let's create a **`requirements.txt`** file to keep track of them:

```bash
pip freeze > requirements.txt
```

Note that `requirements.txt` file should not be manually modified, rather generated using commands like `pip freeze`. Our project does not depend on this file, but we will use this file to resolve test environment dependencies. This file should be overwritten every time we add a new dependency.

We will need a **`tox.ini`** file to configure our test environments. For now, we will add Python 3.8, but other python environments can be easily added in a similar fashion.

```ini
[tox]
envlist =
    py38
    lint

[pytest]
filterwarnings =
    error::DeprecationWarning
    error::PendingDeprecationWarning

[flake8]
max-line-length = 120
select = B,C,E,F,W,T4,B9,B950
ignore = E203,E266,E501,W503,D1

[testenv]
passenv = USERNAME
commands = py.test --cov myapi {posargs} --cov-report term-missing
deps = -rrequirements.txt

[testenv:lint]
basepython = python3.8
commands = flake8 myapi tests
deps = flake8
```

Let's add a **`.coveragerc`** file to configure code coverage:

```conf
[run]
omit =
    myapi/manage.py
    myapi/version.py
    myapi/wsgi.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    def __del__
```

Let's run tox and we should see it failing since we haven't added any tests yet.

```bash
tox --recreate
```

Note that, `--recreate` flag is necessary every time a new dependency is added. We can target specific test environments with `-e` parameter, for example: `tox -e py38`, or `tox -e lint`.

Tests can also be run using `pytest -s` directly.

At this point, our project directory should include these (not including gitignored files and directories):

```bash
flask-tutorial
├── .coveragerc
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── myapi
│   ├── __init__.py
│   └── version.py
├── .pre-commit-config.yaml
├── pyproject.toml
├── README.md
├── requirements.txt
├── setup.cfg
├── setup.py
├── tests
│   └── __init__.py
└── tox.ini
```

We are now ready to move on to the new section, creating our Flask application.

### Create a Flask application

We will create a few files that will help define our Flask application.

**`myapi/config.py`:**

Behavior of a Flask application can be controlled by a number of [configuration parameters](https://flask.palletsprojects.com/en/1.1.x/config). A common practice is to load these configurations from a file or a python object instead of manually updating Flask's `app.config` dictionary. A lot of example applications tend to create several different configuration classes in `config.py` file for various environments such as `development`, `production` and `testing`. But this is not necessary, because a Flask application can only run with one environment configuration. Which means we are creating multiple classes that are never going to be used. A better approach is to use `config.py` file as a set of default configurations, or a way of loading custom environment variables into the application. Later we will see how we can use instance specific configurations to load configurations for different environments.

`myapi/config.py`
```python
# -*- coding: utf-8 -*-
import os

ENV = os.getenv("FLASK_ENV", "development")
SECRET_KEY = os.getenv("FLASK_SECRET", "bb9ba2817ef62e261d3adaf90c2727bb").encode("utf-8")
```

**`myapi/app.py`:**

This is going to be our script for creating the actual Flask application. We will enrich this file in future as we add more features to our application.

`myapi/app.py`
```python
# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask_cors import CORS


def create_app(instance_name, app_name="flask-tutorial"):
    app = Flask(app_name, instance_path=os.path.join(os.getcwd(), "instance"), instance_relative_config=True)
    app.config.from_object("myapi.config")
    app.config.from_pyfile(f"{instance_name}/application.cfg", silent=True)
    initialize_extensions(app)
    initialize_blueprints(app)
    return app


def initialize_extensions(app):
    CORS(app)


def initialize_blueprints(app):
    pass
```

We will talk about `instance_relative_config` in a later section.

**`myapi/wsgi.py`:**

A simple script exposing an app object which can be used as `FLASK_APP` parameter.

`myapi/wsgi.py`
```python
# -*- coding: utf-8 -*-
import os

from myapi.app import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))
```

