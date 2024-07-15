
def printer(component, print_collection):
    """print parameters, variables, constraints

    Args:
        component: energiapy components 
        print_collection (str): 'parameters', 'variables', 'constraints'
    """
    for i in getattr(component, print_collection):
        print(i)
