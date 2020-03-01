# flake8-plugin-utils

[![pypi](https://badge.fury.io/py/flake8-plugin-utils.svg)](https://pypi.org/project/flake8-plugin-utils)
[![Python: 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://pypi.org/project/flake8-plugin-utils)
[![Downloads](https://img.shields.io/pypi/dm/flake8-plugin-utils.svg)](https://pypistats.org/packages/flake8-plugin-utils)
[![Build Status](https://travis-ci.org/Afonasev/flake8-plugin-utils.svg?branch=master)](https://travis-ci.org/Afonasev/flake8-plugin-utils)
[![Code coverage](https://codecov.io/gh/afonasev/flake8-plugin-utils/branch/master/graph/badge.svg)](https://codecov.io/gh/afonasev/flake8-plugin-utils)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://en.wikipedia.org/wiki/MIT_License)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

The package provides base classes and utils for flake8 plugin writing.

## Installation

```bash
pip install flake8-plugin-utils
```

## Example

Write simple plugin

```python
from flake8_plugin_utils import Error, Visitor, Plugin

class MyError(Error):
    code = 'X100'
    message = 'my error'

class MyVisitor(Visitor):
    def visit_ClassDef(self, node):
        self.error_from_node(MyError, node)

class MyPlugin(Plugin):
    name = 'MyPlugin'
    version = '0.1.0'
    visitors = [MyVisitor]
```

and test it with pytest

```python
from flake8_plugin_utils import assert_error, assert_not_error

def test_code_with_error():
    assert_error(MyVisitor, 'class Y: pass', MyError)

def test_code_without_error():
    assert_not_error(MyVisitor, 'x = 1')
```

### Configuration

To add configuration to a plugin, do the following:

1. Implement classmethod `add_options` in your plugin class, as per the
[flake8 docs](https://flake8.pycqa.org/en/latest/plugin-development/plugin-parameters.html#registering-options).
1. Override classmethod `parse_options_to_config` in your plugin class
to return any object holding the options you need.
1. If you need a custom `__init__` for your visitor, make sure it accepts
a keyword argument named `config` and pass it to `super().__init__`
1. Use `self.config` in visitor code.

Example:

```python
from flake8_plugin_utils import Error, Visitor, Plugin

class MyError(Error):
    code = 'X100'
    message = 'my error with {thing}'

class MyConfig:
    def __init__(self, config_option):
        self.config_option = config_option

class MyVisitorWithConfig(Visitor):
    def visit_ClassDef(self, node):
        self.error_from_node(
            MyError, node, thing=f'{node.name} {self.config.config_option}'
        )

class MyPluginWithConfig(Plugin):
    name = 'MyPluginWithConfig'
    version = '0.0.1'
    visitors = [MyVisitorWithConfig]

    @classmethod
    def add_options(cls, options_manager):
        options_manager.add_option('--config_option', ...)

    @classmethod
    def parse_options_to_config(cls, option_manager, options, args):
        return MyConfig(config_option=options.config_option)
```

### Formatting

Your `Error`s can take formatting arguments in their `message`:

```python
from flake8_plugin_utils import Error, Visitor, assert_error

class MyFormattedError(Error):
    code = 'X101'
    message = 'my error with {thing}'

class MyFormattedVisitor(Visitor):
    def visit_ClassDef(self, node):
        self.error_from_node(MyFormattedError, node, thing=node.name)

def test_code_with_error():
    assert_error(
        MyFormattedVisitor,
        'class Y: pass',
        MyFormattedError,
        thing='Y',
    )
```

### Usage with typing/mypy

The `Plugin` and `Visitor` classes are generic with the config class as type
parameter.  If your plugin does not have any config, inherit it from
`Plugin[None]` and the visitors from `Visitor[None]`.  Otherwise, use the
config class as the type parameter (e.g. `Plugin[MyConfig]` and
`Visitor[MyConfig]` in the above example).

## License

MIT

## Change Log

Unreleased
-----

* ...

1.1.1 - 2020-03-02
-----

* ignore encoding errors when reading strings for noqa validation

1.1.0 - 2020-03-01
-----

* add ability for plugins to parse and use configuration
**NB: this change breaks type-checking if you use typing/mypy. Change your
code to inherit from `Plugin[None]` and `Visitor[None]` to fix.**

1.0.0 - 2019-05-23
-----

* add message formatting to Error

0.2.1 - 2019-04-01
-----

* don`t strip before src dedent in _error_from_src
* add is_none, is_true, is_false util functions

0.2.0 - 2019.02.21
-----

* add assert methods

0.1.0 - 2019.02.09
-----

* initial
