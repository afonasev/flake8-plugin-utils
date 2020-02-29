import ast
from typing import NamedTuple

import pytest
from flake8_plugin_utils.plugin import Error, Plugin, Visitor, check_noqa
from flake8_plugin_utils.utils import assert_error, assert_not_error

CODE = 'x = 1'
CODE_WITH_ERROR = 'class Y: pass'


class MyError(Error):
    code = 'X100'
    message = 'my error with {thing}'


class MyVisitor(Visitor[None]):
    def visit_ClassDef(self, node):
        self.error_from_node(MyError, node, thing=node.name)


class MyPlugin(Plugin[None]):
    name = 'MyPlugin'
    version = '0.0.1'
    visitors = [MyVisitor]


class MyConfig(NamedTuple):
    config_option: str


class MyVisitorWithConfig(Visitor[MyConfig]):
    def visit_ClassDef(self, node):
        self.error_from_node(
            MyError, node, thing=f'{node.name} {self.config.config_option}'
        )


class MyPluginWithConfig(Plugin[MyConfig]):
    name = 'MyPluginWithConfig'
    version = '0.0.1'
    visitors = [MyVisitorWithConfig]


@pytest.fixture()
def code_file(tmpdir):
    code_file = tmpdir.join('./code.py')
    code_file.write('class X:\n    pass')
    return code_file


@pytest.mark.parametrize(
    ('line', 'code', 'result'),
    [
        ('x = 1 # noqa', '', True),
        ('x = 1 # noqa', 'X100', True),
        ('x = 1 # noqa:X100', 'X100', True),
        ('x = 1 # NOQA : x100', 'X100', True),
        ('x = 1 # noqa:X101', 'X100', False),
        ('x = 1 # some comment', 'X100', False),
    ],
)
def test_check_noqa(line, code, result):
    assert check_noqa(line, code) is result


def test_assert_error_ok():
    assert_error(MyVisitor, CODE_WITH_ERROR, MyError, thing='Y')


@pytest.mark.parametrize(
    ('code', 'kwargs'),
    [(CODE, {}), (CODE_WITH_ERROR, {'thing': 'X'})],
    ids=('no error', 'wrong kwargs'),
)
def test_assert_error_fail(code, kwargs):
    with pytest.raises(AssertionError):
        assert_error(MyVisitor, code, MyError, **kwargs)


def test_assert_not_error_ok():
    assert_not_error(MyVisitor, CODE)


def test_assert_not_error_fail():
    with pytest.raises(AssertionError):
        assert_not_error(MyVisitor, CODE_WITH_ERROR)


def test_error_formatting_ok():
    error = MyError(1, 1, thing='XXX')
    assert error.message == 'my error with XXX'


def test_error_formatting_fail():
    with pytest.raises(KeyError):
        MyError(1, 1, wrong_arg='XXX')


def test_plugin_run(code_file):
    with MyPlugin.test_config(None):
        plugin = MyPlugin(ast.parse(''), code_file)
        error = list(plugin.run())[0]
    assert error == (1, 0, 'X100 my error with X', plugin)


def test_plugin_with_config_run(code_file):
    with MyPluginWithConfig.test_config(MyConfig(config_option='123')):
        plugin = MyPluginWithConfig(ast.parse(''), code_file)
        error = list(plugin.run())[0]
    assert error == (1, 0, 'X100 my error with X 123', plugin)
