# Contributing Guidelines

Guidelines for users, contributors, and maintainers of this project.

## Issue Tracker

If you are having trouble using panki or if you have a feature request, please
create a new issue in the project's [Issue Tracker].

## Developing

If you would like to make contributions to Anki's codebase, please make sure you
have first discussed your intended changes in the project's [Issue Tracker] with
the project's maintainers. Unexpected merge requests are appreciated, of course,
but thoroughly discussed changes are usually much easier for both the maintainer
and contributor.

### Virtual Environment

We recommend that you use a virtual environment when working on panki.

If you do not have `virtualenv`, you can install it with `pip`:
```sh
$ pip install virtualenv
```

To create a virtual environment:
```sh
$ virtualenv venv
```

To activate the virtual environment:
```sh
$ . venv/bin/activate
```

When you're done, you can deactivate the virtual environment:
```sh
$ deactivate
```

### Installation

You can install the project requirements using `pip`:
```sh
$ pip install -r requirements-dev.txt
```

### Testing

To run the unit tests with `coverage`:
```sh
$ coverage run
```

To generate an HTML coverage report:
```sh
$ coverage html
```

This will generate the report under the `htmlcov/` directory.

To open the report:
```sh
$ open htmlcov/index.html
```

### Linting

To link the project with `flake8`:
```sh
$ flake8
```

### Building and Installing

To build and install the project with `setuptools`:
```sh
$ python setup.py build install
```

You should be able to use the newly installed version of panki:
```sh
$ panki -h
```

To uninstall the project:
```sh
$ pip uninstall panki
```

### CICD pipeline

If you're working on the CICD pipeline, it is highly recommended that you test
your changes to `.gitlab-ci.yml` locally using [gitlab-runner] and [Docker].

For example, to execute the `build` job using the docker executor:
```sh
$ gitlab-runner exec docker build
```

## Releases

This section is mainly for use by project maintainers.

Make sure you have configured your system for publishing to [TestPyPI] and
[PyPI]. Your `~/.pypirc` config file should look similar to the following:
```
[pypi]
username = __token__
password = <token>

[testpypi]
username = __token__
password = <token>
```

Replace `<token>` with your tokens.

Remove the `dist/` directory, if it exists:
```sh
$ rm -rf dist
```

Build the project:
```sh
$ python setup.py clean build
```

Create a new distribution of the project using `setuptools`:
```sh
$ python setup.py bdist_wheel --build-number $(date +'%Y%m%d%H%M%S')
```

It is recommended that you first publish the new release to [TestPyPI] before
publishing to [PyPI]. See [Using TestPyPI] for more information.

Publish the distribution to [TestPyPI]:
```sh
$ twine upload -r testpypi dist/*
```

Install the new distribution from [TestPyPI]:
```sh
$ pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  panki
```

It's a good idea to test the new distribution with the example projects in the
`examples/` directory to confirm that everything is working properly.

Publish the distribution to [PyPI]:
```sh
$ twine upload -r pypi dist/*
```

Tag the head commit with the current project version:
```sh
$ git tag <version>
$ git push origin <version>
```

The version in `panki/metadata/metadata.json` should be bumped accordingly, and
the changed metadata file should merged to master.


<!-- links -->
[Issue Tracker]: https://gitlab.com/x4ku/panki/-/issues

[TestPyPI]: https://test.pypi.org
[PyPI]: https://pypi.org

[Using TestPyPI]: https://packaging.python.org/guides/using-testpypi/
[gitlab-runner]: https://gitlab.com/gitlab-org/gitlab-runner
[Docker]: https://www.docker.com/
