---
layout: post
title:  "Adopting Black Code Formatter"
date:   2020-08-23 12:01:01 +0600
categories: black pre-commit code-format python
---
Finally, we've decided to adopt [Black](https://github.com/psf/black) code styling for all our python projects. I wanted to do this without making too many side-changes to the project file structures, so I went with another python tool called [Pre-Commit](https://pre-commit.com/).

Although not everyone may like how black modifies the source code, especially around some of the PEP8 guidelines and quotes, I think it is necessary to maintain a single code styling throughout the entire project. The main advantage of black is that, you can write code in whatever style you want and then black will reformat the code to a single style before you commit your files.

Biggest issue developers faces with black is the use of double quotes everywhere. In fact, this is probably the biggest controversy in black's history. I must say, the entire [discussion](https://github.com/psf/black/issues/118) was pretty hilarious to read. Many Python developers prefer single quotes for quoting string literals. However, as most of the developers in my team came from C++ and Java backgrounds, they actually preferred double quotes over single quotes.

Another major complaint, black isn't very configurable. Black defends this by saying, if it allowed a lot of options then it would lose its purpose as an opinionated code-style, which is quite agreeable.

In the next few sections, I'll try to describe the changes.

## Installing black and pre-commit
To install the libraries, run: `pip install black pre-commit`. I do not think we needed to add these dependencies in the main `requirements.txt` file, as these are mostly required for code reviewers and mergers. But I'd strongly encourage all python developers to use these in their local environments as well.

## Generating a simple pre-commit config
Create a file named `.pre-commit-config.yaml`. Here's a simple pre-commit configuration with black:

{% highlight yaml %}
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v3.2.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
-   repo: https://github.com/psf/black
    rev: 19.10b0
    hooks:
    -   id: black
        language_version: python3.6
        exclude: setup.py
{% endhighlight %}

You can check official documentations for other configuration options.

## Initialize pre-commit
Once you've created the configuration file, make sure all its dependencies are up-to-date by running `pre-commit autoupdate`. You may see output like this:

{% highlight bash %}
(venv) [zobayer@hyperion boing]$ pre-commit autoupdate
Updating https://github.com/pre-commit/pre-commit-hooks ... [INFO] Initializing environment for https://github.com/pre-commit/pre-commit-hooks.
updating v2.4.0 -> v3.2.0.
Updating https://github.com/psf/black ... already up to date.
{% endhighlight %}

Next step would be to install pre-commit hooks for your git repository. Run `pre-commit install` to set up git-hook scripts. On success, it will tell you something like this:

{% highlight bash %}
(venv) [zobayer@hyperion boing]$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
{% endhighlight %}

You can check its contents using `cat .git/hooks/pre-commit` and you can modify anything to your liking, although I'd recommend not to manually modify any hook.

It's usually a good idea to run the hooks against all the files when adding new hooks (usually pre-commit will only run on the changed files during git hooks). Run `pre-commit run --all-files`. If any of these fails, it means pre-commit has modified some files and you have to add changes and commit again.

{% highlight bash %}
(venv) [zobayer@hyperion boing]$ pre-commit run --all-files
[INFO] Installing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
Trim Trailing Whitespace.................................................Failed
- hook id: trailing-whitespace
- exit code: 1
- files were modified by this hook

Fixing ... (truncated output)

Fix End of Files.........................................................Failed
- hook id: end-of-file-fixer
- exit code: 1
- files were modified by this hook

Fixing ... (truncated output)

Check Yaml...........................................(no files to check)Skipped
Check for added large files..............................................Passed
black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted ... (truncated output)
All done! ✨ 🍰 ✨
27 files reformatted, 3 files left unchanged.
{% endhighlight %}

## Further configruations
You can add a `pyproject.toml` file and include additional configurations for black. For example:

{% highlight toml %}
[tool.black]
line-length = 120
target-version = ['py36', 'py37', 'py38']
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.pytest_cache
  | \.tox
  | \.venv
  | schema_dir
  | scripts
  | build
  | dist
  | setup.py
)/
'''
{% endhighlight %}

Do not forget to run `pre-commit run --all-files` again if you've modified any configuration.

## Commit your code
Once all issues are resolved, you can commit normally.

{% highlight bash %}
(venv) [zobayer@hyperion boing]$ git add . --all
(venv) [zobayer@hyperion boing]$ git commit -am "Adopt Black"
Trim Trailing Whitespace.................................................Passed
Fix End of Files.........................................................Passed
Check Yaml...............................................................Passed
Check for added large files..............................................Passed
black....................................................................Passed
{% endhighlight %}

Each time your commit fails, it will tell you that there were some changes made by one or more pre-commit rules. Just add the changed files and commit again. Alternatively, you can run `pre-commit run` first and then try to commit.

## Excluding inspections in your IDEs
If you are using PyCharm, you can go to editor inspection configuraiton and exclude following `Pep8` warnings

- `E203`
- `E266`
- `E501`
- `E231`

## Add a cool badge [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
You can include a `README` badge to show people that you are using black

`[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)`

╰( ͡° ͜ʖ ͡° )つ──☆*:・ﾟ
