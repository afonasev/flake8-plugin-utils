import pytest
from flake8_plugin_utils.plugin import Error, Visitor, check_noqa
from flake8_plugin_utils.utils import assert_error, assert_not_error

CODE = 'x = 1'
CODE_WITH_ERROR = 'class Y: pass'


class MyError(Error):
    code = 'X100'
    message = 'my error'


class MyVisitor(Visitor):
    def visit_ClassDef(self, node):
        self.error_from_node(MyError, node)


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


def test_assert_error_ok():
    assert_error(MyVisitor, CODE_WITH_ERROR, MyError)


def test_assert_error_fail():
    with pytest.raises(AssertionError):
        assert_error(MyVisitor, CODE, MyError)


def test_assert_not_error_ok():
    assert_not_error(MyVisitor, CODE)


def test_assert_not_error_fail():
    with pytest.raises(AssertionError):
        assert_not_error(MyVisitor, CODE_WITH_ERROR)
