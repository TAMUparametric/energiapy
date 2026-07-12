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


Wrong Python Version
--------------------

Energia 2.0.0+ requires Python 3.12 or higher. 
If you are using an older version of Python, and older version of Energia (1.0.7) will be installed instead.
The two are not backward compatible, and you will likely run into errors.

To check your Python version, run:

.. code-block:: console

    $ python --version
    Python 3.12.0

To check your Energia version, run:

.. code-block:: python

    import energia
    print(energia.__version__)

.. code-block:: console
    
    2.1.6

Older versions use *energiapy* as the package name.




  
