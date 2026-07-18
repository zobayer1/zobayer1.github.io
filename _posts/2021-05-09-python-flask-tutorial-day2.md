---
layout: post
title:  RESTful Application Development with Python Flask, Part 2
date:   2021-05-09 05:00:00 +0600
categories: [Backend]
tags: [Python, Flask, REST, API, Tutorial]
---
Welcome back!!! In [part 1]({% post_url 2021-05-08-python-flask-tutorial-day1 %}) of this series, we built a small Flask application from scratch — packaging files, a `create_app` factory, an `instance/` directory for environment-specific configs, a single health-check endpoint, and a tox-based test setup. Everything lived in a flat `myapi/` package, and we tagged it as `v0.1.0`.

Part 2 picks up exactly where Part 1 ended. In this part, we will focus on:

* Renaming the project (`flask-tutorial` → `flask-restful-boilerplate`) and reorganizing the package
* Adding configurable logging with a queue listener and YAML-based config
* Rotating logs on the server using the system `logrotate` utility
* Adding Swagger UI to our API with `flask-apispec`
* A small CLI command, a few more tests, and pinned dependencies

By the end of this part, we will tag the result as `v0.2.0`. Full source code for this part is available in [Github](https://github.com/zobayer1/flask-restful-boilerplate/tree/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330). Clone the repository and checkout at tag `v0.2.0` if you want to follow along with the final state.

## **Renaming the project**

Before we add anything new, let's deal with a small annoyance. In part 1, the project name was `flask-tutorial`, which is descriptive but not a great name for something we are going to use as a reusable boilerplate. We are going to rename two separate things:

* The **repository** on Github: `flask-tutorial` → `flask-restful-boilerplate`.
* The **distribution package** that gets installed via pip: `flask-tutorial` → `myapi`.

The Python package directory (`myapi/`) does not need to change — we picked a good name already. But the metadata in `setup.py` and the Github URL do. We will trim down `setup.py` significantly while we are here, moving the dependency list out to `setup.cfg` (more on that next):

**[`setup.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/setup.py):**

```python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name="myapi",
    url="https://github.com/zobayer1/flask-restful-boilerplate",
    author="Zobayer Hasan",
    author_email="zobayer1@gmail.com",
    description="A RESTful application server template with Python Flask-RESTful.",
    keywords="python flask restful api server development template boilerplate",
    license="MIT",
    packages=find_packages(exclude=["docs", "tests"]),
    use_scm_version=True,
    platforms=["posix"],
    entry_points={
        "console_scripts": [
            "myapi = myapi.manage:cli",
        ],
    },
)
```

Much shorter, isn't it? `classifiers` and `install_requires` are no longer here. The CLI entry point still points to `myapi.manage:cli`, so `myapi --help` will keep working.

After renaming, the package now installs as `myapi` (matching the Python package directory), and the Github URL points to the new repository.

## **Pinning dependencies in `setup.cfg`**

In part 1, we kept `install_requires` inside `setup.py`. That works, but `setup.cfg` is a friendlier place for it — declarative, version-pinned, and it lets us split test/dev dependencies into `extras_require`.

**[`setup.cfg`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/setup.cfg):**

```conf
[metadata]
license_files = LICENSE

[options]
setup_requires =
    wheel==0.36.2
    setuptools-scm==6.0.1

install_requires =
    flask-apispec==0.11.0
    Flask-Cors==3.0.10
    Flask-RESTful==0.3.9
    gunicorn==20.1.0
    importlib-metadata;python_version<"3.8"
    logging-extras==0.2.0b0

[options.extras_require]
dev =
    pre-commit>=2.13.0
    python-dotenv>=0.17.1

test =
    flake8>=3.9.2
    pytest>=6.2.4
    pytest-cov>=2.12.1
    tox>=3.23.1
```

A few things worth noting:

* `flask-apispec` is new — we will use it for Swagger documentation later in this part.
* `gunicorn` is now a real install dependency, not something we install separately on the server.
* `logging-extras` is a small library that gives us a `QueueListenerHandler` and a YAML loader for the standard logging config. (Side note — this is a pip package I maintain. We will use it in a few sections.)
* The Python 3.7 fallback for `importlib-metadata` is conditional on the running Python version. Most production servers running Python 3.8+ will not even install it.
* Test dependencies move to `extras_require[test]`. To install them, run `pip install -e .[test]`. We will update `tox.ini` to do this automatically.

Now we don't need to keep a manually generated `requirements.txt` around anymore — `tox` can install our project with its test extras directly.

**[`tox.ini`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/tox.ini):**

```ini
[testenv]
passenv = USERNAME
commands =
    pip install --upgrade pip
    pip install -e .[test]
    py.test --cov myapi {posargs} --cov-report term-missing
```

The `deps = -rrequirements.txt` line from part 1 is gone — we resolve dependencies straight from `setup.cfg` now.

## **Reorganizing the package**

The single-file approach from part 1 works, but as the project grows, we want a layout that makes future additions obvious. Let's introduce four new subpackages under `myapi/`:

```bash
myapi
├── apis           # blueprints, grouped by audience (local/apiv1/admin)
├── commons        # shared utilities, enums, errors
├── extensions     # Flask extension wrappers (apispec, etc.)
└── internals      # models, schemas, services (the domain layer)
```

Each subpackage gets its own `__init__.py`. The idea is:

* **`apis/`** — every HTTP entry point lives here, grouped by whether it is local-only (server status, debug routes), versioned public API (`v1`), or admin (internal tools). Each group is a Flask blueprint.
* **`commons/`** — anything cross-cutting: enums, errors, utility helpers. Things that any other layer can import without pulling in cycles.
* **`extensions/`** — small wrapper classes for Flask extensions, exposed as importable singletons. We will write one for `flask-apispec` later in this part.
* **`internals/`** — domain models, marshmallow schemas, services. We are not adding code here yet, but we are creating the empty subpackages now so the structure is in place.

Most of these `__init__.py` files just have the encoding header for now. The interesting bits are coming in the next few sections.

## **Moving the health endpoint**

In part 1, we put our health-check at `/myapi/health/status`, with code under `myapi/health/`. Now that `myapi/apis/local/` exists, that's the better home for it. Local-only routes (only meant to be reached by load balancers, internal tooling, monitoring agents) belong here. The URL changes from `/myapi/health/status` to `/myapi/local/server/status`.

Delete the old `myapi/health/` directory and create the new location:

**[`myapi/apis/local/server_status.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/myapi/apis/local/server_status.py):**

