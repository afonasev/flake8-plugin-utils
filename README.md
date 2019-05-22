# flake8-plugin-utils

[![pypi](https://badge.fury.io/py/flake8-plugin-utils.svg)](https://pypi.org/project/flake8-plugin-utils)
[![Python: 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://pypi.org/project/flake8-plugin-utils)
[![Downloads](https://img.shields.io/pypi/dm/flake8-plugin-utils.svg)](https://pypistats.org/packages/flake8-plugin-utils)
[![Build Status](https://travis-ci.org/Afonasev/flake8-plugin-utils.svg?branch=master)](https://travis-ci.org/Afonasev/flake8-plugin-utils)
[![Code coverage](https://codecov.io/gh/afonasev/flake8-plugin-utils/branch/master/graph/badge.svg)](https://codecov.io/gh/afonasev/flake8-plugin-utils)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://en.wikipedia.org/wiki/MIT_License)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Package provide base classes and utils for flake8 plugin writing.

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

## License

MIT

## Change Log

### Unreleased

* add message formatting to Error

### 0.2.1 - 2019-04-01

* don`t strip before src dedent in _error_from_src
* add is_none, is_true, is_false util functions

### 0.2.0 - 2019.02.21

* add assert methods

### 0.1.0 - 2019.02.09

* initial
