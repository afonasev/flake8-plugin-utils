from typing import Callable, Iterator, Sequence, TypeVar

_T = TypeVar('_T')


def partition_by_indexes(
    lst: Sequence[_T], indexes: Sequence[int]
) -> Iterator[Sequence[_T]]:
    """
    Partitions a sequence around the given indexes.

    The elements at the partition indexes are not present in the result.
    """
    if not indexes:
        yield lst
        return

    last_index = -1
    for index in indexes:
        yield lst[last_index + 1 : index]
        last_index = index
    yield lst[last_index + 1 :]


def match_elements(
    lst1: Sequence[_T], lst2: Sequence[_T], condition: Callable[[_T, _T], bool]
) -> bool:
    """
    Tries to match elements of lst1 and lst2 according to given condition.

    :param condition: a function returning True if the parameters match
    :return: True if for each element in lst1 there is a matching element
    in lst2 according to condition, false otherwise.
    """

    # sanity check, should not happen
    if len(lst1) != len(lst2):
        return False  # pragma: no cover

    # this is N^2, but I don't have an idea how to optimize it
    lst2_copy = list(lst2)
    for elem1 in lst1:
        for elem2 in lst2_copy:
            if condition(elem1, elem2):
                lst2_copy.remove(elem2)
                break
        else:
            return False
    return True