```python
# -*- coding: utf-8 -*-
from flask import current_app as app
from flask_apispec import MethodResource, doc

from myapi.commons.utils.app_utils import app_version


class ServerStatus(MethodResource):
    @doc(tags=["local"], description="Get server health status")
    def get(self):
        app.logger.info("Health status request received")
        return {"server": f"{app.name} v{app_version(app.name)}", "status": "running"}, 200
```

Three things to notice:

1. We extend `flask_apispec.MethodResource` instead of `flask_restful.Resource`. This still gives us a REST-style class, but it also lets us decorate the methods with `@doc(...)` for Swagger.
2. We log an info-level message every time the endpoint is hit. We will see this show up in our log file once logging is wired in.
3. `app_version` is a small helper we will write next, in `commons/utils/`.

**[`myapi/apis/local/__init__.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/myapi/apis/local/__init__.py):**

```python
# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api

from myapi.apis.local.server_status import ServerStatus

blueprint = Blueprint("local", __name__)

api = Api(blueprint)
api.add_resource(ServerStatus, "/server/status")

__all__ = ["blueprint", "ServerStatus"]
```

We export both the `blueprint` (for registration) and the `ServerStatus` class (so the apispec extension can pull it in for documentation later).

The `admin` and `apiv1` packages get a similar skeleton, but with no resources yet. Here's `apiv1` — `admin` is identical with a different blueprint name:

**[`myapi/apis/apiv1/__init__.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/myapi/apis/apiv1/__init__.py):**

