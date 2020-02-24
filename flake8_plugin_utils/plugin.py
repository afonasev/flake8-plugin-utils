import argparse
import ast
import re
from typing import Any, ClassVar, Generic, Iterable, List, Tuple, Type, TypeVar

from flake8.options.manager import OptionManager

FLAKE8_ERROR = Tuple[int, int, str, 'BasePlugin']
NOQA_REGEXP = re.compile(r'#.*noqa\s*($|[^:\s])', re.I)
NOQA_ERROR_CODE_REGEXP = re.compile(r'#.*noqa\s*:\s*(\w+)', re.I)


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


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[Error] = []

    def error_from_node(
        self, error: Type[Error], node: ast.AST, **kwargs: Any
    ) -> None:
        self.errors.append(error(node.lineno, node.col_offset, **kwargs))


TVisitor = TypeVar('TVisitor', bound=Visitor)


class BasePlugin(Generic[TVisitor]):
    name: str
    version: str
    visitors: List[Type[TVisitor]]

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
        with open(self._filename) as f:
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
    def _create_visitor(cls, visitor_cls: Type[TVisitor]) -> TVisitor:
        return visitor_cls()


class Plugin(BasePlugin[Visitor]):
    pass


TConfig = TypeVar('TConfig')


class ConfigurableVisitor(Generic[TConfig], Visitor):
    def __init__(self, config: TConfig) -> None:
        super().__init__()
        self.config: TConfig = config


class ConfigurablePlugin(
    Generic[TConfig], BasePlugin[ConfigurableVisitor[TConfig]]
):
    config: ClassVar[TConfig]

    @classmethod
    def add_options(cls, option_manager: OptionManager) -> None:
        raise NotImplementedError(
            f'Subclass {cls!r} of ConfigurablePlugin must override add_options'
        )

    @classmethod
    def parse_options(
        cls,
        option_manager: OptionManager,
        options: argparse.Namespace,
        args: List[str],
    ) -> None:
        cls.config = cls.parse_options_to_config(option_manager, options, args)

    @classmethod
    def parse_options_to_config(
        cls,
        option_manager: OptionManager,
        options: argparse.Namespace,
        args: List[str],
    ) -> TConfig:
        raise NotImplementedError(
            f'Subclass {cls!r} of ConfigurablePlugin must override parse_options_to_config'
        )

    @classmethod
    def _create_visitor(
        cls, visitor_cls: Type[ConfigurableVisitor[TConfig]]
    ) -> ConfigurableVisitor[TConfig]:
        return visitor_cls(cls.config)


def check_noqa(line: str, code: str) -> bool:
    if NOQA_REGEXP.search(line):
        return True

    match = NOQA_ERROR_CODE_REGEXP.search(line)
    if match:
        return match.groups()[0].lower() == code.lower()

    return False
