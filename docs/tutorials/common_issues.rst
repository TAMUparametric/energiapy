.. _common_issues:

Common Issues
=================


Name exclusivity
-----------------

When defining components, ensure that each component has a unique name irrespective of component type. 
For example, you cannot have a `Resource` and `Process` both named "solar". 

The following will raise an error:

.. code-block:: python

    from energia import Model, Resource, Process

    m = Model()

    m.solar = Resource()
    m.solar = Process()  # This will raise an error


.. code-block:: console

    Traceback (most recent call last):
      ...
    ValueError: solar already defined

    