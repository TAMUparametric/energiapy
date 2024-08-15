def get_depth(dict_: dict) -> int:
    """finds depth of dict_

    Args:
        dict_ (dict): dict_

    Returns:
        int: depth of dict_
    """
    if not isinstance(dict_, dict) or not dict_:
        # If the input is not a dict_ or is an empty dict_, return 0
        return 0

    # Recursively find the maximum depth of nested dictionaries
    max_depth = max(get_depth(value) for value in dict_.values())

    # Return one more than the maximum depth found
    return 1 + max_depth


def flatten(dict_: dict, key_: tuple = ()) -> dict:
    """makes a flat dictionary from a nested dictionary

    Args:
        dict_ (dict): nested dictionary. {'a': {'b': {'c': 1}}}
        key_ (tuple, optional): empty, dont give an input here. Defaults to ().

    Returns:
        dict: flat dictionary. {('a', 'b', 'c'): 1}
    """
    items = []
    for key, val in dict_.items():
        key_upd = key_ + (key,)
        if isinstance(val, dict):
            items.extend(flatten(val, key_upd).items())
        else:
            items.append((key_upd, val))
    return dict(items)
