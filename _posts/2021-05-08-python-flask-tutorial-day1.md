---
layout: post
title:  RESTful Application Development with Python Flask, Part 1
date:   2021-05-08 05:00:00 +0600
categories: python flask restful api professional
---
[Flask](https://pypi.org/project/Flask) is a popular micro-framework written in Python. It has a very small core and it is very easy to extend. There are barely any restrictions or fixed structures for Flask framework, which means, it is also very easy to mess things up. In this tutorial series, I will try to demonstrate how to build a Flask RESTful application from scratch.

There are already tons of tutorials out there on building Flask RESTful applications. Flask itself is very well documented. There are lots of options to quick-start a flask application, for example, [cookiecutter-flask-restful](https://github.com/karec/cookiecutter-flask-restful). These are all very good resources, and should be explored. However, almost none of them are suitable for starting a codebase that can support a long term real world projects. Having worked on several large Flask projects over the last couple of years, I think the best way to learn Flask application development is to start from scratch. The main goal of this tutorial series is to guide the reader though every steps of designing, testing, distributing a RESTful application using Flask. I will try to include as many references as possible along with tips on best practices where applicable.

## Part 1

In part 1 of this series, we will focus on:

* Preparing project directory
* Creating and configuring an application
* Adding a resource endpoint and testing
* Preparing distribution packages and testing

Complete source code for **part 1** can be checked out from [here](https://github.com/zobayer1/flask-tutorial).

### Preparing project directory

#### Add initial files

Alright, let's start by creating our project's root directory, let's call it `flask-tutorial`. All our project files will reside within this directory. Let's quickly create three essential files within this directory:

* `README.md`: A README file. It often serves the purpose of an introductory page for the project. We should include developer instructions in this file. [Here's an example README file](https://raw.githubusercontent.com/zobayer1/flask-tutorial/main/README.md).
* `LICENSE`: A license file. Typically this will contain copyright notices for our project. For this exercise, we will simply start with a [MIT license](https://github.com/zobayer1/flask-tutorial/blob/main/LICENSE). [https://choosealicense.com](https://choosealicense.com) is quite helpful for finding the correct license.
* `.gitignore`: A gitignore file. We do not want everything from our project directory to end up in the version control tree. [Here is an example gitignore file](https://raw.githubusercontent.com/zobayer1/flask-tutorial/main/.gitignore).

At this point, our project directory will look like this:

{% highlight console %}

    flask-tutorial
    ├── .gitignore
    ├── LICENSE
    └── README.md

{% endhighlight %}

#### Initialize Git

Now we can `git init` and add our favorite remote origin. Let's add our first commit:

{% highlight console %}

    git init
    git remote add origin <origin_url>
    git branch -M main
    git add . --all
    git commit -am "Initial commit"
    git push -u origin main

{% endhighlight %}

#### Initialize virtualenv

As a server application, it is highly unlikely that we will make this server compatible with a lot of different python versions or platforms. However, build specifications can be changed anytime later on. Let's create our virtual environment with Python 3.8:

{% highlight console %}

    python3.8 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install wheel setuptools-scm

{% endhighlight %}

#### Add packaging files

We should be able to create source and binary distribution packages for our project. In order to do so, we have to add a few files, namely, `setup.py`, `setup.cfg` and `MANIFEST.in` at the root of our project.

**`setup.py`** is a python file, the presence of which is an indication that the package we are about to install has likely been packaged and distributed with Distutils, which is the standard for distributing Python Modules. Learn more about [writing setup scripts here](https://docs.python.org/3/distutils/setupscript.html). Let's start with a simple `setup.py` file for our project, feel free to change values in `setup()` as necessary:

{% highlight python %}

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

{% endhighlight %}

**`setup.cfg`** simply configures the behavior of the various setup commands for our project. This file is used in conjunction with `setup.py` file to supply metadata to the `setup()` function. We won't need to add much in `setup.cfg` file:

{% highlight conf %}

    [metadata]
    license_files = LICENSE

    [options]
    setup_requires =
        wheel==0.36.2
        setuptools-scm==6.0.1

{% endhighlight %}

**`MANIFEST.in`** is a manifest template file that contains instructions about how to generate the `MANIFEST` file, which is the exact list of files to include in our source distribution. Let's start with adding inclusion and exclusion rules for our project:

{% highlight ini %}
```
exclude .pre-commit-config.yaml
exclude .gitignore
include requirements.txt
include README.md
include .coveragerc
include tox.ini
recursive-include tests *.py
```
{% endhighlight %}

Note that, we haven't created some of these files yet. Don't worry about these files now, we will be creating them in the next section.
