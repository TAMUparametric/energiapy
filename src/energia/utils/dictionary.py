"""dictionary utils"""

from collections import defaultdict


def get_depth(dict_: dict) -> int:
    """
    Finds the depth of a dictionary.

    Parameters
    ----------
    dict_ : :class:`dict`
        The dictionary to measure.

    Returns
    -------
    int
        Depth of the dictionary.
    """
    if not isinstance(dict_, dict) or not dict_:
        # If the input is not a dict_ or is an empty dict_, return 0
        return 0

    # Recursively find the maximum depth of nested dictionaries
    max_depth = max(get_depth(value) for value in dict_.values())

    # Return one more than the maximum depth found
    return 1 + max_depth


def flatten(dict_: dict, key_: tuple = ()) -> dict:
    """
    Makes a flat dictionary from a nested dictionary.

    Parameters
    ----------
    dict_ : :class:`dict`
        Nested dictionary. For example: ``{'a': {'b': {'c': 1}}}``.
    key_ : :class:`tuple`, optional
        Internal use; do not provide an input. Defaults to ``()``.

    Returns
    -------
    :class:`dict`
        Flattened dictionary. For example: ``{('a', 'b', 'c'): 1}``.
    """
    items = []
    for key, val in dict_.items():
        key_upd = key_ + (key,)
        if isinstance(val, dict):
            items.extend(flatten(val, key_upd).items())
        else:
            items.append((key_upd, val))
    return dict(items)


def tupler(d: dict, path: tuple = ()) -> list[tuple[str]]:
    """
    Makes a list of tuples of keys in a nested dictionary.

    Parameters
    ----------
    d : :class:`dict`
        The dictionary to traverse.
    current_path : :class:`tuple`, optional
        Path taken to get to a value. Defaults to ``()``.

    Returns
    -------
    :class:`list` of :class:`tuple` of :class:`str`
        List of tuples of keys representing the paths to each value.
    """

    result = []

    for k, v in d.items():
        path_ = path + (k,)
        result.append(path_)

        if isinstance(v, dict):
            result.extend(tupler(v, path_))

        if isinstance(v, set):
            for v_ in v:
                result.append(path_ + (v_,))

    return result


def merge_trees(d1: dict, d2: dict) -> dict:
    """Recursively merge two tree-like dicts (values always dicts)."""
    result = dict(d1)  # shallow copy of d1
    for k, v in d2.items():
        if k in result:
            result[k] = merge_trees(
                result[k],
                v,
            )  # recurse since v must also be a dict
        else:
            result[k] = v
    return result


def dictify(d: defaultdict | dict) -> dict:
    """Recursively convert defaultdict to dict."""
    if isinstance(d, defaultdict):
        return {k: dictify(v) for k, v in d.items()}
    return d
