from ...model.type.aspect import AspectType
from ...model.aspect import Aspect


def is_aspect_ready(component, attr_name, attr_value) -> bool:
    """Checks if attribute is ready to be made into an Aspect

    Args:
        component (energiapy.components): Resource, Process, Location, Transport, Linkage
        attr_name (str): name of attribute
        attr_value (): value assigned to aspect attribute

    Returns:
        bool: True if attribute is ready to be aspected
    """
    # TODO - write value types
    cndtn_named = hasattr(component, 'named') and getattr(component, 'named')
    cndtn_is_aspect = attr_name in AspectType.aspects()
    cndtn_value = attr_value is not None

    if cndtn_named and cndtn_is_aspect and cndtn_value:
        return True
    else:
        return False


def aspecter(component, attr_name, attr_value):
    """updates the attribute as an Aspect

    Args:
        component: energiapy component
        attr_name (str): name of the attribute
        attr_value: value of the attribute 
    """
    current_value = getattr(component, attr_name)

    if not isinstance(current_value, Aspect):
        new_value = Aspect(
            aspect=AspectType.match(attr_name), component=component)
    else:
        new_value = current_value

    if not isinstance(attr_value, Aspect):
        new_value.add(value=attr_value, aspect=AspectType.match(attr_name), component=component,
                      horizon=component.horizon, declared_at=component.declared_at)
        setattr(component, attr_name, new_value)

        for i in ['parameters', 'variables', 'constraints']:
            if hasattr(new_value, i):
                getattr(component, i).extend(getattr(new_value, i))
