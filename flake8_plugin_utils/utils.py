import ast
from textwrap import dedent
from typing import Optional, Type

from .plugin import Error, Visitor


def _error_from_src(visitor_cls: Type[Visitor], src: str) -> Optional[Error]:
    visitor = visitor_cls()
    tree = ast.parse(dedent(src.strip()))
    visitor.visit(tree)
    if not visitor.errors:
        return None
    assert len(visitor.errors) == 1
    return visitor.errors[0]


def assert_error(
    visitor_cls: Type[Visitor], src: str, expected: Type[Error]
) -> None:
    err = _error_from_src(visitor_cls, src)
    assert err, f'Error "{expected.message}" not found in\n{src}'
    assert isinstance(err, expected)


def assert_not_error(visitor_cls: Type[Visitor], src: str) -> None:
    err = _error_from_src(visitor_cls, src)
    assert not err, f'Error "{err.message}" found in\n{src}'  # type: ignore
