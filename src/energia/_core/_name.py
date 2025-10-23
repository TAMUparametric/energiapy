"""Inherited _Name (reprs) class"""

from ._hash import _Hash


# Donot use this for any component that has a built-in name generating scheme
# Use Hash instead
class _Name(_Hash):
    """
    Inherited by components that only have a name.

    These do not feature as indices in the model
    nor do they have modeling aspects.

    For components with a:
        - mathematical program, use `X`
        - mathematical program and
          input parameters (modeling aspects), use `Component`

    :param label: Label used for plotting. Defaults to None.
    :type label: str, optional

    :ivar name: Name of the object. Defaults to ''.
    :vartype name: str

    .. note:
        - `name` is set when the component is made a Model attribute.
    """

    def __init__(self, label: str = ""):
        self.label = label
        self.name = ""
