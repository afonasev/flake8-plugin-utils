import pytest
from flake8_plugin_utils import Error, Plugin, Visitor, check_noqa, get_error


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


@pytest.mark.parametrize(
    ('line', 'code', 'result'),
    (
        ('x = 1 # noqa', '', True),
        ('x = 1 # noqa', 'X100', True),
        ('x = 1 # noqa:X100', 'X100', True),
        ('x = 1 # NOQA : x100', 'X100', True),
        ('x = 1 # noqa:X101', 'X100', False),
    ),
)
def test_check_noqa(line, code, result):
    assert check_noqa(line, code) is result


def test_error_msg(tmpdir):
    assert get_error(MyPlugin, tmpdir, 'class Y: pass') == 'X100 my error'


@pytest.mark.parametrize('src', ('class X:\n    pass', '\nclass Y: pass'))
def test_error_exists(tmpdir, src):
    assert get_error(MyPlugin, tmpdir, src)


@pytest.mark.parametrize('src', ('def x():\n    pass', '\nx = 13'))
def test_error_not_exists(tmpdir, src):
    assert not get_error(MyPlugin, tmpdir, src)
