import ast
from collections import deque
from typing import Any, Deque, List, Optional, Tuple

from ._internal import match_elements, partition_by_indexes

_DictKVPair = Tuple[Optional[ast.AST], ast.AST]


def _check_equivalent_key_value_pair(
    pair1: _DictKVPair, pair2: _DictKVPair,
) -> bool:
    """
    Callback for _match_list_elements for dict key-value pairs.
    """
    key1, value1 = pair1
    key2, value2 = pair2

    # should not happen because keys are None only on partition positions
    if key1 is None or key2 is None:
        return False  # pragma: no cover

    return check_equivalent_nodes(key1, key2) and check_equivalent_nodes(
        value1, value2
    )


def _check_duplicate_dict_item(pair1: _DictKVPair, pair2: _DictKVPair) -> bool:
    key1, value1 = pair1
    key2, value2 = pair2

    if key1 is None and key2 is None:  # both are expansions
        return check_equivalent_nodes(value1, value2)

    if key1 is None or key2 is None:  # one is expansion, other is not
        return False

    return check_equivalent_nodes(key1, key2)


def _key_value_pairs_without_duplicates(node: ast.Dict) -> List[_DictKVPair]:
    """
    Returns the list of key-value pairs of given ast.Dict without duplicates.

    If duplicates are found, the element closer to the end is kept,
    in accordance with Python's behaviour for such dicts.
    """
    all_pairs = list(zip(node.keys, node.values))
    result: List[_DictKVPair] = []
    for candidate in reversed(all_pairs):
        if any(
            _check_duplicate_dict_item(candidate, added) for added in result
        ):
            continue
        result.append(candidate)
    result.reverse()
    return result


def _check_equivalent_dicts(node1: ast.Dict, node2: ast.Dict) -> bool:
    """
    Checks whether two given AST dicts are equivalent.
    """

    # 1: remove duplicates
    pairs1 = _key_value_pairs_without_duplicates(node1)
    pairs2 = _key_value_pairs_without_duplicates(node2)

    # 2: check size
    if len(pairs1) != len(pairs2):
        return False

    # 3: check expansions, e.g. {**other}
    # must be same expressions on the same positions
    expansion_positions = [
        i for i, (key, _) in enumerate(pairs1) if key is None
    ]
    if expansion_positions != [
        i for i, (key, _) in enumerate(pairs2) if key is None
    ]:
        return False

    for index in expansion_positions:
        if not check_equivalent_nodes(pairs1[index][1], pairs2[index][1]):
            return False

    # 4: check chunks between expansions,
    # regardless of order within chunk
    for chunk1, chunk2 in zip(
        partition_by_indexes(pairs1, expansion_positions),
        partition_by_indexes(pairs2, expansion_positions),
    ):
        if not match_elements(
            chunk1, chunk2, condition=_check_equivalent_key_value_pair
        ):
            return False
    return True


def _set_elements_without_duplicates(node: ast.Set) -> List[ast.AST]:
    """
    Returns the list of elements of the given ast.Set without duplicates.

    If duplicates are found, the element closer to the beginning is kept,
    in accordance with Python's behaviour for such sets.
    """
    result: List[ast.AST] = []
    for candidate in node.elts:
        if any(check_equivalent_nodes(candidate, added) for added in result):
            continue
        result.append(candidate)
    return result


def _check_equivalent_sets(node1: ast.Set, node2: ast.Set) -> bool:
    """
    Checks whether two given AST sets are equivalent.
    """

    # 1: remove duplicates
    elements1 = _set_elements_without_duplicates(node1)
    elements2 = _set_elements_without_duplicates(node2)

    # 2: check size
    if len(elements1) != len(elements2):
        return False

    # 3: check elements regardless of order
    return match_elements(
        elements1, elements2, condition=check_equivalent_nodes
    )


def check_equivalent_nodes(  # noqa:C901 pylint:disable=too-many-return-statements,too-many-branches
    node1: ast.AST, node2: ast.AST
) -> bool:
    """
    Checks that two given AST nodes represent the same AST.

    Line and column numbers are not taken into account.
    """

    queue1: Deque[Any] = deque([node1])
    queue2: Deque[Any] = deque([node2])

    while queue1:
        value1 = queue1.popleft()
        value2 = queue2.popleft()
        if type(value1) != type(  # pylint: disable=unidiomatic-typecheck
            value2
        ):
            return False

        if isinstance(value1, ast.Dict):
            if not _check_equivalent_dicts(value1, value2):
                return False
        elif isinstance(value1, ast.Set):
            if not _check_equivalent_sets(value1, value2):
                return False
        elif isinstance(value1, ast.AST):
            for field_name in value1._fields:
                queue1.append(getattr(value1, field_name))
                queue2.append(getattr(value2, field_name))
        elif isinstance(value1, (list, tuple)):
            if len(value1) != len(value2):
                return False
            queue1.extend(value1)
            queue2.extend(value2)
        else:
            if value1 != value2:
                return False

    return True
