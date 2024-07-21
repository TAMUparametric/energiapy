from ..model.type.aspect import AspectType


def namer(component, name, horizon):
    """Updates component name and horizon 
    triggers the updating of attributes to Aspect

    Args:
        component: energiapy component
        name (str): name of component
        horizon (Horizon): Horizon of the problem
    """
    setattr(component, 'name', name)
    setattr(component, 'horizon', horizon)
    setattr(component, 'named', True)

    for i in AspectType.aspects():
        if hasattr(component, i) and getattr(component, i) is not None:
            setattr(component, i, getattr(component, i))