```python
# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api

blueprint = Blueprint("apiv1", __name__)

api = Api(blueprint)

__all__ = ["blueprint"]
```

We are setting the scaffolding for future endpoints. As soon as we add a resource to `apiv1`, we just import it here and call `api.add_resource(...)`.

## **The `commons/utils` helper**

Earlier, `myapi/apis/local/server_status.py` imported an `app_version` helper from `myapi.commons.utils.app_utils`. Let's add it — it's a tiny shim around `importlib.metadata.version` that gracefully handles Python 3.7:

**[`myapi/commons/utils/app_utils.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/myapi/commons/utils/app_utils.py):**

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

The `commons/enums/` and `commons/errors/` directories are still empty at this point — just placeholder `__init__.py` files. We will populate them in future parts when we add real models and error handlers.

## **A YAML-based logging configuration**

The Python standard library has excellent logging support, but its programmatic configuration is verbose. Python's `logging.config` module can also load configuration from a dictionary or a file, which is much cleaner. We are going to drive logging from a YAML file under `instance/`, so every environment can ship its own config.

We will use `logging-extras` for two things:

1. A `YAMLConfig.from_file` helper that loads our YAML, expands environment variable placeholders, and calls `logging.config.dictConfig` for us.
2. A `QueueListenerHandler` that lets slow handlers (file, SMTP) run on a background thread without blocking request handlers.

Add `logging-extras==0.2.0b0` to `install_requires` in `setup.cfg` (we already did this above) and create our logging config:

**[`instance/testing/logging.yaml`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/instance/testing/logging.yaml):**

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

* **`objects:`** — this is a `logging-extras` extension. We declare a `queue.Queue` once here, and reference it as `cfg://objects.queue` later. The standard library does not let you declare arbitrary objects in `dictConfig`, but our YAML loader does.
* **Three formatters** — `simple` for stderr (compact), `extended` for the file (includes module + line number), `email` for SMTP alerts.
* **`${LOGGING_ROOT:.}`** — environment variable expansion. If `LOGGING_ROOT` is set, the log file goes there; otherwise it goes to `.` (the current working directory). This is how we tell development, testing, and production where to write logs without changing the YAML file.
* **`file_handler`** is a plain `logging.FileHandler` — not a `RotatingFileHandler`. We will rotate logs externally with `logrotate`. More on that shortly.
* **`mail_handler`** sends `CRITICAL` log records as emails. The Mailtrap credentials above are just placeholders — change them in your own deployment.
* **`queue_handler`** — this is the non-blocking one. We will explain it in the next section.
* **`loggers.myapi`** — our application logger. It uses both `console` (immediate stderr output) and `queue_handler` (which fans out to the file and email handlers on a background thread). `propagate: no` stops messages from bubbling up to the root logger and getting duplicated.
* **`root`** — a fallback for messages that don't match any named logger. Catches output from third-party libraries.

Notice the application logger is `myapi`, not `flask.app` or similar. That matches the package name, which means `import logging; logging.getLogger(__name__)` inside any `myapi.*` module will inherit the right configuration automatically.

We also need to tell Flask where the logging config lives:

**[`myapi/config.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/myapi/config.py):**

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

"""APISPEC_SWAGGER_URL: URL for swagger.json file.

Set None to disable serving this resource.
"""
APISPEC_SWAGGER_URL = "/myapi/apispec/spec"

"""APISPEC_SWAGGER_UI_URL: URL for swagger-ui.

Set None to disable serving this view.
"""
APISPEC_SWAGGER_UI_URL = "/myapi/apispec"
```

Notice two changes from part 1's `config.py`:

* `SECRET_KEY` no longer has a default. If `$FLASK_SECRET` isn't set, the app refuses to start. We do not want a real secret key to be checked into version control as a fallback.
* We've added a few new keys for logging (`LOGGING_CONFIG`) and swagger (`APISPEC_*`). We are also being a bit more diligent with docstrings.

## **Wiring logging into the factory**

The critical thing about initializing logging is **timing**. We need it set up before any other module starts logging — including Flask's own startup. So our `create_app` function calls our logging setup as its very first step, before `Flask(...)` is constructed:

**[`myapi/app.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/myapi/app.py):**

```python
# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask_cors import CORS
from logging_.config import YAMLConfig

from myapi.apis import admin, apiv1, local
from myapi.extensions import apispec


def create_app(app_name: str, instance_name: str = None, instance_path: str = None):
    """Creates a Flask app"""
    instance_name = instance_name or os.getenv("FLASK_ENV", "development")
    instance_path = instance_path or os.path.join(os.getcwd(), "instance")
    _initialize_logging(f"{instance_name}/logging.yaml", instance_path, silent=True)
    app = Flask(
        app_name,
        instance_path=instance_path,
        static_url_path="/myapi/static",
        static_folder="myapi/static",
        instance_relative_config=True,
    )
    app.config.from_object("myapi.config")
    app.config.from_pyfile(f"{instance_name}/application.cfg", silent=True)
    if app.debug or app.testing:
        _register_apispec(app)
    _register_extensions(app)
    _register_blueprints(app)
    return app


def _initialize_logging(filename: str, instance_path: str, **kwargs: bool):
    """Initializes logging, must be done before creating Flask app"""
    YAMLConfig.from_file(os.path.join(instance_path, filename), **kwargs)


def _register_extensions(app: Flask):
    """Initializes extensions with app config"""
    CORS(app)


def _register_blueprints(app: Flask):
    """Initializes blueprints with URL prefixes"""
    app.register_blueprint(admin.blueprint, url_prefix="/myapi/admin")
    app.register_blueprint(local.blueprint, url_prefix="/myapi/local")
    app.register_blueprint(apiv1.blueprint, url_prefix="/myapi/v1")


def _register_apispec(app: Flask):
    """Initializes apispec plugin and registers resources for swagger"""
    apispec.init_app(app)
    apispec.register(local.ServerStatus, blueprint=local.blueprint)
```

Compared to part 1, the factory has grown but the structure is still clear:

* The function signature now takes `app_name` explicitly, plus optional overrides for `instance_name` and `instance_path` (handy for tests).
* We use **type hints** on parameters and return values throughout the file. This makes it easier for IDEs and tools like `mypy` to catch bugs.
* `_initialize_logging` runs first. By the time `Flask(...)` is called, every logger in the application — including `flask.app`, which is what `app.logger` resolves to under the hood — already has its handlers attached.
* `silent=True` means a missing logging config doesn't crash the app; it just falls back to the root logger.
* Swagger UI (apispec) only gets registered in `debug` or `testing` mode — we don't want to expose it in production. This is a sane default, you can change it if you want.
* All three blueprints (`admin`, `apiv1`, `local`) are registered up front, even though `admin` and `apiv1` are empty. Better to wire it once.

And the matching change in `wsgi.py`:

**[`myapi/wsgi.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/myapi/wsgi.py):**

```python
# -*- coding: utf-8 -*-
from myapi.app import create_app

app = create_app("myapi")
```

We no longer pass `FLASK_ENV` explicitly — `create_app` reads it from the environment itself (with a default of `development`).

## **Non-blocking logging with `QueueListenerHandler`**

A common rookie mistake with Python logging is to attach a slow handler — say, an `SMTPHandler` — directly to a hot logger. Every time you log a `CRITICAL` message, your request thread blocks on a TCP connection to the SMTP server. Under load, that means your endpoint latency tracks the worst-case SMTP latency.

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
3. The request thread continues immediately — it doesn't care how long the file write or the SMTP round-trip takes.

The console handler stays attached directly to the `myapi` logger so we still get immediate, synchronous stderr output during development. Slow handlers go behind the queue. Best of both worlds.

## **Rotating logs with `logrotate`**

If our application keeps writing to `myapi.log` forever, that file gets huge and we never get to compress or archive yesterday's logs. We need rotation.

Python's `logging.handlers` has rotating file handlers (`RotatingFileHandler`, `TimedRotatingFileHandler`), but they have a well-known caveat — they don't play nicely with multi-process workers like `gunicorn -w 4`. If four worker processes all try to rotate the same file at midnight, you end up with race conditions, lost log lines, or workers writing to the wrong file descriptor.

Linux already ships a robust solution for this: the `logrotate` daemon. It runs once a day via cron, handles rotation outside our application, and takes care of compression and retention. Our app just keeps writing to one file (`myapi.log`); `logrotate` does everything else.

On your server, create `/etc/logrotate.d/myapi`:

```conf
/var/log/myapi/myapi.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    create 0640 myapi myapi
}
```

Let's go through the directives:

* **`daily`** — rotate once a day. You can use `weekly`, `monthly`, or a size-based trigger like `size 100M` instead.
* **`rotate 14`** — keep 14 old logs around. Anything older is deleted.
* **`compress`** + **`delaycompress`** — gzip rotated logs, but skip the most recent one so it doesn't get compressed before our app finishes writing.
* **`missingok`** + **`notifempty`** — don't fail if the log file is absent, and skip rotation if it's empty.
* **`copytruncate`** — copy the current file to the rotated name, then truncate the original in place. This is the trick that makes rotation work without telling our app to reopen its file handle. The alternative is `create` plus a `postrotate` block that sends `SIGUSR1` to the app, but `copytruncate` is simpler and good enough for most setups.
* **`create 0640 myapi myapi`** — only used if we drop `copytruncate`; sets permissions on the freshly created file.

Set `LOGGING_ROOT=/var/log/myapi` in your production environment, make sure the `myapi` user owns that directory, and you are good. Force a test rotation with:

```bash
sudo logrotate -f /etc/logrotate.d/myapi
```

After the first rotation, you should see `myapi.log.1` (or `myapi.log.1.gz` after the next round) appear alongside the live `myapi.log`.

One small caveat — `copytruncate` is not atomic. There's a very small window where log records written during the copy can be lost. For most applications this is fine; for an audit log where every record matters, prefer the `create` + `postrotate kill -USR1` route and teach your handler to reopen the file on signal.

## **The apispec extension**

We hinted earlier that we register an `apispec` extension in `create_app`. Let's actually write it. The goal is to wrap `flask-apispec` so the rest of the app can use it as a singleton via `from myapi.extensions import apispec`.

**[`myapi/extensions/apispece_ext.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/myapi/extensions/apispece_ext.py):**

```python
# -*- coding: utf-8 -*-
from typing import Type

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, Blueprint
from flask_apispec import FlaskApiSpec
from flask_restful import Resource

from myapi.commons.utils.app_utils import app_version


class ApiSpecExt(object):
    def __init__(self, app: Flask = None):
        self.apispec = FlaskApiSpec()
        if app:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app: Flask):
        app.config.update(
            {
                "APISPEC_SPEC": APISpec(
                    title=app.name,
                    version=app_version(app.name),
                    openapi_version="3.0.2",
                    plugins=[MarshmallowPlugin()],
                )
            }
        )
        self.apispec.init_app(app)

    def register(self, resource: Type[Resource], blueprint: Blueprint):
        blueprint.before_app_first_request(lambda: self.apispec.register(resource, blueprint=blueprint.name))
```

A few notes:

* The class follows the classic two-phase Flask extension pattern — `__init__` (no app), `init_app(app)` (configures the actual app). This way, we can declare `apispec = ApiSpecExt()` as a module-level singleton and bind it to a Flask app later.
* `APISpec` is the actual OpenAPI 3.0.2 spec object. We point it at our `marshmallow` schemas (we'll write some in part 3) so request and response models show up in Swagger automatically.
* `register(resource, blueprint)` defers the registration until the first request comes in, using `before_app_first_request`. This avoids ordering problems where we try to register a resource before its blueprint is attached.

And the singleton in **[`myapi/extensions/__init__.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/myapi/extensions/__init__.py)**:

```python
# -*- coding: utf-8 -*-
from myapi.extensions.apispece_ext import ApiSpecExt

apispec = ApiSpecExt()

__all__ = ["apispec"]
```

We already added the wiring in `create_app` — in debug/testing mode, it calls `apispec.init_app(app)` and registers `ServerStatus` for documentation. When you visit `/myapi/apispec` in development, you'll get a fully interactive Swagger UI listing the local health endpoint.

## **A small CLI command**

It's handy to be able to ask the running app what environment variables it sees. Let's add a `myapi env` subcommand. The `manage.py` file gets a bit of a rewrite from part 1:

**[`myapi/manage.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/myapi/manage.py):**

```python
# -*- coding: utf-8 -*-
import os

import click
from flask.cli import FlaskGroup

from myapi.app import create_app


cli = FlaskGroup(create_app=lambda: create_app("myapi"))


@cli.command()
def env():
    """Check env variables for the app."""
    env_vars = ["FLASK_ENV", "FLASK_SECRET", "LOGGING_ROOT", "LOGGING_CONFIG"]
    for var in env_vars:
        click.echo(f"${var}={os.getenv(var)}")
```

Now `myapi env` prints every Flask-related environment variable our app cares about. This is the kind of small CLI command that pays for itself the first time you have to debug a production deployment.

```bash
$ myapi env
$FLASK_ENV=development
$FLASK_SECRET=bb9ba2817ef62e261d3adaf90c2727bb
$LOGGING_ROOT=None
$LOGGING_CONFIG=None
```

You can keep adding `@cli.command()` decorated functions for tasks like database migrations, seeding, periodic cleanup, etc.

## **Updating the tests**

Our tests have to keep up with the changes. Three things change here:

1. The test app needs to set environment variables before calling `create_app`.
2. The health-check test moves to `tests/test_apis/test_public/test_status.py`.
3. We add a new CLI test for the `env` command.

First, a small helper for environment variables in **[`tests/envvars.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/tests/envvars.py)**:

```python
# -*- coding: utf-8 -*-
variables = {
    "LOGGING_ROOT": ".",
    "FLASK_SECRET": "bb9ba2817ef62e261d3adaf90c2727bb",
    "FLASK_ENV": "testing",
}
```

Then the updated **[`tests/conftest.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/tests/conftest.py)**:

```python
# -*- coding: utf-8 -*-
import os

import pytest

from myapi.app import create_app
from tests.envvars import variables


@pytest.fixture(scope="module")
def app():
    """A flask app with testing configurations"""
    os.environ.update(variables)
    return create_app("myapi")


@pytest.fixture(scope="module")
def client(app):
    """An HTTP test client to test api endpoints"""
    return app.test_client()


@pytest.fixture(scope="module")
def runner(app):
    """A CLI test client to test shell commands"""
    return app.test_cli_runner()
```

We set `FLASK_ENV=testing` and `LOGGING_ROOT=.` so the testing instance config and logging YAML are picked up, and the log file lives in the project root during tests (not somewhere unexpected).

The health-check test moves to its new location. Delete `tests/test_health/` entirely and create a `tests/test_apis/test_public/` package with the new test:

**[`tests/test_apis/test_public/test_status.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/tests/test_apis/test_public/test_status.py):**

```python
# -*- coding: utf-8 -*-
import json


def test_server_status_returns_success(client):
    """Test fails if /myapi/local/server/status does not return success"""
    response = client.get("/myapi/local/server/status")
    assert response.status_code == 200
    assert json.loads(response.data).get("status") == "running"
```

The only real difference from part 1's test is the URL — `/myapi/health/status` is now `/myapi/local/server/status`.

And a new test for the CLI command, in **[`tests/test_cli.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/tests/test_cli.py)**:

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

We use the `runner` fixture (a `FlaskCliRunner`) to invoke `myapi env` and check that all four environment variable names show up in the output.

The existing `tests/test_config.py` gets a tiny touch-up — `app.name` is `myapi` now, and we use `app_version` from our utils:

**[`tests/test_config.py`](https://github.com/zobayer1/flask-restful-boilerplate/blob/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330/tests/test_config.py):**

```python
# -*- coding: utf-8 -*-
from myapi.commons.utils.app_utils import app_version


def test_env(app):
    """Test fails if app was not initialized with testing configurations"""
    assert app.env == "testing"
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

tests/test_apis/test_public/test_status.py .                                       [ 25%]
tests/test_cli.py .                                                                [ 50%]
tests/test_config.py ..                                                            [100%]

---------- coverage: platform linux, python 3.8.x-final-0 ----------
Name                                              Stmts   Miss  Cover
---------------------------------------------------------------------
myapi/__init__.py                                     0      0   100%
myapi/apis/__init__.py                                0      0   100%
myapi/apis/admin/__init__.py                          5      0   100%
myapi/apis/apiv1/__init__.py                          5      0   100%
myapi/apis/local/__init__.py                          7      0   100%
myapi/apis/local/server_status.py                     8      0   100%
myapi/app.py                                         24      0   100%
myapi/commons/utils/app_utils.py                      4      0   100%
myapi/config.py                                       5      0   100%
myapi/extensions/__init__.py                          2      0   100%
myapi/extensions/apispece_ext.py                     14      0   100%
myapi/manage.py                                       8      0   100%
---------------------------------------------------------------------
TOTAL                                                82      0   100%

================================ 4 passed in 0.18s ================================
```

Now start the development server:

```bash
flask run -h 0.0.0.0 -p 5000
```

Navigate to [http://localhost:5000/myapi/local/server/status](http://localhost:5000/myapi/local/server/status). You should get:

```json
{
    "server": "myapi v0.2.0",
    "status": "running"
}
```

While you're at it, open [http://localhost:5000/myapi/apispec](http://localhost:5000/myapi/apispec) — Swagger UI should render, with the `ServerStatus` endpoint documented and a "Try it out" button.

Finally, check the log file. There should now be a `myapi.log` in the project root (because `LOGGING_ROOT=.` for development), and every request to the health endpoint should produce a line like:

```text
[2021-05-09 05:00:00.000] [pid 12345] [INFO] - [server_status:11]: Health status request received
```

If you want to see log rotation in action without waiting until tomorrow, copy the `/etc/logrotate.d/myapi` config to your server, set `LOGGING_ROOT=/var/log/myapi`, and run `sudo logrotate -f /etc/logrotate.d/myapi`.

## **Wrapping up**

This was a big part. To recap, we have:

* Renamed the project and slimmed down `setup.py`.
* Pinned dependencies in `setup.cfg` with `extras_require` for dev and test groups.
* Reorganized the package into `apis/`, `commons/`, `extensions/`, and `internals/` subpackages.
* Moved the health endpoint to `apis/local/` and updated its URL.
* Added a YAML-driven logging config with a non-blocking queue listener.
* Set up `logrotate` for production log rotation.
* Added Swagger UI through a custom `flask-apispec` extension.
* Added a CLI `env` command and updated the test suite.

Tag this state as **v0.2.0**. Full source code for this part is available in [Github](https://github.com/zobayer1/flask-restful-boilerplate/tree/845f3c60b8dbe0d10bf22aa8db6bed58f26ac330). Clone the repository and checkout at tag `v0.2.0`.

In part 3, we will dig into the `internals/` package — models, marshmallow schemas, and services — and start building out a real `apiv1` resource with an error handler base class. Stay tuned!!!
