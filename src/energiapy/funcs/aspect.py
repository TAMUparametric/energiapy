from ..model.aspect import Aspect
from ..model.type.input import Input


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
            aspect=Input.match(attr_name), component=component)
    else:
        new_value = current_value

    if not isinstance(attr_value, Aspect):
        new_value.add(value=attr_value, aspect=Input.match(attr_name), component=component,
                      horizon=component.horizon, declared_at=component.declared_at)
        setattr(component, attr_name, new_value)

        for i in ['parameters', 'variables', 'constraints']:
            if hasattr(new_value, i):
                getattr(component, i).extend(getattr(new_value, i))
