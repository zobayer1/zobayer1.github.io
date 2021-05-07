---
layout: post
title:  RESTful Application Development with Python Flask, Part 1
date:   2021-05-08 05:00:00 +0600
categories: python flask restful api professional
---
[Flask](https://pypi.org/project/Flask/) is a popular micro-framework written in Python. It has a very small core and it is very easy to extend. There are barely any restrictions or fixed structures for Flask framework, which means, it is very easy to mess up your application. In this tutorial series, I will try to show you how to build a Flask RESTful application from scratch.

There are tons of tutorials on building Flask RESTful applications. Flask itself is very well documented. There are lots of options to quick-start a flask application, for example, [cookiecutter-flask-restful](https://github.com/karec/cookiecutter-flask-restful). These are all very good resources, and should be explored if you are interested to know more about Flask. However, almost none of them are suitable for starting a codebase that can support your long term real world projects. I have been working on several large Flask based projects over last couple of years, and I think the best way to learn Flask application development is to start from scratch. The main goal of this tutorial series is to guide you though every steps of designing, testing, distributing a RESTful application using Flask. I will try to include as many references as possible along with tips on best practices where applicable.

## Part 1

In part 1 of this series, we will focus on:

* Preparing project directory
* Creating and configuring an application
* Adding a resource endpoint and testing
* Preparing distribution packages and testing

### Preparing project directory

Alright, let's start by creating our project's root directory, let's call it `flask-tutorial`. All our project files will reside within this directory. Let's quickly create three essential files within this directory:

* `README.md`: A README file. It often serves the purpose of an introductory page for the project. We should include developer instructions in this file. [Here's an example README file](https://raw.githubusercontent.com/zobayer1/flask-tutorial/main/README.md).
* `LICENSE`: A license file. Typically this will contain copyright notices for your project. For this exercise, we will simply start with a [MIT license](https://github.com/zobayer1/flask-tutorial/blob/main/LICENSE). You can visit [https://choosealicense.com/](https://choosealicense.com/) to create another license that might be more suitable for your need.
* `.gitignore`: A gitignore file. We do not want everything from our project directory to end up in the version control tree. [Here is an example gitignore file](https://raw.githubusercontent.com/zobayer1/flask-tutorial/main/.gitignore).

At this point, our project directory will look like this:

{% highlight bash %}

    flask-tutorial
    ├── .gitignore
    ├── LICENSE
    └── README.md

{% endhighlight %}

Now we can `git init` and add our favorite remote origin. When you open a new repository in github, bitbucket, etc, they will include the instructions to add remote origins to your local repository. Just follow those steps. Let's add our first commit:

{% highlight bash %}

    git add . --all
    git commit -am "Initial commit"
    git push -u origin main

{% highlight bash %}

