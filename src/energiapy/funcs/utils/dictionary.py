def get_depth(attr_input: dict) -> int:
    """finds depth of attr_input

    Args:
        attr_input (dict): attr_input

    Returns:
        int: depth of attr_input
    """
    if not isinstance(attr_input, dict) or not attr_input:
        # If the input is not a attr_input or is an empty attr_input, return 0
        return 0

    # Recursively find the maximum depth of nested dictionaries
    max_depth = max(get_depth(value) for value in attr_input.values())

    # Return one more than the maximum depth found
    return 1 + max_depth
