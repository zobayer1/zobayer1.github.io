---
layout: post
title:  "Python Flask from Zero, Part 2: Layers, Logging, and a CLI"
date:   2021-05-09 05:00:00 +0600
categories: [Backend]
tags: [Python, Flask, REST, API, Tutorial]
---
Welcome back!!! In [part 1]({% post_url 2021-05-08-python-flask-tutorial-day1 %}) of this series, we built a small Flask application from scratch: packaging files, a `create_app` factory, an `instance/` directory for environment-specific configuration, and a single health-check endpoint under `myapi/endpoints/v1/`, all covered by a tox-based test setup. We tagged that state as `v0.1.0`.

Part 2 picks up exactly where part 1 ended. Here we will:

* Pin dependencies in `setup.cfg` and trim `setup.py` to match
* Grow the package into audience-grouped `endpoints/`, plus `commons/`, `models/`, `services/`, and `extensions/` layers
* Add configurable logging driven by a YAML file and a non-blocking queue listener
* Add a small CLI command and a few more tests

By the end of this part, we will tag the result as `v0.2.0`.

> **Where the code lives.** The full source is in the [flask-restful-tutorial](https://github.com/zobayer1/flask-restful-tutorial) repo, organized one branch per part. This post corresponds to the `part-2` branch. Check out `part-2` to explore the code shown here.
{: .prompt-info }

## **Pinning dependencies in `setup.cfg`**

In part 1, we kept the dependency list inline in `setup.py` via `install_requires`, with loose, unversioned names. That's fine for a quick start, but it's risky for a server: a fresh `pip install` can silently pull a newer release of Flask or one of its transitive dependencies, and suddenly the code that ran yesterday behaves differently. Pinning each dependency to an exact version keeps the build reproducible; every environment, from a developer's laptop to CI to production, resolves the same package set, so we get real dev/prod parity and no surprise upgrades. `setup.cfg` is a friendlier home for those pins too. It's declarative, and it lets us split test and dev dependencies into `extras_require`. Let's move them there:

**[`setup.cfg`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/setup.cfg):**

```ini
[metadata]
license_files = LICENSE

[options]
install_requires =
    click==8.1.8
    Flask==3.0.3
    Flask-Cors==5.0.0
    gunicorn==23.0.0
    importlib-metadata;python_version<"3.8"
    logging-extras==0.4.0b0

[options.extras_require]
dev =
    pre-commit>=3.5.0
    python-dotenv>=1.0.1

test =
    flake8>=7.1.2
    pytest>=8.3.5
    pytest-cov>=5.0.0
    tox>=4.25.0
```

A few things worth noting:

* `click` is pinned explicitly now, since the CLI command we add later uses it directly.
* `gunicorn` is a real install dependency, not something we install separately on the server.
* `logging-extras` is a small library that gives us a `QueueListenerHandler` and a YAML loader for the standard logging config. (Side note: this is a pip package I maintain. We will wire it up a few sections down.)
* `importlib-metadata` is only pulled in on Python < 3.8. Servers on 3.8+ won't even install it.
* Dev and test dependencies move to `extras_require`. Install everything for local work with `pip install -e .[dev,test]`; `tox` installs just the `test` extra on its own.

With the dependencies declared here, `setup.py` is otherwise the same file from part 1; `install_requires` simply falls away, leaving project metadata, `use_scm_version`, the package-discovery rule, and the console-script entry point:

**[`setup.py`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/setup.py):**

```python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name="myapi",
    url="https://github.com/zobayer1/flask-restful-tutorial",
    author="Zobayer Hasan",
    author_email="zobayer1@gmail.com",
    description="A RESTful application server template built with Python and Flask.",
    keywords="python flask restful api server development template boilerplate",
    license="MIT",
    packages=find_packages(exclude=["docs", "tests", "tests.*"]),
    use_scm_version=True,
    platforms=["posix"],
    entry_points={
        "console_scripts": [
            "myapi = myapi.manage:cli",
        ],
    },
)
```

The CLI entry point still points to `myapi.manage:cli`, so `myapi --help` keeps working.

With test dependencies declared in `setup.cfg`, `tox` can install our project with its test extras directly, with no separate dependency file to maintain.

**[`tox.ini`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/tox.ini):**

```ini
[testenv]
passenv = USERNAME
commands =
    pip install --upgrade pip
    pip install -e .[test]
    py.test --cov myapi {posargs} --cov-report term-missing
```

The inline `deps` list from part 1 is gone; we resolve dependencies straight from `setup.cfg` now.

## **Reorganizing the package**

Part 1 already nudged us toward structure: the health endpoint lives under `myapi/endpoints/v1/`, not in a flat module. Part 2 builds that out into a layout where future additions have an obvious home. The target structure:

```bash
myapi
├── app.py
├── config.py
├── manage.py
├── wsgi.py
├── commons          # shared, cross-cutting code
│   ├── enums
│   ├── errors
│   └── helpers
├── endpoints        # HTTP entry points, grouped by audience
│   ├── admin        # internal tooling (empty for now)
│   ├── local        # load-balancer / monitoring routes (empty for now)
│   └── v1           # versioned public API, holds the health check from part 1
├── extensions       # Flask extension wrappers (empty for now)
├── models           # domain models (empty for now)
└── services         # business logic (empty for now)
```

Every directory gets an `__init__.py` so it's a real package. The idea behind each:

* **`endpoints/`** holds every HTTP entry point, grouped by who is meant to reach it: `local` for routes only internal callers hit (load balancers, monitoring agents), `v1` for the versioned public API, `admin` for internal tooling. Part 1's health check already lives under `v1`.
* **`commons/`** is cross-cutting code any layer can import without creating cycles: shared `helpers`, `enums`, and `errors`.
* **`models/`** holds the domain models, the data structures the app is actually about. Empty for now; we start filling it in part 3.
* **`services/`** is the business logic that operates on those models, kept out of the HTTP layer so it stays testable on its own. Empty for now too.
* **`extensions/`** are thin wrappers around Flask extensions, exposed as importable singletons.

Most of these `__init__.py` files hold nothing but the encoding header for now; we are laying down the skeleton so later parts just drop files into the right place. The one directory with real code in this part is `commons/helpers`.

## **The `commons/helpers` package**

Part 1's health endpoint looked up the running version with `from importlib.metadata import version`, inlined right in the module. Now that we have a `commons/` layer, that belongs in a shared helper: it's the kind of utility more than one module will want, and it lets us paper over the Python 3.7 fallback once, in one place:

**[`myapi/commons/helpers/metadata.py`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/myapi/commons/helpers/metadata.py):**

```python
# -*- coding: utf-8 -*-
import sys


def app_version(name: str) -> str:
    if sys.version_info < (3, 8):  # pragma: no cover
        # noinspection PyUnresolvedReferences
        from importlib_metadata import version
    else:  # pragma: no cover
        from importlib.metadata import version
    return version(name)
```

The only change to the health endpoint is to use it. Everything else about the route (the blueprint, the URL, the response) stays exactly as it was in part 1:

**[`myapi/endpoints/v1/health.py`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/myapi/endpoints/v1/health.py):**

```python
# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import current_app as app

from myapi.commons.helpers.metadata import app_version

health_blueprint = Blueprint("health", __name__)


@health_blueprint.route("/status", methods=["GET"])
def status():
    return {"server": f"{app.name} v{app_version(app.name)}", "status": "running"}, 200
```

The URL is unchanged: `/myapi/v1/health/status`. The `commons/enums/` and `commons/errors/` packages stay empty for now; we populate them in later parts when real models and error handlers arrive.

## **Logging**

Good logging is the difference between a five-minute production diagnosis and a five-hour one. We set it up in a few steps: a YAML-driven configuration, wiring it into the app factory so it's ready before anything logs, a non-blocking queue listener so slow handlers don't stall requests, and finally a quick look at it working.

### **A YAML-based logging configuration**

The Python standard library has excellent logging support, but its programmatic configuration is verbose. Python's `logging.config` module can also load configuration from a dictionary or a file, which is much cleaner. We are going to drive logging from a YAML file under `instance/`, so every environment can ship its own config.

We will use `logging-extras` for two things:

1. A `YAMLConfig.from_file` helper that loads our YAML, expands environment-variable placeholders, and calls `logging.config.dictConfig` for us.
2. A `QueueListenerHandler` that lets slow handlers (file, SMTP) run on a background thread without blocking request handlers.

We already added `logging-extras==0.4.0b0` to `install_requires` above. Now create the logging config. Just like the `application.cfg` files from part 1, this lives under `instance/`, which we keep out of git entirely, so it never ships in the repo, and you create it yourself:

**`instance/testing/logging.yaml`:**

```yaml
# Logger configuration
version: 1

objects:
  queue:
    class: queue.Queue
    maxsize: 1000

formatters:
  simple:
    format: "[%(asctime)s.%(msecs)03d] [pid %(process)d] [%(levelname)s]: %(message)s"
    datefmt: "%Y-%m-%d %H:%M:%S"
  extended:
    format: "[%(asctime)s.%(msecs)03d] [pid %(process)d] [%(levelname)s] - [%(module)s:%(lineno)d]: %(message)s"
    datefmt: "%Y-%m-%d %H:%M:%S"
  email:
    format: "Message Severity: %(levelname)s\r\nModule Locations: %(filename)s %(module)s:%(lineno)d\r\nServer Timestamp: %(asctime)s\r\nMessage:\r\n%(message)s"
    datefmt: "%Y-%m-%d %H:%M:%S"

handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: simple
    stream: ext://sys.stderr

  file_handler:
    class: logging.FileHandler
    level: DEBUG
    formatter: extended
    filename: ${LOGGING_ROOT:.}/myapi.log

  mail_handler:
    class: logging.handlers.SMTPHandler
    level: CRITICAL
    formatter: email
    mailhost: ["smtp.mailtrap.io", 2525]
    fromaddr: "myapi-no-reply@myapi.com"
    toaddrs: ["myapi-admin@myapi.com"]
    subject: "MyAPI Alert"
    credentials: ["4ede6aef7b1908", "4330ca394c2c40"]

  queue_handler:
    class: logging_.handlers.QueueListenerHandler
    queue: cfg://objects.queue
    handlers:
      - cfg://handlers.file_handler
      - cfg://handlers.mail_handler

loggers:
  myapi:
    level: DEBUG
    handlers: [console, queue_handler]
    propagate: no

root:
  level: NOTSET
  handlers: [console]
```

Let's walk through the interesting bits:

* **`objects:`** is a `logging-extras` extension. We declare a `queue.Queue` once here, and reference it as `cfg://objects.queue` later. The standard library does not let you declare arbitrary objects in `dictConfig`, but our YAML loader does.
* **Three formatters**: `simple` for stderr (compact), `extended` for the file (includes module + line number), and `email` for SMTP alerts.
* **`${LOGGING_ROOT:.}`** is environment-variable expansion. If `LOGGING_ROOT` is set, the log file goes there; otherwise it goes to `.` (the current working directory). This is how we tell development, testing, and production where to write logs without changing the YAML file.
* **`file_handler`** is a plain `logging.FileHandler`, not a `RotatingFileHandler`; rotating and pruning log files is left to the deployment environment (more on that below).
* **`mail_handler`** sends `CRITICAL` log records as emails. The Mailtrap credentials above are just placeholders; change them in your own deployment.
* **`queue_handler`** is the non-blocking one. We will explain it in the next section.
* **`loggers.myapi`** is our application logger. It uses both `console` (immediate stderr output) and `queue_handler` (which fans out to the file and email handlers on a background thread). `propagate: no` stops messages from bubbling up to the root logger and getting duplicated.
* **`root`** is a fallback for messages that don't match any named logger. It catches output from third-party libraries.

Notice the application logger is `myapi`, not `flask.app` or similar. That matches the package name, which means `import logging; logging.getLogger(__name__)` inside any `myapi.*` module inherits the right configuration automatically.

We put this one under `testing/` because the test suite needs a known config to run against, so `instance/testing/logging.yaml` is the file to create first. Every other environment gets its own copy under `instance/<env>/logging.yaml`: `instance/development/logging.yaml`, `instance/production/logging.yaml`, and so on. Because the whole `instance/` directory stays out of version control (exactly as in part 1), none of these are committed; each deployment supplies its own, and real secrets and per-host settings never land in git.

We also need to tell Flask where the logging config lives:

**[`myapi/config.py`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/myapi/config.py):**

```python
# -*- coding: utf-8 -*-
import os

"""ENV: Flask application environment.

Examples: `development`, `production`, `testing`.
"""
ENV = os.getenv("FLASK_ENV", "development")

"""SECRET_KEY: Secret key used for signing cookies and tokens.

Application will fail to start if $FLASK_SECRET is not set.
"""
try:
    SECRET_KEY = os.getenv("FLASK_SECRET").encode("utf-8")
except AttributeError:  # pragma: no cover
    raise RuntimeError("Environment variable $FLASK_SECRET was not set")

"""LOGGING_CONFIG: Path to logging configurations.

Logger extension will read configurations from the specified file.
"""
LOGGING_CONFIG = os.getenv("LOGGING_CONFIG", f"instance/{ENV}/logging.yaml")
```

Two changes from part 1's `config.py`:

* `SECRET_KEY` no longer has a hard-coded fallback. If `$FLASK_SECRET` isn't set, the app refuses to start; we never want a real secret key living in version control as a default.
* We add `LOGGING_CONFIG`, pointing at `instance/<env>/logging.yaml` by default, and give every setting a docstring while we're here.

### **Wiring logging into the factory**

The critical thing about initializing logging is **timing**. We need it set up before any other module starts logging, including Flask's own startup. So our `create_app` function calls our logging setup as its very first step, before `Flask(...)` is constructed:

**[`myapi/app.py`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/myapi/app.py):**

```python
# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask_cors import CORS
from logging_.config import YAMLConfig

from myapi.endpoints.v1.health import health_blueprint


def create_app(instance_name: str, app_name: str = "myapi"):
    """Creates a Flask app"""
    instance_path = os.path.join(os.getcwd(), "instance")
    initialize_logging(f"{instance_name}/logging.yaml", instance_path, silent=True)
    app = Flask(
        app_name,
        instance_path=instance_path,
        static_url_path="/myapi/static",
        static_folder="myapi/static",
        instance_relative_config=True,
    )
    app.config.from_object("myapi.config")
    app.config.from_pyfile(f"{instance_name}/application.cfg", silent=True)
    initialize_extensions(app)
    initialize_blueprints(app)
    return app


def initialize_logging(filename: str, instance_path: str, **kwargs: bool):
    """Initializes logging, must be done before creating Flask app"""
    YAMLConfig.from_file(os.path.join(instance_path, filename), **kwargs)


def initialize_extensions(app: Flask):
    """Initializes extensions with app config"""
    CORS(app)


def initialize_blueprints(app: Flask):
    """Initializes blueprints with URL prefixes"""
    app.register_blueprint(health_blueprint, url_prefix="/myapi/v1/health")
```

Compared to part 1, the factory has grown but the structure is still clear:

* The signature is unchanged from part 1: it takes the `instance_name` and an optional `app_name` (defaulting to `"myapi"`). Callers like `wsgi.py` still pass the environment in, so nothing downstream has to change.
* We add **type hints** on parameters throughout the file. This makes it easier for IDEs and tools like `mypy` to catch bugs.
* `initialize_logging` runs first. By the time `Flask(...)` is called, and by the time `app.logger` exists, the `myapi` logger already has its handlers attached.
* `silent=True` means a missing logging config doesn't crash the app; it just falls back to the root logger. (This is why running in `development` without an `instance/development/logging.yaml` simply logs nothing extra instead of erroring.)
* We serve static files under `/myapi/static` and register the health blueprint at `/myapi/v1/health`. As `local`, `admin`, and future `v1` resources grow, they get registered here too.

Because the signature didn't change, `wsgi.py` carries over from part 1 untouched; it still calls `create_app(os.getenv("FLASK_ENV", "development"))`.

### **Non-blocking logging with `QueueListenerHandler`**

A common mistake with Python logging is to attach a slow handler (say, an `SMTPHandler`) directly to a hot logger. Every time you log a `CRITICAL` message, your request thread blocks on a TCP connection to the SMTP server. Under load, that means your endpoint latency tracks the worst-case SMTP latency.

The standard library ships `logging.handlers.QueueHandler` and `QueueListener` to solve exactly this problem, but `dictConfig` does not make them easy to compose. `logging-extras` provides a `QueueListenerHandler` that combines both, so all you have to do in your YAML config is point it at a queue and a list of handlers:

```yaml
queue_handler:
  class: logging_.handlers.QueueListenerHandler
  queue: cfg://objects.queue
  handlers:
    - cfg://handlers.file_handler
    - cfg://handlers.mail_handler
```

Now, when our application logs a message:

1. The log record gets dropped onto the queue (a very fast, non-blocking enqueue).
2. A background thread (the `QueueListener`) pulls records off the queue and dispatches them to `file_handler` and `mail_handler`.
3. The request thread continues immediately; it doesn't care how long the file write or the SMTP round-trip takes.

The console handler stays attached directly to the `myapi` logger so we still get immediate, synchronous stderr output during development. Slow handlers go behind the queue. Best of both worlds.

One thing we deliberately leave out is log **rotation**. Our app simply writes to `myapi.log`; rotating, compressing, and pruning those files is not the application's job. In most deployments that concern is handled outside the app, by the system (`logrotate`, `journald`) or by the container runtime and its logging driver. Keeping it out of the app also sidesteps the multi-process pitfalls of Python's `RotatingFileHandler` under `gunicorn -w 4`.

### **Seeing logging in action**

Nothing in the app logs to the `myapi` logger yet (the health check is a plain status route), so let's watch a record flow through the whole chain. We wrote `instance/testing/logging.yaml` above for the tests; the development server needs its own config too, so give it one; copying the testing file is the quickest start:

```bash
cp instance/testing/logging.yaml instance/development/logging.yaml
```

Then drop a temporary line into the health handler:

```python
@health_blueprint.route("/status", methods=["GET"])
def status():
    app.logger.info("health status requested")
    return {"server": f"{app.name} v{app_version(app.name)}", "status": "running"}, 200
```

`current_app.logger` resolves to the `myapi` logger (Flask names it after the app), so this one line fans out to every handler we configured. Run the server with `LOGGING_ROOT` pointed somewhere and hit the endpoint:

```bash
export LOGGING_ROOT=.
flask run -h 0.0.0.0 -p 5000
curl http://localhost:5000/myapi/v1/health/status
```

You'll see it on stderr immediately (the `console` handler, `simple` format):

```text
[2021-05-09 05:00:00.000] [pid 12345] [INFO]: health status requested
```

and a moment later in `myapi.log` (the `queue_handler` → `file_handler`, `extended` format, written on the background thread):

```text
[2021-05-09 05:00:00.000] [pid 12345] [INFO] - [health:12]: health status requested
```

We'll add real and meaningful logging in part 3 as the endpoints grow. The point here is the plumbing: one `app.logger` call reaches a fast console handler and a non-blocking file handler with zero per-call setup.

## **A small CLI command**

Part 1 already set up the CLI: `manage.py` wires a `FlaskGroup` so `myapi run` and `myapi shell` work out of the box. Adding our own command is just a matter of decorating a function with `@cli.command()`. Let's create a new command `myapi env` that prints the current configuration.

> **This is a learning aid, not a production feature.** A command that dumps secrets and running configuration is fine for experimenting on your own machine, but you should never ship one in a real app. Keep commands like this out of anything that runs in production.
{: .prompt-warning }

**[`myapi/manage.py`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/myapi/manage.py):**

```python
# -*- coding: utf-8 -*-
import os

import click
from flask.cli import FlaskGroup

from myapi.app import create_app


def create_cli_app():
    return create_app(os.getenv("FLASK_ENV", "development"))


@click.group(cls=FlaskGroup, create_app=create_cli_app)
def cli():
    """Management interface for myapi"""
    pass


@cli.command()
def env():
    """Check env variables for the app."""
    env_vars = ["FLASK_ENV", "FLASK_SECRET", "LOGGING_ROOT", "LOGGING_CONFIG"]
    for var in env_vars:
        click.echo(f"${var}={os.getenv(var)}")


if __name__ == "__main__":
    cli()
```

The output looks like this:

```bash
$ myapi env
$FLASK_ENV=development
$FLASK_SECRET=bb9ba2817ef62e261d3adaf90c2727bb
$LOGGING_ROOT=.
$LOGGING_CONFIG=None
```

You can keep adding `@cli.command()` decorated functions for tasks like database migrations, seeding, periodic cleanup, and so on.

## **Updating the tests**

Our tests have to keep up with the changes. Three things change here:

1. The test fixture pins the environment (`FLASK_ENV`, `FLASK_SECRET`, `LOGGING_ROOT`) before calling `create_app`, so the suite runs the same regardless of what's set in your shell.
2. We add a new CLI test for the `env` command.
3. The existing config test gets a tiny touch-up for the shared `app_version` helper.

Start with the updated **[`tests/conftest.py`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/tests/conftest.py)**:

```python
# -*- coding: utf-8 -*-
import os

import pytest

from myapi.app import create_app


@pytest.fixture(scope="module")
def app():
    """A flask app with testing configurations"""
    os.environ.update(
        {
            "FLASK_ENV": "testing",
            "FLASK_SECRET": "bb9ba2817ef62e261d3adaf90c2727bb",
            "LOGGING_ROOT": ".",
        }
    )
    return create_app("testing")


@pytest.fixture(scope="module")
def client(app):
    """An HTTP test client to test api endpoints"""
    return app.test_client()


@pytest.fixture(scope="module")
def runner(app):
    """A CLI test client to test shell commands"""
    return app.test_cli_runner()
```

We pass `"testing"` to `create_app`, exactly as in part 1, so it loads `instance/testing/`. The `os.environ.update(...)` above is about **test isolation**: a unit or integration test should behave identically no matter what a developer happens to have exported, so we pin every variable the app reads rather than inheriting the ambient shell. `FLASK_SECRET` is the one the app strictly requires: part 2's `config.py` dropped the hard-coded fallback and refuses to start without it. `LOGGING_ROOT=.` keeps the test log file (`myapi.log`) in the project root instead of wherever an ambient `LOGGING_ROOT` might point. `FLASK_ENV=testing` is belt-and-suspenders: `create_app("testing")` and the testing instance config already force the environment, but pinning it makes the intent explicit and guards against future code that reads it. We also add a `runner` fixture (a `FlaskCliRunner`) for testing CLI commands.

The health-check test carries over from part 1 unchanged; the endpoint didn't move, so **[`tests/test_health/test_status.py`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/tests/test_health/test_status.py)** still hits `/myapi/v1/health/status`:

```python
# -*- coding: utf-8 -*-
import json


def test_server_status_returns_success(client):
    """Test fails if /myapi/v1/health/status does not return success"""
    response = client.get("/myapi/v1/health/status")
    assert response.status_code == 200
    assert json.loads(response.data).get("status") == "running"
```

A new test for the CLI command goes in **[`tests/test_cli.py`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/tests/test_cli.py)**:

```python
# -*- coding: utf-8 -*-
from myapi import manage


def test_command_env_exits_with_success(runner):
    """Test fails if `myapi env` does not execute with success status"""
    result = runner.invoke(manage.cli, ["env"])
    env_vars = ["FLASK_ENV", "FLASK_SECRET", "LOGGING_ROOT", "LOGGING_CONFIG"]
    for var in env_vars:
        assert var in result.output
    assert result.exit_code == 0
```

We use the `runner` fixture to invoke `myapi env` and check that all four environment variable names show up in the output.

Finally, `tests/test_config.py` gets a tiny touch-up: it now imports `app_version` from our new `commons/helpers` package instead of calling `importlib.metadata` directly:

**[`tests/test_config.py`](https://github.com/zobayer1/flask-restful-tutorial/blob/part-2/tests/test_config.py):**

```python
# -*- coding: utf-8 -*-
from myapi.commons.helpers.metadata import app_version


def test_env(app):
    """Test fails if app was not initialized with testing configurations"""
    assert app.config["ENV"] == "testing"
    assert app.testing


def test_application_version(app):
    """Test fails if importlib metadata could not be loaded from metadata"""
    assert app.name == "myapi"
    assert len(app_version(app.name)) > 0
```

## **Running it all together**

Let's verify everything still works. From the project root:

```bash
pip install -e .[test]
tox --recreate
```

If everything was wired correctly, the output should look something like this:

```bash
collected 4 items

tests/test_cli.py .                                                      [ 25%]
tests/test_config.py ..                                                  [ 75%]
tests/test_health/test_status.py .                                       [100%]

---------- coverage: platform linux, python 3.8.11-final-0 -----------
Name                                Stmts   Miss  Cover
-------------------------------------------------------
myapi/__init__.py                       0      0   100%
myapi/app.py                           20      0   100%
myapi/commons/__init__.py               0      0   100%
myapi/commons/enums/__init__.py         0      0   100%
myapi/commons/errors/__init__.py        0      0   100%
myapi/commons/helpers/__init__.py       0      0   100%
myapi/commons/helpers/metadata.py       3      0   100%
myapi/config.py                         5      0   100%
myapi/endpoints/__init__.py             0      0   100%
myapi/endpoints/admin/__init__.py       0      0   100%
myapi/endpoints/local/__init__.py       0      0   100%
myapi/endpoints/v1/__init__.py          0      0   100%
myapi/endpoints/v1/health.py            7      0   100%
myapi/extensions/__init__.py            0      0   100%
myapi/models/__init__.py                0      0   100%
myapi/services/__init__.py              0      0   100%
-------------------------------------------------------
TOTAL                                  35      0   100%


============================== 4 passed in 0.17s ================================
```

Now start the development server:

```bash
flask run -h 0.0.0.0 -p 5000
```

Navigate to [http://localhost:5000/myapi/v1/health/status](http://localhost:5000/myapi/v1/health/status). You should get:

```json
{
    "server": "myapi v0.2.0",
    "status": "running"
}
```

## **Wrapping up**

This was a big part. To recap, we have:

* Pinned dependencies in `setup.cfg` with `extras_require` for dev and test groups, and trimmed `setup.py` to match.
* Reorganized the package into `endpoints/`, `commons/`, `models/`, `services/`, and `extensions/` subpackages.
* Added a shared `app_version` helper and pointed the health endpoint at it (its URL is unchanged).
* Added a YAML-driven logging config with a non-blocking queue listener.
* Added a CLI `env` command and grew the test suite.

Commit this state and tag it as **v0.2.0**. With a tag in place, `python -m build` and `use_scm_version` will stamp the package as `0.2.0` rather than a development version. Full source code for this part is available on [GitHub](https://github.com/zobayer1/flask-restful-tutorial/tree/part-2). Clone the repository and check out the `part-2` branch.

In part 3, we will start filling in the `models/` and `services/` layers and build out a real `v1` resource with an error-handler base class. Stay tuned!!!
