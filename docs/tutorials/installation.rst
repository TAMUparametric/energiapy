.. _installation:

Installation
============

This should help you get Energia up and running on your PC.

What you are going to need:

1. A computer
2. Python >=3.12
3. Will power

Setting up an Environment
-------------------------


The choice of whether to use a conda or virtual environment is up to you.

In your terminal, run the following:

For a virtual environment (preferred, in the root directory):

.. code-block:: bash

    python3.13 -m venv energiaenv

.. tip:: For a conda environment:

    .. code-block:: bash

        conda create --name energiaenv python=3.13

Now that your environment is ready, you will need to activate it.

Activating an Environment
-------------------------

For a virtual environment on Windows PowerShell or Command Prompt:

.. code-block:: bat

    energiaenv\Scripts\activate

.. tip:: On Mac or Linux:

    .. code-block:: bash

        source energiaenv/bin/activate

.. tip:: For a conda environment:

    .. code-block:: bash

        conda activate energiaenv



Installing Energia
------------------

Energia supports the standard pip installation:

.. code-block:: bash

    pip install energiapy


Integrated Development Environments (IDEs)
------------------------------------------

Handling environments and such is much simpler if you use an IDE. Here are some guides for popular IDEs:

- **Visual Studio Code**: `Python environments in VS Code <https://code.visualstudio.com/docs/python/environments>`_

- **PyCharm**: `Configuring Python interpreter <https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html>`_




