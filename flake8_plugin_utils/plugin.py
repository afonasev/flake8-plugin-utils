import argparse
import ast
import re
from contextlib import contextmanager
from typing import (
    Any,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

from flake8.options.manager import OptionManager

FLAKE8_ERROR = Tuple[int, int, str, 'Plugin']
NOQA_REGEXP = re.compile(r'#.*noqa\s*($|[^:\s])', re.I)
NOQA_ERROR_CODE_REGEXP = re.compile(r'#.*noqa\s*:\s*(\w+)', re.I)

TConfig = TypeVar('TConfig')


class Error:
    code: str
    message: str
    lineno: int
    col_offset: int

    def __init__(self, lineno: int, col_offset: int, **kwargs: Any) -> None:
        self.lineno = lineno
        self.col_offset = col_offset
        self.message = self.formatted_message(**kwargs)

    @classmethod
    def formatted_message(cls, **kwargs: Any) -> str:
        return cls.message.format(**kwargs)


class Visitor(Generic[TConfig], ast.NodeVisitor):
    def __init__(self, config: Optional[TConfig] = None) -> None:
        self.errors: List[Error] = []
        self._config: Optional[TConfig] = config

    @property
    def config(self) -> TConfig:
        if self._config is None:
            raise TypeError(
                f'{self} was initialized without a config.  Did you forget '
                f'to override parse_options_to_config in your plugin class?'
            )
        return self._config

    def error_from_node(
        self, error: Type[Error], node: ast.AST, **kwargs: Any
    ) -> None:
        self.errors.append(error(node.lineno, node.col_offset, **kwargs))


class Plugin(Generic[TConfig]):
    name: str
    version: str
    visitors: List[Type[Visitor[TConfig]]]
    config: TConfig

    def __init__(self, tree: ast.AST, filename: str) -> None:
        self._tree: ast.AST = tree
        self._filename: str = filename
        self._lines: List[str] = []

    def run(self) -> Iterable[FLAKE8_ERROR]:
        if not self._tree or not self._lines:
            self._load_file()

        for visitor_cls in self.visitors:
            visitor = self._create_visitor(visitor_cls)
            visitor.visit(self._tree)

            for error in visitor.errors:
                line = self._lines[error.lineno - 1]
                if not check_noqa(line, error.code):
                    yield self._error(error)

    def _load_file(self) -> None:
        # lines is only used for noqa verification,
        # and we can ignore encoding errors
        with open(self._filename, errors='replace') as f:
            self._lines = f.readlines()
        self._tree = ast.parse(''.join(self._lines))

    def _error(self, error: Error) -> FLAKE8_ERROR:
        return (
            error.lineno,
            error.col_offset,
            f'{error.code} {error.message}',
            self,
        )

    @classmethod
    def _create_visitor(
        cls, visitor_cls: Type[Visitor[TConfig]]
    ) -> Visitor[TConfig]:
        if cls.config is None:
            return visitor_cls()

        return visitor_cls(config=cls.config)

    @classmethod
    def parse_options(
        cls,
        option_manager: OptionManager,
        options: argparse.Namespace,
        args: List[str],
    ) -> None:
        cls.config = cls.parse_options_to_config(option_manager, options, args)

    @classmethod
    def parse_options_to_config(  # pylint: disable=unused-argument
        cls,
        option_manager: OptionManager,
        options: argparse.Namespace,
        args: List[str],
    ) -> Optional[TConfig]:
        return None

    @classmethod
    @contextmanager
    def test_config(cls, config: TConfig) -> Iterator[None]:
        """
        Context manager to add a config to the plugin class for testing.

        Normally flake8 will call `parse_options` on the plugin, which will
        set the config on the plugin class.  However, this is not the case
        when creating a plugin manually in tests.  This context manager can
        be used to pass in a config and clean up afterwards.
        """
        cls.config = config
        try:
            yield
        finally:
            del cls.config


def check_noqa(line: str, code: str) -> bool:
    if NOQA_REGEXP.search(line):
        return True

    match = NOQA_ERROR_CODE_REGEXP.search(line)
    if match:
        return match.groups()[0].lower() == code.lower()

    return False
