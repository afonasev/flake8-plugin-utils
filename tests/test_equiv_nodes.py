import ast

import pytest
from flake8_plugin_utils.utils import check_equivalent_nodes


@pytest.mark.parametrize(
    ('expr1', 'expr2', 'expected'),
    [
        ('True', 'True', True),
        ('True', 'False', False),
        ('[1, 2, 3]', '[1, 2, 3]', True),
        ('[1, 2, 3]', '[1, 2, 3, 4]', False),
        (
            """[1, {'2': "3"}, 4, some_name, lambda a, b: a + b]""",
            """[
                1,
                {
                    '2': "3"
                },
                4,
                some_name,
                lambda a, b: a + b
            ]""",
            True,
        ),
        (
            """[1, {'2': "3"}, 4, some_name]""",
            """[1, {'2': "3"}, 4, other_name]""",
            False,
        ),
        ('(1, 2, 3)', '[1, 2, 3]', False),
        ('(1, 2, *other, 3)', '(1, 2, *other, 3)', True),
        ('(1, 2, *other, 3)', '(1, *other, 2, 3)', False),
        # set-specific tests
        ('{1, 2, 3}', '{3, 1, 2}', True),
        ('{1, 2, 3}', '{1, 2}', False),
        ('{1, 2, 3}', '{1, 2, 4}', False),
        ("{1, '2', *other, i}", "{'2', 1, *other, i}", True),
        ('{1, 2, *other, 3}', '{2, 1, *another, 3}', False),
        ('{1, 1, 2, 3}', '{1, 2, 3}', True),
        ('{1, 1, 2, 3}', '{1, 2, 3, 1}', True),
        ('{*other}', '{*other, *other}', True),
        ('{*first, *second}', '{*second, *first}', True),
        # dict-specific tests
        ('{1: 2, 3: 4}', '{1: 2}', False),
        ('{1: 2, 3: 4}', '{3: 4, 1: 2}', True),
        ('{1: 2, 3: 4}', '{3: 2, 1: 4}', False),
        ('{1: 2, 3: 4, **other, 5: 6}', '{3: 4, 1: 2, **other, 5: 6}', True),
        ('{1: 2, **other, 3: 4, 5: 6}', '{1: 2, 3: 4, **other, 5: 6}', False),
        (
            '{1: 2, 3: 4, **other, 5: 6}',
            '{3: 4, 1: 2, **another, 5: 6}',
            False,
        ),
        ('{**first, **second}', '{**first, **second}', True),
        ('{**first, **second}', '{**second, **first}', False),
        ('{1: 2, 1: 3}', '{1: 3}', True),
        ('{1: 2, **other, 1: 3}', '{**other, 1: 3}', True),
        ('{1: 2, **other, 1: 3}', '{**other, 1: 2, 1: 3}', True),
        ('{**other}', '{**other, **other}', True),
        ('{1: 2, **other}', '{**other, 1: 2, **other}', True),
    ],
)
def test_equivalent_nodes(expr1, expr2, expected):
    node1 = ast.parse(expr1).body[0]
    node2 = ast.parse(expr2).body[0]
    assert check_equivalent_nodes(node1, node2) is expected
