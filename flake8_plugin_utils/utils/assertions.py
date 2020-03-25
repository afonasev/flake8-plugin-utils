import ast
from textwrap import dedent
from typing import Any, Optional, Type

from ..plugin import Error, TConfig, Visitor


def _error_from_src(
    visitor_cls: Type[Visitor[TConfig]],
    src: str,
    config: Optional[TConfig] = None,
) -> Optional[Error]:
    visitor = visitor_cls(config=config)
    tree = ast.parse(dedent(src))
    visitor.visit(tree)
    if not visitor.errors:
        return None
    assert len(visitor.errors) == 1
    return visitor.errors[0]


def assert_error(
    visitor_cls: Type[Visitor[TConfig]],
    src: str,
    expected: Type[Error],
    config: Optional[TConfig] = None,
    **kwargs: Any,
) -> None:
    err = _error_from_src(visitor_cls, src, config=config)
    assert err, f'Error "{expected.message}" not found in\n{src}'
    assert isinstance(err, expected)

    expected_message = expected.formatted_message(**kwargs)
    assert (
        expected_message == err.message
    ), f'Expected error with message "{expected_message}", got "{err.message}"'


def assert_not_error(
    visitor_cls: Type[Visitor[TConfig]],
    src: str,
    config: Optional[TConfig] = None,
) -> None:
    err = _error_from_src(visitor_cls, src, config=config)
    assert not err, f'Error "{err.message}" found in\n{src}'  # type: ignore
